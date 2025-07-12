from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from services.df_operator import get_csv_tools
from utils.logger import log
import os
from dotenv import load_dotenv

load_dotenv()

class CSVAgentExecutor:
    def __init__(self):
        # Initialize Gemini model for LangChain
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True,
            verbose=False
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a CSV/Excel file editing assistant. Your role is to help users modify data files using the available tools.

IMPORTANT RULES:
1. Always use the provided tools to interact with files
2. File paths are provided by the user - use them exactly as given
3. Row indices are 1-based (first row is row 1, not 0)
4. When adding rows, ensure values match the column count and order
5. Always provide clear feedback about what was changed
6. If an operation fails, explain why and suggest alternatives
7. Never return the file path in the response

Available operations:
- Add/remove rows and columns  
- Rename column
- Modify individual cells or entire rows
- Get file statistics and structure

Always confirm successful operations and provide helpful context about the changes made."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.tools = get_csv_tools()
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
        """Execute user query against the specified file"""
        try:
            # Fix: Validate file_path is not None
            if not file_path:
                return "Error: No file provided. Please upload a CSV or Excel file first."
            
            # Validate file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Prepare input with context
            full_input = f"File: {file_path}\nUser Request: {question}"
            
            result = self.executor.invoke({
                "input": full_input
            })

            output = result.get("output", "No output generated")
            steps = result.get("intermediate_steps", [])

            # Log tool usage for debugging
            if steps:
                log("=== TOOL EXECUTION TRACE ===", "INFO")
                for i, (action, observation) in enumerate(steps, 1):
                    tool_name = action.tool if hasattr(action, 'tool') else 'Unknown'
                    tool_input = action.tool_input if hasattr(action, 'tool_input') else {}
                    log(f"Step {i} - Tool: {tool_name}", "INFO")
                    log(f"Input: {tool_input}", "INFO") 
                    log(f"Result: {observation}", "INFO")
                    log("-" * 50, "INFO")
                log("=== END TRACE ===", "INFO")

            return output

        except Exception as e:
            error_msg = f"Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return error_msg