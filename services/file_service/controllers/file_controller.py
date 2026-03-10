from flask import jsonify
from ..firestore_client import FirebaseClient

client = FirebaseClient()


def get_file(file_id: str):
    """Retrieve file metadata and generate a signed download URL."""
    try:
        metadata = client.get_file(file_id)
        if not metadata:
            return jsonify({'error': 'file not found'}), 404

        # Generate signed URL (valid for 1 hour)
        signed_url = client.get_signed_url(file_id, expiration_minutes=60)

        response = {
            'file_id': file_id,
            'metadata': metadata,
            'signed_url': signed_url  # Client can download via this URL
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_metadata(file_id: str):
    try:
        metadata = client.get_file(file_id)
        if not metadata:
            return jsonify({'error': 'file not found'}), 404
        return jsonify({'file_id': file_id, 'metadata': metadata}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_preview(file_id: str):
    from flask import request
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 100))
        preview = client.generate_preview(file_id, page=page, page_size=size)
        if not preview:
            return jsonify({'error': 'preview not available'}), 404
        return jsonify(preview), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def overwrite_file(file_id: str, request):
    try:
        # Accept multipart file or base64 payload
        if 'file' in request.files:
            f = request.files['file']
            content = f.read()
            meta = {'filename': f.filename, 'content_type': f.content_type, 'editor': request.headers.get('X-Editor')}
        else:
            payload = request.get_json(force=True)
            import base64
            content = base64.b64decode(payload.get('content_base64'))
            meta = {'filename': payload.get('filename'), 'content_type': payload.get('content_type', 'application/octet-stream'), 'editor': payload.get('requested_by')}

        # Parse optional If-Match-Version header for optimistic locking
        expected_version = None
        try:
            raw_ver = request.headers.get('If-Match-Version')
            if raw_ver is not None:
                expected_version = int(raw_ver)
        except Exception:
            expected_version = None

        result = client.overwrite_file(file_id, content, meta, expected_version=expected_version)

        if isinstance(result, dict) and result.get('success'):
            # Optionally update preview doc (fire-and-forget) and broadcast via SSE
            try:
                preview = client.generate_preview(file_id, page=1, page_size=50)
                if preview:
                    try:
                        if client.enabled and client.db:
                            client.db.collection('previews').document(file_id).set(preview)
                    except Exception:
                        pass
                    # Broadcast to local subscribers (SSE)
                    try:
                        from ..utils.preview_broadcaster import broadcast_preview
                        broadcast_preview(file_id, preview)
                    except Exception:
                        pass
            except Exception:
                pass

            return jsonify({'success': True, 'file_id': file_id, 'version': result.get('version')}), 200
        else:
            # Version mismatch -> 409
            if isinstance(result, dict) and result.get('error') == 'version_mismatch':
                return jsonify({'error': 'version_mismatch', 'current_version': result.get('current_version')}), 409
            return jsonify({'error': result.get('error') if isinstance(result, dict) else 'overwrite failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def apply_op(file_id: str, request):
    try:
        payload = request.get_json(force=True)
        op_type = payload.get('op_type')
        requested_by = payload.get('requested_by')

        if op_type == 'patch' or 'patch' in payload:
            patch = payload.get('patch') or payload.get('delta') or payload
            patch['requested_by'] = requested_by
            result = client.apply_patch(file_id, patch)

            # update preview doc if successful
            try:
                if result.get('success'):
                    preview = client.generate_preview(file_id, page=1, page_size=50)
                    if preview:
                        try:
                            if client.enabled and client.db:
                                client.db.collection('previews').document(file_id).set(preview)
                        except Exception:
                            pass
                        try:
                            from ..utils.preview_broadcaster import broadcast_preview
                            broadcast_preview(file_id, preview)
                        except Exception:
                            pass
            except Exception:
                pass

            if not result.get('success') and result.get('error') == 'version_mismatch':
                return jsonify(result), 409
            return jsonify(result), 200 if result.get('success') else 500

        # For natural language ops we currently return not implemented
        if op_type == 'nl' or 'operation' in payload:
            return jsonify({'success': False, 'error': 'natural-language ops not implemented; send structured patch'}), 501

        return jsonify({'error': 'unknown operation type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
