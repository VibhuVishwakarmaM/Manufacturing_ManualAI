from django.conf import settings
from .base import BaseEmbeddingProvider
from .mock_provider import MockEmbeddingProvider
from .openai_provider import OpenAIEmbeddingProvider
from .local_provider import LocalEmbeddingProvider

def get_embedding_provider(name: str = None) -> BaseEmbeddingProvider:
    """Factory to instantiate the configured embedding provider."""
    ai_cfg = getattr(settings, 'AI_SETTINGS', {})
    provider_name = (name or ai_cfg.get('EMBEDDING_PROVIDER', 'mock')).lower()

    if provider_name == 'openai':
        return OpenAIEmbeddingProvider()
    elif provider_name == 'local':
        return LocalEmbeddingProvider()
    elif provider_name == 'mock':
        return MockEmbeddingProvider(dimension=128)
    else:
        # Fallback to mock with warning
        return MockEmbeddingProvider(dimension=128)
