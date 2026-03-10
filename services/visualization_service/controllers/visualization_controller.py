from ..visualization_agent import VisualizationAgentExecutor
from ..utils.logger import log
import os
import requests
from werkzeug.utils import secure_filename


def execute_visualization_task(file_id=None, user_prompt=None):
    try:
        if not file_id:
            return {"error": "No file_id provided"}

        FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
        try:
            resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}", timeout=30)
            resp.raise_for_status()
            info = resp.json()
            signed_url = info.get('signed_url') or info.get('metadata', {}).get('signed_url')

            if not signed_url:
                log(f"No signed URL for file {file_id}", "ERROR")
                return {"error": "No download URL available for file"}

            file_bytes_resp = requests.get(signed_url, timeout=120)
            file_bytes_resp.raise_for_status()
            file_bytes = file_bytes_resp.content
            log(f"Fetched file bytes for visualization: {file_id}", "INFO")
        except Exception as e:
            log(f"Failed to download file {file_id}: {str(e)}", "ERROR")
            return {"error": f"Failed to fetch file: {str(e)}"}

        agent = VisualizationAgentExecutor()
        result = agent.execute(file_bytes=file_bytes, question=user_prompt)
        return result
    except Exception as e:
        log(f"Visualization controller error: {str(e)}", "ERROR")
        return {"error": str(e)}