import logging
from typing import List, Dict, Any
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_PHRASE = "Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably."

class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider for automated tests and offline demonstrations.
    Extracts relevant facts directly from retrieved context passages.
    If no relevant facts match or context is empty, strictly adheres to the insufficient evidence policy.
    """

    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        if not context_chunks:
            return {
                'answer_text': INSUFFICIENT_EVIDENCE_PHRASE,
                'status': 'INSUFFICIENT_EVIDENCE',
                'raw_response': {'mock': True, 'reason': 'No context provided.'}
            }

        # Check if the query asks for known absent fields or if context lacks words from prompt
        q_lower = user_prompt.lower()
        
        # Collect all text from context chunks
        combined_text = " ".join([c.get('content', '') for c in context_chunks]).lower()

        # Check keyword presence
        query_keywords = [w for w in q_lower.replace('?', '').replace(',', '').split() if len(w) > 3]
        matches = [kw for kw in query_keywords if kw in combined_text]

        # If question asks about specifications not in context (e.g., "maximum operating temperature", "coolant pressure", etc.)
        if len(query_keywords) > 0 and len(matches) == 0:
            return {
                'answer_text': INSUFFICIENT_EVIDENCE_PHRASE,
                'status': 'INSUFFICIENT_EVIDENCE',
                'raw_response': {'mock': True, 'reason': 'Keywords not located in retrieved chunks.'}
            }

        # Synthesize evidence-grounded response from top context chunk
        top_chunk = context_chunks[0]
        manual_title = top_chunk.get('manual_title', 'Equipment Manual')
        revision = top_chunk.get('revision', 'Rev 1.0')
        page_num = top_chunk.get('page_number', top_chunk.get('page_start', 1))
        content = top_chunk.get('content', '').strip()

        answer = (
            f"**Direct Answer:** Based on {manual_title} ({revision}), page {page_num}:\n\n"
            f"{content[:350]}...\n\n"
            f"**Maintenance Instructions:** Follow all manufacturer guidelines specified in {manual_title}.\n\n"
            f"**Source Citation:** {manual_title}, Revision: {revision}, Page: {page_num}."
        )

        return {
            'answer_text': answer,
            'status': 'ANSWERED',
            'raw_response': {'mock': True, 'top_chunk_id': top_chunk.get('chunk_id')}
        }
