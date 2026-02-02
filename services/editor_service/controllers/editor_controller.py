from ..editor_agent import CSVAgentExecutor
from ..utils.logger import log

def execute_editor_task(file_path, user_prompt):
    try:
        agent = CSVAgentExecutor()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result
    except Exception as e:
        log(f"Editor controller error: {str(e)}", "ERROR")
        return {"error": str(e)}