# transformer_operator.py
from langchain_core.tools import tool
from tools.transformer import DataTransformer
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
def standardize_column(file_path: str, column_name: str) -> str:
    """Standardize a numeric column using Z-score.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to standardize
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"

        transformer = DataTransformer(file_path)
        return transformer.standardize_column(column_name)
    except Exception as e:
        return f"Error standardizing column: {str(e)}"

@tool
def remove_duplicate_rows(file_path: str) -> str:
    """Remove duplicate rows from the dataset.
    
    Args:
        file_path: Path to the CSV/Excel file
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"

        transformer = DataTransformer(file_path)
        return transformer.remove_duplicates()
    except Exception as e:
        return f"Error removing duplicates: {str(e)}"

@tool
def drop_rows_with_missing_values(file_path: str) -> str:
    """Drop all rows that contain any missing values.
    
    Args:
        file_path: Path to the CSV/Excel file
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"

        transformer = DataTransformer(file_path)
        return transformer.drop_missing_rows()
    except Exception as e:
        return f"Error dropping rows with missing values: {str(e)}"

def get_transformer_tools():
    """Return all available transformer tools"""
    return [
        fill_missing_values,
        change_column_dtype,
        normalize_column,
        standardize_column,
        remove_duplicate_rows,
        drop_rows_with_missing_values
    ]