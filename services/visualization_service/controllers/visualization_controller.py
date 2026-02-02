from ..visualization_agent import VisualizationAgentExecutor
from ..utils.logger import log

def execute_visualization_task(file_path, user_prompt):
    try:
        agent = VisualizationAgentExecutor()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result
    except Exception as e:
        log(f"Visualization controller error: {str(e)}", "ERROR")
        return {"error": str(e)}