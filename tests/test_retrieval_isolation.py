import pytest
from apps.machines.models import Machine
from apps.manuals.models import Manual
from apps.document_processing.models import DocumentChunk
from integrations.embeddings import get_embedding_provider
from integrations.vector_store import get_vector_store
from apps.rag_engine.engine import RAGEngine
from django.contrib.auth.models import User

@pytest.fixture
def isolation_setup(db):
    user = User.objects.create_user('isolation_tester', 'iso@test.com', 'Pass123!')
    emb_provider = get_embedding_provider()

    # Machine A: CNC Milling Center
    machine_a = Machine.objects.create(name='Machine A (CNC Mill)', model_number='MODEL-A')
    manual_a = Manual.objects.create(
        machine=machine_a,
        title='Machine A Operation Manual',
        original_filename='manual_a.pdf',
        revision='Rev A',
        processing_status=Manual.STATUS_INDEXED
    )

    content_a1 = "Machine A spindle lubrication procedure: Fill reservoir with Mobil SHC 625 synthetic oil."
    content_a2 = "Machine A spindle bearing tolerance must not exceed 0.005 mm runout."

    vec_a1 = emb_provider.embed_text(content_a1)
    vec_a2 = emb_provider.embed_text(content_a2)

    chunk_a1 = DocumentChunk.objects.create(
        manual=manual_a,
        machine=machine_a,
        chunk_index=0,
        page_start=1,
        page_end=1,
        content=content_a1,
        metadata={"machine_id": str(machine_a.id), "page_number": 1, "manual_title": manual_a.title},
        embedding=vec_a1
    )
    chunk_a2 = DocumentChunk.objects.create(
        manual=manual_a,
        machine=machine_a,
        chunk_index=1,
        page_start=2,
        page_end=2,
        content=content_a2,
        metadata={"machine_id": str(machine_a.id), "page_number": 2, "manual_title": manual_a.title},
        embedding=vec_a2
    )

    # Machine B: Hydraulic Press
    machine_b = Machine.objects.create(name='Machine B (Hydraulic Press)', model_number='MODEL-B')
    manual_b = Manual.objects.create(
        machine=machine_b,
        title='Machine B Hydraulic Manual',
        original_filename='manual_b.pdf',
        revision='Rev B',
        processing_status=Manual.STATUS_INDEXED
    )

    content_b1 = "Machine B hydraulic relief valve cracks at 350 bar pressure. Use ISO VG 46 oil."
    vec_b1 = emb_provider.embed_text(content_b1)

    chunk_b1 = DocumentChunk.objects.create(
        manual=manual_b,
        machine=machine_b,
        chunk_index=0,
        page_start=1,
        page_end=1,
        content=content_b1,
        metadata={"machine_id": str(machine_b.id), "page_number": 1, "manual_title": manual_b.title},
        embedding=vec_b1
    )

    return {
        'user': user,
        'machine_a': machine_a,
        'machine_b': machine_b,
        'chunk_a1': chunk_a1,
        'chunk_b1': chunk_b1,
    }

@pytest.mark.django_db
class TestRetrievalIsolation:

    def test_mandatory_test_2_machine_specific_retrieval_isolation(self, isolation_setup):
        """
        MANDATORY ORGANIZER TEST 2:
        Verify that when Machine A is selected, passages belonging to Machine B are excluded from retrieval.
        Even if the query explicitly asks for keywords that exist in Machine B's manual,
        retrieval must NEVER return passages belonging to Machine B.
        """
        vector_store = get_vector_store()
        emb_provider = get_embedding_provider()

        # Query specifically mentions concepts found in Machine B ("hydraulic relief valve pressure")
        query_text = "What is the hydraulic relief valve pressure setting?"
        q_vec = emb_provider.embed_text(query_text)

        # 1. Search scoped to Machine A with zero threshold to catch any potential leak
        results_machine_a = vector_store.search(
            query_vector=q_vec,
            machine_id=str(isolation_setup['machine_a'].id),
            top_k=10,
            threshold=0.0  # Zero threshold
        )

        # Assert that EVERY retrieved passage strictly belongs to Machine A
        for r in results_machine_a:
            assert r['machine_id'] == str(isolation_setup['machine_a'].id), \
                f"LEAK DETECTED: Passage from machine {r['machine_id']} returned when querying Machine A!"
            assert r['manual_title'] != 'Machine B Hydraulic Manual', \
                "LEAK DETECTED: Machine B manual returned in Machine A search!"

        # 2. Search scoped to Machine B
        results_machine_b = vector_store.search(
            query_vector=q_vec,
            machine_id=str(isolation_setup['machine_b'].id),
            top_k=10,
            threshold=0.0
        )

        # Assert that EVERY retrieved passage strictly belongs to Machine B
        for r in results_machine_b:
            assert r['machine_id'] == str(isolation_setup['machine_b'].id), \
                f"LEAK DETECTED: Passage from machine {r['machine_id']} returned when querying Machine B!"
            assert r['manual_title'] != 'Machine A Operation Manual', \
                "LEAK DETECTED: Machine A manual returned in Machine B search!"

    def test_rag_pipeline_insufficient_evidence_when_querying_other_machine_topic(self, isolation_setup):
        """
        When Machine A is selected and queried about a Machine B topic (hydraulic relief valve),
        the system must return INSUFFICIENT_EVIDENCE rather than hallucinating or pulling Machine B evidence.
        """
        rag = RAGEngine()
        result = rag.answer_question(
            user=isolation_setup['user'],
            machine_id=str(isolation_setup['machine_a'].id),
            question_text="What is the hydraulic relief valve cracking pressure?"
        )

        assert result['status'] == 'INSUFFICIENT_EVIDENCE', \
            "Querying Machine A about Machine B topics must result in INSUFFICIENT_EVIDENCE"
        assert "Insufficient information" in result['answer']
        assert len(result['evidence']) == 0
