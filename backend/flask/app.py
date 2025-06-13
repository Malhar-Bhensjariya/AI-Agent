from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
from werkzeug.exceptions import RequestEntityTooLarge
from agents.agent_executor import execute_agent
from tools.file_handler import save_uploaded_file, allowed_file
from utils.logger import log

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def read_file_with_preserved_order(file_path: str) -> pd.DataFrame:
    """Read file while preserving original column order"""
    try:
        ext = file_path.rsplit('.', 1)[1].lower()
        if ext == 'csv':
            # Read CSV with explicit encoding and preserve column order
            df = pd.read_csv(file_path, encoding='utf-8')
        elif ext in ('xls', 'xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # CRITICAL FIX: Ensure we maintain the exact column order from the file
        # Don't perform any operations that might shuffle columns
        log(f"Read file with columns in order: {df.columns.tolist()}", "INFO")
        return df
    except Exception as e:
        log(f"Error reading file {file_path}: {str(e)}", "ERROR")
        raise

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
    Upload CSV/Excel files for chat analysis
    Returns: file_path for use in chat messages
    """
    try:
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
    
    except Exception as e:
        log(f"Upload error: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - handles all user messages and agent routing
    Accepts: message, optional file upload
    Returns: Complex response (text, chart config, files, etc.)
    """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '').strip()
            file_path = data.get('file_path')
        else:
            # Handle form data with file upload
            user_message = request.form.get('message', '').strip()
            file_path = None
            
            # Handle file upload - FIXED: Properly save the file
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                        log(f"File saved for chat: {file_path}", "INFO")
                    except Exception as e:
                        log(f"Error saving file: {str(e)}", "ERROR")
                        return jsonify({
                            "success": False,
                            "error": f"Failed to save file: {str(e)}"
                        }), 500

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400

        # Validate file exists if provided
        if file_path and not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": f"File not found: {file_path}"
            }), 404

        log(f"Processing chat message: '{user_message}'" + (f" with file: {file_path}" if file_path else ""), "INFO")

        # Execute agent (backend handles which agent to use)
        result = execute_agent(file_path=file_path, user_prompt=user_message)
        
        # Parse the response and determine type
        response_data = {
            "success": True,
            "message": user_message
        }

        # Add file info if present
        if file_path:
            response_data["file_path"] = file_path
            
            # Read and return updated file data with preserved column order
            try:
                df = read_file_with_preserved_order(file_path)
                
                # Ensure consistent data structure with preserved order
                response_data["updated_data"] = df.to_dict('records')
                #print("\n\n\n", response_data["updated_data"])
                response_data["headers"] = df.columns.tolist()
                response_data["file_info"] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_order": df.columns.tolist()  # Explicitly include column order
                }
                
                # log(f"Returning updated file data: {len(df)} rows, {len(df.columns)} columns", "INFO")
                # log(f"Column order preserved: {df.columns.tolist()}", "INFO")
            except Exception as e:
                log(f"Error reading updated file: {str(e)}", "ERROR")
                response_data["error"] = f"Failed to read updated file: {str(e)}"

        # Determine response type based on result
        if _is_json_string(result):
            try:
                # Try to parse as chart configuration
                chart_config = json.loads(result)
                response_data.update({
                    "type": "chart",
                    "chart_config": chart_config,
                    "text": "Chart generated from your data"
                })
                log("Chart response generated", "INFO")
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as text
                response_data.update({
                    "type": "text",
                    "text": result
                })
        else:
            # Regular text response
            response_data.update({
                "type": "text", 
                "text": result
            })
            log("Text response generated", "INFO")

        return jsonify(response_data)

    except Exception as e:
        log(f"Chat processing error: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Processing failed: {str(e)}"
        }), 500

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    """Serve uploaded files when needed"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "File not found"
        }), 404

# Helper functions
def _is_json_string(text: str) -> bool:
    """Check if a string is valid JSON"""
    if not isinstance(text, str):
        return False
    
    text = text.strip()
    if not text:
        return False
        
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