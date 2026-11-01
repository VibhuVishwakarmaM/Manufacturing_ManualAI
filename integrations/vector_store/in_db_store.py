import logging
import numpy as np
from typing import List, Dict, Any
from .base import BaseVectorStore

logger = logging.getLogger(__name__)

class InDatabaseVectorStore(BaseVectorStore):
    """
    Database-backed Vector Store using Django ORM and NumPy cosine similarity.
    Provides backend-enforced machine isolation directly in SQL filtering.
    Works natively across PostgreSQL and SQLite test environments.
    """

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        from apps.document_processing.models import DocumentChunk
        # Chunks are typically created or updated via bulk or individually
        count = 0
        for item in chunks:
            chunk_obj = item.get('chunk_instance')
            if chunk_obj and 'embedding' in item:
                chunk_obj.embedding = item['embedding']
                chunk_obj.save(update_fields=['embedding'])
                count += 1
        return count

    def search(self, query_vector: List[float], machine_id: str, top_k: int = 4, threshold: float = 0.5) -> List[Dict[str, Any]]:
        from apps.document_processing.models import DocumentChunk

        if not query_vector or not machine_id:
            return []

        # MANDATORY SECURITY ISOLATION:
        # Strictly restrict queryset to chunks belonging to machine_id
        chunks_qs = DocumentChunk.objects.filter(
            machine_id=machine_id
        ).select_related('manual', 'machine')

        if not chunks_qs.exists():
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_vec = q_vec / q_norm

        scored_results = []

        for chunk in chunks_qs:
            emb = chunk.embedding
            if not emb or len(emb) == 0:
                continue

            c_vec = np.array(emb, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            c_vec = c_vec / c_norm

            sim = float(np.dot(q_vec, c_vec))

            # Apply similarity threshold
            if sim >= threshold:
                meta = chunk.metadata or {}
                scored_results.append({
                    'chunk_id': str(chunk.id),
                    'score': round(sim, 4),
                    'content': chunk.content,
                    'machine_id': str(chunk.machine_id),
                    'machine_name': chunk.machine.name,
                    'manual_id': str(chunk.manual_id),
                    'manual_title': chunk.manual.title,
                    'revision': chunk.manual.revision,
                    'page_number': meta.get('page_number', chunk.page_start),
                    'page_start': chunk.page_start,
                    'page_end': chunk.page_end,
                    'chunk_index': chunk.chunk_index,
                })

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]

    def delete_manual(self, manual_id: str) -> int:
        from apps.document_processing.models import DocumentChunk
        deleted_count, _ = DocumentChunk.objects.filter(manual_id=manual_id).delete()
        return deleted_count
