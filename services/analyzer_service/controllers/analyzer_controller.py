from ..data_analyzer_agent import AnalyzerAgentExecutor
from ..utils.logger import log

def execute_analyzer_task(file_path, user_prompt):
    try:
        agent = AnalyzerAgentExecutor()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result
    except Exception as e:
        log(f"Analyzer controller error: {str(e)}", "ERROR")
        return {"error": str(e)}