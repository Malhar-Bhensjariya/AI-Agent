import pandas as pd
import os
from typing import List, Dict, Union, Tuple
from utils.logger import log
from tools.file_handler import load_file_as_dataframe

class DataEditor:
    def __init__(self, file_path: str):
        """Initialize with file path and load DataFrame"""
        self.file_path = file_path
        self.df = load_file_as_dataframe(file_path)
        # Store original column order - this is the key fix
        self.original_columns = self.df.columns.tolist()

    def _save_dataframe(self):
        """Save DataFrame back to file, preserving original column order"""
        try:
            # CRITICAL FIX: Always reorder columns to match original order before saving
            # First, get columns that still exist in original order
            existing_original_cols = [col for col in self.original_columns if col in self.df.columns]
            # Then add any new columns that weren't in original
            new_cols = [col for col in self.df.columns if col not in self.original_columns]
            # Final order: original columns first, then new columns
            final_order = existing_original_cols + new_cols
            
            # Reorder the DataFrame columns
            self.df = self.df[final_order]
            
            ext = self.file_path.rsplit('.', 1)[1].lower()
            if ext == 'csv':
                # Save with explicit column order preservation
                self.df.to_csv(self.file_path, index=False, encoding='utf-8')
            elif ext in ('xls', 'xlsx'):
                self.df.to_excel(self.file_path, index=False, engine='openpyxl')
            
            log(f"Successfully saved file with shape: {self.df.shape}", "INFO")
            log(f"Column order preserved: {self.df.columns.tolist()}", "INFO")
        except Exception as e:
            log(f"Error saving file: {str(e)}", "ERROR")
            raise

    def _validate_row_index(self, user_row: int) -> int:
        """Convert 1-based user row to 0-based pandas index"""
        if not isinstance(user_row, int) or user_row < 1:
            raise ValueError(f"Row index must be a positive integer, got: {user_row}")
        
        idx = user_row - 1
        if idx >= len(self.df):
            raise ValueError(f"Row {user_row} does not exist (max: {len(self.df)})")
        return idx

    def _validate_column(self, column_name: str):
        """Validate column exists"""
        if column_name not in self.df.columns:
            available = list(self.df.columns)
            raise ValueError(f"Column '{column_name}' does not exist. Available: {available}")

    def remove_row(self, user_row: int) -> Tuple[str, pd.DataFrame]:
        """Remove a row and save the file"""
        idx = self._validate_row_index(user_row)
        self.df = self.df.drop(index=self.df.index[idx]).reset_index(drop=True)
        self._save_dataframe()
        log(f"Removed row {user_row} from {self.file_path}", "INFO")
        return f"Removed row {user_row}", self.df

    def remove_column(self, column_name: str) -> Tuple[str, pd.DataFrame]:
        """Remove a column and save the file"""
        self._validate_column(column_name)
        
        # Update original columns list when removing
        if column_name in self.original_columns:
            self.original_columns.remove(column_name)
        
        self.df = self.df.drop(columns=[column_name])
        self._save_dataframe()
        log(f"Removed column '{column_name}' from {self.file_path}", "INFO")
        return f"Removed column '{column_name}'", self.df

    def add_column(self, column_name: str, default_value: Union[str, int, float] = "", position: int = None) -> Tuple[str, pd.DataFrame]:
        """Add a new column and save the file"""
        if column_name in self.df.columns:
            raise ValueError(f"Column '{column_name}' already exists")
        
        # Add column to dataframe
        self.df[column_name] = default_value
        
        # Update original columns list - add to end unless position specified
        if position is not None and 0 <= position <= len(self.original_columns):
            self.original_columns.insert(position, column_name)
        else:
            self.original_columns.append(column_name)
        
        self._save_dataframe()
        log(f"Added column '{column_name}' to {self.file_path}", "INFO")
        return f"Added column '{column_name}' with default value '{default_value}'", self.df

    def add_row(self, row_values: List[Union[str, int, float]]) -> Tuple[str, pd.DataFrame]:
        """Add a new row and save the file"""
        if len(row_values) != len(self.df.columns):
            raise ValueError(f"Row length mismatch. Expected {len(self.df.columns)} values, got {len(row_values)}")
        
        # Create new row as DataFrame with correct column order
        new_row = pd.DataFrame([row_values], columns=self.df.columns)
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_dataframe()
        log(f"Added row {row_values} to {self.file_path}", "INFO")
        return f"Added row: {row_values}", self.df

    def set_cell_value(self, user_row: int, column_name: str, value: Union[str, int, float]) -> Tuple[str, pd.DataFrame]:
        """Set a specific cell value and save the file"""
        idx = self._validate_row_index(user_row)
        self._validate_column(column_name)
        
        old_value = self.df.at[idx, column_name]
        self.df.at[idx, column_name] = value
        self._save_dataframe()
        log(f"Set cell [{user_row}, '{column_name}'] from '{old_value}' to '{value}'", "INFO")
        return f"Set value at row {user_row}, column '{column_name}' to '{value}'", self.df

    def set_row_values(self, user_row: int, values: List[Union[str, int, float]]) -> Tuple[str, pd.DataFrame]:
        """Replace all values in a row and save the file"""
        idx = self._validate_row_index(user_row)
        if len(values) != len(self.df.columns):
            raise ValueError(f"Value count mismatch. Expected {len(self.df.columns)}, got {len(values)}")
        
        old_values = self.df.loc[idx].tolist()
        self.df.loc[idx] = values
        self._save_dataframe()
        log(f"Updated row {user_row} from {old_values} to {values}", "INFO")
        return f"Updated row {user_row} with {values}", self.df

    def get_preview(self, n: int = 5) -> Dict:
        """Get a preview of the DataFrame with preserved column order"""
        # Ensure columns are in original order for preview
        ordered_df = self.df[self.original_columns] if all(col in self.df.columns for col in self.original_columns) else self.df
        return {
            "columns": ordered_df.columns.tolist(),
            "data": ordered_df.head(n).fillna("").to_dict(orient="records"),
            "shape": ordered_df.shape,
            "file_path": self.file_path
        }

    def get_summary(self) -> Dict:
        """Get comprehensive DataFrame summary with preserved column order"""
        # Use ordered DataFrame for summary
        ordered_df = self.df[self.original_columns] if all(col in self.df.columns for col in self.original_columns) else self.df
        
        numeric_cols = ordered_df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = ordered_df.select_dtypes(include=['object']).columns.tolist()
        
        summary = {
            "basic_info": {
                "file_path": self.file_path,
                "columns": ordered_df.columns.tolist(),  # Ordered columns
                "shape": ordered_df.shape,
                "dtypes": ordered_df.dtypes.astype(str).to_dict(),
                "missing_values": ordered_df.isnull().sum().to_dict(),
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols
            }
        }
        
        # Add statistical summary
        if not ordered_df.empty:
            try:
                stats = ordered_df.describe(include="all").fillna("").to_dict()
                summary["statistics"] = stats
            except Exception as e:
                summary["statistics"] = f"Error generating stats: {str(e)}"
        
        return summary

    def get_cell_value(self, user_row: int, column_name: str) -> Union[str, int, float]:
        """Get value from specific cell"""
        idx = self._validate_row_index(user_row)
        self._validate_column(column_name)
        return self.df.at[idx, column_name]