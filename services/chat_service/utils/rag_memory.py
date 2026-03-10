import os
import json
import time
import hashlib
from math import sqrt

# Simple on-disk RAG memory: stores per-user JSONL entries with embeddings
MEMORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'memory')


def _ensure_dir():
    try:
        os.makedirs(MEMORY_DIR, exist_ok=True)
    except Exception:
        pass


def _embed_texts(texts):
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(texts).tolist()
    except Exception:
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode('utf-8')).digest()
            vec = [((b % 128) - 64) / 64.0 for b in h[:32]]
            out.append(vec)
        return out


def _cosine(a, b):
    # small utility for cosine similarity
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norma = sqrt(sum(x * x for x in a))
    normb = sqrt(sum(y * y for y in b))
    if norma == 0 or normb == 0:
        return 0.0
    return dot / (norma * normb)


def store_interaction(user_id: str, query: str, response: str, metadata: dict = None):
    """Store a user query + agent response with an embedding."""
    _ensure_dir()
    uid = user_id or 'global'
    path = os.path.join(MEMORY_DIR, f"{uid}.jsonl")
    text = f"User: {query}\nAssistant: {response}"
    emb = _embed_texts([text])[0]
    entry = {
        'ts': int(time.time()),
        'query': query,
        'response': response,
        'text': text,
        'embedding': emb,
        'metadata': metadata or {}
    }
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def retrieve_context(user_id: str, query: str, k: int = 5):
    """Return up to k most similar stored interactions as a joined context string."""
    uid = user_id or 'global'
    path = os.path.join(MEMORY_DIR, f"{uid}.jsonl")
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            entries = [json.loads(l) for l in f.read().splitlines() if l.strip()]
    except Exception:
        return None

    if not entries:
        return None

    q_emb = _embed_texts([query])[0]
    scored = []
    for e in entries:
        emb = e.get('embedding')
        sim = _cosine(q_emb, emb) if emb else 0.0
        scored.append((sim, e))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s[1] for s in scored[:k]]
    parts = []
    for e in top:
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e.get('ts', 0)))
        parts.append(f"[{ts}] User: {e.get('query')}\nAssistant: {e.get('response')}")

    return "\n\n".join(parts) if parts else None
