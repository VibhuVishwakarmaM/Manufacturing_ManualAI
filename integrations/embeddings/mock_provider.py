import hashlib
import numpy as np
from typing import List
from .base import BaseEmbeddingProvider

STOP_WORDS = {
    'the', 'a', 'an', 'is', 'in', 'of', 'for', 'to', 'at', 'on', 'with',
    'and', 'or', 'what', 'which', 'how', 'does', 'do', 'this', 'that', 'are', 'be'
}

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic pseudo-semantic embedding generator for testing and offline development.
    Uses hashed term-frequency projection over non-stopwords to produce reliable cosine
    similarities without requiring live external API credentials.
    """

    def __init__(self, dimension: int = 128):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _text_to_vector(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dim

        vec = np.zeros(self._dim, dtype=np.float32)
        # Strip punctuation
        clean_text = text.lower().replace('?', ' ').replace('.', ' ').replace(',', ' ').replace(':', ' ')
        words = [w for w in clean_text.split() if w not in STOP_WORDS and len(w) > 1]

        if not words:
            # Fallback to all words if only stop words existed
            words = clean_text.split()

        for word in words:
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % self._dim
            vec[idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self._text_to_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]
