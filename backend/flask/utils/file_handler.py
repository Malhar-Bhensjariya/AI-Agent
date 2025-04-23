import os
import pandas as pd
from typing import Union

def save_file(file, upload_folder: str) -> str:
    """Securely save uploaded file with validation"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    
    filename = os.path.join(upload_folder, file.filename)
    
    # Validate file extension
    allowed_extensions = {'.csv', '.xls', '.xlsx'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(f"Unsupported file type: {ext}")
    
    file.save(filename)
    return filename

def load_dataframe(path: str) -> pd.DataFrame:
    """Load dataframe with enhanced validation"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path, engine='python', on_bad_lines='warn')
        elif path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(path, engine='openpyxl')
        else:
            raise ValueError("Unsupported file format")
            
        # Basic data validation
        if df.empty:
            raise ValueError("Uploaded file is empty")
            
        return df.dropna(how='all').reset_index(drop=True)
        
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {str(e)}")