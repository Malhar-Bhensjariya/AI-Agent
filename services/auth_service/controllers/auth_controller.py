import os
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from functools import wraps
from ..utils.logger import log

try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
    FIREBASE_AVAILABLE = True
except Exception as e:
    FIREBASE_AVAILABLE = False
    log(f"Firebase not available: {e}", "WARNING")

# MongoDB setup
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client['aida_db']
users_collection = db['users']

# Firebase setup (optional)
if FIREBASE_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            firebase_admin.initialize_app(cred)
        FIREBASE_ENABLED = True
    except Exception as e:
        FIREBASE_ENABLED = False
        log(f"Firebase initialization failed: {e}", "WARNING")
else:
    FIREBASE_ENABLED = False


def verify_firebase_token(f):
    """Middleware to verify Firebase ID token from Authorization header."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not FIREBASE_ENABLED:
            return {"error": "Firebase not configured"}, 500

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {"error": "Missing Authorization header"}, 401

        try:
            # Expected format: "Bearer <idToken>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            decoded_token = firebase_auth.verify_id_token(token)
            request.firebase_user = decoded_token
            return f(*args, **kwargs)
        except firebase_auth.InvalidIdTokenError:
            return {"error": "Invalid ID token"}, 401
        except firebase_auth.ExpiredIdTokenError:
            return {"error": "ID token expired"}, 401
        except Exception as e:
            log(f"Token verification error: {str(e)}", "ERROR")
            return {"error": "Token verification failed"}, 401

    return decorated_function


def sync_firebase_user_to_db(firebase_user_id, email, display_name=""):
    """Sync Firebase user data to MongoDB."""
    try:
        user_data = {
            'firebase_uid': firebase_user_id,
            'email': email,
            'display_name': display_name,
            'created_via': 'firebase'
        }
        users_collection.update_one(
            {'firebase_uid': firebase_user_id},
            {'$set': user_data},
            upsert=True
        )
        return True
    except Exception as e:
        log(f"User sync error: {str(e)}", "ERROR")
        return False


def register_user(username, password):
    """Traditional email/password registration (backward compatibility)."""
    try:
        if users_collection.find_one({'username': username}):
            return {"error": "User already exists"}, 400

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password, 'created_via': 'local'})

        return {"message": "User registered successfully"}, 201
    except Exception as e:
        log(f"Registration error: {str(e)}", "ERROR")
        return {"error": "Registration failed"}, 500


def login_user(username, password):
    """Traditional email/password login (backward compatibility)."""
    try:
        user = users_collection.find_one({'username': username})
        if not user or not check_password_hash(user['password'], password):
            return {"error": "Invalid credentials"}, 401

        return {"message": "Login successful", "user": username}, 200
    except Exception as e:
        log(f"Login error: {str(e)}", "ERROR")
        return {"error": "Login failed"}, 500


def verify_firebase_user():
    """Verify Firebase ID token and return user info (requires @verify_firebase_token decorator)."""
    try:
        if not hasattr(request, 'firebase_user'):
            return {"error": "Not authenticated"}, 401

        firebase_user = request.firebase_user
        firebase_uid = firebase_user.get('uid')
        email = firebase_user.get('email')
        name = firebase_user.get('name', '')

        # Sync user to MongoDB
        sync_firebase_user_to_db(firebase_uid, email, name)

        return {
            "success": True,
            "user": {
                "uid": firebase_uid,
                "email": email,
                "name": name,
                "emailVerified": firebase_user.get('email_verified', False)
            }
        }, 200
    except Exception as e:
        log(f"Firebase user verification error: {str(e)}", "ERROR")
        return {"error": "Verification failed"}, 500
 