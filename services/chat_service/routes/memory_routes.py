from flask import Blueprint, request, jsonify
from ..controllers.memory_controller import clear_memory, export_memory, prune_memory

memory_bp = Blueprint('memory', __name__)


@memory_bp.route('/clear', methods=['POST'])
def clear():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    res = clear_memory(user_id=user_id)
    return jsonify(res)


@memory_bp.route('/export', methods=['POST'])
def export():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    res = export_memory(user_id=user_id)
    return jsonify(res)


@memory_bp.route('/prune', methods=['POST'])
def prune():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    keep = data.get('keep_last_n', 100)
    res = prune_memory(user_id=user_id, keep_last_n=keep)
    return jsonify(res)
