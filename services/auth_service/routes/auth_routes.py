from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    response, status = register_user(username, password)
    return jsonify(response), status

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    response, status = login_user(username, password)
    return jsonify(response), status