import os
import time
import json
import traceback
from typing import Optional, List

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
PERSIST_DIR = os.path.join(BASE_DIR, 'chroma_store')


def _ensure_persist_dir():
    try:
        os.makedirs(PERSIST_DIR, exist_ok=True)
    except Exception:
        pass


class ChromaMemoryUnavailable(Exception):
    pass


def _init_chroma():
    try:
        import chromadb
        from chromadb.config import Settings
        from chromadb.utils import embedding_functions

        _ensure_persist_dir()
        client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        return client, ef
    except Exception:
        raise ChromaMemoryUnavailable()


def _get_collection(user_id: str):
    try:
        client, ef = _init_chroma()
        # use per-user collection name to keep data scoped
        name = f"memory_{user_id or 'global'}"
        try:
            coll = client.get_collection(name=name)
        except Exception:
            coll = client.create_collection(name=name, embedding_function=ef)
        return coll
    except ChromaMemoryUnavailable:
        return None


def store_interaction(user_id: str, query: str, response: str, metadata: dict = None):
    """Store a single interaction into Chroma. Falls back to file-based JSONL if unavailable."""
    uid = user_id or 'global'
    coll = _get_collection(uid)
    ts = int(time.time())
    record = {
        'ts': ts,
        'query': query,
        'response': response,
        'metadata': metadata or {}
    }

    if coll is not None:
        try:
            # Upsert as a document with id = timestamp_uuid
            doc_id = f"{uid}_{ts}"
            coll.add(ids=[doc_id], metadatas=[{'ts': ts, 'query': query, **(metadata or {})}], documents=[f"User: {query}\nAssistant: {response}"])
            try:
                coll.client.persist()
            except Exception:
                pass
            return True
        except Exception:
            traceback.print_exc()

    # Fallback: append to JSONL
    try:
        path = os.path.join(BASE_DIR, 'memory_fallback')
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{uid}.jsonl")
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return True
    except Exception:
        traceback.print_exc()
        return False


def retrieve_context(user_id: str, query: str, k: int = 5) -> Optional[str]:
    """Retrieve top-k similar interactions for `query` as a single joined string with timestamps."""
    uid = user_id or 'global'
    coll = _get_collection(uid)
    if coll is not None:
        try:
            results = coll.query(query_texts=[query], n_results=k)
            docs = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            parts = []
            for doc, meta in zip(docs, metadatas):
                ts = meta.get('ts') if isinstance(meta, dict) else None
                ts_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)) if ts else ''
                parts.append(f"[{ts_str}] {doc}")
            return "\n\n".join(parts) if parts else None
        except Exception:
            traceback.print_exc()

    # Fallback to JSONL
    try:
        file_path = os.path.join(BASE_DIR, 'memory_fallback', f"{uid}.jsonl")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            entries = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        # naive last-k
        top = sorted(entries, key=lambda e: e.get('ts', 0), reverse=True)[:k]
        parts = []
        for e in top:
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e.get('ts', 0)))
            parts.append(f"[{ts}] User: {e.get('query')}\nAssistant: {e.get('response')}")
        return "\n\n".join(parts) if parts else None
    except Exception:
        traceback.print_exc()
        return None


def clear_user_memory(user_id: str) -> bool:
    uid = user_id or 'global'
    coll = _get_collection(uid)
    if coll is not None:
        try:
            # chroma has delete method
            coll.delete()
            try:
                coll.client.persist()
            except Exception:
                pass
            return True
        except Exception:
            traceback.print_exc()

    # Fallback: remove file
    try:
        file_path = os.path.join(BASE_DIR, 'memory_fallback', f"{uid}.jsonl")
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        traceback.print_exc()
        return False


def export_user_memory(user_id: str) -> Optional[List[dict]]:
    uid = user_id or 'global'
    coll = _get_collection(uid)
    if coll is not None:
        try:
            # Scan collection documents via get method
            res = coll.get()
            docs = res.get('documents', [])
            metadatas = res.get('metadatas', [])
            ids = res.get('ids', [])
            out = []
            for _id, doc, meta in zip(ids, docs, metadatas):
                out.append({'id': _id, 'text': doc, 'metadata': meta})
            return out
        except Exception:
            traceback.print_exc()

    # Fallback: read JSONL
    try:
        file_path = os.path.join(BASE_DIR, 'memory_fallback', f"{uid}.jsonl")
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            entries = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        return entries
    except Exception:
        traceback.print_exc()
        return None


def prune_user_memory(user_id: str, keep_last_n: int = 100) -> bool:
    uid = user_id or 'global'
    coll = _get_collection(uid)
    if coll is not None:
        try:
            # naive export then clear then re-add last N
            entries = export_user_memory(uid) or []
            sorted_entries = sorted(entries, key=lambda e: e.get('metadata', {}).get('ts', 0) if isinstance(e.get('metadata', {}), dict) else 0, reverse=True)
            to_keep = sorted_entries[:keep_last_n][::-1]
            clear_user_memory(uid)
            for e in to_keep:
                text = e.get('text') if isinstance(e.get('text'), str) else ''
                meta = e.get('metadata', {})
                coll.add(ids=[e.get('id')], metadatas=[meta], documents=[text])
            try:
                coll.client.persist()
            except Exception:
                pass
            return True
        except Exception:
            traceback.print_exc()

    # Fallback for JSONL
    try:
        file_path = os.path.join(BASE_DIR, 'memory_fallback', f"{uid}.jsonl")
        if not os.path.exists(file_path):
            return True
        with open(file_path, 'r', encoding='utf-8') as f:
            entries = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        entries = sorted(entries, key=lambda e: e.get('ts', 0), reverse=True)[:keep_last_n]
        with open(file_path, 'w', encoding='utf-8') as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + '\n')
        return True
    except Exception:
        traceback.print_exc()
        return False
