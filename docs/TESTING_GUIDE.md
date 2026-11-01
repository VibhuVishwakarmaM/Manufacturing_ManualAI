# Testing Guide

The project includes an automated test suite implemented with `pytest` and `pytest-django`. All tests mock external LLM and embedding APIs, requiring zero paid external credits to execute.

---

## 1. Running the Automated Test Suite

### Run All Tests
```bash
pytest -v
```

### Run Mandatory Organizer Tests Only
```bash
# MANDATORY TEST 1: Restricted upload access
pytest tests/test_rbac_permissions.py -k "test_mandatory_test_1" -v

# MANDATORY TEST 2: Machine-specific retrieval isolation
pytest tests/test_retrieval_isolation.py -k "test_mandatory_test_2" -v
```

---

## 2. Test Suite Breakdown

### 1. `tests/test_rbac_permissions.py`
- `test_anonymous_user_blocked_from_protected_endpoints`: Verifies anonymous requests receive 302/401/403.
- `test_mandatory_test_1_engineer_cannot_upload_manual`: **[MANDATORY TEST 1]** Verifies an Engineer cannot upload manuals via API or Web, cannot register machines, and cannot access user administration.
- `test_administrator_can_perform_administrative_actions`: Verifies Administrator can create machines and manage operators.
- `test_supervisor_history_review_permissions`: Verifies Supervisor can view cross-engineer history while engineers are blocked from accessing supervisor endpoints.

### 2. `tests/test_retrieval_isolation.py`
- `test_mandatory_test_2_machine_specific_retrieval_isolation`: **[MANDATORY TEST 2]** Seeds Machine A and Machine B with distinct manuals and verifies that querying Machine A returns zero passages from Machine B even with zero threshold.
- `test_rag_pipeline_insufficient_evidence_when_querying_other_machine_topic`: Verifies asking Machine A about a Machine B concept returns `INSUFFICIENT_EVIDENCE`.

### 3. `tests/test_pdf_processing.py`
- `test_pymupdf_extraction_and_page_preservation`: Verifies PyMuPDF page-by-page extraction preserving 1-indexed numbering.
- `test_document_chunker_metadata_preservation`: Verifies chunker retains `manual_id`, `machine_id`, and page spans.
- `test_invalid_pdf_validation`: Rejects non-PDF extensions, 0-byte files, and corrupted binaries.

### 4. `tests/test_rag_pipeline.py`
- `test_evidence_grounded_answer_and_citations`: Verifies grounded response generation, manual title, revision, and page citations.
- `test_unsupported_question_insufficient_evidence`: Verifies unsupported specs return the required insufficient evidence response.
- `test_answer_feedback_submission`: Verifies operator feedback persistence.

### 5. `tests/test_api_endpoints.py`
- `test_auth_login_and_me_endpoints`: Tests session login and user role profile.
- `test_dashboard_summary_endpoint`: Tests dashboard telemetry API.
- `test_manual_status_endpoint`: Tests manual processing status endpoint.
- `test_unauthorized_pdf_view_requires_authentication`: Verifies PDF files cannot be downloaded without authentication.
