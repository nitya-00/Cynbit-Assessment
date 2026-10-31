import uuid
from datetime import datetime, timezone
from pathlib import Path
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE
from app.ingestion.pdf_loader import extract_pdf_text
from app.processing.text_processing import clean_pages, create_document_chunks
from app.retrieval.vector_store import build_vector_store
from app.services.document_registry import load_registry, save_registry, update_document
def upload_document(content, filename):
    if not content: raise ValueError("Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_SIZE: raise ValueError("Uploaded file exceeds the 20 MB limit.")
    if not content.startswith(b"%PDF-"): raise ValueError("Invalid PDF file signature.")
    if not filename.lower().endswith(".pdf"): raise ValueError("Only PDF files are supported.")
    document_id=str(uuid.uuid4()); safe=Path(filename).name; path=UPLOAD_DIR/f"{document_id}.pdf"; path.write_bytes(content)
    registry=load_registry(); registry[document_id]={"document_id":document_id,"filename":safe,"file_path":str(path),"status":"uploaded","created_at":datetime.now(timezone.utc).isoformat()}; save_registry(registry); return registry[document_id]
def process_document(document_id):
    from app.services.document_registry import get_document
    doc=get_document(document_id)
    if not doc: raise KeyError("Document not found.")
    pages=clean_pages(extract_pdf_text(doc["file_path"]))
    if not any(page["text"].strip() for page in pages):
        raise ValueError("No extractable text found. This may be a scanned PDF; OCR is not enabled.")
    chunks=create_document_chunks(pages,doc["filename"])
    count=build_vector_store(document_id,chunks); return update_document(document_id,status="processed",page_count=len(pages),chunk_count=count)
