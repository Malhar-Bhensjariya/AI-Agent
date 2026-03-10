from ..data_transform_agent import DataTransformAgentExecutor
from ..utils.logger import log
import os
import tempfile
import base64
import requests
from werkzeug.utils import secure_filename


def execute_transform_task(file_id=None, user_prompt=None):
    try:
        if not file_id:
            return {"error": "No file_id provided"}

        # Download bytes from File Service
        try:
            FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
            resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}", timeout=30)
            resp.raise_for_status()
            info = resp.json()
            signed_url = info.get('signed_url') or info.get('metadata', {}).get('signed_url')

            if not signed_url:
                meta_resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}/metadata", timeout=15)
                meta_resp.raise_for_status()
                meta = meta_resp.json()
                # Fail if no download URL
                log(f"No signed URL returned for file {file_id}", "ERROR")
                return {"error": "No download URL available for file"}

            file_bytes_resp = requests.get(signed_url, timeout=120)
            file_bytes_resp.raise_for_status()
            file_bytes = file_bytes_resp.content

            filename = info.get('metadata', {}).get('filename') or f"{file_id}.csv"
            safe_name = secure_filename(filename)
            log(f"Fetched file bytes for transform: {file_id} -> {safe_name}", "INFO")
        except Exception as e:
            log(f"Failed to download file {file_id}: {str(e)}", "ERROR")
            return {"error": f"Failed to fetch file: {str(e)}"}

        # Write to a temporary local file so existing transformer tools can operate
        tmp_dir = tempfile.mkdtemp(prefix='transform_')
        tmp_path = os.path.join(tmp_dir, safe_name)
        with open(tmp_path, 'wb') as f:
            f.write(file_bytes)

        # Run agent on local temp file (agent expects file path)
        agent = DataTransformAgentExecutor()
        result = agent.execute(file_path=tmp_path, question=user_prompt)

        # After agent runs, read file back and push overwrite to File Service
        try:
            with open(tmp_path, 'rb') as f:
                new_bytes = f.read()

            # Call File Service PUT /file/{file_id} with base64 payload
            file_service_url = os.getenv('FILE_SERVICE_URL', 'http://file_service:5010')
            put_url = f"{file_service_url}/file/{file_id}"
            payload = {
                'content_base64': base64.b64encode(new_bytes).decode('utf-8'),
                'filename': safe_name,
                'content_type': file_info.get('content_type', 'text/csv'),
                'requested_by': 'transform_service'
            }
            resp = requests.put(put_url, json=payload, timeout=60)
            try:
                put_result = resp.json()
            except Exception:
                put_result = {'error': resp.text}

            if resp.status_code >= 400 or not put_result.get('success'):
                log(f"Failed to write back transformed file {file_id}: {put_result}", "ERROR")
                return {"error": "Transformation applied locally but failed to write back", "details": put_result}

        except Exception as e:
            log(f"Failed to upload transformed file for {file_id}: {e}", "ERROR")
            return {"error": f"Failed to upload transformed file: {str(e)}"}

        return {"success": True, "result": result}

    except Exception as e:
        log(f"Transform controller error: {str(e)}", "ERROR")
        return {"error": str(e)}