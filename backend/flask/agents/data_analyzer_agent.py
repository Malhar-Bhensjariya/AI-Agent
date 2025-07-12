# data_analyzer_agent.py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from services.analyzer_operator import get_analyzer_tools
from utils.logger import log
import os
from dotenv import load_dotenv

load_dotenv()

class AnalyzerAgentExecutor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data analysis agent. Your job is to:

1. Understand the user's request for data insights
2. Use the appropriate tool to extract insights from the file
3. Respond with clear summaries or relevant stats

Supported tasks:
- Identify columns with missing values
- Calculate average of one or more numeric columns
- Return basic statistics (mean, median, std, min, max)
- Provide full/descriptive/deep/in-depth statistical summary (for all column types)
- Detect outliers using Z-score threshold
- List column names
- Show frequency counts of values in a column
- Count duplicate rows
- Provide full descriptive summary (for all column types)

Rules:
- Only handle analysis-related queries
- Always use tools responsibly  
- Always call tools with file_path as an argument
- The tools return JSON formatted responses - parse and present them in a user-friendly way
- Extract key insights from JSON responses and present them clearly to users
- For in-depth analysis requests, use get_deep_statistics and describe_full_data tools
- Convert JSON data into readable summaries with key findings highlighted
- Keep responses informative and well-structured
- If a request is truly unsupported, reply with 'This request is outside my scope.'"""),

            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.tools = get_analyzer_tools()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        
        # FIX: Adjust executor settings to handle function calling better
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            return_intermediate_steps=False,  # Set to False to avoid function response issues
            max_iterations=3
        )

    def execute(self, file_path: str, question: str):
        try:
            if not os.path.exists(file_path):
                return f"Error: File {file_path} not found"

            full_input = f"File: {file_path}\nUser Request: {question}"
            
            # FIX: Wrap the execution with better error handling
            try:
                result = self.executor.invoke({
                    "input": full_input
                })
                
                output = result.get("output", "")
                return output
                
            except Exception as invoke_error:
                error_msg = str(invoke_error)
                log(f"Agent invocation error: {error_msg}", "ERROR")
                
                # Handle specific Gemini function response error
                if "function_response.name: Name cannot be empty" in error_msg:
                    log("Detected Gemini function response error, retrying with simpler approach", "WARN")
                    
                    # Retry with a more direct approach
                    simplified_input = f"Analyze the data file at {file_path}. The user wants: {question}. Use the appropriate analysis tools."
                    
                    result = self.executor.invoke({
                        "input": simplified_input
                    })
                    return result.get("output", "Analysis completed but response formatting failed.")
                else:
                    return f"Analysis error: {error_msg}"

        except Exception as e:
            log(f"Analyzer Agent Error: {str(e)}", "ERROR")
            return f"Analyzer Error: {str(e)}"