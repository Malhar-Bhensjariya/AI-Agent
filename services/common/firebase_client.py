import os
import uuid
import datetime
import json
from typing import Optional, Dict, Any

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False

LOCAL_STORE_PATH = os.path.join(os.path.dirname(__file__), 'local_store')
os.makedirs(LOCAL_STORE_PATH, exist_ok=True)


class FirebaseHelper:
    def __init__(self):
        self.enabled = False
        self.db = None
        self.bucket = None

        if not FIREBASE_AVAILABLE:
            return

        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            return

        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(creds_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                })

            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.enabled = True
        except Exception as e:
            print(f"FirebaseHelper init error: {e}")
            self.enabled = False

    def get_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        if self.enabled and self.db:
            try:
                doc = self.db.collection('files').document(file_id).get()
                if not doc.exists:
                    return None
                return doc.to_dict()
            except Exception as e:
                print(f"Firebase get_metadata error: {e}")
                return self._get_local_metadata(file_id)
        else:
            return self._get_local_metadata(file_id)

    def download_bytes(self, file_id: str) -> Optional[bytes]:
        meta = self.get_metadata(file_id)
        if not meta:
            return None

        storage_path = meta.get('storage_path')
        if not storage_path:
            return None

        if self.enabled and self.bucket:
            try:
                blob = self.bucket.blob(storage_path)
                return blob.download_as_bytes()
            except Exception as e:
                print(f"Firebase download error: {e}")
                return None
        else:
            # Local fallback: read from local_store if present
            path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.bin")
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read()
            return None

    def upload_bytes(self, content: bytes, metadata: Dict[str, Any]) -> str:
        file_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow()

        metadata_doc = {
            'file_id': file_id,
            'filename': metadata.get('filename', 'unknown'),
            'content_type': metadata.get('content_type', 'application/octet-stream'),
            'size': len(content),
            'checksum': self._compute_checksum(content),
            'created_at': now,
            'uploader': metadata.get('uploader', 'service'),
            'storage_path': f'files/{file_id}'
        }

        if self.enabled and self.bucket and self.db:
            try:
                blob = self.bucket.blob(metadata_doc['storage_path'])
                blob.upload_from_string(content, content_type=metadata_doc['content_type'])
                self.db.collection('files').document(file_id).set(metadata_doc)
                return file_id
            except Exception as e:
                print(f"Firebase upload error: {e}")
                return self._save_local(content, metadata_doc, file_id)
        else:
            return self._save_local(content, metadata_doc, file_id)

    def _save_local(self, content: bytes, metadata_doc: Dict[str, Any], file_id: str) -> str:
        # Save metadata + binary locally for development
        metadata_doc['storage_path'] = f'local://{file_id}'
        meta_path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_doc, f, default=str)
        bin_path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.bin")
        with open(bin_path, 'wb') as f:
            f.write(content)
        return file_id

    def _get_local_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _compute_checksum(content: bytes) -> str:
        import hashlib
        return hashlib.sha256(content).hexdigest()


# Singleton helper instance
helper = FirebaseHelper()
