import json

import pytest

from app.processing.text_processing import (
    clean_pages,
    clean_text,
    create_document_chunks,
    save_chunks,
    split_text_into_chunks,
    validate_chunks,
)


def test_clean_text_normalizes_unicode_whitespace_and_hyphenation() -> None:
    raw = "Cafe\u0301  require-\nments\nneed\tconsistent   spacing.\n\nSecond paragraph."
    assert clean_text(raw) == "Café requirements need consistent spacing.\n\nSecond paragraph."


def test_chunking_is_nonempty_bounded_and_overlapping() -> None:
    text = " ".join(f"Sentence {index}." for index in range(80))
    chunks = split_text_into_chunks(text, chunk_size=120, chunk_overlap=25)
    assert len(chunks) > 2
    assert all(chunk.strip() and len(chunk) <= 120 for chunk in chunks)
    assert any(chunks[index][-15:] in chunks[index + 1] for index in range(len(chunks) - 1))


def test_chunking_rejects_invalid_settings() -> None:
    with pytest.raises(ValueError):
        split_text_into_chunks("text", chunk_size=0)
    with pytest.raises(ValueError):
        split_text_into_chunks("text", chunk_size=10, chunk_overlap=10)


def test_pages_become_valid_persisted_chunks(tmp_path) -> None:
    pages = clean_pages([
        {"text": "React is the frontend. " * 20, "page_number": 1, "document_metadata": {"title": "Requirements"}},
        {"text": "FastAPI is the backend.", "page_number": 2, "document_metadata": {"title": "Requirements"}},
    ])
    chunks = create_document_chunks(pages, "client_requirements.pdf")
    assert validate_chunks(chunks) is True
    assert chunks[0]["document_id"] == "client_requirements"
    assert chunks[-1]["page_number"] == 2
    output_path = save_chunks(chunks, tmp_path / "chunks.json")
    assert json.loads(output_path.read_text(encoding="utf-8"))[0]["source"] == "client_requirements.pdf"
