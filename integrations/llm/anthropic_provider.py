import logging
import requests
from typing import List, Dict, Any
from django.conf import settings
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class AnthropicLLMProvider(BaseLLMProvider):
    """Anthropic Claude Messages API Provider."""

    def __init__(self, api_key: str = None, model: str = None):
        ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.api_key = api_key or ai_cfg.get('LLM_API_KEY')
        self.model = model or 'claude-3-5-sonnet-20241022'
        self.endpoint = "https://api.anthropic.com/v1/messages"

    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Anthropic API key is missing. Set LLM_API_KEY in .env.")

        context_str = ""
        for i, c in enumerate(context_chunks, 1):
            context_str += (
                f"\n--- EVIDENCE #{i} ---\n"
                f"Manual: {c.get('manual_title')} (Revision: {c.get('revision')})\n"
                f"Page: {c.get('page_number')}\n"
                f"Content: {c.get('content')}\n"
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"EVIDENCE PASSAGES:\n{context_str}\n\nQUESTION: {user_prompt}"}
            ],
            "max_tokens": 1024,
            "temperature": temperature,
        }

        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            raise RuntimeError(f"Anthropic API Error ({response.status_code}): {response.text}")

        data = response.json()
        answer = data['content'][0]['text'].strip()

        status_flag = 'ANSWERED'
        if "insufficient information" in answer.lower():
            status_flag = 'INSUFFICIENT_EVIDENCE'

        return {
            'answer_text': answer,
            'status': status_flag,
            'raw_response': data
        }

class OllamaLLMProvider(BaseLLMProvider):
    """Local Ollama Provider."""

    def __init__(self, base_url: str = None, model: str = None):
        ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.base_url = base_url or ai_cfg.get('LLM_API_BASE_URL', 'http://localhost:11434')
        self.model = model or ai_cfg.get('LLM_MODEL', 'llama3')

    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        endpoint = f"{self.base_url.rstrip('/')}/api/generate"

        context_str = ""
        for i, c in enumerate(context_chunks, 1):
            context_str += f"\nEVIDENCE #{i} ({c.get('manual_title')}, p.{c.get('page_number')}):\n{c.get('content')}\n"

        prompt = f"{system_prompt}\n\nEVIDENCE:\n{context_str}\n\nQUESTION: {user_prompt}\nANSWER:"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }

        response = requests.post(endpoint, json=payload, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API Error ({response.status_code}): {response.text}")

        data = response.json()
        answer = data.get('response', '').strip()

        status_flag = 'ANSWERED'
        if "insufficient information" in answer.lower():
            status_flag = 'INSUFFICIENT_EVIDENCE'

        return {
            'answer_text': answer,
            'status': status_flag,
            'raw_response': data
        }
