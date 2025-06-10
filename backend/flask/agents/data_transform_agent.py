# data_transform_agent.py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from flask_app.services.transformer_operator import get_transformer_tools
from flask_app.utils.logger import log
import os
from dotenv import load_dotenv

load_dotenv()

class DataTransformAgentExecutor:
    def __init__(self):
        # Initialize LangChain-compatible Gemini model
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data transformation agent. Your job is to:

1. Analyze the user's transformation request
2. Use the appropriate tool to perform the transformation
3. Provide clear feedback about what was done

Available operations:
- Fill missing values: "Fill missing values in 'Age' with 30"
- Change data types: "Change column 'Price' to float" 
- Normalize columns: "Normalize column 'Score'"
- Get dataset info: "Show dataset information"

Rules:
- Only handle data transformation tasks
- Use tools appropriately 
- Always include the file_path parameter when calling tools
- Be concise and clear in your responses"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.tools = get_transformer_tools()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
            max_iterations=3
        )

    def execute(self, file_path: str, question: str):
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                return f"Error: File {file_path} not found"

            result = self.executor.invoke({
                "input": f"File path: {file_path}\nUser request: {question}",
                "file_path": file_path
            })

            output = result.get("output", "")
            steps = result.get("intermediate_steps", [])

            if steps:
                log("=== TRANSFORM TRACE START ===", "INFO")
                for i, step in enumerate(steps):
                    action, observation = step
                    tool_name = action.tool if hasattr(action, 'tool') else 'Unknown'
                    tool_input = action.tool_input if hasattr(action, 'tool_input') else {}
                    
                    log(f"Step {i+1}:", "INFO")
                    log(f"  Tool Used: {tool_name}", "INFO")
                    log(f"  Input: {tool_input}", "INFO")
                    log(f"  Output: {observation}", "INFO")
                    log("-" * 50, "INFO")
                log("=== TRANSFORM TRACE END ===", "INFO")

            return output

        except Exception as e:
            log(f"Transform Agent Error: {str(e)}", "ERROR")
            return f"Transform Error: {str(e)}"