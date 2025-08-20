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
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True,
            verbose=False
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced CSV data manipulation assistant with powerful capabilities for complex data operations.

CORE CAPABILITIES:
BASIC OPERATIONS: Add/remove rows & columns, rename columns, modify cells, preview data
ADVANCED OPERATIONS: Conditional filtering, bulk updates, calculated columns, data transformation
ANALYSIS: Statistics, unique values, value counts, data profiling
SMART FILTERING: Complex conditions with operators (==, !=, >, <, >=, <=)

IMPORTANT GUIDELINES:

1. **CONDITION SYNTAX**: When users mention conditions, translate them properly:
   - "Category is Burgers" → condition: "Burgers" or "== Burgers"  
   - "Calories greater than 500" → condition: "> 500"
   - "Price less than or equal to 15" → condition: "<= 15"
   - "Status is not Active" → condition: "!= Active"

2. **SMART TOOL SELECTION**: Choose the most efficient tool for the task:
   - For "Remove all rows where..." → use `remove_rows_by_condition`
   - For "Set column X to Y where..." → use `update_column_conditional` 
   - For "Add column with conditional values" → use `add_conditional_column`
   - For "Show me unique categories" → use `get_unique_values`

3. **BATCH OPERATIONS**: Handle complex multi-step requests intelligently:
   - Can chain operations (remove → add → update) in logical sequence
   - Always explain what you're doing at each step
   - Provide status after each major operation

4. **DATA UNDERSTANDING**: Before major operations:
   - Use `get_preview` to understand data structure
   - Use `get_unique_values` to see available options
   - Use `count_values` to understand data distribution

5. **USER COMMUNICATION**:
   - Explain what operations you're performing
   - Show results/counts after operations
   - Suggest optimizations or alternatives when relevant
   - Never assume - ask for clarification on ambiguous requests

6. **ERROR HANDLING**: If operations fail:
   - Explain what went wrong in simple terms
   - Suggest corrective actions
   - Offer alternative approaches

EXAMPLE WORKFLOWS:

**Conditional Column Creation**:
User: "Add Unhealthy column: 1 if Calories > 500, else 0"
→ Use: `add_conditional_column(file, "Unhealthy", "Calories", "> 500", 1, 0)`

**Bulk Row Removal**:
User: "Remove all rows with Category as Burgers"  
→ Use: `remove_rows_by_condition(file, "Category", "Burgers")`

**Complex Updates**:
User: "Set Status to 'Discontinued' for items with Price > 20"
→ Use: `update_column_conditional(file, "Status", "Price", "> 20", "Discontinued")`

Always provide clear, actionable responses and make data manipulation feel effortless for users."""),
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
            return_intermediate_steps=True,  # Changed to True for better debugging
            max_iterations=5  # Increased for complex operations
        )

    def execute(self, file_path: str, question: str):
        """Execute user query against the specified file"""
        try:
            # Validate file_path is not None
            if not file_path:
                return "❌ Error: No file provided. Please upload a CSV or Excel file first."
            
            # Validate file exists
            if not os.path.exists(file_path):
                return f"❌ Error: File not found at {file_path}"
            
            # Prepare input with enhanced context
            full_input = f"""
FILE: {file_path}
USER REQUEST: {question}

Instructions: Analyze the request and use the most appropriate tools to fulfill it efficiently. For complex operations, break them down into logical steps and explain your process.
"""
            
            result = self.executor.invoke({
                "input": full_input
            })

            output = result.get("output", "No output generated")
            steps = result.get("intermediate_steps", [])

            # Enhanced logging with better formatting
            if steps:
                log("=== ENHANCED TOOL EXECUTION TRACE ===", "INFO")
                for i, (action, observation) in enumerate(steps, 1):
                    tool_name = action.tool if hasattr(action, 'tool') else 'Unknown'
                    tool_input = action.tool_input if hasattr(action, 'tool_input') else {}
                    
                    log(f"Step {i} - Tool: {tool_name}", "INFO")
                    log(f"Input: {tool_input}", "INFO") 
                    log(f"Result: {observation[:200]}{'...' if len(str(observation)) > 200 else ''}", "INFO")
                    log("─" * 60, "INFO")
                log("=== END ENHANCED TRACE ===", "INFO")

            # Enhance output with emojis and formatting for better UX
            enhanced_output = self._enhance_output_formatting(output)
            return enhanced_output

        except Exception as e:
            error_msg = f"❌ Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return error_msg

    def _enhance_output_formatting(self, output: str) -> str:
        """Add visual enhancements to output for better user experience"""
        
        # Add emojis and formatting to common patterns
        enhancements = [
            ("successfully", "Successfully"),
            ("Successfully", "Successfully"), 
            ("Error", "Error"),
            ("error", "error"),
            ("Updated", "Updated"),
            ("updated", "updated"),
            ("Added", "Added"),
            ("added", "added"),
            ("Removed", "Removed"),
            ("removed", "removed"),
            ("Found", "Found"),
            ("found", "found"),
            ("File updated", "File saved"),
            ("New shape:", "New shape:"),
            ("Shape:", "Shape:"),
            ("rows", "rows "),
            ("columns", "columns ")
        ]
        
        enhanced = output
        for old, new in enhancements:
            if old in enhanced:
                enhanced = enhanced.replace(old, new, 1)  # Only replace first occurrence
        
        return enhanced

    def get_capabilities_summary(self) -> str:
        """Return a summary of available capabilities"""
        return """
**ENHANCED DATA MANIPULATION CAPABILITIES**

**BASIC OPERATIONS**:
• Add/remove rows and columns
• Modify individual cells or entire rows  
• Rename columns and preview data
• Get file statistics and structure

**ADVANCED FILTERING & SEARCH**:
• Remove rows by conditions (>, <, ==, !=, etc.)
• Filter and save data based on criteria
• Find and replace values across columns
• Get unique values and count occurrences

**SMART TRANSFORMATIONS**:
• Add calculated columns (math operations)
• Create conditional columns (if-then logic)
• Update values based on conditions in other columns
• Bulk update multiple cells efficiently

**DATA ANALYSIS**:
• Statistical summaries for columns or entire dataset  
• Sort data by multiple columns
• Duplicate specific rows
• Count value frequencies

**EXAMPLE REQUESTS**:
• "Remove all rows where Category equals Burgers"
• "Add column 'Healthy' with 1 if Calories < 400, else 0"  
• "Set Status to 'Expensive' where Price > 15"
• "Show me statistics for the Calories column"
• "Sort data by Category then Price descending"

Just tell me what you want to do with your data in plain English!
"""