from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.exceptions import RequestEntityTooLarge

from flask_app.agents.agent_executor import execute_agent
from flask_app.utils.file_handler import save_uploaded_file, allowed_file
from flask_app.utils.logger import log

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['STATIC_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static')

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'plots'), exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "CSV Agent Flask App is running"
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload CSV/Excel files
    Returns: file_path for use in subsequent requests
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Only CSV, XLS, XLSX files are allowed"
            }), 400

        # Save the file
        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        log(f"File uploaded successfully: {file_path}", "INFO")
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file_path": file_path,
            "filename": file.filename
        })

    except RequestEntityTooLarge:
        return jsonify({
            "success": False,
            "error": "File too large. Maximum size is 50MB"
        }), 413
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
    except Exception as e:
        log(f"Upload error: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/message', methods=['POST'])
def process_message():
    """
    Main endpoint for processing user messages
    Handles all agent types and returns appropriate responses
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400

        file_path = data.get('file_path')
        user_prompt = data.get('message', '').strip()

        # Validate required fields
        if not file_path:
            return jsonify({
                "success": False,
                "error": "file_path is required"
            }), 400

        if not user_prompt:
            return jsonify({
                "success": False,
                "error": "message is required"
            }), 400

        # Validate file exists
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": f"File not found: {file_path}"
            }), 404

        log(f"Processing message: '{user_prompt}' for file: {file_path}", "INFO")

        # Execute agent
        result = execute_agent(file_path=file_path, user_prompt=user_prompt)
        
        # Determine response type based on content
        response_data = {
            "success": True,
            "message": user_prompt,
            "file_path": file_path
        }

        # Check if result is JSON (chart configuration)
        if _is_json_string(result):
            try:
                chart_config = json.loads(result)
                response_data.update({
                    "response_type": "visualization",
                    "chart_config": chart_config,
                    "text_response": "Chart generated successfully"
                })
                log("Visualization response generated", "INFO")
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as text
                response_data.update({
                    "response_type": "text",
                    "text_response": result
                })
        else:
            # Text response (from editor, transform, or chat agents)
            response_data.update({
                "response_type": "text", 
                "text_response": result
            })
            log("Text response generated", "INFO")

        return jsonify(response_data)

    except Exception as e:
        log(f"Message processing error: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Processing failed: {str(e)}"
        }), 500

@app.route('/files/<path:filename>', methods=['GET'])
def serve_uploaded_file(filename):
    """
    Serve uploaded files (for download or preview)
    """
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "File not found"
        }), 404

@app.route('/files', methods=['GET'])
def list_uploaded_files():
    """
    List all uploaded files
    """
    try:
        files = []
        upload_dir = app.config['UPLOAD_FOLDER']
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if allowed_file(filename):
                    file_path = os.path.join(upload_dir, filename)
                    file_stats = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "file_path": file_path,
                        "size": file_stats.st_size,
                        "modified": file_stats.st_mtime
                    })
        
        return jsonify({
            "success": True,
            "files": files
        })
    
    except Exception as e:
        log(f"Error listing files: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }), 500

@app.route('/file-info', methods=['POST'])
def get_file_info():
    """
    Get basic information about an uploaded file
    """
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "Invalid file path"
            }), 400

        # Use DataEditor to get file preview and summary
        from flask_app.tools.df_editor import DataEditor
        
        editor = DataEditor(file_path)
        preview = editor.get_preview(n=5)
        summary = editor.get_summary()
        
        return jsonify({
            "success": True,
            "preview": preview,
            "summary": summary
        })
    
    except Exception as e:
        log(f"Error getting file info: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Failed to get file info: {str(e)}"
        }), 500

# Helper functions
def _is_json_string(text: str) -> bool:
    """Check if a string is valid JSON"""
    if not isinstance(text, str):
        return False
    
    text = text.strip()
    if not text:
        return False
        
    # Quick check for JSON-like structure
    if not ((text.startswith('{') and text.endswith('}')) or 
            (text.startswith('[') and text.endswith(']'))):
        return False
    
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 50MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    log(f"Internal server error: {str(e)}", "ERROR")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Development server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask app on port {port}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )