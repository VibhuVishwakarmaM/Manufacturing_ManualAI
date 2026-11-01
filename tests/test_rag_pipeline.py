import pytest
from django.contrib.auth.models import User
from apps.machines.models import Machine
from apps.manuals.models import Manual
from apps.document_processing.models import DocumentChunk
from integrations.embeddings import get_embedding_provider
from apps.rag_engine.engine import RAGEngine, INSUFFICIENT_EVIDENCE_RESPONSE
from apps.question_history.models import QuestionHistory, AnswerFeedback

@pytest.fixture
def rag_fixture(db):
    user = User.objects.create_user('rag_engineer', 'rag@test.com', 'Pass123!')
    machine = Machine.objects.create(name='Haas CNC VF-2', model_number='VF2-2024')
    manual = Manual.objects.create(
        machine=machine,
        title='VF-2 Maintenance & Lubrication Guide',
        original_filename='vf2_manual.pdf',
        revision='Rev 2.0',
        processing_status=Manual.STATUS_INDEXED
    )

    emb = get_embedding_provider()
    passage_text = "The spindle bearings require Mobil SHC 625 synthetic oil at 25 PSI pressure every 2000 hours."
    vec = emb.embed_text(passage_text)

    chunk = DocumentChunk.objects.create(
        manual=manual,
        machine=machine,
        chunk_index=0,
        page_start=14,
        page_end=14,
        content=passage_text,
        metadata={
            "machine_id": str(machine.id),
            "manual_id": str(manual.id),
            "manual_title": manual.title,
            "revision": manual.revision,
            "page_number": 14,
        },
        embedding=vec
    )

    return {
        'user': user,
        'machine': machine,
        'manual': manual,
        'chunk': chunk
    }

@pytest.mark.django_db
class TestRAGPipeline:

    def test_evidence_grounded_answer_and_citations(self, rag_fixture):
        """Verify the RAG pipeline answers based on evidence and includes verifiable citations."""
        rag = RAGEngine()
        result = rag.answer_question(
            user=rag_fixture['user'],
            machine_id=str(rag_fixture['machine'].id),
            question_text="What oil is required for the spindle bearings?"
        )

        assert result['status'] == 'ANSWERED'
        assert len(result['citations']) > 0
        citation = result['citations'][0]
        assert citation['manual_title'] == 'VF-2 Maintenance & Lubrication Guide'
        assert citation['revision'] == 'Rev 2.0'
        assert citation['page_number'] == 14
        assert 'Mobil SHC 625' in result['answer']

        # Verify persistence in QuestionHistory
        saved_q = QuestionHistory.objects.get(id=result['id'])
        assert saved_q.user == rag_fixture['user']
        assert saved_q.machine == rag_fixture['machine']
        assert saved_q.status == 'ANSWERED'

    def test_unsupported_question_insufficient_evidence(self, rag_fixture):
        """
        Verify that unsupported questions (e.g. maximum operating temperature)
        strictly return the configured insufficient evidence response.
        """
        rag = RAGEngine()
        result = rag.answer_question(
            user=rag_fixture['user'],
            machine_id=str(rag_fixture['machine'].id),
            question_text="What is the maximum operating ambient temperature of this machine?"
        )

        assert result['status'] == 'INSUFFICIENT_EVIDENCE'
        assert result['answer'] == INSUFFICIENT_EVIDENCE_RESPONSE

        # Verify recorded with insufficient status
        saved_q = QuestionHistory.objects.get(id=result['id'])
        assert saved_q.status == QuestionHistory.STATUS_INSUFFICIENT

    def test_answer_feedback_submission(self, rag_fixture):
        """Verify engineer can submit feedback on an answer."""
        rag = RAGEngine()
        result = rag.answer_question(
            user=rag_fixture['user'],
            machine_id=str(rag_fixture['machine'].id),
            question_text="What oil is required for spindle?"
        )

        q_obj = QuestionHistory.objects.get(id=result['id'])
        feedback = AnswerFeedback.objects.create(
            question=q_obj,
            user=rag_fixture['user'],
            rating=AnswerFeedback.RATING_HELPFUL,
            feedback_text="Accurate page reference."
        )

        assert feedback.rating == 'HELPFUL'
        assert q_obj.feedbacks.count() == 1
