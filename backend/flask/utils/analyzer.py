import pandas as pd
import numpy as np

def basic_analysis(df: pd.DataFrame) -> dict:
    def convert_dtypes(dtype):
        if pd.api.types.is_numeric_dtype(dtype):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        return str(dtype)
    
    return {
        'columns': list(df.columns),
        'dtypes': {col: convert_dtypes(df[col].dtype) for col in df.columns},
        'stats': df.describe().fillna('').to_dict(),
        'shape': {'rows': df.shape[0], 'cols': df.shape[1]},
        'missing': df.isnull().sum().to_dict()
    }