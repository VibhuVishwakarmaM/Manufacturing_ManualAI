from .mock_provider import MockEmbeddingProvider

class LocalEmbeddingProvider(MockEmbeddingProvider):
    """Local offline embedding provider using 256-dimensional vector projection."""
    def __init__(self, dimension: int = 256):
        super().__init__(dimension=dimension)
