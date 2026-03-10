from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import register_user, login_user, verify_firebase_user, verify_firebase_token

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

@auth_bp.route('/firebase/verify', methods=['POST'])
@verify_firebase_token
def verify_firebase():
    """Verify Firebase ID token and return user info.
    Requires Authorization header: Bearer <idToken>
    """
    response, status = verify_firebase_user()
    return jsonify(response), status