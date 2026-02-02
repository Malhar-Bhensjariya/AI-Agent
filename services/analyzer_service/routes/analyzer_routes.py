from flask import Blueprint, request, jsonify
from ..controllers.analyzer_controller import execute_analyzer_task

analyzer_bp = Blueprint('analyzer', __name__)

@analyzer_bp.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        user_prompt = data.get('user_prompt')

        if not user_prompt:
            return jsonify({"error": "user_prompt is required"}), 400

        result = execute_analyzer_task(file_path, user_prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500