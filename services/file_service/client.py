"""Client library for file_service API (microservices)."""

import requests
from typing import Optional, Dict, Any


class FileServiceClient:
    """Python client for file_service endpoints."""

    def __init__(self, base_url: str = 'http://localhost:5010'):
        self.base_url = base_url

    def upload_file(self, file_path: str, uploader: str = 'service') -> str:
        """
        Upload a file to file_service and return the file_id.

        Args:
            file_path: Path to the file to upload
            uploader: User/service identifier for provenance tracking

        Returns:
            file_id (str) to reference the file in later API calls
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{self.base_url}/upload',
                    files=files,
                    timeout=60
                )
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                return data['file_id']
            else:
                raise ValueError(data.get('error', 'Upload failed'))
        except Exception as e:
            raise RuntimeError(f"Failed to upload file {file_path}: {str(e)}")

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Retrieve file metadata and signed download URL.

        Args:
            file_id: The file ID returned from upload_file()

        Returns:
            dict with 'metadata' and 'signed_url'
        """
        try:
            response = requests.get(
                f'{self.base_url}/file/{file_id}',
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return {
                'metadata': data.get('metadata'),
                'signed_url': data.get('signed_url')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get file metadata for {file_id}: {str(e)}")

    def get_signed_url(self, file_id: str) -> Optional[str]:
        """Convenience method to get just the signed download URL."""
        try:
            result = self.get_file_metadata(file_id)
            return result.get('signed_url')
        except Exception:
            return None
