# analyzer_operator.py
from langchain_core.tools import tool
from tools import analyzer
import os

# FIX: Use simpler tool definitions to avoid schema warnings
@tool
def get_missing_columns(file_path: str) -> str:
    """Identify columns with missing values and their respective counts."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.identify_missing_columns(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_column_average(file_path: str, column_names: str) -> str:
    """Calculate average for one or more numeric columns (comma-separated)."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        columns = [col.strip() for col in column_names.split(",")]
        return analyzer.calculate_column_average(file_path, columns)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_basic_statistics(file_path: str) -> str:
    """Return basic statistics (mean, median, std, min, max) for numeric columns."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.basic_statistical_summary(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_deep_statistics(file_path: str) -> str:
    """Provide deep statistical summary including quartiles, skewness, and kurtosis for numeric columns."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.deep_statistical_analysis(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def detect_zscore_outliers(file_path: str, threshold: float = 3.0) -> str:
    """Detect outliers in numeric columns using Z-score threshold."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.detect_outliers_zscore(file_path, threshold)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def list_column_names(file_path: str) -> str:
    """List all column names and their data types in the dataset."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.unique_column_names(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def column_frequency_counts(file_path: str, column: str) -> str:
    """Get frequency counts for a specific column."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.frequency_counts(file_path, column)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def count_duplicates(file_path: str) -> str:
    """Count the number of duplicate rows in the dataset."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.count_duplicate_rows(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def describe_full_data(file_path: str) -> str:
    """Return comprehensive descriptive summary including all column types (numeric, categorical, object)."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        return analyzer.describe_data(file_path)
    except Exception as e:
        return f"Error: {str(e)}"

def get_analyzer_tools():
    """Return all available analyzer tools with proper naming."""
    return [
        get_missing_columns,
        get_column_average,
        get_basic_statistics,
        get_deep_statistics,
        detect_zscore_outliers,
        list_column_names,
        column_frequency_counts,
        count_duplicates,
        describe_full_data
    ]