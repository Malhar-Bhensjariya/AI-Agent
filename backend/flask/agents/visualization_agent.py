from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from services.visualize_operator import get_visualization_tools
from utils.logger import log
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

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
            ("system", """You are a data visualization assistant. Your role is to help users create interactive charts and plots from their data files using Chart.js.

IMPORTANT RULES:
1. Always use the provided tools to generate interactive chart configurations
2. File paths are provided by the user - use them exactly as given
3. Only respond to visualization-related queries
4. Support various plot types: bar plots, line plots, scatter plots, pie charts, histograms, multi-series charts
5. Always validate that the requested columns exist in the data
6. Return the chart configuration as JSON that can be used with Chart.js
7. If a visualization fails, explain why and suggest alternatives
8. Provide clear feedback about the visualization created and describe what the chart shows

Available visualization operations:
- Create interactive bar plots, line plots, scatter plots
- Generate interactive pie charts and histograms
- Create multi-series plots with multiple data series
- Get plot recommendations based on data types
- Provide data summaries for visualization planning

Chart Types Supported:
- Bar Chart: For categorical vs numeric data
- Line Chart: For time series or continuous numeric data
- Scatter Plot: For correlation between two numeric variables
- Pie Chart: For categorical data distribution (max 10 categories)
- Histogram: For numeric data distribution
- Multi-series Chart: For comparing multiple variables

Example requests:
- "Create a bar plot with x='Category' and y='Sales'"
- "Generate line plot for Date vs Temperature"
- "Show pie chart of 'Status' column"
- "Create scatter plot of Height vs Weight"
- "Make a multi-series line chart with Sales and Profit over Time"

The response will include Chart.js configuration JSON that the frontend can use to render interactive charts.

Always extract and return the chart configuration JSON from tool responses for the frontend to use."""),
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
            return_intermediate_steps=False,
            max_iterations=3
        )

    def _extract_chart_config(self, tool_response: str) -> dict:
        """Extract Chart.js configuration JSON from tool response"""
        try:
            # Look for JSON in the response using regex - improved pattern
            json_pattern = r'Chart data: (\{.*?\})(?=\s|$)'
            match = re.search(json_pattern, tool_response, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            else:
                # Try to find any complete JSON object with proper nesting
                json_pattern = r'(\{(?:[^{}]|{[^{}]*})*\})'
                matches = re.findall(json_pattern, tool_response, re.DOTALL)
                for json_str in matches:
                    try:
                        parsed = json.loads(json_str)
                        if 'type' in parsed and 'data' in parsed:
                            return parsed
                    except:
                        continue
                
            return None
        except (json.JSONDecodeError, AttributeError) as e:
            log(f"Failed to extract chart configuration: {str(e)}", "WARNING")
            return None

    def execute(self, file_path: str, question: str) -> dict:
        """Execute user visualization query against the specified file"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"Error: File not found at {file_path}",
                    "chart_config": None
                }
            
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
                    log(f"Result: {observation[:200]}...", "INFO")  # Truncate long results
                    log("-" * 50, "INFO")
                log("=== END VISUALIZATION TRACE ===", "INFO")

            # Extract chart configuration from the output
            chart_config = None
            if steps:
                # Try to extract from the last tool observation
                last_observation = steps[-1][1] if steps else ""
                chart_config = self._extract_chart_config(last_observation)
            
            # If no chart config found in steps, try the final output
            if not chart_config:
                chart_config = self._extract_chart_config(output)

            # Determine if this was a successful chart generation
            success = chart_config is not None
            
            # Clean up the message for user display
            clean_message = self._clean_message(output, success)

            return {
                "success": success,
                "message": clean_message,
                "chart_config": chart_config,
                "chart_type": chart_config.get("type") if chart_config else None
            }

        except Exception as e:
            error_msg = f"Visualization Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return {
                "success": False,
                "message": error_msg,
                "chart_config": None
            }

    def _clean_message(self, message: str, has_chart: bool) -> str:
        """Clean up the message for user display"""
        # Remove chart data JSON from message since it's returned separately
        cleaned = re.sub(r'Chart data: \{.*\}', '', message, flags=re.DOTALL)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # If the message is too technical, provide a friendlier version
        if has_chart:
            if "configuration generated successfully" in cleaned.lower():
                chart_type = "chart"
                if "bar plot" in cleaned.lower():
                    chart_type = "bar chart"
                elif "line plot" in cleaned.lower():
                    chart_type = "line chart"
                elif "pie chart" in cleaned.lower():
                    chart_type = "pie chart"
                elif "histogram" in cleaned.lower():
                    chart_type = "histogram"
                elif "scatter plot" in cleaned.lower():
                    chart_type = "scatter plot"
                
                return f"✅ Interactive {chart_type} created successfully! The chart is ready to display."
        
        return cleaned if cleaned else "Visualization request processed."

    def get_data_summary(self, file_path: str) -> dict:
        """Get a summary of the data for visualization planning"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"Error: File not found at {file_path}"
                }
            
            result = self.executor.invoke({
                "input": f"File: {file_path}\nRequest: Get data summary for plotting"
            })
            
            return {
                "success": True,
                "message": result.get("output", "Data summary generated"),
                "summary": result.get("output", "")
            }
            
        except Exception as e:
            error_msg = f"Error getting data summary: {str(e)}"
            log(error_msg, "ERROR")
            return {
                "success": False,
                "message": error_msg
            }