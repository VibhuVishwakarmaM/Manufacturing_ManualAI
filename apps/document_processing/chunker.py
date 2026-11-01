import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class DocumentChunker:
    """
    Configurable document chunker that maintains page traceability and avoids losing text.
    Respects page boundaries where possible while preserving page ranges when overlapping.
    """

    def __init__(self, chunk_size=None, chunk_overlap=None):
        ai_cfg = getattr(settings, 'AI_SETTINGS', {})
        self.chunk_size = chunk_size or ai_cfg.get('CHUNK_SIZE', 500)
        self.chunk_overlap = chunk_overlap or ai_cfg.get('CHUNK_OVERLAP', 100)
        if self.chunk_overlap >= self.chunk_size:
            self.chunk_overlap = self.chunk_size // 4

    def chunk_pages(self, pages_data, manual_id, machine_id, manual_title, revision):
        """
        Takes extracted page dictionaries and segments text into overlapping chunks,
        preserving page numbers and metadata.
        """
        chunks = []
        chunk_index = 0

        # We process page by page, tracking words and page attribution
        # Each token-unit is (word_str, page_number)
        tokens_with_pages = []
        for page in pages_data:
            text = page.get('text', '')
            if not text:
                continue
            words = text.split()
            page_num = page['page_number']
            for w in words:
                tokens_with_pages.append((w, page_num))

        if not tokens_with_pages:
            return chunks

        # Convert chunk_size (approx characters or words) to word count: ~4 chars per word
        target_words = max(20, self.chunk_size // 5)
        overlap_words = max(5, self.chunk_overlap // 5)
        step = max(1, target_words - overlap_words)

        i = 0
        total_tokens = len(tokens_with_pages)

        while i < total_tokens:
            chunk_slice = tokens_with_pages[i : i + target_words]
            if not chunk_slice:
                break

            words_in_chunk = [item[0] for item in chunk_slice]
            pages_in_chunk = sorted(list(set(item[1] for item in chunk_slice)))

            content_text = " ".join(words_in_chunk).strip()

            if content_text:
                page_start = pages_in_chunk[0]
                page_end = pages_in_chunk[-1]
                page_number_repr = page_start if page_start == page_end else f"{page_start}-{page_end}"

                chunk_meta = {
                    "machine_id": str(machine_id),
                    "manual_id": str(manual_id),
                    "manual_title": str(manual_title),
                    "revision": str(revision),
                    "page_number": page_number_repr,
                    "page_start": page_start,
                    "page_end": page_end,
                    "chunk_index": chunk_index,
                }

                chunks.append({
                    "chunk_index": chunk_index,
                    "page_start": page_start,
                    "page_end": page_end,
                    "content": content_text,
                    "metadata": chunk_meta,
                })
                chunk_index += 1

            i += step

        return chunks
