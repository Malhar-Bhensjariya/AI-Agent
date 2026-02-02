from ..data_transform_agent import DataTransformAgentExecutor
from ..utils.logger import log

def execute_transform_task(file_path, user_prompt):
    try:
        agent = DataTransformAgentExecutor()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result
    except Exception as e:
        log(f"Transform controller error: {str(e)}", "ERROR")
        return {"error": str(e)}