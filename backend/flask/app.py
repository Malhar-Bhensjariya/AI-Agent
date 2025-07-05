from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
import re
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

def strip_markdown(text):
    """Remove markdown formatting from text"""
    if not isinstance(text, str):
        return text
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)     # Remove *italic*
    text = re.sub(r'__(.*?)__', r'\1', text)     # Remove __bold__
    text = re.sub(r'_(.*?)_', r'\1', text)       # Remove _italic_
    text = re.sub(r'`(.*?)`', r'\1', text)       # Remove `code`
    text = re.sub(r'```[\s\S]*?```', '', text)   # Remove ```code blocks```
    text = re.sub(r'#{1,6}\s+', '', text)        # Remove # headers
    
    return text

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

def _validate_chart_config(chart_config: dict) -> bool:
    """Validate that the chart config is properly formatted for Chart.js"""
    if not isinstance(chart_config, dict):
        return False
    
    # Check required Chart.js fields
    required_fields = ['type', 'data']
    if not all(field in chart_config for field in required_fields):
        log(f"Chart config missing required fields: {required_fields}", "WARNING")
        return False
    
    # Validate chart type
    valid_types = ['bar', 'line', 'scatter', 'pie', 'doughnut', 'radar', 'polarArea']
    if chart_config.get('type') not in valid_types:
        log(f"Invalid chart type: {chart_config.get('type')}", "WARNING")
        return False
    
    # Validate data structure
    data = chart_config.get('data', {})
    if not isinstance(data, dict):
        log("Chart data is not a dictionary", "WARNING")
        return False
    
    # For most chart types, we need datasets
    if chart_config.get('type') != 'pie':
        if 'datasets' not in data or not isinstance(data['datasets'], list):
            log("Chart data missing datasets array", "WARNING")
            return False
    
    return True

def _extract_chart_from_response(result) -> dict:
    """Extract chart configuration from various response formats"""
    chart_data = None
    
    # Case 1: Result is already a structured dict from visualization agent
    if isinstance(result, dict):
        if result.get('type') == 'chart' and result.get('chart_config'):
            chart_config = result['chart_config']
            if _validate_chart_config(chart_config):
                return {
                    'chart_config': chart_config,
                    'chart_type': result.get('chart_type', chart_config.get('type', 'bar')),
                    'message': result.get('message', 'Chart created successfully'),
                    'success': result.get('success', True)
                }
        return None
    
    # Case 2: Result is a JSON string
    if isinstance(result, str):
        try:
            # Try to parse as JSON first
            if result.strip().startswith('{'):
                parsed = json.loads(result)
                if isinstance(parsed, dict) and parsed.get('type') == 'chart':
                    chart_config = parsed.get('chart_config')
                    if chart_config and _validate_chart_config(chart_config):
                        return {
                            'chart_config': chart_config,
                            'chart_type': parsed.get('chart_type', chart_config.get('type', 'bar')),
                            'message': parsed.get('message', 'Chart created successfully'),
                            'success': True
                        }
        except json.JSONDecodeError:
            pass
        
        # Case 3: Look for chart config markers in text
        config_pattern = r'CHART_CONFIG_START\s*(\{.*?\})\s*CHART_CONFIG_END'
        match = re.search(config_pattern, result, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                chart_config = json.loads(json_str)
                if _validate_chart_config(chart_config):
                    return {
                        'chart_config': chart_config,
                        'chart_type': chart_config.get('type', 'bar'),
                        'message': 'Chart created successfully',
                        'success': True
                    }
            except json.JSONDecodeError:
                pass
        
        # Case 4: Look for JSON code blocks
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, result, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                chart_config = json.loads(json_str)
                if _validate_chart_config(chart_config):
                    return {
                        'chart_config': chart_config,
                        'chart_type': chart_config.get('type', 'bar'),
                        'message': 'Chart created successfully',
                        'success': True
                    }
            except json.JSONDecodeError:
                pass
    
    return None

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
            
            # Handle file upload
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
        
        log(f"Agent result type: {type(result)}", "INFO")
        log(f"Agent result preview: {str(result)[:200]}...", "INFO")
        
        # Initialize response structure
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
                response_data["headers"] = df.columns.tolist()
                response_data["file_info"] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_order": df.columns.tolist()
                }
                
            except Exception as e:
                log(f"Error reading updated file: {str(e)}", "ERROR")
                response_data["error"] = f"Failed to read updated file: {str(e)}"

        # Try to extract chart configuration from result
        chart_data = _extract_chart_from_response(result)
        
        if chart_data and chart_data.get('success'):
            # This is a successful chart response
            response_data.update({
                "type": "chart",
                "chart_config": chart_data["chart_config"],
                "chart_type": chart_data["chart_type"],
                "text": strip_markdown(chart_data["message"]),  # Strip markdown here
                "success": True
            })
            log(f"Chart response generated successfully: {chart_data['chart_type']}", "INFO")
            
        else:
            # This is a text response or failed chart
            if isinstance(result, dict) and 'message' in result:
                text_response = strip_markdown(result['message'])  # Strip markdown here
            elif isinstance(result, str):
                text_response = strip_markdown(result)  # Strip markdown here
            else:
                text_response = strip_markdown(str(result))  # Strip markdown here
            
            response_data.update({
                "type": "text",
                "text": text_response,
                "success": True
            })
            log("Text response generated", "INFO")

        log(f"Final response type: {response_data.get('type')}", "INFO")
        return jsonify(response_data)

    except Exception as e:
        log(f"Chat processing error: {str(e)}", "ERROR")
        return jsonify({
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "type": "error"
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