from typing import List, Any, Dict
from langchain_core.tools import tool
from tools.df_editor import DataEditor

# Original basic tools
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

@tool
def rename_column(file_path: str, old_name: str, new_name: str) -> str:
    """Rename a column in the CSV/Excel file.
    
    Args:
        file_path: Path to the CSV/Excel file
        old_name: Current name of the column
        new_name: New name for the column
    """
    try:
        editor = DataEditor(file_path)
        message = editor.rename_column(old_name, new_name)
        return f"{message}. File updated."
    except Exception as e:
        return f"Error renaming column: {str(e)}"

# NEW ADVANCED TOOLS

@tool
def remove_rows_by_condition(file_path: str, column_name: str, condition: str) -> str:
    """Remove all rows that match a specific condition. Supports operators: ==, !=, >, <, >=, <=.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to check condition against
        condition: Condition to match (e.g., "Burgers", "> 500", "!= Active", "<= 100")
        
    Examples:
        remove_rows_by_condition("file.csv", "Category", "Burgers") - removes rows where Category equals "Burgers"
        remove_rows_by_condition("file.csv", "Calories", "> 500") - removes rows where Calories > 500
        remove_rows_by_condition("file.csv", "Status", "!= Active") - removes rows where Status is not "Active"
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.remove_rows_by_condition(column_name, condition)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error removing rows by condition: {str(e)}"

@tool
def update_column_conditional(file_path: str, target_column: str, condition_column: str, condition: str, new_value: Any) -> str:
    """Update values in a target column based on conditions in another column.
    
    Args:
        file_path: Path to the CSV/Excel file
        target_column: Column to update values in
        condition_column: Column to check condition against
        condition: Condition to match (supports ==, !=, >, <, >=, <=)
        new_value: New value to set for matching rows
        
    Examples:
        update_column_conditional("file.csv", "Unhealthy", "Calories", "< 500", 0) - sets Unhealthy=0 where Calories < 500
        update_column_conditional("file.csv", "Status", "Category", "Burgers", "Junk") - sets Status="Junk" where Category="Burgers"
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.update_column_conditional(target_column, condition_column, condition, new_value)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error updating column conditionally: {str(e)}"

@tool
def add_calculated_column(file_path: str, new_column: str, source_column: str, operation: str, operand: float = None) -> str:
    """Add a new column with calculated values based on an existing column.
    
    Args:
        file_path: Path to the CSV/Excel file
        new_column: Name of the new column to create
        source_column: Existing column to base calculations on
        operation: Operation to perform (multiply, divide, add, subtract, square, sqrt, absolute)
        operand: Number to use in operation (required for multiply, divide, add, subtract)
        
    Examples:
        add_calculated_column("file.csv", "Double_Calories", "Calories", "multiply", 2)
        add_calculated_column("file.csv", "Calories_Squared", "Calories", "square")
        add_calculated_column("file.csv", "Price_Plus_Tax", "Price", "add", 5.99)
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.add_calculated_column(new_column, source_column, operation, operand)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error adding calculated column: {str(e)}"

@tool
def bulk_update_cells(file_path: str, updates: List[Dict[str, Any]]) -> str:
    """Update multiple cells in one operation for efficiency.
    
    Args:
        file_path: Path to the CSV/Excel file
        updates: List of dictionaries with keys: 'row' (1-based), 'column', 'value'
        
    Example:
        updates = [
            {'row': 1, 'column': 'Status', 'value': 'Active'},
            {'row': 2, 'column': 'Status', 'value': 'Inactive'},
            {'row': 1, 'column': 'Priority', 'value': 'High'}
        ]
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.bulk_update_cells(updates)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error bulk updating cells: {str(e)}"

@tool
def filter_and_save(file_path: str, column_name: str, condition: str, save_filtered: bool = False) -> str:
    """Filter data based on condition and optionally save the filtered result.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Column to filter on
        condition: Condition to match (supports ==, !=, >, <, >=, <=)
        save_filtered: If True, replace file with filtered data; if False, just show preview
        
    Examples:
        filter_and_save("file.csv", "Category", "Burgers", True) - keep only Burger rows
        filter_and_save("file.csv", "Calories", "> 300", False) - preview rows with Calories > 300
    """
    try:
        editor = DataEditor(file_path)
        message, result_df = editor.filter_and_save(column_name, condition, save_filtered)
        return f"{message}. Result shape: {result_df.shape}"
    except Exception as e:
        return f"Error filtering data: {str(e)}"

@tool
def sort_data(file_path: str, columns: List[str], ascending: bool = True) -> str:
    """Sort data by one or more columns.
    
    Args:
        file_path: Path to the CSV/Excel file
        columns: List of column names to sort by (in order of priority)
        ascending: True for ascending order, False for descending
        
    Examples:
        sort_data("file.csv", ["Calories"], False) - sort by Calories descending
        sort_data("file.csv", ["Category", "Calories"], True) - sort by Category then Calories, both ascending
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.sort_data(columns, ascending)
        return f"{message}. File updated. Shape: {updated_df.shape}"
    except Exception as e:
        return f"Error sorting data: {str(e)}"

@tool
def get_statistics(file_path: str, column_name: str = None) -> str:
    """Get statistical summary of data or specific column.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Specific column to analyze (optional - if None, analyzes whole dataset)
        
    Examples:
        get_statistics("file.csv") - overall dataset statistics
        get_statistics("file.csv", "Calories") - statistics for Calories column only
    """
    try:
        editor = DataEditor(file_path)
        stats = editor.get_statistics(column_name)
        
        if column_name:
            # Format single column stats
            col_stats = stats[column_name]
            result = f"Statistics for column '{column_name}':\n"
            for key, value in col_stats.items():
                result += f"  {key}: {value}\n"
        else:
            # Format overall stats
            result = f"Dataset Overview:\n"
            result += f"  Shape: {stats['shape']} (rows, columns)\n"
            result += f"  Columns: {', '.join(stats['columns'])}\n"
            result += f"\nData Types:\n"
            for col, dtype in stats['dtypes'].items():
                result += f"  {col}: {dtype}\n"
            result += f"\nMissing Values:\n"
            for col, nulls in stats['null_counts'].items():
                if nulls > 0:
                    result += f"  {col}: {nulls} missing\n"
        
        return result
        
    except Exception as e:
        return f"Error getting statistics: {str(e)}"

@tool
def duplicate_rows(file_path: str, row_indices: List[int], count: int = 1) -> str:
    """Duplicate specific rows a given number of times.
    
    Args:
        file_path: Path to the CSV/Excel file
        row_indices: List of row numbers to duplicate (1-based)
        count: Number of times to duplicate each row (default: 1)
        
    Examples:
        duplicate_rows("file.csv", [1, 3], 2) - duplicate rows 1 and 3, each 2 times
        duplicate_rows("file.csv", [5], 1) - duplicate row 5 once
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.duplicate_rows(row_indices, count)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error duplicating rows: {str(e)}"

@tool
def find_and_replace(file_path: str, column_name: str, find_value: Any, replace_value: Any) -> str:
    """Find and replace all occurrences of a value in a specific column.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Column to search in
        find_value: Value to find and replace
        replace_value: New value to replace with
        
    Examples:
        find_and_replace("file.csv", "Status", "Active", "Enabled")
        find_and_replace("file.csv", "Category", "Burger", "Burgers")
        find_and_replace("file.csv", "Price", 9.99, 10.99)
    """
    try:
        editor = DataEditor(file_path)
        message, updated_df = editor.find_and_replace(column_name, find_value, replace_value)
        return f"{message}. File updated. New shape: {updated_df.shape}"
    except Exception as e:
        return f"Error in find and replace: {str(e)}"

@tool
def add_conditional_column(file_path: str, new_column: str, condition_column: str, condition: str, true_value: Any, false_value: Any) -> str:
    """Add a new column with values based on a condition in another column.
    
    Args:
        file_path: Path to the CSV/Excel file
        new_column: Name of the new column to create
        condition_column: Column to check condition against
        condition: Condition to evaluate (supports ==, !=, >, <, >=, <=)
        true_value: Value to set when condition is True
        false_value: Value to set when condition is False
        
    Examples:
        add_conditional_column("file.csv", "Unhealthy", "Calories", "> 500", 1, 0)
        add_conditional_column("file.csv", "Category_Type", "Category", "Burgers", "Fast Food", "Other")
        add_conditional_column("file.csv", "High_Price", "Price", ">= 15.00", "Expensive", "Affordable")
    """
    try:
        editor = DataEditor(file_path)
        
        # Check if column already exists
        if new_column in editor.df.columns:
            return f"Error: Column '{new_column}' already exists"
        
        # Validate condition column
        if condition_column not in editor.df.columns:
            return f"Error: Condition column '{condition_column}' does not exist"
        
        # Parse condition and create mask
        mask = editor._parse_condition(condition, condition_column)
        
        # Add new column with conditional values
        editor.df[new_column] = false_value  # Default value
        editor.df.loc[mask, new_column] = true_value  # True condition value
        
        # Update original columns list
        editor.original_columns.append(new_column)
        editor._save_dataframe()
        
        true_count = mask.sum()
        false_count = len(editor.df) - true_count
        
        message = f"Added conditional column '{new_column}': {true_count} rows = '{true_value}', {false_count} rows = '{false_value}'"
        return f"{message}. File updated. New shape: {editor.df.shape}"
        
    except Exception as e:
        return f"Error adding conditional column: {str(e)}"

@tool  
def get_unique_values(file_path: str, column_name: str) -> str:
    """Get all unique values in a specific column.
    
    Args:
        file_path: Path to the CSV/Excel file
        column_name: Name of the column to get unique values from
        
    Example:
        get_unique_values("file.csv", "Category") - shows all unique categories
    """
    try:
        editor = DataEditor(file_path)
        editor._validate_column(column_name)
        
        unique_values = editor.df[column_name].unique()
        unique_count = len(unique_values)
        
        # Handle NaN values
        unique_values = [str(val) if pd.notna(val) else "NULL" for val in unique_values]
        
        result = f"Unique values in column '{column_name}' ({unique_count} total):\n"
        for i, value in enumerate(unique_values, 1):
            result += f"  {i}. {value}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting unique values: {str(e)}"

@tool
def count_values(file_path: str, column_name: str) -> str:
    """Count occurrences of each value in a specific column.
    
    Args:
        file_path: Path to the CSV/Excel file  
        column_name: Name of the column to count values in
        
    Example:
        count_values("file.csv", "Category") - shows count of each category
    """
    try:
        editor = DataEditor(file_path)
        editor._validate_column(column_name)
        
        value_counts = editor.df[column_name].value_counts(dropna=False)
        
        result = f"Value counts for column '{column_name}':\n"
        for value, count in value_counts.items():
            display_value = str(value) if pd.notna(value) else "NULL"
            result += f"  {display_value}: {count}\n"
        
        return result
        
    except Exception as e:
        return f"Error counting values: {str(e)}"


def get_csv_tools():
    """Return all available DataFrame editing tools"""
    return [
        # Basic tools
        remove_row,
        remove_column, 
        add_column,
        add_row,
        set_cell,
        set_row,
        get_preview,
        rename_column,
        
        # Advanced tools
        remove_rows_by_condition,
        update_column_conditional,
        add_calculated_column,
        bulk_update_cells,
        filter_and_save,
        sort_data,
        get_statistics,
        duplicate_rows,
        find_and_replace,
        add_conditional_column,
        get_unique_values,
        count_values
    ]