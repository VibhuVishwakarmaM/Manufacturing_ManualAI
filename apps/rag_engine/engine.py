import os
import logging
from pathlib import Path
from django.conf import settings
from django.shortcuts import get_object_or_404

from apps.machines.models import Machine
from apps.question_history.models import QuestionHistory
from integrations.embeddings import get_embedding_provider
from integrations.vector_store import get_vector_store
from integrations.llm import get_llm_provider

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_RESPONSE = (
    "Insufficient information: The selected machine's available manuals "
    "do not provide enough evidence to answer this question reliably."
)

class RAGEngine:
    """
    Production-grade RAG Engine for Manufacturing Equipment Manuals.
    Enforces machine-isolated vector retrieval, evidence validation,
    and anti-hallucination guardrails.
    """

    def __init__(self):
        self.ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.embedding_provider = get_embedding_provider()
        self.vector_store = get_vector_store()
        self.llm_provider = get_llm_provider()
        self.top_k = self.ai_cfg.get('TOP_K', 4)
        self.similarity_threshold = self.ai_cfg.get('SIMILARITY_THRESHOLD', 0.65)
        self.prompt_version = self.ai_cfg.get('RAG_PROMPT_VERSION', 'v1')
        self._load_system_prompt()

    def _load_system_prompt(self):
        prompt_path = Path(__file__).parent / 'prompts' / f"system_{self.prompt_version}.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = (
                "You are an industrial equipment maintenance assistant. "
                "Answer using ONLY the provided evidence. Cite manual and page number."
            )

    def answer_question(self, user, machine_id: str, question_text: str) -> dict:
        """
        Execute full RAG pipeline:
        1. Validate selected machine
        2. Embed question
        3. Retrieve machine-isolated chunks
        4. Validate evidence sufficiency
        5. Generate response
        6. Persist history
        """
        question_clean = question_text.strip()
        if not question_clean:
            raise ValueError("Question text cannot be empty.")

        machine = get_object_or_404(Machine, id=machine_id)

        # Step 1: Embed question
        try:
            q_vec = self.embedding_provider.embed_text(question_clean)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise RuntimeError(f"Embedding service error: {str(e)}")

        # Step 2: Machine-Scoped Vector Retrieval
        # The vector store strictly filters by machine_id!
        retrieved_chunks = self.vector_store.search(
            query_vector=q_vec,
            machine_id=str(machine.id),
            top_k=self.top_k,
            threshold=self.similarity_threshold
        )

        # Step 3: Evidence Relevance Validation & Insufficient Evidence Check
        if not retrieved_chunks:
            # No chunks met similarity threshold or no manuals indexed for this machine
            record = QuestionHistory.objects.create(
                user=user,
                machine=machine,
                question_text=question_clean,
                answer_text=INSUFFICIENT_EVIDENCE_RESPONSE,
                status=QuestionHistory.STATUS_INSUFFICIENT,
                confidence_score=0.0,
                retrieved_evidence=[],
                llm_provider=self.ai_cfg.get('LLM_PROVIDER', 'mock'),
                prompt_version=self.prompt_version
            )

            return {
                'id': str(record.id),
                'machine_id': str(machine.id),
                'machine_name': machine.name,
                'question': question_clean,
                'answer': INSUFFICIENT_EVIDENCE_RESPONSE,
                'status': 'INSUFFICIENT_EVIDENCE',
                'confidence_score': 0.0,
                'citations': [],
                'evidence': []
            }

        # Step 4: Context Construction & LLM Generation
        top_score = retrieved_chunks[0]['score'] if retrieved_chunks else 0.0

        try:
            llm_result = self.llm_provider.generate_answer(
                system_prompt=self.system_prompt,
                user_prompt=question_clean,
                context_chunks=retrieved_chunks
            )
            answer_text = llm_result.get('answer_text', '').strip()
            answer_status = llm_result.get('status', QuestionHistory.STATUS_ANSWERED)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            answer_text = f"An error occurred while communicating with the AI model: {str(e)}"
            answer_status = QuestionHistory.STATUS_FAILED

        # Build citations list
        citations = []
        for c in retrieved_chunks:
            citation_item = {
                'manual_id': c.get('manual_id'),
                'manual_title': c.get('manual_title'),
                'revision': c.get('revision'),
                'page_number': c.get('page_number'),
                'similarity_score': c.get('score'),
                'snippet': c.get('content')[:200] + '...' if len(c.get('content', '')) > 200 else c.get('content')
            }
            if citation_item not in citations:
                citations.append(citation_item)

        # Step 5: Persist in QuestionHistory
        record = QuestionHistory.objects.create(
            user=user,
            machine=machine,
            question_text=question_clean,
            answer_text=answer_text,
            status=answer_status,
            confidence_score=top_score,
            retrieved_evidence=retrieved_chunks,
            llm_provider=self.ai_cfg.get('LLM_PROVIDER', 'mock'),
            prompt_version=self.prompt_version
        )

        return {
            'id': str(record.id),
            'machine_id': str(machine.id),
            'machine_name': machine.name,
            'question': question_clean,
            'answer': answer_text,
            'status': answer_status,
            'confidence_score': top_score,
            'citations': citations,
            'evidence': retrieved_chunks
        }
