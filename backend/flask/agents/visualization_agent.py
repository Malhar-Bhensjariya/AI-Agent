from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from flask_app.tools.visualize_operator import get_visualization_tools
from flask_app.utils.logger import log
import os


class VisualizationAgentExecutor:
    def __init__(self):
        # Initialize Gemini model for LangChain (following the pattern from CSVAgentExecutor)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data visualization assistant. Your role is to help users create charts and plots from their data files.

IMPORTANT RULES:
1. Always use the provided tools to generate visualizations
2. File paths are provided by the user - use them exactly as given
3. Only respond to visualization-related queries
4. Support various plot types: bar plots, line plots, scatter plots, pie charts, histograms, etc.
5. Always validate that the requested columns exist in the data
6. Provide clear feedback about the visualization created
7. If a visualization fails, explain why and suggest alternatives

Available visualization operations:
- Create bar plots, line plots, scatter plots
- Generate pie charts and histograms
- Create multi-series plots
- Customize plot appearance (titles, labels, colors)

Example requests:
- "Create a bar plot with x='Category' and y='Sales'"
- "Generate line plot for Date vs Temperature"
- "Show pie chart of 'Status' column"
- "Create scatter plot of Height vs Weight"

Always confirm successful visualizations and provide helpful context about the charts created."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.tools = get_visualization_tools()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            return_intermediate_steps=Flase,
            max_iterations=3
        )

    def execute(self, file_path: str, question: str) -> str:
        """Execute user visualization query against the specified file"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Prepare input with context
            full_input = f"File: {file_path}\nVisualization Request: {question}"
            
            result = self.executor.invoke({
                "input": full_input
            })

            output = result.get("output", "No output generated")
            steps = result.get("intermediate_steps", [])

            # Log tool usage for debugging
            if steps:
                log("=== VISUALIZATION TOOL EXECUTION TRACE ===", "INFO")
                for i, (action, observation) in enumerate(steps, 1):
                    tool_name = action.tool if hasattr(action, 'tool') else 'Unknown'
                    tool_input = action.tool_input if hasattr(action, 'tool_input') else {}
                    log(f"Step {i} - Tool: {tool_name}", "INFO")
                    log(f"Input: {tool_input}", "INFO") 
                    log(f"Result: {observation}", "INFO")
                    log("-" * 50, "INFO")
                log("=== END VISUALIZATION TRACE ===", "INFO")

            return output

        except Exception as e:
            error_msg = f"Visualization Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return error_msg