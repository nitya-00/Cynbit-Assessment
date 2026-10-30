"""Text normalization, chunking, and validation for DocuMind AI."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def clean_text(text: str) -> str:
    """Normalize extracted text while retaining meaningful paragraphs.

    Wrapped lines are joined into a space, blank lines become paragraph
    boundaries, and a hyphen immediately followed by a line break is removed.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)", "", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"[ \t]*\n[ \t]*\n[ \t]*", "\n\n", text)
    paragraphs = (re.sub(r"\s*\n\s*", " ", paragraph).strip() for paragraph in text.split("\n\n"))
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph)


def _preferred_break(text: str, start: int, limit: int) -> int:
    """Find the rightmost natural break before ``limit``."""
    segment = text[start:limit]
    minimum = max(1, len(segment) // 2)
    candidates: list[int] = []
    for pattern in (r"\n\n", r"\n", r"(?<=[.!?])\s", r"\s"):
        matches = list(re.finditer(pattern, segment))
        if matches:
            candidate = matches[-1].end()
            if candidate >= minimum:
                candidates.append(candidate)
                break
    return start + (candidates[0] if candidates else len(segment))


def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    """Split text into overlapping, boundary-aware character chunks."""
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Chunk overlap must be at least zero and smaller than chunk size.")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        limit = min(start + chunk_size, text_length)
        end = limit if limit == text_length else _preferred_break(text, start, limit)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break
        start = max(end - chunk_overlap, start + 1)
        while start < text_length and text[start].isspace():
            start += 1
    return chunks


def clean_pages(extracted_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Clean page text without discarding page-level source metadata."""
    cleaned_pages = []
    for page in extracted_pages:
        cleaned = {**page, "text": clean_text(page["text"])}
        cleaned["character_count"] = len(cleaned["text"])
        cleaned["has_text"] = bool(cleaned["text"])
        cleaned_pages.append(cleaned)
    return cleaned_pages


def create_document_chunks(cleaned_pages: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """Create traceable chunks from already-cleaned PDF pages."""
    document_id = Path(source).stem
    chunks: list[dict[str, Any]] = []
    for page in cleaned_pages:
        for chunk_index, chunk_text in enumerate(split_text_into_chunks(page["text"]), start=1):
            chunks.append(
                {
                    "chunk_id": f"{document_id}_page_{page['page_number']}_chunk_{chunk_index}",
                    "document_id": document_id,
                    "source": source,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "character_count": len(chunk_text),
                    "document_metadata": page.get("document_metadata", {}),
                }
            )
    return chunks


def validate_chunks(chunks: list[dict[str, Any]]) -> bool:
    """Validate the minimum invariants required for retrieval."""
    if not chunks:
        raise ValueError("No chunks generated.")
    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids)), "Duplicate chunk IDs detected."
    for chunk in chunks:
        assert chunk["text"].strip(), "Empty chunk detected."
        assert chunk["source"], "Missing source document."
        assert chunk["page_number"] > 0, "Invalid page number."
        assert chunk["character_count"] == len(chunk["text"]), "Incorrect character count."
    return True


def save_chunks(chunks: list[dict[str, Any]], output_path: str | Path) -> Path:
    """Persist validated chunk records as UTF-8 JSON."""
    validate_chunks(chunks)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)
    return path
