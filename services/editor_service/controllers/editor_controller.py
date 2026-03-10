from ..editor_agent import CSVAgentExecutor
from ..utils.logger import log
import os
import requests
from werkzeug.utils import secure_filename


def execute_editor_task(file_id=None, user_prompt=None):
    try:
        # Download file from File Service when a file_id is provided
        if not file_id:
            return {"error": "No file_id provided"}

        try:
            FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
            resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}", timeout=30)
            resp.raise_for_status()
            info = resp.json()
            signed_url = info.get('signed_url') or info.get('metadata', {}).get('signed_url')

            if not signed_url:
                # Fallback: file_service may return direct metadata with storage path
                # Try metadata endpoint
                meta_resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}/metadata", timeout=15)
                meta_resp.raise_for_status()
                meta = meta_resp.json()
                # No direct bytes available; fail gracefully
                log(f"No signed URL returned for file {file_id}", "ERROR")
                return {"error": "No download URL available for file"}

            # Download the file bytes from the signed URL
            file_bytes_resp = requests.get(signed_url, timeout=120)
            file_bytes_resp.raise_for_status()
            file_bytes = file_bytes_resp.content

            log(f"Fetched file bytes for editing: {file_id}", "INFO")

        except Exception as e:
            log(f"Failed to fetch file {file_id} from File Service: {str(e)}", "ERROR")
            return {"error": f"Failed to fetch file: {str(e)}"}

        agent = CSVAgentExecutor()
        result = agent.execute(file_bytes=file_bytes, question=user_prompt)
        return result
    except Exception as e:
        log(f"Editor controller error: {str(e)}", "ERROR")
        return {"error": str(e)}