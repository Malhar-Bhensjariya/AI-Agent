import os
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from ..utils.logger import log

# MongoDB setup
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client['aida_db']
users_collection = db['users']

def register_user(username, password):
    try:
        if users_collection.find_one({'username': username}):
            return {"error": "User already exists"}, 400
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        log(f"Registration error: {str(e)}", "ERROR")
        return {"error": "Registration failed"}, 500

def login_user(username, password):
    try:
        user = users_collection.find_one({'username': username})
        if not user or not check_password_hash(user['password'], password):
            return {"error": "Invalid credentials"}, 401
        
        # For simplicity, return success. JWT can be generated here if needed
        return {"message": "Login successful", "user": username}, 200
    except Exception as e:
        log(f"Login error: {str(e)}", "ERROR")
        return {"error": "Login failed"}, 500