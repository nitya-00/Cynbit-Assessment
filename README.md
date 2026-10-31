# Document Reader

Document Reader is a Python proof of concept for ingesting PDFs, building semantic-search indexes, and retrieving source passages with page-level metadata. It runs locally with Ollama, Nomic Embed Text, FAISS, FastAPI, and Streamlit.

## Features

- PDF upload, signature validation, and page-level PyMuPDF extraction
- Text normalization and overlapping chunking
- Local Nomic embeddings and per-document FAISS indexes
- FastAPI upload, processing, listing, and retrieval endpoints
- Streamlit dashboard for upload, processing, question entry, and citations
- Tests for ingestion, processing, and upload validation

## Architecture

`PDF → extraction → cleaning/chunking → Nomic embeddings → FAISS → retrieved passages + page citations`

The notebooks contain RAG and structured-extraction experiments. The current API `/api/chat` returns retrieved evidence and citations; integrating LLM answer generation into the API remains future work.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull nomic-embed-text
```

Optional: install `qwen3:4b` for Notebook 03's generation experiments, subject to available disk/RAM.

## Run

```bash
venv/bin/uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
venv/bin/streamlit run streamlit_app.py
```

Open `http://127.0.0.1:8000/docs` for the API or `http://localhost:8501` for the dashboard.

## Tests

```bash
venv/bin/python -m pytest -q
```

## Limitations

- Scanned/image-only PDFs require OCR and are rejected.
- Storage is local JSON and files: appropriate only for a single-user MVP.
- FAISS citations identify retrieved chunks; they do not prove every claim is supported.
- Public deployment requires authentication, access control, rate limits, and stronger file security.
