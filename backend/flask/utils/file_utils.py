"""
File processing utilities for Flask app
Handles file reading, cleaning, and data processing
"""

import os
import pandas as pd
from utils.logger import log
from utils.response_handler import clean_for_json_serialization


def read_file_with_preserved_order(file_path: str) -> pd.DataFrame:
    """
    Read file while preserving original column order and cleaning data
    This prevents JSON serialization issues with NaN/Infinity values
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = file_path.rsplit('.', 1)[1].lower()
        
        if ext == 'csv':
            # Read CSV with explicit encoding and preserve column order
            df = pd.read_csv(file_path, encoding='utf-8')
        elif ext in ('xls', 'xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # CRITICAL FIX: Clean the DataFrame to prevent JSON issues
        # Replace NaN, inf, -inf with None
        df = df.replace([float('inf'), float('-inf')], None)
        df = df.where(pd.notnull(df), None)
        
        log(f"Read and cleaned file with {len(df)} rows, {len(df.columns)} columns", "INFO")
        log(f"Columns in order: {df.columns.tolist()}", "INFO")
        
        return df
        
    except Exception as e:
        log(f"Error reading file {file_path}: {str(e)}", "ERROR")
        raise


def get_file_info(file_path: str) -> dict:
    """Get basic information about a file"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get file stats
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Read file to get data info
        df = read_file_with_preserved_order(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": file_size,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
    except Exception as e:
        log(f"Error getting file info for {file_path}: {str(e)}", "ERROR")
        raise


def prepare_file_data_for_response(file_path: str) -> dict:
    """
    Prepare file data for JSON response
    Returns cleaned data suitable for frontend consumption
    """
    try:
        df = read_file_with_preserved_order(file_path)
        
        # Clean data for JSON serialization
        updated_data = clean_for_json_serialization(df.to_dict('records'))
        headers = clean_for_json_serialization(df.columns.tolist())
        
        return {
            "updated_data": updated_data,
            "headers": headers,
            "file_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_order": headers,
                "filename": os.path.basename(file_path)
            }
        }
        
    except Exception as e:
        log(f"Error preparing file data for {file_path}: {str(e)}", "ERROR")
        raise


def validate_file_path(file_path: str, upload_folder: str) -> bool:
    """Validate that file path is safe and exists"""
    try:
        if not file_path:
            return False
            
        # Check if file exists
        if not os.path.exists(file_path):
            log(f"File does not exist: {file_path}", "WARNING")
            return False
            
        # Security check: ensure file is in upload folder
        abs_file_path = os.path.abspath(file_path)
        abs_upload_folder = os.path.abspath(upload_folder)
        
        if not abs_file_path.startswith(abs_upload_folder):
            log(f"Security violation: File outside upload folder: {file_path}", "ERROR")
            return False
            
        return True
        
    except Exception as e:
        log(f"Error validating file path {file_path}: {str(e)}", "ERROR")
        return False


def clean_dataframe_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame to ensure all values are JSON serializable
    This is specifically for your nutrition dataset's NaN issues
    """
    try:
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Replace NaN, inf, -inf with None
        cleaned_df = cleaned_df.replace([float('inf'), float('-inf')], None)
        cleaned_df = cleaned_df.where(pd.notnull(cleaned_df), None)
        
        # Handle any object columns that might have problematic values
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].astype(str)
            cleaned_df[col] = cleaned_df[col].replace('nan', None)
            cleaned_df[col] = cleaned_df[col].replace('None', None)
            cleaned_df[col] = cleaned_df[col].replace('', None)
        
        log(f"Cleaned DataFrame: {len(cleaned_df)} rows, {len(cleaned_df.columns)} columns", "INFO")
        return cleaned_df
        
    except Exception as e:
        log(f"Error cleaning DataFrame: {str(e)}", "ERROR")
        raise


def get_supported_file_extensions() -> list:
    """Get list of supported file extensions"""
    return ['csv', 'xls', 'xlsx']


def is_supported_file(filename: str) -> bool:
    """Check if file extension is supported"""
    if not filename:
        return False
        
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in get_supported_file_extensions()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
        
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"