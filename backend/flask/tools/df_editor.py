import pandas as pd
import os
import numpy as np
from typing import List, Dict, Union, Tuple, Any, Optional
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

    def _parse_condition(self, condition: str, column_name: str) -> pd.Series:
        """Parse condition string and return boolean mask"""
        condition = condition.strip()
        
        # Handle different operators
        operators = ['>=', '<=', '==', '!=', '>', '<']
        operator = None
        value = None
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    operator = op
                    value = parts[1].strip()
                    break
        
        if operator is None:
            # Assume equality if no operator found
            operator = '=='
            value = condition
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        
        # Try to convert to numeric if possible
        try:
            numeric_value = float(value)
            if numeric_value.is_integer():
                numeric_value = int(numeric_value)
        except:
            numeric_value = None
        
        # Apply condition
        column_data = self.df[column_name]
        
        if operator == '==':
            if numeric_value is not None:
                return (column_data == numeric_value) | (column_data.astype(str) == value)
            return column_data.astype(str) == value
        elif operator == '!=':
            if numeric_value is not None:
                return (column_data != numeric_value) & (column_data.astype(str) != value)
            return column_data.astype(str) != value
        elif operator == '>':
            return pd.to_numeric(column_data, errors='coerce') > float(value)
        elif operator == '<':
            return pd.to_numeric(column_data, errors='coerce') < float(value)
        elif operator == '>=':
            return pd.to_numeric(column_data, errors='coerce') >= float(value)
        elif operator == '<=':
            return pd.to_numeric(column_data, errors='coerce') <= float(value)
        
        return pd.Series([False] * len(self.df))

    # Enhanced existing methods
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

    def get_cell_value(self, user_row: int, column_name: str) -> Union[str, int, float]:
        """Get value from specific cell"""
        idx = self._validate_row_index(user_row)
        self._validate_column(column_name)
        return self.df.at[idx, column_name]
    
    def rename_column(self, old_name: str, new_name: str) -> str:
        """Rename a column, ensuring no conflict and preserving original order"""
        if old_name not in self.df.columns:
            raise ValueError(f"Column '{old_name}' not found. Available columns: {list(self.df.columns)}")

        if new_name in self.df.columns:
            raise ValueError(f"Column '{new_name}' already exists.")

        try:
            self.df = self.df.rename(columns={old_name: new_name})

            # Update original_columns if needed
            if old_name in self.original_columns:
                idx = self.original_columns.index(old_name)
                self.original_columns[idx] = new_name

            self._save_dataframe()
            log(f"Renamed column '{old_name}' to '{new_name}'", level="INFO")
            return f"Renamed column '{old_name}' to '{new_name}'"
        except Exception as e:
            log(f"Error renaming column: {e}", level="ERROR")
            raise ValueError(f"Failed to rename column: {str(e)}")

    # NEW ADVANCED METHODS
    
    def remove_rows_by_condition(self, column_name: str, condition: str) -> Tuple[str, pd.DataFrame]:
        """Remove rows based on a condition"""
        self._validate_column(column_name)
        
        # Get boolean mask for rows to remove
        mask = self._parse_condition(condition, column_name)
        rows_to_remove = self.df[mask]
        removed_count = len(rows_to_remove)
        
        if removed_count == 0:
            return f"No rows found matching condition: {column_name} {condition}", self.df
        
        # Remove matching rows
        self.df = self.df[~mask].reset_index(drop=True)
        self._save_dataframe()
        
        log(f"Removed {removed_count} rows where {column_name} {condition}", "INFO")
        return f"Removed {removed_count} rows where {column_name} {condition}", self.df

    def update_column_conditional(self, column_name: str, condition_column: str, condition: str, new_value: Any) -> Tuple[str, pd.DataFrame]:
        """Update values in a column based on condition in another column"""
        self._validate_column(column_name)
        self._validate_column(condition_column)
        
        # Get boolean mask for rows to update
        mask = self._parse_condition(condition, condition_column)
        update_count = mask.sum()
        
        if update_count == 0:
            return f"No rows found matching condition: {condition_column} {condition}", self.df
        
        # Update matching rows
        self.df.loc[mask, column_name] = new_value
        self._save_dataframe()
        
        log(f"Updated {update_count} rows in '{column_name}' where {condition_column} {condition}", "INFO")
        return f"Updated {update_count} rows in '{column_name}' to '{new_value}' where {condition_column} {condition}", self.df

    def add_calculated_column(self, new_column: str, source_column: str, operation: str, operand: Union[int, float] = None) -> Tuple[str, pd.DataFrame]:
        """Add a new column based on calculations from existing column"""
        self._validate_column(source_column)
        
        if new_column in self.df.columns:
            raise ValueError(f"Column '{new_column}' already exists")
        
        source_data = pd.to_numeric(self.df[source_column], errors='coerce')
        
        if operation == 'multiply' and operand is not None:
            self.df[new_column] = source_data * operand
        elif operation == 'divide' and operand is not None:
            self.df[new_column] = source_data / operand
        elif operation == 'add' and operand is not None:
            self.df[new_column] = source_data + operand
        elif operation == 'subtract' and operand is not None:
            self.df[new_column] = source_data - operand
        elif operation == 'square':
            self.df[new_column] = source_data ** 2
        elif operation == 'sqrt':
            self.df[new_column] = np.sqrt(source_data)
        elif operation == 'absolute':
            self.df[new_column] = abs(source_data)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Update original columns list
        self.original_columns.append(new_column)
        self._save_dataframe()
        
        log(f"Added calculated column '{new_column}' based on {operation} of '{source_column}'", "INFO")
        return f"Added calculated column '{new_column}' based on {operation} of '{source_column}'", self.df

    def bulk_update_cells(self, updates: List[Dict[str, Any]]) -> Tuple[str, pd.DataFrame]:
        """Update multiple cells in one operation"""
        update_count = 0
        
        for update in updates:
            try:
                row = update.get('row')
                column = update.get('column') 
                value = update.get('value')
                
                if row is None or column is None or value is None:
                    continue
                
                idx = self._validate_row_index(row)
                self._validate_column(column)
                self.df.at[idx, column] = value
                update_count += 1
                
            except Exception as e:
                log(f"Failed to update cell at row {row}, column {column}: {e}", "WARNING")
                continue
        
        if update_count > 0:
            self._save_dataframe()
        
        log(f"Bulk updated {update_count} cells", "INFO")
        return f"Successfully updated {update_count} cells", self.df

    def filter_and_save(self, column_name: str, condition: str, save_filtered: bool = False) -> Tuple[str, pd.DataFrame]:
        """Filter data and optionally save filtered version"""
        self._validate_column(column_name)
        
        # Get boolean mask for rows to keep
        mask = self._parse_condition(condition, column_name)
        filtered_df = self.df[mask].reset_index(drop=True)
        filtered_count = len(filtered_df)
        
        if save_filtered:
            # Replace current data with filtered data
            self.df = filtered_df
            self._save_dataframe()
            log(f"Saved filtered data: {filtered_count} rows where {column_name} {condition}", "INFO")
            return f"Filtered and saved {filtered_count} rows where {column_name} {condition}", self.df
        else:
            log(f"Filtered {filtered_count} rows where {column_name} {condition} (not saved)", "INFO")
            return f"Found {filtered_count} rows where {column_name} {condition} (preview only)", filtered_df

    def sort_data(self, columns: List[str], ascending: bool = True) -> Tuple[str, pd.DataFrame]:
        """Sort data by one or more columns"""
        for col in columns:
            self._validate_column(col)
        
        self.df = self.df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)
        self._save_dataframe()
        
        direction = "ascending" if ascending else "descending"
        log(f"Sorted data by {columns} in {direction} order", "INFO")
        return f"Sorted data by {columns} in {direction} order", self.df

    def get_statistics(self, column_name: str = None) -> Dict:
        """Get statistical summary of data"""
        if column_name:
            self._validate_column(column_name)
            if pd.api.types.is_numeric_dtype(self.df[column_name]):
                stats = self.df[column_name].describe().to_dict()
                stats['data_type'] = str(self.df[column_name].dtype)
                return {column_name: stats}
            else:
                return {
                    column_name: {
                        'count': len(self.df[column_name]),
                        'unique': self.df[column_name].nunique(),
                        'top': self.df[column_name].mode().iloc[0] if len(self.df[column_name].mode()) > 0 else None,
                        'data_type': str(self.df[column_name].dtype)
                    }
                }
        else:
            # Overall statistics
            stats = {
                'shape': self.df.shape,
                'columns': self.df.columns.tolist(),
                'dtypes': self.df.dtypes.to_dict(),
                'memory_usage': self.df.memory_usage(deep=True).to_dict(),
                'null_counts': self.df.isnull().sum().to_dict()
            }
            return stats

    def duplicate_rows(self, row_indices: List[int], count: int = 1) -> Tuple[str, pd.DataFrame]:
        """Duplicate specific rows"""
        for row_idx in row_indices:
            self._validate_row_index(row_idx)
        
        # Convert to 0-based indices
        zero_based_indices = [idx - 1 for idx in row_indices]
        
        # Get rows to duplicate
        rows_to_duplicate = self.df.iloc[zero_based_indices]
        
        # Duplicate each row the specified number of times
        duplicated_rows = pd.concat([rows_to_duplicate] * count, ignore_index=True)
        
        # Append to original dataframe
        self.df = pd.concat([self.df, duplicated_rows], ignore_index=True)
        self._save_dataframe()
        
        total_added = len(row_indices) * count
        log(f"Duplicated {len(row_indices)} rows {count} times each, added {total_added} new rows", "INFO")
        return f"Duplicated rows {row_indices} {count} times each, added {total_added} new rows", self.df

    def find_and_replace(self, column_name: str, find_value: Any, replace_value: Any) -> Tuple[str, pd.DataFrame]:
        """Find and replace values in a specific column"""
        self._validate_column(column_name)
        
        # Count matches before replacement
        if pd.api.types.is_numeric_dtype(self.df[column_name]):
            mask = self.df[column_name] == find_value
        else:
            mask = self.df[column_name].astype(str) == str(find_value)
        
        match_count = mask.sum()
        
        if match_count == 0:
            return f"No matches found for '{find_value}' in column '{column_name}'", self.df
        
        # Replace values
        self.df.loc[mask, column_name] = replace_value
        self._save_dataframe()
        
        log(f"Replaced {match_count} occurrences of '{find_value}' with '{replace_value}' in column '{column_name}'", "INFO")
        return f"Replaced {match_count} occurrences of '{find_value}' with '{replace_value}' in column '{column_name}'", self.df