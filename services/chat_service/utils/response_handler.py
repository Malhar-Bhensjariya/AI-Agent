"""
Response handling utilities for Flask app
Handles JSON serialization, data cleaning, and response validation
"""

import json
import pandas as pd
import re
from utils.logger import log


def clean_for_json_serialization(obj):
    """
    Recursively clean data to ensure JSON serialization compatibility
    This is the KEY FIX for JSON parsing issues with NaN/Infinity values
    """
    if obj is None:
        return None
    elif isinstance(obj, (bool, int)):
        return obj
    elif isinstance(obj, float):
        # Handle NaN, Infinity, -Infinity - CRITICAL FIX
        # Compatible with all pandas versions
        import math
        if pd.isna(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, str):
        # Clean potentially problematic strings
        try:
            # Remove control characters that can break JSON
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', obj)
            # Ensure proper encoding
            cleaned.encode('utf-8')
            return cleaned
        except (UnicodeDecodeError, UnicodeEncodeError):
            return str(obj).encode('utf-8', errors='replace').decode('utf-8')
    elif isinstance(obj, dict):
        return {key: clean_for_json_serialization(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json_serialization(item) for item in obj]
    elif isinstance(obj, pd.DataFrame):
        # Convert DataFrame to clean dict format
        return clean_for_json_serialization(obj.to_dict('records'))
    elif hasattr(obj, '__dict__'):
        # Handle objects with attributes
        return clean_for_json_serialization(obj.__dict__)
    else:
        # Fallback: convert to string
        return str(obj)


def validate_json_response(data):
    """
    Validate that data can be serialized to JSON
    Returns (is_valid, cleaned_data, error_message)
    """
    try:
        # First clean the data
        cleaned_data = clean_for_json_serialization(data)
        
        # Try to serialize
        json_string = json.dumps(cleaned_data, ensure_ascii=False, separators=(',', ':'))
        
        # Verify it's not too large (1MB limit for response)
        if len(json_string) > 1024 * 1024:
            return False, None, "Response too large"
        
        # Try to parse it back
        parsed = json.loads(json_string)
        
        return True, cleaned_data, None
    except Exception as e:
        return False, None, str(e)


def strip_markdown(text):
    """Remove markdown formatting from text"""
    if not isinstance(text, str):
        return str(text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)     # Remove *italic*
    text = re.sub(r'__(.*?)__', r'\1', text)     # Remove __bold__
    text = re.sub(r'_(.*?)_', r'\1', text)       # Remove _italic_
    text = re.sub(r'`(.*?)`', r'\1', text)       # Remove `code`
    text = re.sub(r'```[\s\S]*?```', '', text)   # Remove ```code blocks```
    text = re.sub(r'#{1,6}\s+', '', text)        # Remove # headers
    
    return text.strip()


def validate_chart_config(chart_config: dict) -> bool:
    """Validate that the chart config is properly formatted for Chart.js"""
    if not isinstance(chart_config, dict):
        return False
    
    # Check required Chart.js fields
    required_fields = ['type', 'data']
    if not all(field in chart_config for field in required_fields):
        log(f"Chart config missing required fields: {required_fields}", "WARNING")
        return False
    
    # Validate chart type
    valid_types = ['bar', 'line', 'scatter', 'pie', 'doughnut', 'radar', 'polarArea']
    if chart_config.get('type') not in valid_types:
        log(f"Invalid chart type: {chart_config.get('type')}", "WARNING")
        return False
    
    # Validate data structure
    data = chart_config.get('data', {})
    if not isinstance(data, dict):
        log("Chart data is not a dictionary", "WARNING")
        return False
    
    return True


def extract_chart_from_response(result) -> dict:
    """Extract chart configuration from various response formats"""
    # Case 1: Result is already a structured dict from visualization agent
    if isinstance(result, dict):
        if result.get('type') == 'chart' and result.get('chart_config'):
            chart_config = result['chart_config']
            if validate_chart_config(chart_config):
                return {
                    'chart_config': chart_config,
                    'chart_type': result.get('chart_type', chart_config.get('type', 'bar')),
                    'message': result.get('message', 'Chart created successfully'),
                    'success': result.get('success', True)
                }
        return None
    
    # Case 2: Result is a JSON string
    if isinstance(result, str):
        try:
            # Try to parse as JSON first
            if result.strip().startswith('{'):
                parsed = json.loads(result)
                if isinstance(parsed, dict) and parsed.get('type') == 'chart':
                    chart_config = parsed.get('chart_config')
                    if chart_config and validate_chart_config(chart_config):
                        return {
                            'chart_config': chart_config,
                            'chart_type': parsed.get('chart_type', chart_config.get('type', 'bar')),
                            'message': parsed.get('message', 'Chart created successfully'),
                            'success': True
                        }
        except json.JSONDecodeError:
            pass
        
        # Look for chart config patterns in text
        config_pattern = r'CHART_CONFIG_START\s*(\{.*?\})\s*CHART_CONFIG_END'
        match = re.search(config_pattern, result, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                chart_config = json.loads(json_str)
                if validate_chart_config(chart_config):
                    return {
                        'chart_config': chart_config,
                        'chart_type': chart_config.get('type', 'bar'),
                        'message': 'Chart created successfully',
                        'success': True
                    }
            except json.JSONDecodeError:
                pass
        
        # Look for JSON code blocks
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, result, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                chart_config = json.loads(json_str)
                if validate_chart_config(chart_config):
                    return {
                        'chart_config': chart_config,
                        'chart_type': chart_config.get('type', 'bar'),
                        'message': 'Chart created successfully',
                        'success': True
                    }
            except json.JSONDecodeError:
                pass
    
    return None


def create_safe_response(response_data: dict) -> dict:
    """
    Create a safe JSON response by cleaning and validating data
    Returns cleaned response or fallback response
    """
    try:
        # Clean all response data
        cleaned_response = clean_for_json_serialization(response_data)
        
        # Validate JSON serialization
        is_valid, final_response, error = validate_json_response(cleaned_response)
        
        if not is_valid:
            log(f"Response validation failed: {error}", "ERROR")
            log(f"Original response keys: {response_data.keys()}", "ERROR")
            
            # Return minimal safe response
            return {
                "success": True,
                "type": "text",
                "text": "I received your message and I'm ready to help analyze your data. Could you please rephrase your question?"
            }
        
        return final_response
        
    except Exception as e:
        log(f"Error creating safe response: {str(e)}", "ERROR")
        
        # Ultimate fallback
        return {
            "success": True,
            "type": "text",
            "text": "I'm ready to help analyze your data. What would you like to know?"
        }


def create_error_response(error_message: str, include_details: bool = False) -> dict:
    """Create a standardized error response"""
    response = {
        "success": False,
        "type": "error",
        "error": str(error_message)[:200]  # Limit error message length
    }
    
    if include_details:
        response["details"] = "Check server logs for more information"
    
    return response


def create_chart_response(chart_data: dict, message: str = None) -> dict:
    """Create a standardized chart response"""
    return {
        "success": True,
        "type": "chart",
        "chart_config": clean_for_json_serialization(chart_data["chart_config"]),
        "chart_type": chart_data["chart_type"],
        "text": strip_markdown(message or chart_data.get("message", "Chart created successfully"))
    }


def create_text_response(text: str, success: bool = True) -> dict:
    """Create a standardized text response"""
    return {
        "success": success,
        "type": "text",
        "text": strip_markdown(str(text))
    }


def create_file_response(file_info: dict, message: str = None) -> dict:
    """Create a response that includes file information"""
    response = {
        "success": True,
        "type": "file",
        "file_info": clean_for_json_serialization(file_info)
    }
    
    if message:
        response["text"] = strip_markdown(message)
    
    return response