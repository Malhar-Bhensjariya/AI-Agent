import os
import base64
from flask import jsonify
from ..firestore_client import FirebaseClient
from ..utils.allowed_extensions import is_allowed

client = FirebaseClient()


def handle_upload(request):
    try:
        # support multipart form 'file' or JSON payload with base64
        if 'file' in request.files:
            f = request.files['file']
            if f.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if not is_allowed(f.filename):
                return jsonify({'error': 'File type not allowed'}), 400

            content = f.read()
            metadata = {
                'filename': f.filename,
                'content_type': f.content_type
            }

        else:
            payload = request.get_json(force=True)
            filename = payload.get('filename')
            b64 = payload.get('content_base64')
            if not filename or not b64:
                return jsonify({'error': 'Missing filename or content_base64'}), 400
            if not is_allowed(filename):
                return jsonify({'error': 'File type not allowed'}), 400
            content = base64.b64decode(b64)
            metadata = {'filename': filename, 'content_type': 'application/octet-stream'}

        file_id = client.save_file(content, metadata)
        return jsonify({'success': True, 'file_id': file_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
