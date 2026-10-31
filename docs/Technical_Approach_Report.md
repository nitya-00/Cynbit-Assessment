# Technical Approach Report - Local Document Reader

## Overview

Local Document Reader is a simple local document reader. It reads text-based PDFs and creates a separate search index for every uploaded document.

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

## Why I selected these tools

### Ollama

I selected Ollama because I was comfortable working with it locally. It lets me run models on my Mac instead of depending on a paid cloud API. This was useful for a student project because it keeps the setup simple, avoids API-key management, and gives better control over where document text is processed. Ollama is free to use locally; the models and their licences should still be checked individually before commercial use.

### Nomic Embed Text

I used `nomic-embed-text` because it is designed for embeddings rather than writing answers. It converts both document chunks and user questions into vectors. I use `search_document:` for document text and `search_query:` for questions, so both are prepared for retrieval in the same vector space.

### FAISS

I used FAISS because it is a fast and simple vector-search library. After normalizing the vectors, FAISS can compare a question with the document chunks using cosine similarity. It is a good fit for this local MVP because it does not require a separate database server.

### RAG

RAG means Retrieval-Augmented Generation. I chose this approach because a language model should not try to answer a document question from memory. First, the system retrieves the most relevant chunks from the uploaded PDF. Then a local LLM can use only those chunks as context. This makes the system more useful for private documents and allows it to show source page references. RAG reduces hallucinations but does not remove them completely.

### FastAPI and Streamlit

I used FastAPI to separate the backend processing from the user interface. It gives clear endpoints for upload, processing, and retrieval. I used Streamlit because it is quick to build for a demonstration and lets a user upload a PDF and see citations without building a full frontend from scratch.

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
