from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""

    @abstractmethod
    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate evidence-grounded response.
        Returns dict with:
            - answer_text: str
            - status: str ('ANSWERED' | 'INSUFFICIENT_EVIDENCE' | 'FAILED')
            - raw_response: Any
        """
        pass
