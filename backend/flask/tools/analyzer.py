import pandas as pd
import json
from typing import Dict, List, Union
from utils.logger import log
from tools.file_handler import load_file_as_dataframe

def identify_missing_columns(file_path: str) -> str:
    """Identify columns with missing values and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        result = missing.to_dict()
        
        if not result:
            response = {
                "message": "No missing values found in any columns",
                "missing_columns": {}
            }
        else:
            response = {
                "message": f"Found missing values in {len(result)} columns",
                "missing_columns": result,
                "total_missing": sum(result.values())
            }
        
        log(f"Missing columns analysis: {result}", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in identify_missing_columns: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def calculate_column_average(file_path: str, columns: Union[str, List[str]]) -> str:
    """Calculate average for specified columns and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            return json.dumps({
                "error": f"Columns not found: {missing_cols}",
                "available_columns": df.columns.tolist()
            })
        
        # Calculate averages for numeric columns only
        result = {}
        non_numeric = []
        
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Handle missing values
                avg = df[col].mean()
                result[col] = round(avg, 4) if not pd.isna(avg) else None
            else:
                non_numeric.append(col)
        
        response = {
            "message": f"Calculated averages for {len(result)} numeric columns",
            "column_averages": result
        }
        
        if non_numeric:
            response["non_numeric_columns"] = non_numeric
            response["message"] += f" ({len(non_numeric)} non-numeric columns skipped)"
        
        log(f"Column averages: {result}", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in calculate_column_average: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def basic_statistical_summary(file_path: str) -> str:
    """Generate basic statistical summary for numeric columns and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        numeric_df = df.select_dtypes(include='number')
        
        if numeric_df.empty:
            return json.dumps({
                "message": "No numeric columns found for statistical analysis",
                "numeric_columns": []
            })
        
        summary = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()  # Remove NaN for calculations
            if len(col_data) > 0:
                summary[col] = {
                    "count": int(len(col_data)),
                    "mean": round(col_data.mean(), 4),
                    "median": round(col_data.median(), 4),
                    "std": round(col_data.std(), 4),
                    "min": round(col_data.min(), 4),
                    "max": round(col_data.max(), 4),
                    "missing_values": int(numeric_df[col].isnull().sum())
                }
        
        response = {
            "message": f"Statistical summary for {len(summary)} numeric columns",
            "statistical_summary": summary,
            "total_numeric_columns": len(numeric_df.columns)
        }
        
        log(f"Basic statistical summary generated for {len(summary)} columns", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in basic_statistical_summary: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def deep_statistical_analysis(file_path: str) -> str:
    """Generate deep statistical analysis including quartiles, skewness, kurtosis and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        numeric_df = df.select_dtypes(include='number')
        
        if numeric_df.empty:
            return json.dumps({
                "message": "No numeric columns found for deep statistical analysis",
                "numeric_columns": []
            })
        
        summary = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            if len(col_data) > 1:  # Need at least 2 values for std, skew, kurtosis
                summary[col] = {
                    "count": int(len(col_data)),
                    "mean": round(col_data.mean(), 4),
                    "Q1": round(col_data.quantile(0.25), 4),
                    "median": round(col_data.median(), 4),
                    "Q3": round(col_data.quantile(0.75), 4),
                    "std": round(col_data.std(), 4),
                    "min": round(col_data.min(), 4),
                    "max": round(col_data.max(), 4),
                    "skewness": round(col_data.skew(), 4),
                    "kurtosis": round(col_data.kurtosis(), 4),
                    "missing_values": int(numeric_df[col].isnull().sum()),
                    "IQR": round(col_data.quantile(0.75) - col_data.quantile(0.25), 4)
                }
        
        response = {
            "message": f"Deep statistical analysis for {len(summary)} numeric columns",
            "deep_analysis": summary,
            "interpretation": {
                "skewness": "Values near 0 indicate symmetric distribution, >1 or <-1 indicate high skewness",
                "kurtosis": "Values near 0 indicate normal distribution, >0 indicates heavy tails"
            }
        }
        
        log(f"Deep statistical analysis generated for {len(summary)} columns", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in deep_statistical_analysis: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def detect_outliers_zscore(file_path: str, threshold: float = 3.0) -> str:
    """Detect outliers using Z-score method and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        numeric_df = df.select_dtypes(include='number')
        
        if numeric_df.empty:
            return json.dumps({
                "message": "No numeric columns found for outlier detection",
                "outliers": {}
            })
        
        # Import scipy for zscore
        try:
            from scipy.stats import zscore
        except ImportError:
            return json.dumps({
                "error": "scipy library not available for Z-score calculation",
                "message": "Please install scipy: pip install scipy"
            })
        
        outliers = {}
        total_outliers = 0
        
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            if len(col_data) > 0:
                z_scores = zscore(col_data)
                outlier_indices = col_data.index[abs(z_scores) > threshold].tolist()
                
                if outlier_indices:
                    outliers[col] = {
                        "outlier_count": len(outlier_indices),
                        "outlier_rows": outlier_indices,
                        "outlier_values": [round(float(df.loc[idx, col]), 4) for idx in outlier_indices],
                        "percentage": round((len(outlier_indices) / len(col_data)) * 100, 2)
                    }
                    total_outliers += len(outlier_indices)
        
        response = {
            "message": f"Outlier detection complete using Z-score threshold {threshold}",
            "outliers_found": len(outliers) > 0,
            "columns_with_outliers": len(outliers),
            "total_outliers": total_outliers,
            "outlier_details": outliers,
            "threshold_used": threshold
        }
        
        if not outliers:
            response["message"] = f"No outliers detected using Z-score threshold {threshold}"
        
        log(f"Z-score outlier detection: {len(outliers)} columns with outliers", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in detect_outliers_zscore: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def unique_column_names(file_path: str) -> str:
    """Get all column names and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        columns = df.columns.tolist()
        
        # Categorize columns by data type
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        text_cols = df.select_dtypes(include='object').columns.tolist()
        datetime_cols = df.select_dtypes(include='datetime').columns.tolist()
        boolean_cols = df.select_dtypes(include='bool').columns.tolist()
        
        response = {
            "message": f"Dataset contains {len(columns)} columns",
            "total_columns": len(columns),
            "all_columns": columns,
            "column_types": {
                "numeric": {
                    "count": len(numeric_cols),
                    "columns": numeric_cols
                },
                "text": {
                    "count": len(text_cols),
                    "columns": text_cols
                },
                "datetime": {
                    "count": len(datetime_cols),
                    "columns": datetime_cols
                },
                "boolean": {
                    "count": len(boolean_cols),
                    "columns": boolean_cols
                }
            }
        }
        
        log(f"Column analysis: {len(columns)} total columns", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in unique_column_names: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def frequency_counts(file_path: str, column: str) -> str:
    """Get frequency counts for a specific column and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        
        if column not in df.columns:
            return json.dumps({
                "error": f"Column '{column}' not found",
                "available_columns": df.columns.tolist()
            })
        
        # Get value counts
        counts = df[column].value_counts()
        total_values = len(df[column].dropna())
        missing_count = df[column].isnull().sum()
        
        # Handle large number of unique values
        if len(counts) > 50:
            top_counts = counts.head(20)
            response = {
                "message": f"Column '{column}' has {len(counts)} unique values (showing top 20)",
                "column": column,
                "total_unique_values": len(counts),
                "total_non_missing": total_values,
                "missing_values": int(missing_count),
                "top_20_frequencies": {str(k): int(v) for k, v in top_counts.items()},
                "top_20_percentages": {str(k): round((v/total_values)*100, 2) for k, v in top_counts.items()},
                "truncated": True
            }
        else:
            response = {
                "message": f"Frequency analysis for column '{column}'",
                "column": column,
                "total_unique_values": len(counts),
                "total_non_missing": total_values,
                "missing_values": int(missing_count),
                "frequencies": {str(k): int(v) for k, v in counts.items()},
                "percentages": {str(k): round((v/total_values)*100, 2) for k, v in counts.items()},
                "truncated": False
            }
        
        log(f"Frequency counts for {column}: {len(counts)} unique values", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in frequency_counts: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def count_duplicate_rows(file_path: str) -> str:
    """Count duplicate rows and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        
        total_rows = len(df)
        duplicate_count = int(df.duplicated().sum())
        unique_rows = total_rows - duplicate_count
        
        if duplicate_count > 0:
            # Get some example duplicate rows
            duplicate_mask = df.duplicated(keep=False)
            duplicate_examples = df[duplicate_mask].head(5).to_dict('records')
        else:
            duplicate_examples = []
        
        response = {
            "message": f"Found {duplicate_count} duplicate rows out of {total_rows} total rows",
            "total_rows": int(total_rows),
            "duplicate_rows": int(duplicate_count),
            "unique_rows": int(unique_rows),
            "duplication_percentage": round((duplicate_count/total_rows)*100, 2) if total_rows > 0 else 0,
            "has_duplicates": bool(duplicate_count > 0)
        }
        
        if duplicate_count > 0:
            response["sample_duplicates"] = duplicate_examples[:3]  # Show first 3 examples
            response["note"] = "Use remove_duplicates() function to clean the data"
        
        log(f"Duplicate analysis: {duplicate_count} duplicates found", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in count_duplicate_rows: {e}", "ERROR")
        return json.dumps({"error": str(e)})

def describe_data(file_path: str) -> str:
    """Generate comprehensive data description and return as JSON string"""
    try:
        df = load_file_as_dataframe(file_path)
        
        # Basic info
        total_rows, total_cols = df.shape
        memory_usage = df.memory_usage(deep=True).sum()
        
        # Column type analysis
        dtype_counts = df.dtypes.value_counts().to_dict()
        dtype_counts = {str(k): int(v) for k, v in dtype_counts.items()}
        
        # Missing value analysis
        missing_data = df.isnull().sum()
        columns_with_missing = (missing_data > 0).sum()
        total_missing = missing_data.sum()
        
        # For numeric columns, get describe() stats
        numeric_description = {}
        if not df.select_dtypes(include='number').empty:
            numeric_desc = df.describe()
            for col in numeric_desc.columns:
                numeric_description[col] = {
                    "count": int(numeric_desc.loc['count', col]),
                    "mean": round(numeric_desc.loc['mean', col], 4),
                    "std": round(numeric_desc.loc['std', col], 4),
                    "min": round(numeric_desc.loc['min', col], 4),
                    "25%": round(numeric_desc.loc['25%', col], 4),
                    "50%": round(numeric_desc.loc['50%', col], 4),
                    "75%": round(numeric_desc.loc['75%', col], 4),
                    "max": round(numeric_desc.loc['max', col], 4)
                }
        
        # For object columns, get basic stats
        categorical_description = {}
        for col in df.select_dtypes(include='object').columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                categorical_description[col] = {
                    "count": len(col_data),
                    "unique": col_data.nunique(),
                    "most_frequent": str(col_data.mode().iloc[0]) if len(col_data.mode()) > 0 else "N/A",
                    "most_frequent_count": int(col_data.value_counts().iloc[0]) if len(col_data) > 0 else 0
                }
        
        response = {
            "message": f"Comprehensive data analysis for dataset with {total_rows} rows and {total_cols} columns",
            "dataset_overview": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "memory_usage_bytes": int(memory_usage),
                "memory_usage_mb": round(memory_usage / (1024*1024), 2)
            },
            "column_types": dtype_counts,
            "missing_data_summary": {
                "total_missing_values": int(total_missing),
                "columns_with_missing": int(columns_with_missing),
                "missing_percentage": round((total_missing / (total_rows * total_cols)) * 100, 2)
            },
            "numeric_columns_stats": numeric_description,
            "categorical_columns_stats": categorical_description
        }
        
        log(f"Comprehensive data description generated", "INFO")
        return json.dumps(response, indent=2)
    except Exception as e:
        log(f"Error in describe_data: {e}", "ERROR")
        return json.dumps({"error": str(e)})