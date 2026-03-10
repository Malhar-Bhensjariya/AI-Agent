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

# Fallback local store when Firebase credentials not configured
LOCAL_STORE_PATH = os.path.join(os.path.dirname(__file__), 'local_store')
os.makedirs(LOCAL_STORE_PATH, exist_ok=True)


class FirebaseClient:
    """Client for Firebase Storage (binary files) + Firestore (metadata)."""

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
            # Initialize Firebase Admin SDK (once per process)
            if not firebase_admin._apps:
                cred = credentials.Certificate(creds_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'aida-57fc0.firebasestorage.app')
                })

            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.enabled = True
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.enabled = False

    def save_file(self, content: bytes, metadata: Dict[str, Any]) -> str:
        """Save file to Firebase Storage and metadata to Firestore."""
        file_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow()

        # Prepare metadata document
        metadata_doc = {
            'file_id': file_id,
            'filename': metadata.get('filename', 'unknown'),
            'content_type': metadata.get('content_type', 'application/octet-stream'),
            'size': len(content),
            'checksum': self._compute_checksum(content),
            'created_at': now,
            'uploader': metadata.get('uploader', 'anonymous'),
            'storage_path': f'files/{file_id}'
        }

        if self.enabled and self.bucket and self.db:
            try:
                # Upload to Firebase Storage
                blob = self.bucket.blob(f'files/{file_id}')
                blob.upload_from_string(content, content_type=metadata_doc['content_type'])

                # Save metadata to Firestore
                self.db.collection('files').document(file_id).set(metadata_doc)
                return file_id
            except Exception as e:
                print(f"Firebase save error: {e}. Falling back to local storage.")
                self.enabled = False
                return self._save_file_local(content, metadata, file_id, metadata_doc)
        else:
            return self._save_file_local(content, metadata, file_id, metadata_doc)

    def _save_file_local(self, content: bytes, metadata: Dict[str, Any], file_id: str, metadata_doc: Dict[str, Any]) -> str:
        """Fallback: save to local JSON file (for development)."""
        metadata_doc['storage_path'] = f'local://{file_id}'
        path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(metadata_doc, f, indent=2, default=str)
        return file_id

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve file metadata and optionally content."""
        if self.enabled and self.db:
            try:
                doc = self.db.collection('files').document(file_id).get()
                if not doc.exists:
                    return None
                return doc.to_dict()
            except Exception as e:
                print(f"Firebase get error: {e}")
                return self._get_file_local(file_id)
        else:
            return self._get_file_local(file_id)

    def download_bytes(self, file_id: str) -> Optional[bytes]:
        """Download the raw bytes for a file_id from Storage or local store."""
        if self.enabled and self.bucket:
            try:
                blob = self.bucket.blob(f'files/{file_id}')
                return blob.download_as_bytes()
            except Exception as e:
                print(f"Firebase download_bytes error: {e}")
                return None
        else:
            path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.bin")
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read()
            return None

    def overwrite_file(self, file_id: str, content: bytes, metadata: Dict[str, Any], expected_version: Optional[int] = None) -> Dict[str, Any]:
        """Overwrite an existing file at files/{file_id} and update metadata.
        Returns dict {'success': bool, 'version': int} or error details.
        """
        now = datetime.datetime.utcnow()

        metadata_doc = {
            'file_id': file_id,
            'filename': metadata.get('filename', f'{file_id}'),
            'content_type': metadata.get('content_type', 'application/octet-stream'),
            'size': len(content),
            'checksum': self._compute_checksum(content),
            'updated_at': now,
            'last_editor': metadata.get('editor', 'service'),
            'storage_path': f'files/{file_id}'
        }

        if self.enabled and self.bucket and self.db:
            try:
                doc_ref = self.db.collection('files').document(file_id)
                prev_doc = doc_ref.get()
                prev_data = prev_doc.to_dict() if prev_doc.exists else None
                prev_version = prev_data.get('version', 0) if prev_data else 0

                # Optimistic locking check
                if expected_version is not None and prev_version != expected_version:
                    return {'success': False, 'error': 'version_mismatch', 'current_version': prev_version}

                blob = self.bucket.blob(metadata_doc['storage_path'])
                blob.upload_from_string(content, content_type=metadata_doc['content_type'])

                # Preserve created_at
                if prev_data and 'created_at' in prev_data:
                    metadata_doc['created_at'] = prev_data.get('created_at', now)
                else:
                    metadata_doc['created_at'] = now

                # bump version
                version = (prev_version or 0) + 1
                metadata_doc['version'] = version

                doc_ref.set(metadata_doc, merge=True)

                # Audit log
                try:
                    audit = {
                        'file_id': file_id,
                        'action': 'overwrite',
                        'requested_by': metadata.get('editor') or metadata.get('uploader') or 'service',
                        'summary': metadata.get('summary', ''),
                        'version_before': prev_version,
                        'version_after': version,
                        'timestamp': now
                    }
                    self.db.collection('file_audit').add(audit)
                except Exception:
                    pass

                return {'success': True, 'version': version}
            except Exception as e:
                print(f"Firebase overwrite error: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # local fallback
            meta_path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.json")
            prev_version = 0
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        prev = json.load(f)
                        prev_version = prev.get('version', 0)
                except Exception:
                    prev_version = 0

            if expected_version is not None and prev_version != expected_version:
                return {'success': False, 'error': 'version_mismatch', 'current_version': prev_version}

            metadata_doc['version'] = (prev_version or 0) + 1
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_doc, f, default=str)
            bin_path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.bin")
            with open(bin_path, 'wb') as f:
                f.write(content)

            # local audit
            try:
                audit_path = os.path.join(LOCAL_STORE_PATH, 'audit.log')
                with open(audit_path, 'a', encoding='utf-8') as af:
                    af.write(json.dumps({
                        'file_id': file_id,
                        'action': 'overwrite',
                        'requested_by': metadata.get('editor') or metadata.get('uploader') or 'service',
                        'version_before': prev_version,
                        'version_after': metadata_doc['version'],
                        'timestamp': str(now)
                    }) + '\n')
            except Exception:
                pass

            return {'success': True, 'version': metadata_doc['version']}

    def generate_preview(self, file_id: str, page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """Generate a JSON preview for the given file_id (pageed rows + headers).
        Supports basic CSV reading with chunking.
        """
        try:
            import pandas as pd
        except Exception:
            return None

        bytes_data = self.download_bytes(file_id)
        if not bytes_data:
            return None

        # Try CSV first
        from io import BytesIO
        bio = BytesIO(bytes_data)
        try:
            # Calculate start row for page (skip header)
            start = (page - 1) * page_size
            # Use pandas to read only necessary rows
            df = pd.read_csv(bio, skiprows=range(1, start + 1), nrows=page_size)
            headers = list(df.columns)
            rows = df.fillna('').to_dict(orient='records')
            # get total row count by reading full file may be expensive; attempt fast heuristic
            total_rows = None
            try:
                bio.seek(0)
                total_rows = sum(1 for _ in bio.getvalue().splitlines()) - 1
            except Exception:
                total_rows = None

            return {
                'file_id': file_id,
                'page': page,
                'page_size': page_size,
                'row_count': total_rows,
                'headers': headers,
                'rows': rows
            }
        except Exception:
            # Try Excel as fallback
            try:
                bio.seek(0)
                df = pd.read_excel(bio, engine='openpyxl')
                headers = list(df.columns)
                rows = df.fillna('').to_dict(orient='records')
                return {
                    'file_id': file_id,
                    'page': 1,
                    'page_size': len(rows),
                    'row_count': len(rows),
                    'headers': headers,
                    'rows': rows[:page_size]
                }
            except Exception:
                return None

    def apply_patch(self, file_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a structured patch (inserts/updates/deletes) to a CSV/Excel file.
        Returns metadata about the application (success, new_version).
        The patch format is expected to be {
            'updates': [ { 'row_index': int, 'values': {...} } ],
            'deletes': [ row_index, ... ],
            'inserts': [ { 'values': {...} }, ... ]
        }
        """
        try:
            import pandas as pd
        except Exception:
            return {'success': False, 'error': 'pandas not available'}

        bytes_data = self.download_bytes(file_id)
        if bytes_data is None:
            return {'success': False, 'error': 'file bytes not found'}

        from io import BytesIO
        bio = BytesIO(bytes_data)

        # Read as CSV if possible
        try:
            df = pd.read_csv(bio)
            modified = False

            # Deletes: remove by index (if provided)
            for d in patch.get('deletes', []):
                if 0 <= d < len(df):
                    df.drop(df.index[d], inplace=True)
                    modified = True

            # Updates: row_index and values
            for u in patch.get('updates', []):
                idx = u.get('row_index')
                vals = u.get('values', {})
                if idx is None or not (0 <= idx < len(df)):
                    continue
                for k, v in vals.items():
                    df.at[df.index[idx], k] = v
                modified = True

            # Inserts: append values
            for ins in patch.get('inserts', []):
                vals = ins.get('values', {})
                df = pd.concat([df, pd.DataFrame([vals])], ignore_index=True)
                modified = True

            # Drop columns
            for col in patch.get('drop_columns', []):
                if col in df.columns:
                    df = df.drop(columns=[col])
                    modified = True

            # Add columns with default
            for add in patch.get('add_columns', []):
                name = add.get('name')
                default = add.get('default', '')
                if name and name not in df.columns:
                    df[name] = default
                    modified = True

            # Rename columns
            for ren in patch.get('rename_columns', []):
                frm = ren.get('from')
                to = ren.get('to')
                if frm in df.columns and to and to not in df.columns:
                    df = df.rename(columns={frm: to})
                    modified = True

            # Sort
            if 'sort' in patch:
                s = patch.get('sort', {})
                cols = s.get('columns', [])
                asc = s.get('ascending', True)
                if cols:
                    df = df.sort_values(by=cols, ascending=asc).reset_index(drop=True)
                    modified = True

            # Find and replace
            if 'find_and_replace' in patch:
                fr = patch['find_and_replace']
                col = fr.get('column')
                find = fr.get('find')
                replace = fr.get('replace')
                if col in df.columns:
                    df[col] = df[col].astype(str).replace(str(find), str(replace))
                    modified = True

            # Conditional updates (simple parser: uses pandas eval on column)
            if 'conditional_updates' in patch:
                cu = patch['conditional_updates']
                target = cu.get('target')
                cond_col = cu.get('condition_column')
                cond = cu.get('condition')
                new_val = cu.get('new_value')
                if target in df.columns and cond_col in df.columns and cond:
                    try:
                        mask = df[cond_col].astype(str).str.contains(str(cond).strip().strip('"').strip("'"))
                        df.loc[mask, target] = new_val
                        modified = True
                    except Exception:
                        pass

            # Condition deletes (delete rows where column matches condition string)
            if 'condition_deletes' in patch:
                cd = patch['condition_deletes']
                col = cd.get('column')
                cond = cd.get('condition')
                if col in df.columns and cond:
                    try:
                        mask = df[col].astype(str).str.contains(str(cond).strip().strip('"').strip("'"))
                        df = df[~mask].reset_index(drop=True)
                        modified = True
                    except Exception:
                        pass

            # Calculated columns (basic operations)
            for calc in patch.get('calculated_columns', []):
                name = calc.get('name')
                src = calc.get('source')
                op = calc.get('operation')
                operand = calc.get('operand')
                if src in df.columns and name:
                    try:
                        if op == 'multiply' and operand is not None:
                            df[name] = pd.to_numeric(df[src], errors='coerce') * float(operand)
                        elif op == 'divide' and operand is not None:
                            df[name] = pd.to_numeric(df[src], errors='coerce') / float(operand)
                        elif op == 'add' and operand is not None:
                            df[name] = pd.to_numeric(df[src], errors='coerce') + float(operand)
                        elif op == 'subtract' and operand is not None:
                            df[name] = pd.to_numeric(df[src], errors='coerce') - float(operand)
                        elif op == 'square':
                            df[name] = pd.to_numeric(df[src], errors='coerce') ** 2
                        elif op == 'sqrt':
                            df[name] = pd.to_numeric(df[src], errors='coerce') ** 0.5
                        else:
                            continue
                        modified = True
                    except Exception:
                        pass

            # condition_filter_replace: replace entire dataset with filtered rows
            if 'condition_filter_replace' in patch:
                cfr = patch['condition_filter_replace']
                col = cfr.get('column')
                cond = cfr.get('condition')
                if col in df.columns and cond:
                    try:
                        mask = df[col].astype(str).str.contains(str(cond).strip().strip('"').strip("'"))
                        df = df[mask].reset_index(drop=True)
                        modified = True
                    except Exception:
                        pass

            if modified:
                out = df.to_csv(index=False).encode('utf-8')
                expected_version = patch.get('expected_version')
                overwrite_result = self.overwrite_file(file_id, out, {'filename': file_id, 'content_type': 'text/csv', 'editor': patch.get('requested_by'), 'summary': 'apply_patch'}, expected_version=expected_version)

                if not overwrite_result.get('success'):
                    return {'success': False, 'error': overwrite_result.get('error', 'failed to write back'), 'current_version': overwrite_result.get('current_version')}

                # Return success with new version
                return {'success': True, 'file_id': file_id, 'version': overwrite_result.get('version')}
            else:
                # No modification applied
                try:
                    # still write an audit log for attempted no-op
                    if self.enabled and self.db:
                        now = datetime.datetime.utcnow()
                        audit = {
                            'file_id': file_id,
                            'action': 'patch_noop',
                            'requested_by': patch.get('requested_by'),
                            'summary': 'no changes applied',
                            'timestamp': now
                        }
                        self.db.collection('file_audit').add(audit)
                except Exception:
                    pass

                return {'success': True, 'file_id': file_id, 'applied': False}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_file_local(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Fallback: retrieve from local storage."""
        path = os.path.join(LOCAL_STORE_PATH, f"{file_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_signed_url(self, file_id: str, expiration_minutes: int = 60) -> Optional[str]:
        """Generate a signed download URL for a file (Firebase Storage)."""
        if not self.enabled or not self.bucket:
            return None

        try:
            blob = self.bucket.blob(f'files/{file_id}')
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=expiration_minutes),
                method="GET"
            )
            return url
        except Exception as e:
            print(f"Signed URL generation error: {e}")
            return None

    @staticmethod
    def _compute_checksum(content: bytes) -> str:
        import hashlib
        return hashlib.sha256(content).hexdigest()

