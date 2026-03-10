import queue
import threading
import time
import json
from typing import Dict, List, Any

# Simple in-process broadcaster for preview SSE subscriptions.
# Maintains a mapping of file_id -> list of subscriber queues.
_subscriptions: Dict[str, List[queue.Queue]] = {}
_lock = threading.Lock()


def subscribe(file_id: str) -> queue.Queue:
    q = queue.Queue()
    with _lock:
        lst = _subscriptions.get(file_id)
        if lst is None:
            _subscriptions[file_id] = [q]
        else:
            lst.append(q)
    return q


def unsubscribe(file_id: str, q: queue.Queue):
    with _lock:
        lst = _subscriptions.get(file_id)
        if not lst:
            return
        try:
            lst.remove(q)
        except ValueError:
            pass
        if not lst:
            _subscriptions.pop(file_id, None)


def broadcast_preview(file_id: str, preview: Any):
    """Broadcast preview JSON to all in-process subscribers for file_id."""
    data = json.dumps(preview, default=str)
    with _lock:
        lst = list(_subscriptions.get(file_id, []))
    for q in lst:
        try:
            q.put_nowait(data)
        except Exception:
            # If queue is full or broken, ignore
            pass


def event_generator(file_id: str, keepalive: int = 15):
    """Yield Server-Sent Events for a subscriber. Yields existing preview if available
    then streams updates pushed via broadcast_preview.
    """
    q = subscribe(file_id)
    try:
        # Try to send a keepalive comment first
        yield ': connected\n\n'
        last_sent = time.time()
        while True:
            try:
                data = q.get(timeout=keepalive)
                yield f'data: {data}\n\n'
                last_sent = time.time()
            except queue.Empty:
                # Send a comment keepalive to keep connection alive
                yield ': keepalive\n\n'
                # continue loop
    finally:
        unsubscribe(file_id, q)
