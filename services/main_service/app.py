from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import pymongo
import os
from werkzeug.exceptions import RequestEntityTooLarge

# Import blueprints
from .routes.main_routes import main_bp

# Initialize Flask app
app = Flask(__name__)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
jwt = JWTManager(app)

# MongoDB Configuration
mongo_uri = os.getenv('MONGODB_URI')
if mongo_uri:
    client = pymongo.MongoClient(mongo_uri)
    db = client['aida_db']
    users_collection = db['users']
    chats_collection = db['chats']
else:
    client = None
    db = None
    users_collection = None
    chats_collection = None

# Environment-based CORS configuration
debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
environment = os.environ.get('FLASK_ENV', 'development')

if debug_mode or environment == 'development':
    # Development: Allow localhost origins
    CORS(app,
         origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://ai-da-six.vercel.app"],
         supports_credentials=True)
else:
    # Production: Restrict to production domain
    CORS(app,
         resources={r"/*": {"origins": "https://ai-da-six.vercel.app"}},
         supports_credentials=True)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register blueprints
app.register_blueprint(main_bp)

# Error handlers
@app.errorhandler(413)
def too_large(e):
    from .utils.response_handler import create_error_response
    from flask import jsonify
    return jsonify(create_error_response(
        "File too large. Maximum size is 50MB"
    )), 413

@app.errorhandler(404)
def not_found(e):
    from .utils.response_handler import create_error_response
    from flask import jsonify
    return jsonify(create_error_response("Endpoint not found")), 404

@app.errorhandler(500)
def internal_error(e):
    from .utils.logger import log
    from .utils.response_handler import create_error_response
    from flask import jsonify
    return jsonify(create_error_response("Internal server error")), 500

@app.errorhandler(Exception)
def handle_exception(e):
    from .utils.logger import log
    from .utils.response_handler import create_error_response
    from flask import jsonify
    return jsonify(create_error_response(
        "An unexpected error occurred"
    )), 500

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    from .utils.logger import log
    from .utils.file_utils import validate_file_path
    from .utils.response_handler import create_error_response
    from flask import jsonify

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

if __name__ == '__main__':
    from .utils.file_utils import format_file_size
    port = int(os.environ.get('PORT', 5000))

    print(f"Starting Main Service on port {port}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Debug mode: {debug_mode}")
    print(f"Environment: {environment}")
    print(f"Max file size: {format_file_size(app.config['MAX_CONTENT_LENGTH'])}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )