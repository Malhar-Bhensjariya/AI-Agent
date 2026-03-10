from typing import List, Any, Dict
import os
import requests
from langchain_core.tools import tool

# File Service client helper
FILE_SERVICE_URL = os.getenv('FILE_SERVICE_URL', 'http://file_service:5010')

def _send_patch(file_id: str, patch: Dict[str, Any], requested_by: str = 'editor_service') -> Dict[str, Any]:
    url = f"{FILE_SERVICE_URL}/file/{file_id}/apply-op"
    payload = {'op_type': 'patch', 'patch': patch, 'requested_by': requested_by}
    try:
        resp = requests.post(url, json=payload, timeout=30)
        try:
            return resp.json()
        except Exception:
            return {'success': False, 'error': f'bad response: {resp.text}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _get_preview_headers(file_id: str) -> List[str]:
    try:
        url = f"{FILE_SERVICE_URL}/file/{file_id}/preview?page=1&size=1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get('headers') or data.get('columns') or []
    except Exception:
        return []

from .df_editor import DataEditor

# Original basic tools
@tool
def remove_row(file_path: str, row_index: int) -> str:
    """Remove a specific row from the CSV/Excel file (1-based index).
    
    Args:
        file_path: Path to the CSV/Excel file
        row_index: Row number to remove (1-based, e.g., 1 for first row)
    """
    try:
        idx = int(row_index) - 1
        patch = {'deletes': [idx]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Removed row {row_index}. File updated."
        return f"Error removing row: {result.get('error') or result}"
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
        patch = {'updates': [], 'deletes': [], 'inserts': [], 'drop_columns': [column_name]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Removed column '{column_name}'. File updated."
        return f"Error removing column: {result.get('error') or result}"
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
        patch = {'inserts': [], 'updates': [], 'deletes': [], 'add_columns': [{ 'name': column_name, 'default': default_value }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Added column '{column_name}'. File updated."
        return f"Error adding column: {result.get('error') or result}"
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
        headers = _get_preview_headers(file_path)
        values = {}
        if headers and isinstance(row_values, list):
            for i, v in enumerate(row_values):
                if i < len(headers):
                    values[headers[i]] = v
        else:
            return "Error adding row: cannot determine columns"

        patch = {'inserts': [{ 'values': values }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Added row. File updated."
        return f"Error adding row: {result.get('error') or result}"
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
        idx = int(row_index) - 1
        patch = {'updates': [{ 'row_index': idx, 'values': {column_name: value} }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Set cell at row {row_index}, column '{column_name}' to '{value}'. File updated."
        return f"Error setting cell: {result.get('error') or result}"
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
        headers = _get_preview_headers(file_path)
        if not headers:
            return "Error setting row: cannot determine columns"
        if len(values) != len(headers):
            return f"Error setting row: value count {len(values)} does not match columns {len(headers)}"
        vals = {headers[i]: values[i] for i in range(len(headers))}
        idx = int(row_index) - 1
        patch = {'updates': [{ 'row_index': idx, 'values': vals }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Updated row {row_index}. File updated."
        return f"Error setting row: {result.get('error') or result}"
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
        url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size={num_rows}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        headers = data.get('headers') or data.get('columns') or []
        rows = data.get('rows') or []

        result = f"Preview of {file_path} (showing {len(rows)} rows):\n\nColumns: {', '.join(headers)}\n\nData:\n"
        for i, row in enumerate(rows, 1):
            result += f"Row {i}: {row}\n"
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
        patch = {'updates': [], 'deletes': [], 'inserts': [], 'rename_columns': [{ 'from': old_name, 'to': new_name }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Renamed column '{old_name}' to '{new_name}'. File updated."
        return f"Error renaming column: {result.get('error') or result}"
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
        patch = {'condition_deletes': { 'column': column_name, 'condition': condition }}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Removed rows where {column_name} {condition}. File updated."
        return f"Error removing rows by condition: {result.get('error') or result}"
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
        patch = {'conditional_updates': { 'target': target_column, 'condition_column': condition_column, 'condition': condition, 'new_value': new_value }}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Updated column '{target_column}' where {condition_column} {condition}. File updated."
        return f"Error updating column conditionally: {result.get('error') or result}"
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
        patch = {'calculated_columns': [{ 'name': new_column, 'source': source_column, 'operation': operation, 'operand': operand }]}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Added calculated column '{new_column}'. File updated."
        return f"Error adding calculated column: {result.get('error') or result}"
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
        # Convert 1-based rows to 0-based
        conv = []
        for u in updates:
            r = u.get('row')
            c = u.get('column')
            v = u.get('value')
            if r is None or c is None:
                continue
            conv.append({ 'row_index': int(r) - 1, 'values': { c: v } })
        patch = {'updates': conv}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Bulk update applied. File updated."
        return f"Error bulk updating cells: {result.get('error') or result}"
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
        if save_filtered:
            patch = {'condition_filter_replace': { 'column': column_name, 'condition': condition }}
            result = _send_patch(file_path, patch)
            if result.get('success'):
                return f"Filtered and saved rows where {column_name} {condition}. File updated."
            return f"Error filtering data: {result.get('error') or result}"
        else:
            # Preview only: call preview and filter locally on returned rows
            url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size=1000"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            rows = data.get('rows', [])
            # Naive filter in string form
            filtered = [r for r in rows if str(r.get(column_name, '')).find(str(condition).strip().strip('"').strip("'")) != -1]
            return f"Found {len(filtered)} rows where {column_name} {condition} (preview only)"
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
        patch = {'sort': { 'columns': columns, 'ascending': ascending }}
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Sorted by {columns} (ascending={ascending}). File updated."
        return f"Error sorting data: {result.get('error') or result}"
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
        # Use preview to compute lightweight stats
        url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size=1000"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        rows = data.get('rows', [])
        headers = data.get('headers') or data.get('columns') or []
        if column_name:
            vals = [r.get(column_name) for r in rows if column_name in r]
            return f"Statistics for column '{column_name}': count={len(vals)}"
        else:
            return f"Dataset Overview: Columns={', '.join(headers)} Rows sample={len(rows)}"
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
        inserts = []
        # Fetch a small preview to get row data
        url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size=1000"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        rows = data.get('rows', [])
        for r in row_indices:
            idx = int(r) - 1
            if 0 <= idx < len(rows):
                for _ in range(count):
                    inserts.append({ 'values': rows[idx] })
        if not inserts:
            return "Error duplicating rows: rows not found in preview"
        patch = { 'inserts': inserts }
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Duplicated rows {row_indices} {count} times. File updated."
        return f"Error duplicating rows: {result.get('error') or result}"
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
        patch = { 'find_and_replace': { 'column': column_name, 'find': find_value, 'replace': replace_value } }
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Replaced occurrences of '{find_value}' with '{replace_value}' in column '{column_name}'. File updated."
        return f"Error in find and replace: {result.get('error') or result}"
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
        patch = { 'conditional_column': { 'new_column': new_column, 'condition_column': condition_column, 'condition': condition, 'true_value': true_value, 'false_value': false_value } }
        result = _send_patch(file_path, patch)
        if result.get('success'):
            return f"Added conditional column '{new_column}'. File updated."
        return f"Error adding conditional column: {result.get('error') or result}"
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
        url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size=1000"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        rows = data.get('rows', [])
        vals = set()
        for r in rows:
            if column_name in r:
                vals.add(str(r.get(column_name)))
        unique_values = list(vals)
        unique_count = len(unique_values)
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
        url = f"{FILE_SERVICE_URL}/file/{file_path}/preview?page=1&size=1000"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        rows = data.get('rows', [])
        counts = {}
        for r in rows:
            v = r.get(column_name)
            key = str(v)
            counts[key] = counts.get(key, 0) + 1
        result = f"Value counts for column '{column_name}':\n"
        for value, count in counts.items():
            result += f"  {value}: {count}\n"
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