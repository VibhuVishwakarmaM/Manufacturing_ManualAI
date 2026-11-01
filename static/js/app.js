/**
 * MANUFACTURING MANUAL AI ASSISTANT - CLIENT APPLICATION CONTROLLER
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showLoading(message = "Processing equipment manual query...") {
    const overlay = document.getElementById('loadingOverlay');
    const msgEl = document.getElementById('loadingMessage');
    if (msgEl) msgEl.innerText = message;
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

/**
 * Handle AI Question Submission via REST API
 */
async function submitQuestion() {
    const machineSelect = document.getElementById('machineSelector');
    const questionInput = document.getElementById('questionInput');
    const resultsContainer = document.getElementById('qaResultsContainer');
    const answerTextEl = document.getElementById('answerText');
    const evidenceListEl = document.getElementById('evidenceList');
    const questionStatusEl = document.getElementById('questionStatusBadge');
    const confidenceScoreEl = document.getElementById('confidenceScoreBadge');
    const feedbackSection = document.getElementById('feedbackSection');

    if (!machineSelect || !machineSelect.value) {
        alert("Please select a target equipment machine first.");
        return;
    }

    const questionText = questionInput.value.trim();
    if (!questionText) {
        alert("Please enter a maintenance question.");
        return;
    }

    showLoading("Querying machine manual vector index and generating verified answer...");

    try {
        const response = await fetch('/questions/api/questions/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                machine_id: machineSelect.value,
                question: questionText
            })
        });

        const data = await response.json();
        hideLoading();

        if (!response.ok) {
            alert("Error: " + (data.error || "Failed to process question."));
            return;
        }

        // Show Results Container
        if (resultsContainer) resultsContainer.style.display = 'block';

        // Update Status & Score
        if (questionStatusEl) {
            if (data.status === 'ANSWERED') {
                questionStatusEl.className = 'badge badge-status badge-status-indexed';
                questionStatusEl.innerText = 'VERIFIED EVIDENCE';
            } else if (data.status === 'INSUFFICIENT_EVIDENCE') {
                questionStatusEl.className = 'badge badge-status badge-status-failed';
                questionStatusEl.innerText = 'INSUFFICIENT INFORMATION';
            } else {
                questionStatusEl.className = 'badge badge-status';
                questionStatusEl.innerText = data.status;
            }
        }

        if (confidenceScoreEl) {
            confidenceScoreEl.innerText = `Top Relevance: ${(data.confidence_score * 100).toFixed(1)}%`;
        }

        // Render Answer
        if (answerTextEl) {
            answerTextEl.innerHTML = formatMarkdown(data.answer);
            const box = answerTextEl.closest('.answer-box');
            if (box) {
                if (data.status === 'INSUFFICIENT_EVIDENCE') {
                    box.classList.add('insufficient-warning');
                } else {
                    box.classList.remove('insufficient-warning');
                }
            }
        }

        // Render Evidence Cards
        if (evidenceListEl) {
            evidenceListEl.innerHTML = '';
            if (data.citations && data.citations.length > 0) {
                data.citations.forEach((cit, index) => {
                    const card = document.createElement('div');
                    card.className = 'evidence-card';
                    card.innerHTML = `
                        <div class="evidence-header">
                            <div>
                                <span class="evidence-source"><i class="bi bi-file-earmark-pdf me-1"></i> ${escapeHtml(cit.manual_title)}</span>
                                <span class="text-secondary ms-1">(${escapeHtml(cit.revision)})</span>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="evidence-page-badge">Page ${escapeHtml(String(cit.page_number))}</span>
                                <a href="/manuals/${cit.manual_id}/view/#page=${cit.page_number}" target="_blank" class="btn btn-sm btn-outline-industrial" title="Open PDF at this page">
                                    <i class="bi bi-box-arrow-up-right"></i>
                                </a>
                            </div>
                        </div>
                        <div class="evidence-snippet">${escapeHtml(cit.snippet)}</div>
                    `;
                    evidenceListEl.appendChild(card);
                });
            } else {
                evidenceListEl.innerHTML = `
                    <div class="text-secondary text-center py-3">
                        <i class="bi bi-shield-slash fs-3 d-block mb-2 text-warning"></i>
                        No manual passages met the similarity confidence threshold for this query.
                    </div>
                `;
            }
        }

        // Enable feedback buttons
        if (feedbackSection && data.id) {
            feedbackSection.dataset.questionId = data.id;
            feedbackSection.style.display = 'flex';
        }

        // Scroll smoothly to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        hideLoading();
        alert("Unexpected network or server error: " + err);
    }
}

/**
 * Handle feedback rating
 */
async function submitFeedback(rating) {
    const feedbackSection = document.getElementById('feedbackSection');
    if (!feedbackSection || !feedbackSection.dataset.questionId) return;

    const qId = feedbackSection.dataset.questionId;
    try {
        const response = await fetch(`/questions/api/questions/${qId}/feedback/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ rating: rating })
        });
        if (response.ok) {
            const btnHelpful = document.getElementById('btnHelpful');
            const btnUnhelpful = document.getElementById('btnUnhelpful');
            if (rating === 'HELPFUL') {
                btnHelpful.classList.add('active-helpful');
                btnUnhelpful.classList.remove('active-unhelpful');
            } else {
                btnUnhelpful.classList.add('active-unhelpful');
                btnHelpful.classList.remove('active-helpful');
            }
        }
    } catch (e) {
        console.error("Failed to submit feedback", e);
    }
}

function usePresetQuestion(text) {
    const qInput = document.getElementById('questionInput');
    if (qInput) {
        qInput.value = text;
        submitQuestion();
    }
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Line breaks
    html = html.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
    return html;
}
