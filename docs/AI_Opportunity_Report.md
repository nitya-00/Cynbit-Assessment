# AI Opportunity Report - Local Document Reader

## Simple summary

Many companies receive long PDF files such as client requirements, proposals, and technical documents. Finding one small detail can take time. Local Document Reader helps a user upload a PDF, search it using normal questions, and see the page where the information came from.

This is a student project and proof of concept. It does not claim that any specific company has this exact problem or that the system is ready for production.

## Opportunity

| Opportunity | AI capability | Potential value |
| --- | --- | --- |
| Document discovery | Semantic search | Faster passage discovery |
| Requirement review | Structured extraction | More consistent review inputs |
| Knowledge assistance | Retrieval-grounded Q&A | Fewer repetitive document searches |
| Risk review | Missing-information checks | Better review prompts |

## Proposed solution

The solution accepts a PDF, extracts page text, normalizes and chunks it, converts chunks to local Nomic embeddings, and searches normalized FAISS vectors for relevant passages. Results preserve source filename and page number. A local LLM RAG layer has been prototyped in Notebook 03; the current FastAPI API exposes retrieval evidence rather than generated answers.

## Expected value and safeguards

Semantic retrieval can improve accessibility without retraining a model for each document. Local inference can reduce external API exposure, but does not remove security obligations. The MVP rejects invalid/empty PDFs and reports textless scanned PDFs; it still needs OCR, authentication, access controls, safe deployment controls, and human review of extracted information.

## Risks

- Retrieval may select irrelevant passages.
- Citation IDs show retrieved sources but do not independently prove claim support.
- Prompt injection remains a risk for later LLM integration; document text must remain untrusted data.
- The JSON registry and local disk storage are single-user MVP choices.

## Conclusion

Document intelligence is a practical AI opportunity where retrieval, traceability, and human verification matter more than an ungrounded chatbot. A pilot should measure retrieval relevance, review time, and user trust before production rollout.
