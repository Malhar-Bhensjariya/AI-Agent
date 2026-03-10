from flask import Blueprint
from .editor_agent import CSVAgentExecutor

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/execute', methods=['POST'])
def execute():
    # This will be called by the main service
    # For now, keep as function call
    pass