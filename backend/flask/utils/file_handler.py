import os
import pandas as pd
from typing import Union

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file) -> str:
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return filepath

def load_dataframe(path: str) -> pd.DataFrame:
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path, engine='python', on_bad_lines='warn')
        elif path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(path, engine='openpyxl')
        else:
            raise ValueError("Unsupported file format")
            
        # Clean data
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df = df.convert_dtypes().reset_index(drop=True)
        return df
        
    except Exception as e:
        raise RuntimeError(f"Data loading failed: {str(e)}")