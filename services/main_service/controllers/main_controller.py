import requests
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from ..agent_executor import execute_agent
from ..tools.file_handler import save_uploaded_file, allowed_file
import os
import requests
from ..utils.logger import log
from ..utils.response_handler import create_safe_response, create_error_response
from ..utils.file_utils import prepare_file_data_for_response, validate_file_path, format_file_size
import os
import traceback
from werkzeug.exceptions import RequestEntityTooLarge

def upload_file_controller():
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify(create_error_response("No file provided")), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify(create_error_response("No file selected")), 400

        if not allowed_file(file.filename):
            return jsonify(create_error_response(
                "Invalid file type. Only CSV, XLS, XLSX files are allowed"
            )), 400

        # Upload the file to the centralized File Service
        try:
            FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
            files_payload = {'file': (file.filename, file.stream, file.mimetype)}
            resp = requests.post(f"{FILE_SERVICE_URL}/upload", files=files_payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            file_id = data.get('file_id') or data.get('id')
        except Exception as e:
            log(f"File Service upload error: {str(e)}", "ERROR")
            return jsonify(create_error_response(f"Upload failed: {str(e)}")), 500

        log(f"File uploaded to Firebase: {file_id}", "INFO")

        response_data = {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename
        }
        # Try to fetch a small preview from File Service for immediate frontend update
        try:
            FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
            preview_resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}/preview?size=50", timeout=10)
            if preview_resp.status_code == 200:
                response_data['preview'] = preview_resp.json()
        except Exception:
            pass

        return jsonify(create_safe_response(response_data))

    except RequestEntityTooLarge:
        return jsonify(create_error_response("File too large. Maximum size is 50MB")), 413
    except Exception as e:
        log(f"Upload error: {str(e)}", "ERROR")
        return jsonify(create_error_response(f"Upload failed: {str(e)}")), 500

def chat_controller():
    try:
        current_user = request.current_user  # Set by middleware
        
        # Parse request data
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '').strip()
            file_id = data.get('file_id')
        else:
            # Handle form data with file upload
            user_message = request.form.get('message', '').strip()
            file_path = None
            
            # Handle inline file upload (forward to file_service)
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
                    try:
                        files_payload = {'file': (file.filename, file.stream, file.mimetype)}
                        resp = requests.post(f"{FILE_SERVICE_URL}/upload", files=files_payload, timeout=120)
                        resp.raise_for_status()
                        data = resp.json()
                        file_id = data.get('file_id') or data.get('id')
                        log(f"File uploaded for chat to file_service: {file_id}", "INFO")
                    except Exception as e:
                        log(f"Error uploading file to file_service: {str(e)}", "ERROR")
                        return jsonify(create_error_response(
                            f"Failed to upload file: {str(e)}"
                        )), 500

        # Validate input
        if not user_message:
            return jsonify(create_error_response("Message is required")), 400

        # If client provided a file_id, we will forward that to agents. If a
        # local file_path existed previously it is no longer used.

        log(f"Processing chat message: '{user_message}'" + 
            (f" with file_id: {file_id}" if 'file_id' in locals() and file_id else ""), "INFO")

        # Initialize response
        response_data = {
            "success": True,
            "message": user_message
        }

        # Execute agent
        try:
            # Pass file_id (may be None) to agent executor
            fid = locals().get('file_id')
            result = execute_agent(file_id=fid, user_prompt=user_message)
            log(f"Agent result type: {type(result)}", "INFO")
            
        except Exception as e:
            log(f"Agent execution error: {str(e)}", "ERROR")
            log(f"Agent traceback: {traceback.format_exc()}", "ERROR")
            
            # Return fallback response for agent failures
            fallback_text = (
                "I can help you analyze your nutrition dataset! "
                "I can provide insights about nutrients, create visualizations, "
                "and answer questions about your data. What would you like to explore?"
            )
            response_data.update({"response": fallback_text})
            
            # Add original file data for fallback
            if file_path:
                try:
                    file_data = prepare_file_data_for_response(file_path)
                    response_data.update(file_data)
                    response_data["file_path"] = file_path
                except Exception as file_e:
                    log(f"Error preparing file data for fallback: {str(file_e)}", "ERROR")
            
            return jsonify(create_safe_response(response_data))

        # Process agent result for display
        if isinstance(result, dict):
            if 'message' in result:
                text = result['message']
            elif 'text' in result:
                text = result['text']
            elif 'response' in result:
                text = result['response']
            else:
                text = str(result)
        elif isinstance(result, str):
            text = result
        else:
            text = str(result)
        
        response_data.update({"response": text})
        
        # Add file metadata if present (from File Service)
        if 'file_id' in locals() and file_id:
            try:
                FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://localhost:5010')
                resp = requests.get(f"{FILE_SERVICE_URL}/file/{file_id}/metadata", timeout=30)
                if resp.status_code == 200:
                    meta_json = resp.json()
                    # file_service returns {'file_id': ..., 'metadata': {...}}
                    file_info = meta_json.get('metadata') or meta_json.get('file_metadata')
                    if file_info:
                        response_data.update({
                            "file_id": file_id,
                            "file_metadata": file_info,
                        })
                else:
                    log(f"File Service metadata returned {resp.status_code}", "WARN")
            except Exception as e:
                log(f"Error retrieving file metadata from File Service: {str(e)}", "ERROR")
                response_data["error"] = f"Failed to fetch file metadata: {str(e)}"
        
        # Save to DB
        try:
            # Import the global db from app
            from ..app import chats_collection
            if chats_collection:
                import datetime
                chats_collection.insert_one({
                    'user': current_user,
                    'message': user_message,
                    'response': response_data,
                    'timestamp': datetime.datetime.utcnow()
                })
        except Exception as db_e:
            log(f"Database save error: {str(db_e)}", "ERROR")

        # Return safe response
        safe_response = create_safe_response(response_data)
        log(f"Final response type: {safe_response.get('type')}", "INFO")
        return jsonify(safe_response)

    except Exception as e:
        log(f"Chat processing error: {str(e)}", "ERROR")
        log(f"Chat error traceback: {traceback.format_exc()}", "ERROR")
        
        # Always return valid JSON, even on error
        error_response = create_error_response(f"Processing failed: {str(e)}")
        return jsonify(error_response), 500

def register_controller():
    # Call auth_service
    try:
        data = request.get_json()
        response = requests.post('http://localhost:5006/auth/register', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def login_controller():
    # Call auth_service
    try:
        data = request.get_json()
        response = requests.post('http://localhost:5006/auth/login', json=data)
        if response.status_code == 200:
            # Generate JWT here
            user_data = response.json()
            access_token = create_access_token(identity=user_data.get('user'))
            return jsonify({"access_token": access_token}), 200
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500