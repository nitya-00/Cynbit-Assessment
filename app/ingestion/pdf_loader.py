"""Page-level PDF ingestion utilities for Local Document Reader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pymupdf


def extract_pdf_text(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Extract one structured record per page from a text-based PDF.

    Empty text usually indicates a blank page or a scanned/image-only page;
    OCR is deliberately outside Phase 1 and is recorded through ``has_text``.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF documents are supported.")

    extracted_pages: list[dict[str, Any]] = []
    try:
        with pymupdf.open(path) as document:
            document_metadata = document.metadata or {}
            for page_index, page in enumerate(document):
                text = page.get_text("text").strip()
                extracted_pages.append(
                    {
                        "text": text,
                        "source_file": path.name,
                        "source_path": str(path.resolve()),
                        "page_number": page_index + 1,
                        "character_count": len(text),
                        "has_text": bool(text),
                        "document_metadata": document_metadata,
                    }
                )
    except pymupdf.FileDataError as error:
        raise ValueError(f"Invalid or unreadable PDF: {path}") from error

    return extracted_pages
