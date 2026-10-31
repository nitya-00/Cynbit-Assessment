import pytest
from app.services.document_service import upload_document

def test_empty_upload_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        upload_document(b"", "empty.pdf")

def test_non_pdf_upload_is_rejected():
    with pytest.raises(ValueError, match="signature"):
        upload_document(b"This is not a PDF", "fake.pdf")

def test_pdf_extension_is_required():
    with pytest.raises(ValueError, match="PDF files"):
        upload_document(b"%PDF-1.7", "fake.txt")
