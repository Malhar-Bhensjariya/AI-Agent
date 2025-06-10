# transformer_operator.py
from langchain_core.tools import tool
from flask_app.tools.transformer import DataTransformer
import os

@tool
def fill_missing_values(file_path: str, column_name: str, value: str) -> str:
    """Fill missing values in a column with a specific value.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to fill
        value: Value to use for filling missing entries
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        transformer = DataTransformer(file_path)
        result = transformer.fill_missing(column_name, value)
        return result
    except Exception as e:
        return f"Error filling missing values: {str(e)}"

@tool
def change_column_dtype(file_path: str, column_name: str, dtype: str) -> str:
    """Convert a column's data type to int, float, str, etc.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to convert
        dtype: Target data type (int, float, str, bool, etc.)
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        transformer = DataTransformer(file_path)
        result = transformer.change_dtype(column_name, dtype)
        return result
    except Exception as e:
        return f"Error changing column data type: {str(e)}"

@tool
def normalize_column(file_path: str, column_name: str) -> str:
    """Normalize a numeric column using min-max scaling (0-1 range).
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the numeric column to normalize
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        transformer = DataTransformer(file_path)
        result = transformer.normalize_column(column_name)
        return result
    except Exception as e:
        return f"Error normalizing column: {str(e)}"

@tool
def get_dataframe_info(file_path: str) -> str:
    """Get basic information about the dataframe (columns, dtypes, shape).
    
    Args:
        file_path: Path to the CSV/Excel file
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        transformer = DataTransformer(file_path)
        info = transformer.get_column_info()  # Fixed: changed from get_info() to get_column_info()
        
        # Format the info dictionary as a readable string
        if isinstance(info, dict):
            result = []
            result.append(f"Dataset Shape: {info.get('shape', 'Unknown')}")
            result.append(f"Columns: {', '.join(info.get('columns', []))}")
            result.append("\nData Types:")
            for col, dtype in info.get('dtypes', {}).items():
                result.append(f"  {col}: {dtype}")
            result.append("\nMissing Values:")
            for col, missing in info.get('missing_values', {}).items():
                if missing > 0:
                    result.append(f"  {col}: {missing}")
            if not any(missing > 0 for missing in info.get('missing_values', {}).values()):
                result.append("  No missing values found")
            return "\n".join(result)
        else:
            return str(info)
    except Exception as e:
        return f"Error getting dataframe info: {str(e)}"

@tool
def get_column_info(file_path: str, column_name: str) -> str:
    """Get detailed information about a specific column.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to analyze
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        transformer = DataTransformer(file_path)
        info = transformer.get_column_info(column_name)
        
        # Format the column info as a readable string
        if isinstance(info, dict):
            result = []
            result.append(f"Column: {info.get('name', 'Unknown')}")
            result.append(f"Data Type: {info.get('dtype', 'Unknown')}")
            result.append(f"Non-null Count: {info.get('non_null_count', 'Unknown')}")
            result.append(f"Null Count: {info.get('null_count', 'Unknown')}")
            result.append(f"Unique Values: {info.get('unique_count', 'Unknown')}")
            
            # Add numeric statistics if available
            if 'min' in info:
                result.append(f"Min: {info['min']}")
                result.append(f"Max: {info['max']}")
                result.append(f"Mean: {info.get('mean', 'N/A'):.4f}" if info.get('mean') is not None else "Mean: N/A")
                result.append(f"Std Dev: {info.get('std', 'N/A'):.4f}" if info.get('std') is not None else "Std Dev: N/A")
            
            return "\n".join(result)
        else:
            return str(info)
    except Exception as e:
        return f"Error getting column info: {str(e)}"

def get_transformer_tools():
    """Return all available transformer tools"""
    return [
        fill_missing_values,
        change_column_dtype,
        normalize_column,
        get_dataframe_info,
        get_column_info
    ]