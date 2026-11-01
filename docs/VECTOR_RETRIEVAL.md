# Vector Retrieval & Isolation Architecture

## 1. Provider-Independent Abstraction
The vector store abstraction lives in `integrations/vector_store/base.py`:
```python
class BaseVectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int: ...

    @abstractmethod
    def search(self, query_vector: List[float], machine_id: str, top_k: int = 4, threshold: float = 0.5) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def delete_manual(self, manual_id: str) -> int: ...
```

---

## 2. In-Database Vector Store (`InDatabaseVectorStore`)
To ensure compatibility across both PostgreSQL production environments and local automated testing environments without external cloud vector dependencies, `InDatabaseVectorStore` is implemented directly in Django ORM:
- **Storage**: Chunks are stored in `DocumentChunk` with JSONField `embedding`.
- **SQL Pre-Filtering**:
  ```python
  chunks_qs = DocumentChunk.objects.filter(machine_id=machine_id)
  ```
  This is the most critical security control: it filters chunks at the SQL query level before similarity calculations.
- **Similarity Calculation**: Uses NumPy cosine dot-product normalized vectors:
  $$\text{Cosine Similarity} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$
- **Threshold Pruning**: Discards any passage with similarity below `SIMILARITY_THRESHOLD`.

---

## 3. Strict Machine Isolation Guarantees
- Passages from Machine B are physically excluded from the queryset when Machine A is queried.
- Retrieval returns an empty array if no Machine A manuals match the query, triggering the Insufficient Evidence response rather than falling back to general plant knowledge.
- Verified by automated test: `tests/test_retrieval_isolation.py:test_mandatory_test_2_machine_specific_retrieval_isolation`.
