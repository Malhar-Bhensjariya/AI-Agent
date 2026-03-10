from flask import Blueprint, request, jsonify
from ..controllers.chat_controller import execute_chat_task

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        user_prompt = data.get('user_prompt')
        user_id = data.get('user_id')

        if not user_prompt:
            return jsonify({"error": "user_prompt is required"}), 400

        result = execute_chat_task(file_id=file_id, user_prompt=user_prompt, user_id=user_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500