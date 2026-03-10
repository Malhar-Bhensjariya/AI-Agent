try:
    # Prefer a pluggable embedding provider
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer('all-MiniLM-L6-v2')
    def embed_texts(texts):
        return _model.encode(texts).tolist()
except Exception:
    # Fallback stub (deterministic) — DO NOT use in production
    def embed_texts(texts):
        # simple hash-based fallback to have stable numeric vectors
        import hashlib
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode('utf-8')).digest()
            # create list of small floats from bytes
            vec = [((b % 128) - 64) / 64.0 for b in h[:32]]
            out.append(vec)
        return out
