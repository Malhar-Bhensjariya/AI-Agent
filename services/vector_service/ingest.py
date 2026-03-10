import os
import json
from flask import jsonify
from .embeddings import embed_texts

# Minimal chunking helper
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        start = end - overlap if end < length else end
    return chunks


def handle_ingest(request):
    try:
        payload = request.get_json(force=True)
        file_id = payload.get('file_id')
        content = payload.get('content')  # optional: allow passing text directly
        if not file_id and not content:
            return jsonify({'error': 'file_id or content required'}), 400

        text = content
        if not text:
            # client is expected to fetch file from file_service and pass content
            return jsonify({'error': 'no content provided; vector_service remains modular and will not fetch files automatically'}), 400

        # Chunk then embed
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)

        # Store into Chroma (not connected here) — return the prepared data
        docs = [{'id': f'{file_id}_{i}', 'text': c, 'embedding': emb} for i, (c, emb) in enumerate(zip(chunks, embeddings))]

        return jsonify({'success': True, 'count': len(docs), 'docs_preview': docs[:3]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
