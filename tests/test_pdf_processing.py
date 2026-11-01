import pytest
import fitz  # PyMuPDF
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.document_processing.pdf_extractor import PyMuPDFExtractor
from apps.document_processing.chunker import DocumentChunker
from apps.manuals.validators import validate_pdf_file

class TestPDFProcessing:

    def test_pymupdf_extraction_and_page_preservation(self):
        """Verify that PyMuPDF extracts text page-by-page and preserves 1-indexed page numbers."""
        # Create a synthetic 3-page PDF in memory
        doc = fitz.open()
        p1 = doc.new_page()
        p1.insert_text(fitz.Point(50, 72), "This is page one text regarding spindle lubrication.")

        p2 = doc.new_page()
        p2.insert_text(fitz.Point(50, 72), "This is page two text regarding electrical lockouts.")

        p3 = doc.new_page()
        p3.insert_text(fitz.Point(50, 72), "This is page three text regarding coolant filtration.")

        pdf_bytes = doc.tobytes()
        doc.close()

        with PyMuPDFExtractor(pdf_bytes) as extractor:
            assert extractor.get_page_count() == 3
            pages = extractor.extract_pages()
            assert len(pages) == 3

            # Verify 1-indexed numbering
            assert pages[0]['page_number'] == 1
            assert "spindle lubrication" in pages[0]['text']

            assert pages[1]['page_number'] == 2
            assert "electrical lockouts" in pages[1]['text']

            assert pages[2]['page_number'] == 3
            assert "coolant filtration" in pages[2]['text']

    def test_document_chunker_metadata_preservation(self):
        """Verify chunker retains manual_id, machine_id, page_start, page_end, and chunk_index."""
        pages_data = [
            {'page_number': 1, 'text': 'Word ' * 100},
            {'page_number': 2, 'text': 'Procedure ' * 100},
        ]

        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_pages(
            pages_data=pages_data,
            manual_id='man-123',
            machine_id='mach-456',
            manual_title='Test Manual',
            revision='Rev 1.0'
        )

        assert len(chunks) > 0
        for c in chunks:
            assert 'chunk_index' in c
            assert 'page_start' in c
            assert 'page_end' in c
            assert c['page_start'] >= 1
            assert c['metadata']['manual_id'] == 'man-123'
            assert c['metadata']['machine_id'] == 'mach-456'
            assert c['metadata']['manual_title'] == 'Test Manual'

    def test_invalid_pdf_validation(self):
        """Test rejection of non-PDF or corrupted files."""
        # 1. Non-pdf extension
        bad_txt = SimpleUploadedFile("manual.txt", b"plain text", content_type="text/plain")
        with pytest.raises(ValidationError) as exc1:
            validate_pdf_file(bad_txt)
        assert "Invalid file extension" in str(exc1.value)

        # 2. Corrupted PDF content
        corrupted_pdf = SimpleUploadedFile("broken.pdf", b"NOT A VALID PDF HEADER", content_type="application/pdf")
        with pytest.raises(ValidationError) as exc2:
            validate_pdf_file(corrupted_pdf)
        assert "Invalid or corrupted PDF" in str(exc2.value)

        # 3. Empty PDF (0 bytes)
        empty_pdf = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")
        with pytest.raises(ValidationError) as exc3:
            validate_pdf_file(empty_pdf)
        assert "empty" in str(exc3.value)
