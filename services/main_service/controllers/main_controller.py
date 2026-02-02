import requests
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from ..agent_executor import execute_agent
from ..tools.file_handler import save_uploaded_file, allowed_file
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

        # Save the file
        file_path = save_uploaded_file(file, os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        log(f"File uploaded successfully: {file_path}", "INFO")
        
        # Prepare response
        response_data = {
            "success": True,
            "message": "File uploaded successfully",
            "file_path": file_path,
            "filename": file.filename
        }
        
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
            file_path = data.get('file_path')
        else:
            # Handle form data with file upload
            user_message = request.form.get('message', '').strip()
            file_path = None
            
            # Handle inline file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_path = save_uploaded_file(file, os.path.join(os.path.dirname(__file__), '..', 'uploads'))
                        log(f"File saved for chat: {file_path}", "INFO")
                    except Exception as e:
                        log(f"Error saving file: {str(e)}", "ERROR")
                        return jsonify(create_error_response(
                            f"Failed to save file: {str(e)}"
                        )), 500

        # Validate input
        if not user_message:
            return jsonify(create_error_response("Message is required")), 400

        # Validate file if provided
        if file_path and not validate_file_path(file_path, os.path.join(os.path.dirname(__file__), '..', 'uploads')):
            return jsonify(create_error_response(f"File not found: {file_path}")), 404

        log(f"Processing chat message: '{user_message}'" + 
            (f" with file: {file_path}" if file_path else ""), "INFO")

        # Initialize response
        response_data = {
            "success": True,
            "message": user_message
        }

        # Execute agent
        try:
            result = execute_agent(file_path=file_path, user_prompt=user_message)
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
        
        # Add file data if present
        if file_path:
            try:
                file_data = prepare_file_data_for_response(file_path)
                response_data.update(file_data)
                response_data["file_path"] = file_path
                log("Using original file data", "INFO")
            except Exception as e:
                log(f"Error preparing file data: {str(e)}", "ERROR")
                response_data["error"] = f"Failed to read file data: {str(e)}"
        
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