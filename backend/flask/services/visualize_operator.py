from langchain_core.tools import tool
from tools.plot_generator import PlotGenerator
from tools.file_handler import load_file_as_dataframe
from utils.logger import log
import json
import pandas as pd

@tool
def create_bar_plot(file_path: str, x_column: str, y_column: str) -> str:
    """Create an interactive bar plot configuration using two columns (categorical x-axis, numeric y-axis)."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        chart_config = plot_generator.generate_bar_plot(x_column, y_column)
        log(f"Interactive bar plot configuration created for {x_column} vs {y_column} from {file_path}", "INFO")
        
        return json.dumps({
            "type": "chart", 
            "chart_type": "bar", 
            "chart_config": chart_config,
            "message": f"Bar plot configuration generated successfully for '{y_column}' vs '{x_column}'"
        })
    except Exception as e:
        error_msg = f"Error creating bar plot: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def create_line_plot(file_path: str, x_column: str, y_column: str) -> str:
    """Create an interactive line plot configuration using two numeric columns."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        chart_config = plot_generator.generate_line_plot(x_column, y_column)
        log(f"Interactive line plot configuration created for {x_column} vs {y_column} from {file_path}", "INFO")
        
        return json.dumps({
            "type": "chart", 
            "chart_type": "line", 
            "chart_config": chart_config,
            "message": f"Line plot configuration generated successfully for '{y_column}' vs '{x_column}'"
        })
    except Exception as e:
        error_msg = f"Error creating line plot: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def create_scatter_plot(file_path: str, x_column: str, y_column: str) -> str:
    """Create an interactive scatter plot configuration using two numeric columns."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        chart_config = plot_generator.generate_scatter_plot(x_column, y_column)
        log(f"Interactive scatter plot configuration created for {x_column} vs {y_column} from {file_path}", "INFO")
        
        return json.dumps({
            "type": "chart", 
            "chart_type": "scatter", 
            "chart_config": chart_config,
            "message": f"Scatter plot configuration generated successfully for '{y_column}' vs '{x_column}'"
        })
    except Exception as e:
        error_msg = f"Error creating scatter plot: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def create_pie_chart(file_path: str, column_name: str, max_categories: int = 10) -> str:
    """Create an interactive pie chart configuration showing the distribution of a categorical column's values."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        chart_config = plot_generator.generate_pie_chart(column_name, max_categories=max_categories)
        log(f"Interactive pie chart configuration created for {column_name} from {file_path}", "INFO")
        
        return json.dumps({
            "type": "chart", 
            "chart_type": "pie", 
            "chart_config": chart_config,
            "message": f"Pie chart configuration generated successfully for '{column_name}'"
        })
    except Exception as e:
        error_msg = f"Error creating pie chart: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def create_histogram(file_path: str, column_name: str, bins: int = 30) -> str:
    """Create an interactive histogram configuration showing the distribution of a numeric column's values."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        chart_config = plot_generator.generate_histogram(column_name, bins)
        log(f"Interactive histogram configuration created for {column_name} from {file_path}", "INFO")
        
        return json.dumps({
            "type": "chart", 
            "chart_type": "histogram", 
            "chart_config": chart_config,
            "message": f"Histogram configuration generated successfully for '{column_name}'"
        })
    except Exception as e:
        error_msg = f"Error creating histogram: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def get_plot_recommendations(file_path: str) -> str:
    """Get recommendations for which plots work best with the data in the file."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        recommendations = plot_generator.get_plot_recommendations()
        if not recommendations:
            message = "No specific plot recommendations available for this data."
        else:
            message = "Plot recommendations for your data:\n" + "\n".join(f"• {rec}" for rec in recommendations)

        return json.dumps({"type": "info", "message": message})
    except Exception as e:
        error_msg = f"Error getting plot recommendations: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def get_data_summary_for_plotting(file_path: str) -> str:
    """Get a summary of the data that's useful for choosing plots."""
    try:
        df = load_file_as_dataframe(file_path)
        
        total_rows, total_cols = df.shape
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        summary = {
            "type": "info",
            "message": f"Data Summary for Plotting:\n"
                      f"• Total rows: {total_rows}\n"
                      f"• Total columns: {total_cols}\n"
                      f"• Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}\n"
                      f"• Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}",
            "total_rows": total_rows,
            "total_columns": total_cols,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols
        }
        
        return json.dumps(summary)
    except Exception as e:
        error_msg = f"Error getting data summary: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

@tool
def create_multi_series_chart(file_path: str, x_column: str, y_columns: list, chart_type: str = "line") -> str:
    """Create an interactive multi-series chart configuration with multiple y-columns."""
    try:
        df = load_file_as_dataframe(file_path)
        
        missing = [col for col in [x_column] + y_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Columns {missing} not found in data.")
        
        df_sorted = df.sort_values(x_column)
        if len(df_sorted) > 1000:
            df_sorted = df_sorted.iloc[::len(df_sorted) // 1000]

        labels = [str(val) for val in df_sorted[x_column]]

        colors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']

        datasets = []
        for i, y_col in enumerate(y_columns):
            color = colors[i % len(colors)]

            dataset = {
                'label': y_col,
                'data': [float(val) if pd.notna(val) else None for val in df_sorted[y_col]],
                'borderColor': color,
                'backgroundColor': color + '20' if chart_type == 'line' else color,
                'borderWidth': 2 if chart_type == 'line' else 1,
                'fill': False if chart_type == 'line' else True
            }
            datasets.append(dataset)

        chart_config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{chart_type.title()} Chart: {", ".join(y_columns)} vs {x_column}'
                    },
                    'legend': {
                        'display': True
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': x_column
                        }
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'Values'
                        }
                    }
                },
                'interaction': {
                    'intersect': False,
                    'mode': 'index'
                }
            }
        }
        
        return json.dumps({
            "type": "chart", 
            "chart_type": chart_type, 
            "chart_config": chart_config,
            "message": f"Multi-series {chart_type} chart configuration generated successfully for {y_columns} vs {x_column}"
        })
    except Exception as e:
        error_msg = f"Error creating multi-series chart: {str(e)}"
        log(error_msg, "ERROR")
        return json.dumps({"type": "error", "message": error_msg})

def get_visualization_tools():
    """Return all available visualization tools."""
    return [
        create_bar_plot,
        create_line_plot,
        create_scatter_plot,
        create_pie_chart,
        create_histogram,
        create_multi_series_chart,
        get_plot_recommendations,
        get_data_summary_for_plotting
    ]