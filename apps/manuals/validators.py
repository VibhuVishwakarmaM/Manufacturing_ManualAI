import os
import fitz  # PyMuPDF
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_pdf_file(uploaded_file):
    """
    Validates that:
    1. Extension is .pdf
    2. File size is within limits
    3. Content is a valid, readable PDF readable by PyMuPDF
    """
    # 1. Extension check
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError(f"Invalid file extension '{ext}'. Only PDF documents (.pdf) are supported.")

    # 2. File size check
    max_mb = getattr(settings, 'AI_SETTINGS', {}).get('MAX_UPLOAD_SIZE_MB', 25)
    max_bytes = max_mb * 1024 * 1024
    if uploaded_file.size > max_bytes:
        raise ValidationError(f"File size exceeds maximum allowed limit of {max_mb} MB.")

    if uploaded_file.size == 0:
        raise ValidationError("Uploaded file is empty (0 bytes).")

    # 3. PyMuPDF integrity check
    try:
        # Read initial bytes or stream
        uploaded_file.seek(0)
        content_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        doc = fitz.open(stream=content_bytes, filetype="pdf")
        if doc.page_count < 1:
            doc.close()
            raise ValidationError("The uploaded PDF has 0 pages or contains no readable layout.")
        doc.close()
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError(f"Invalid or corrupted PDF file: {str(e)}")

    return True
