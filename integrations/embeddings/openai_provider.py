import logging
import requests
from typing import List
from django.conf import settings
from .base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding Provider using HTTP REST API."""

    def __init__(self, api_key: str = None, model: str = None):
        ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.api_key = api_key or ai_cfg.get('EMBEDDING_API_KEY')
        self.model = model or ai_cfg.get('EMBEDDING_MODEL', 'text-embedding-3-small')
        self.endpoint = "https://api.openai.com/v1/embeddings"
        self._dim = ai_cfg.get('EMBEDDING_DIMENSION', 1536)

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set EMBEDDING_API_KEY in .env.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "input": texts
        }

        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI Embedding API Error ({response.status_code}): {response.text}")

        data = response.json()
        embeddings = [item['embedding'] for item in data['data']]
        return embeddings
