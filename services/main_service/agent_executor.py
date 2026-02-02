import requests
from .tool_selector import detect_agent_type
from .utils.logger import log

# Central registry for service URLs
SERVICE_REGISTRY = {
    "editor": "http://localhost:5001/editor/execute",
    "analyze": "http://localhost:5002/analyzer/execute",
    "transform": "http://localhost:5003/transform/execute",
    "visual": "http://localhost:5004/visualization/execute",
    "chat": "http://localhost:5005/chat/execute"
}

def execute_agent(file_path: str, user_prompt: str) -> str:
    try:
        # Step 1: Let Gemini classify the prompt
        agent_key = detect_agent_type(user_prompt)
        log(f"Selected Agent Type: {agent_key}", "INFO")

        # Step 2: Get corresponding service URL
        service_url = SERVICE_REGISTRY.get(agent_key)
        if not service_url:
            return f"Unknown agent type '{agent_key}' selected."

        # Step 3: Make HTTP POST request to the service
        payload = {
            "file_path": file_path,
            "user_prompt": user_prompt
        }
        response = requests.post(service_url, json=payload, timeout=300)  # 5 min timeout
        response.raise_for_status()
        result = response.json()
        return result

    except requests.exceptions.RequestException as e:
        log(f"Service call error: {str(e)}", "ERROR")
        return f"Service call failed: {str(e)}"
    except Exception as e:
        log(f"Agent Execution Error: {str(e)}", "ERROR")
        return f"Execution failed: {str(e)}"
