from ..chat_agent import ChatAgentExecutor
from ..utils.logger import log
import os
import requests
from werkzeug.utils import secure_filename


def execute_chat_task(file_id=None, user_prompt=None, user_id=None):
    try:
        file_bytes = None
        if file_id:
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
                log(f"Fetched file bytes for chat: {file_id}", "INFO")
            except Exception as e:
                log(f"Failed to download file {file_id}: {str(e)}", "ERROR")
                return {"error": f"Failed to fetch file: {str(e)}"}

        agent = ChatAgentExecutor()
        result = agent.execute(question=user_prompt, file_bytes=file_bytes, user_id=user_id)
        # result is a dict with 'response' and 'retrieved_memory'
        return result
    except Exception as e:
        log(f"Chat controller error: {str(e)}", "ERROR")
        return {"error": str(e)}