from agents.editor_agent import CSVAgentExecutor as EditorAgent
from agents.data_transform_agent import DataTransformAgentExecutor as TransformAgentExecutor
from agents.visualization_agent import VisualizationAgentExecutor
from agents.chat_agent import ChatAgentExecutor
from agents.tool_selector import detect_agent_type
from utils.logger import log

# Central registry for easy mapping
AGENT_REGISTRY = {
    "editor": EditorAgent,
    "transform": TransformAgentExecutor,
    "visual": VisualizationAgentExecutor,
    "chat": ChatAgentExecutor
}

def execute_agent(file_path: str, user_prompt: str) -> str:
    try:
        # Step 1: Let Gemini classify the prompt
        agent_key = detect_agent_type(user_prompt)
        log(f"Selected Agent Type: {agent_key}", "INFO")

        # Step 2: Get corresponding agent executor
        AgentClass = AGENT_REGISTRY.get(agent_key)
        if not AgentClass:
            return f"Unknown agent type '{agent_key}' selected."

        agent = AgentClass()
        result = agent.execute(file_path=file_path, question=user_prompt)
        return result

    except Exception as e:
        log(f"Agent Execution Error: {str(e)}", "ERROR")
        return f"Execution failed: {str(e)}"
