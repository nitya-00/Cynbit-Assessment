# Technical Approach Report — Local Document Reader

## Overview

Local Document Reader is a modular local-Python document-retrieval MVP. It ingests text-based PDFs and creates a separate semantic index per uploaded document.

## Implemented pipeline

1. FastAPI receives a PDF upload and validates its extension, size (20 MB), and `%PDF-` signature.
2. PyMuPDF extracts page-level text and metadata.
3. Text is Unicode-normalized, cleaned, and split into boundary-aware overlapping chunks.
4. `nomic-embed-text` creates document embeddings with the `search_document:` prefix.
5. Vectors are L2-normalized and stored in a document-specific FAISS `IndexFlatIP` index; normalized inner product is cosine similarity.
6. Questions use the `search_query:` prefix and retrieve the top matching chunks with source/page metadata.

## Components

| Layer | Implementation |
| --- | --- |
| Ingestion | PyMuPDF |
| Processing | Python normalization and chunking |
| Embeddings | Ollama + nomic-embed-text |
| Retrieval | FAISS IndexFlatIP |
| API | FastAPI |
| Interface | Streamlit |
| Validation | Pydantic and Pytest |

## Testing and reliability

The repository currently has nine passing tests covering PDF extraction, cleaning/chunking invariants, persisted chunks, and empty/non-PDF upload rejection. Image-only PDFs are not silently indexed: processing raises an OCR-not-enabled error. The evaluation test-case dataset is present, but a generated-answer evaluation score is pending API integration of the LLM RAG chain.

## RAG status

Notebook 03 prototypes local LLM prompt construction, citation-ID checks, missing-information prompts, and structured extraction. The API currently returns retrieved evidence instead of an LLM-generated answer. This distinction is intentional in this report: it avoids claiming an unimplemented production RAG endpoint.

## Limitations and next steps

- Add OCR for scanned PDFs.
- Move local JSON registry/index files to durable multi-user storage.
- Integrate and evaluate the LLM generation service in the API.
- Validate factual support at claim-to-passage level, not only citation-ID membership.
- Add authentication, authorization, rate limiting, malicious-file defenses, logging, and background jobs before deployment.
