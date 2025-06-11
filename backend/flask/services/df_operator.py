from typing import List, Any
from langchain_core.tools import tool
from tools.df_editor import DataEditor

@tool
def remove_row(file_path: str, row_index: int) -> str:
    """Remove a specific row from the CSV/Excel file (1-based index).
    
    Args:
        file_path: Path to the CSV/Excel file
        row_index: Row number to remove (1-based, e.g., 1 for first row)
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.remove_row(row_index)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error removing row: {str(e)}"

@tool
def remove_column(file_path: str, column_name: str) -> str:
    """Remove a specific column by name from the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to remove
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.remove_column(column_name)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error removing column: {str(e)}"

@tool
def add_column(file_path: str, column_name: str, default_value: str = "") -> str:
    """Add a new column to the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the new column
        default_value: Default value for all cells in the new column
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.add_column(column_name, default_value)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error adding column: {str(e)}"

@tool
def add_row(file_path: str, row_values: List[Any]) -> str:
    """Add a new row to the CSV/Excel file. Values must match column order.
    
    Args:
        file_path: Path to the CSV/Excel file
        row_values: List of values for the new row (must match column count and order)
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.add_row(row_values)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error adding row: {str(e)}"

@tool
def set_cell(file_path: str, row_index: int, column_name: str, value: Any) -> str:
    """Set a specific cell's value in the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        row_index: Row number (1-based)
        column_name: Column name
        value: New value for the cell
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.set_cell_value(row_index, column_name, value)
        return f"{message}. File updated."
    except Exception as e:
        return f"Error setting cell: {str(e)}"

@tool
def set_row(file_path: str, row_index: int, values: List[Any]) -> str:
    """Replace all values of a specific row in the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        row_index: Row number (1-based)
        values: List of new values for the row (must match column count)
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.set_row_values(row_index, values)
        return f"{message}. File updated."
    except Exception as e:
        return f"Error setting row: {str(e)}"

@tool
def get_summary(file_path: str) -> str:
    """Get comprehensive summary of the CSV/Excel file including structure and statistics.
    
    Args:
        file_path: Path to the CSV/Excel file
    """
    try:
        editor = DataEditor(file_path)
        summary = editor.get_summary()
        
        # Format summary for better readability
        basic = summary["basic_info"]
        result = f"""File Summary for: {basic['file_path']}
        
Shape: {basic['shape'][0]} rows × {basic['shape'][1]} columns
Columns: {', '.join(basic['columns'])}

Data Types:
{chr(10).join([f'  {col}: {dtype}' for col, dtype in basic['dtypes'].items()])}

Missing Values:
{chr(10).join([f'  {col}: {count}' for col, count in basic['missing_values'].items() if count > 0]) or '  None'}

Numeric Columns: {', '.join(basic['numeric_columns']) if basic['numeric_columns'] else 'None'}
Categorical Columns: {', '.join(basic['categorical_columns']) if basic['categorical_columns'] else 'None'}
"""
        return result
        
    except Exception as e:
        return f"Error getting summary: {str(e)}"

@tool
def get_preview(file_path: str, num_rows: int = 5) -> str:
    """Get a preview of the first few rows of the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        num_rows: Number of rows to preview (default: 5)
    """
    try:
        editor = DataEditor(file_path)
        preview = editor.get_preview(num_rows)
        
        result = f"""Preview of {preview['file_path']} (showing {min(num_rows, len(preview['data']))} of {preview['shape'][0]} rows):

Columns: {', '.join(preview['columns'])}

Data:
"""
        for i, row in enumerate(preview['data'], 1):
            result += f"Row {i}: {dict(row)}\n"
            
        return result
        
    except Exception as e:
        return f"Error getting preview: {str(e)}"

def get_csv_tools():
    """Return all available DataFrame editing tools"""
    return [
        remove_row,
        remove_column,
        add_column,
        add_row,
        set_cell,
        set_row,
        get_summary,
        get_preview,
    ]