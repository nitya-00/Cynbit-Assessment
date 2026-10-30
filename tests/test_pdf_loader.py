from pathlib import Path

import pymupdf
import pytest

from app.ingestion.pdf_loader import extract_pdf_text


def create_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "School Management System")
    document.new_page()  # Deliberately blank: validates has_text handling.
    document.save(path)
    document.close()


def test_extracts_text_and_page_metadata(tmp_path: Path) -> None:
    pdf_path = tmp_path / "requirements.pdf"
    create_pdf(pdf_path)

    pages = extract_pdf_text(pdf_path)

    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert pages[0]["source_file"] == "requirements.pdf"
    assert pages[0]["has_text"] is True
    assert "School Management System" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert pages[1]["has_text"] is False
    assert pages[1]["character_count"] == 0


def test_rejects_missing_and_non_pdf_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_pdf_text(tmp_path / "missing.pdf")

    text_file = tmp_path / "requirements.txt"
    text_file.write_text("not a PDF")
    with pytest.raises(ValueError, match="Only PDF"):
        extract_pdf_text(text_file)
