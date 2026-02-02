from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..controllers.main_controller import upload_file_controller, chat_controller, register_controller, login_controller

main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    from ..utils.logger import log
    from ..utils.file_utils import format_file_size
    from ..utils.response_handler import create_safe_response
    import os
    
    try:
        response = {
            "status": "healthy",
            "message": "Main Service is running",
            "upload_folder": os.path.join(os.path.dirname(__file__), 'uploads'),
            "max_file_size": format_file_size(50 * 1024 * 1024)
        }
        return create_safe_response(response)
    except Exception as e:
        log(f"Health check error: {str(e)}", "ERROR")
        return {"error": "Health check failed"}, 500

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    return upload_file_controller()

@main_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    # Set current_user from JWT
    from flask_jwt_extended import get_jwt_identity
    request.current_user = get_jwt_identity()
    return chat_controller()

@main_bp.route('/register', methods=['POST'])
def register():
    return register_controller()

@main_bp.route('/login', methods=['POST'])
def login():
    return login_controller()