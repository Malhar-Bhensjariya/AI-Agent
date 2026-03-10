# Vector service (skeleton)

This service provides a modular ingestion pipeline for RAG workflows using Chroma (or another vector DB).

- Endpoint: `POST /ingest` expects JSON `{ "file_id": "...", "content": "..." }`.
- The service chunks text, computes embeddings via a pluggable `embed_texts()` function, and returns prepared documents for indexing.
- Intentionally does not fetch files from `file_service` — keep services decoupled.
