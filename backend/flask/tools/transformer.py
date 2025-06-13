import pandas as pd
import os
from utils.logger import log
from tools.file_handler import load_file_as_dataframe

class DataTransformer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = load_file_as_dataframe(file_path)  # Reuse existing file handler

    def _save_file(self):
        """Save DataFrame back to file"""
        try:
            ext = self.file_path.rsplit('.', 1)[1].lower()
            if ext == 'csv':
                self.df.to_csv(self.file_path, index=False)
            elif ext in ('xls', 'xlsx'):
                self.df.to_excel(self.file_path, index=False)
            log(f"Successfully saved file: {self.file_path}", level="INFO")
        except Exception as e:
            log(f"Error saving file in transformer: {e}", level="ERROR")
            raise ValueError(f"File saving failed: {str(e)}")

    def fill_missing(self, column_name: str, value: str) -> str:
        """Fill missing values in a column with specified value"""
        if column_name not in self.df.columns:
            available_cols = list(self.df.columns)
            raise ValueError(f"Column '{column_name}' does not exist. Available columns: {available_cols}")
        
        # Count missing values before filling
        missing_count = self.df[column_name].isnull().sum()
        
        if missing_count == 0:
            log(f"No missing values found in column '{column_name}'", level="INFO")
            return f"No missing values found in column '{column_name}'"
        
        try:
            self.df[column_name] = self.df[column_name].fillna(value)
            self._save_file()
            log(f"Filled {missing_count} missing values in '{column_name}' with '{value}'", level="INFO")
            return f"Filled {missing_count} missing values in '{column_name}' with '{value}'"
        except Exception as e:
            log(f"Error filling missing values: {e}", level="ERROR")
            raise ValueError(f"Failed to fill missing values: {str(e)}")

    def change_dtype(self, column_name: str, dtype: str) -> str:
        """Change data type of a column"""
        if column_name not in self.df.columns:
            available_cols = list(self.df.columns)
            raise ValueError(f"Column '{column_name}' does not exist. Available columns: {available_cols}")
        
        # Get current dtype
        current_dtype = str(self.df[column_name].dtype)
        
        try:
            # Handle common dtype aliases
            dtype_mapping = {
                'int': 'int64',
                'float': 'float64',
                'str': 'object',
                'string': 'object',
                'bool': 'bool',
                'boolean': 'bool',
                'datetime': 'datetime64[ns]'
            }
            
            target_dtype = dtype_mapping.get(dtype.lower(), dtype)
            
            # Special handling for datetime conversion
            if target_dtype.startswith('datetime'):
                self.df[column_name] = pd.to_datetime(self.df[column_name])
            else:
                self.df[column_name] = self.df[column_name].astype(target_dtype)
            
            self._save_file()
            log(f"Changed data type of '{column_name}' from '{current_dtype}' to '{target_dtype}'", level="INFO")
            return f"Changed data type of '{column_name}' from '{current_dtype}' to '{target_dtype}'"
            
        except Exception as e:
            log(f"Error changing dtype: {e}", level="ERROR")
            raise ValueError(f"Failed to convert column '{column_name}' to '{dtype}': {str(e)}")

    def normalize_column(self, column_name: str) -> str:
        """Normalize a numeric column using min-max normalization"""
        if column_name not in self.df.columns:
            available_cols = list(self.df.columns)
            raise ValueError(f"Column '{column_name}' does not exist. Available columns: {available_cols}")
        
        try:
            # Check if column can be converted to numeric
            col = pd.to_numeric(self.df[column_name], errors='coerce')
            
            # Check for non-numeric values
            if col.isnull().sum() > self.df[column_name].isnull().sum():
                raise ValueError(f"Column '{column_name}' contains non-numeric values that cannot be converted")
            
            # Check if all values are the same (would cause division by zero)
            if col.min() == col.max():
                log(f"All values in column '{column_name}' are the same, normalization not needed", level="WARNING")
                return f"All values in column '{column_name}' are the same ({col.min()}), normalization not performed"
            
            # Perform min-max normalization
            self.df[column_name] = (col - col.min()) / (col.max() - col.min())
            self._save_file()
            
            log(f"Normalized column '{column_name}' using min-max normalization", level="INFO")
            return f"Successfully normalized column '{column_name}' using min-max normalization (range: 0-1)"
            
        except Exception as e:
            log(f"Error normalizing column: {e}", level="ERROR")
            raise ValueError(f"Normalization failed for column '{column_name}': {str(e)}")

    def standardize_column(self, column_name: str) -> str:
        """Standardize a numeric column using Z-score"""
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' does not exist. Available columns: {list(self.df.columns)}")
        try:
            col = pd.to_numeric(self.df[column_name], errors='coerce')
            if col.isnull().sum() > self.df[column_name].isnull().sum():
                raise ValueError(f"Column '{column_name}' contains non-numeric values")

            mean = col.mean()
            std = col.std()
            if std == 0:
                return f"All values in column '{column_name}' are the same. Z-score standardization not needed."

            self.df[column_name] = (col - mean) / std
            self._save_file()
            log(f"Standardized column '{column_name}' using Z-score", level="INFO")
            return f"Successfully standardized column '{column_name}' using Z-score"
        except Exception as e:
            log(f"Error standardizing column: {e}", level="ERROR")
            raise ValueError(f"Failed to standardize column '{column_name}': {str(e)}")

    def remove_duplicates(self) -> str:
        """Remove duplicate rows from the dataset"""
        try:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            after = len(self.df)
            removed = before - after
            self._save_file()
            log(f"Removed {removed} duplicate rows", level="INFO")
            return f"Removed {removed} duplicate rows"
        except Exception as e:
            log(f"Error removing duplicates: {e}", level="ERROR")
            raise ValueError(f"Failed to remove duplicates: {str(e)}")

    def drop_missing_rows(self) -> str:
        """Drop all rows with any missing values"""
        try:
            before = len(self.df)
            self.df = self.df.dropna()
            after = len(self.df)
            removed = before - after
            self._save_file()
            log(f"Dropped {removed} rows with missing values", level="INFO")
            return f"Dropped {removed} rows containing missing values"
        except Exception as e:
            log(f"Error dropping missing rows: {e}", level="ERROR")
            raise ValueError(f"Failed to drop rows: {str(e)}")
