from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorStore(ABC):
    """Abstract Base Class for Vector Stores with mandatory machine isolation."""

    @abstractmethod
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Store chunks with their embedding vectors and metadata.
        Each chunk item must include: id, machine_id, manual_id, content, metadata, embedding.
        """
        pass

    @abstractmethod
    def search(self, query_vector: List[float], machine_id: str, top_k: int = 4, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Strictly search within chunks belonging to machine_id.
        Retrieval must NEVER leak passages belonging to another machine.
        """
        pass

    @abstractmethod
    def delete_manual(self, manual_id: str) -> int:
        """Remove all chunks associated with a manual."""
        pass
