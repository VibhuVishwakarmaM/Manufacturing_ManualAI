import logging
import requests
from typing import List, Dict, Any
from django.conf import settings
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_PHRASE = "Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably."

class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI Chat Completion Provider."""

    def __init__(self, api_key: str = None, model: str = None):
        ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.api_key = api_key or ai_cfg.get('LLM_API_KEY')
        self.model = model or ai_cfg.get('LLM_MODEL', 'gpt-4o-mini')
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set LLM_API_KEY in .env.")

        # Build context prompt
        context_str = ""
        for i, c in enumerate(context_chunks, 1):
            context_str += (
                f"\n--- EVIDENCE #{i} ---\n"
                f"Manual: {c.get('manual_title')} (Revision: {c.get('revision')})\n"
                f"Page: {c.get('page_number')}\n"
                f"Content: {c.get('content')}\n"
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"EVIDENCE PASSAGES:\n{context_str}\n\nQUESTION: {user_prompt}"}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API Error ({response.status_code}): {response.text}")

        data = response.json()
        answer = data['choices'][0]['message']['content'].strip()

        status_flag = 'ANSWERED'
        if INSUFFICIENT_EVIDENCE_PHRASE.lower() in answer.lower() or "insufficient information" in answer.lower():
            status_flag = 'INSUFFICIENT_EVIDENCE'

        return {
            'answer_text': answer,
            'status': status_flag,
            'raw_response': data
        }
