import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PyMuPDFExtractor:
    """
    Page-accurate PDF text extraction using PyMuPDF (fitz).
    Preserves 1-indexed page references and per-page boundaries.
    """

    def __init__(self, file_path_or_bytes):
        self.source = file_path_or_bytes
        self.doc = None

    def __enter__(self):
        if isinstance(self.source, (bytes, bytearray)):
            self.doc = fitz.open(stream=self.source, filetype="pdf")
        else:
            self.doc = fitz.open(self.source)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()

    def get_page_count(self) -> int:
        if not self.doc:
            raise RuntimeError("PDF document is not opened.")
        return len(self.doc)

    def extract_pages(self):
        """
        Extract text page-by-page preserving 1-indexed page numbering.
        Returns:
            list[dict]: List of page dictionaries:
                - page_number (int, 1-indexed)
                - text (str)
                - char_count (int)
                - has_content (bool)
        """
        if not self.doc:
            raise RuntimeError("PDF document is not opened.")

        pages_data = []
        for index in range(len(self.doc)):
            page_num = index + 1  # 1-indexed page numbering
            try:
                page = self.doc[index]
                # Extract text using standard layout-preserving text mode
                raw_text = page.get_text("text")
                # Normalize line breaks and multiple whitespaces while preserving paragraphs
                lines = [line.strip() for line in raw_text.splitlines()]
                cleaned_text = "\n".join([line for line in lines if line])

                has_content = bool(cleaned_text.strip())
                pages_data.append({
                    'page_number': page_num,
                    'text': cleaned_text,
                    'char_count': len(cleaned_text),
                    'has_content': has_content,
                })
            except Exception as e:
                logger.error(f"Error extracting page {page_num}: {e}")
                pages_data.append({
                    'page_number': page_num,
                    'text': '',
                    'char_count': 0,
                    'has_content': False,
                    'error': str(e)
                })

        return pages_data
