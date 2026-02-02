from ..chat_agent import ChatAgentExecutor
from ..utils.logger import log

def execute_chat_task(file_path, user_prompt):
    try:
        agent = ChatAgentExecutor()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result
    except Exception as e:
        log(f"Chat controller error: {str(e)}", "ERROR")
        return {"error": str(e)}