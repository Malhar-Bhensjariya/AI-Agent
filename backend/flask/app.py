from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
from werkzeug.exceptions import RequestEntityTooLarge

# Import agents and tools
from agents.agent_executor import execute_agent
from tools.file_handler import save_uploaded_file, allowed_file

# Import utilities
from utils.logger import log
from utils.response_handler import (
    create_safe_response,
    create_error_response,
    create_chart_response,
    create_text_response,
    extract_chart_from_response,
    strip_markdown
)
from utils.file_utils import (
    read_file_with_preserved_order,
    prepare_file_data_for_response,
    validate_file_path,
    format_file_size
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        response = {
            "status": "healthy",
            "message": "CSV Agent Flask App is running",
            "upload_folder": app.config['UPLOAD_FOLDER'],
            "max_file_size": format_file_size(app.config['MAX_CONTENT_LENGTH'])
        }
        return jsonify(create_safe_response(response))
    except Exception as e:
        log(f"Health check error: {str(e)}", "ERROR")
        return jsonify(create_error_response("Health check failed")), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload CSV/Excel files for chat analysis"""
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
        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
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


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - handles all user messages and agent routing
    FIXED: Robust JSON handling with proper error recovery
    """
    try:
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
                        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
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
        if file_path and not validate_file_path(file_path, app.config['UPLOAD_FOLDER']):
            return jsonify(create_error_response(f"File not found: {file_path}")), 404

        log(f"Processing chat message: '{user_message}'" + 
            (f" with file: {file_path}" if file_path else ""), "INFO")

        # Initialize response
        response_data = {
            "success": True,
            "message": user_message
        }

        # Add file data if present
        if file_path:
            try:
                file_data = prepare_file_data_for_response(file_path)
                response_data.update(file_data)
                response_data["file_path"] = file_path
            except Exception as e:
                log(f"Error preparing file data: {str(e)}", "ERROR")
                response_data["error"] = f"Failed to read file data: {str(e)}"

        # Execute agent with error handling
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
            response_data.update(create_text_response(fallback_text))
            return jsonify(create_safe_response(response_data))
        
        # Process agent result
        chart_data = extract_chart_from_response(result)
        
        if chart_data and chart_data.get('success'):
            # Chart response
            chart_response = create_chart_response(chart_data)
            response_data.update(chart_response)
            log(f"Chart response: {chart_data['chart_type']}", "INFO")
            
        else:
            # Text response
            if isinstance(result, dict) and 'message' in result:
                text = result['message']
            elif isinstance(result, str):
                text = result
            else:
                text = str(result)
            
            text_response = create_text_response(text)
            response_data.update(text_response)
            log("Text response generated", "INFO")

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


@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    """Serve uploaded files when needed"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not validate_file_path(file_path, app.config['UPLOAD_FOLDER']):
            return jsonify(create_error_response("File not found or access denied")), 404
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    except FileNotFoundError:
        return jsonify(create_error_response("File not found")), 404
    except Exception as e:
        log(f"File serving error: {str(e)}", "ERROR")
        return jsonify(create_error_response("Failed to serve file")), 500


# Error handlers
@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors"""
    return jsonify(create_error_response(
        "File too large. Maximum size is 50MB"
    )), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify(create_error_response("Endpoint not found")), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    log(f"Internal server error: {str(e)}", "ERROR")
    return jsonify(create_error_response("Internal server error")), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions"""
    log(f"Unhandled exception: {str(e)}", "ERROR")
    log(f"Exception traceback: {traceback.format_exc()}", "ERROR")
    
    return jsonify(create_error_response(
        "An unexpected error occurred"
    )), 500


# Development server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask app on port {port}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Debug mode: {debug_mode}")
    print(f"Max file size: {format_file_size(app.config['MAX_CONTENT_LENGTH'])}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )