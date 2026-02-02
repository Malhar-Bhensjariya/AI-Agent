from flask import Blueprint, request, jsonify
from ..controllers.transform_controller import execute_transform_task

transform_bp = Blueprint('transform', __name__)

@transform_bp.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        user_prompt = data.get('user_prompt')

        if not user_prompt:
            return jsonify({"error": "user_prompt is required"}), 400

        result = execute_transform_task(file_path, user_prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500