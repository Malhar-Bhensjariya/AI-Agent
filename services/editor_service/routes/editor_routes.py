from flask import Blueprint, request, jsonify
from ..controllers.editor_controller import execute_editor_task

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        user_prompt = data.get('user_prompt')

        if not user_prompt:
            return jsonify({"error": "user_prompt is required"}), 400

        result = execute_editor_task(file_path, user_prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500