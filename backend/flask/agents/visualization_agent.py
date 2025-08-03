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

When you receive a chart configuration from the tools, you MUST return it in the following format:
CHART_CONFIG_START
{{chart_config_json_here}}
CHART_CONFIG_END

This format helps the system extract the chart configuration properly."""),
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
            return_intermediate_steps=True,  # Enable to capture tool outputs
            max_iterations=3
        )

    def _extract_chart_config(self, text: str) -> dict:
        """Extract Chart.js configuration JSON from text response"""
        try:
            # First, try to find the special markers
            config_pattern = r'CHART_CONFIG_START\s*(\{.*?\})\s*CHART_CONFIG_END'
            match = re.search(config_pattern, text, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            
            # If no markers, try to find JSON in the response
            json_pattern = r'(\{(?:"type":\s*"(?:bar|line|scatter|pie|histogram|doughnut)"[^}]*\{.*?\}.*?)\})'
            match = re.search(json_pattern, text, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            
            # Try to find any complete JSON object that looks like a chart config
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
            for json_str in json_objects:
                try:
                    parsed = json.loads(json_str)
                    # Check if it's a valid chart config
                    if isinstance(parsed, dict) and 'type' in parsed and 'data' in parsed:
                        return parsed
                except:
                    continue
                    
            return None
        except Exception as e:
            log(f"Failed to extract chart configuration: {str(e)}", "WARNING")
            return None

    def _extract_chart_from_tool_response(self, tool_response: str) -> dict:
        """Extract chart configuration from tool response JSON"""
        try:
            # Tool responses are JSON strings, so parse them first
            if tool_response.startswith('{') and tool_response.endswith('}'):
                parsed_response = json.loads(tool_response)
                
                # Check if it's a chart response
                if parsed_response.get('type') == 'chart':
                    return parsed_response.get('chart_config')
                    
                # Check if chart_config is directly in the response
                if 'chart_config' in parsed_response:
                    return parsed_response['chart_config']
                    
            return None
        except Exception as e:
            log(f"Failed to extract chart from tool response: {str(e)}", "WARNING")
            return None

    def execute(self, file_path: str, question: str) -> dict:
        """Execute user visualization query against the specified file"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"Error: File not found at {file_path}",
                    "chart_config": None,
                    "type": "error"
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
                    log(f"Result: {observation[:500]}...", "INFO")  # Show more of the result
                    log("-" * 50, "INFO")
                log("=== END VISUALIZATION TRACE ===", "INFO")

            # Extract chart configuration - try multiple approaches
            chart_config = None
            chart_type = None
            message = "Request processed."
            
            # First, try to extract from tool responses
            if steps:
                for action, observation in steps:
                    tool_name = action.tool if hasattr(action, 'tool') else ''
                    if 'chart' in tool_name.lower() or 'plot' in tool_name.lower():
                        # This is a chart-generating tool
                        chart_config = self._extract_chart_from_tool_response(observation)
                        if chart_config:
                            chart_type = chart_config.get('type', 'bar')
                            # Try to extract message from tool response
                            try:
                                parsed_obs = json.loads(observation)
                                message = parsed_obs.get('message', f'{chart_type.title()} chart created successfully!')
                            except:
                                message = f'{chart_type.title()} chart created successfully!'
                            break
            
            # If no chart config from tools, try the final output
            if not chart_config:
                chart_config = self._extract_chart_config(output)
                if chart_config:
                    chart_type = chart_config.get('type', 'bar')
                    message = self._clean_message_for_chart(output, chart_type)

            # Determine success and create response
            success = chart_config is not None
            
            if success:
                return {
                    "success": True,
                    "message": message,
                    "chart_config": chart_config,
                    "chart_type": chart_type,
                    "type": "chart"
                }
            else:
                # No chart generated, return as text response
                clean_message = self._clean_message(output, False)
                return {
                    "success": False,
                    "message": clean_message,
                    "chart_config": None,
                    "type": "text"
                }

        except Exception as e:
            error_msg = f"Visualization Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return {
                "success": False,
                "message": error_msg,
                "chart_config": None,
                "type": "error"
            }

    def _clean_message_for_chart(self, message: str, chart_type: str) -> str:
        """Clean up message for successful chart generation"""
        # Remove any JSON or technical details from the message
        cleaned = re.sub(r'```json.*?```', '', message, flags=re.DOTALL)
        cleaned = re.sub(r'CHART_CONFIG_START.*?CHART_CONFIG_END', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'\{.*?\}', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Create a friendly message
        chart_name = chart_type.replace('_', ' ').title()
        if cleaned and len(cleaned) > 10:
            # If there's meaningful text left, use it
            return f"✅ {chart_name} created successfully! {cleaned}"
        else:
            # Default friendly message
            return f"✅ Interactive {chart_name} created successfully! The chart is ready to display."

    def _clean_message(self, message: str, has_chart: bool) -> str:
        """Clean up the message for display"""
        # Remove chart data JSON from message since it's returned separately
        cleaned = re.sub(r'```json.*?```', '', message, flags=re.DOTALL)
        cleaned = re.sub(r'CHART_CONFIG_START.*?CHART_CONFIG_END', '', cleaned, flags=re.DOTALL)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if cleaned else "Request processed."

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