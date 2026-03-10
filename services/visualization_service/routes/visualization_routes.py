from flask import Blueprint, request, jsonify
from ..controllers.visualization_controller import execute_visualization_task

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        user_prompt = data.get('user_prompt')

        if not user_prompt:
            return jsonify({"error": "user_prompt is required"}), 400

        result = execute_visualization_task(file_id=file_id, user_prompt=user_prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500