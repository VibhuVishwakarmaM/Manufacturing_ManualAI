# PDF Processing & Extraction Specification

## 1. Engine: PyMuPDF (`fitz`)
The application uses **PyMuPDF** (`fitz`), an ultra-fast, C-backed PDF parsing engine.

### Why PyMuPDF?
- **Speed**: PyMuPDF parses multi-hundred-page technical manuals in milliseconds.
- **Accurate Text Extraction**: Preserves layout text flow without scrambling multi-column equipment manuals.
- **Strict Page Indexing**: Provides direct page array access (`doc[page_index]`), making 1-indexed page preservation trivial and exact.

---

## 2. Extraction Pipeline (`PyMuPDFExtractor`)
Located in `apps/document_processing/pdf_extractor.py`:
1. **Document Loading**: Accepts either a file path or in-memory byte buffer via context manager (`__enter__` / `__exit__`), ensuring file handles are closed cleanly.
2. **Page Enumeration**: Iterates from `0` to `len(doc) - 1`, setting `page_number = index + 1`.
3. **Text Cleaning**: Normalizes linebreaks and multiple whitespaces while preserving paragraph separations.
4. **Metadata Preservation**:
   ```python
   {
       'page_number': 1,       # 1-indexed
       'text': "...",          # Cleaned content
       'char_count': 1250,     # Character count
       'has_content': True     # Flags non-blank pages
   }
   ```

---

## 3. Chunking Strategy (`DocumentChunker`)
Located in `apps/document_processing/chunker.py`:
- **Word-Boundary Token Tracking**: Couples each word with its contributing PDF page number `(word, page_number)`.
- **Sliding Window**: Uses configurable `CHUNK_SIZE` (default 500 characters / ~100 words) and `CHUNK_OVERLAP` (default 100 characters / ~20 words).
- **Page Span Preservation**: When a chunk spans across page boundaries, it records both `page_start` and `page_end` (e.g. `page_number: "1-2"`), preventing loss of traceability for maintenance procedures that span across pages.
