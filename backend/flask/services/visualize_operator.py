from langchain_core.tools import tool
from flask_app.tools.plot_generator import PlotGenerator
from flask_app.utils.file_handler import load_file_as_dataframe
from flask_app.utils.logger import log

@tool
def create_bar_plot(file_path: str, x_column: str, y_column: str, save_path: str = None) -> str:
    """Create a bar plot using two columns (categorical x-axis, numeric y-axis)."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        result = plot_generator.generate_bar_plot(x_column, y_column, save_path)
        log(f"Bar plot created for {x_column} vs {y_column} from {file_path}", "INFO")
        return result
    except Exception as e:
        error_msg = f"Error creating bar plot: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

@tool
def create_line_plot(file_path: str, x_column: str, y_column: str, save_path: str = None) -> str:
    """Create a line plot using two numeric columns."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        result = plot_generator.generate_line_plot(x_column, y_column, save_path)
        log(f"Line plot created for {x_column} vs {y_column} from {file_path}", "INFO")
        return result
    except Exception as e:
        error_msg = f"Error creating line plot: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

@tool
def create_pie_chart(file_path: str, column_name: str, save_path: str = None, max_categories: int = 10) -> str:
    """Create a pie chart showing the distribution of a categorical column's values."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        result = plot_generator.generate_pie_chart(column_name, save_path, max_categories)
        log(f"Pie chart created for {column_name} from {file_path}", "INFO")
        return result
    except Exception as e:
        error_msg = f"Error creating pie chart: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

@tool
def create_histogram(file_path: str, column_name: str, bins: int = 30, save_path: str = None) -> str:
    """Create a histogram showing the distribution of a numeric column's values."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        result = plot_generator.generate_histogram(column_name, bins, save_path)
        log(f"Histogram created for {column_name} from {file_path}", "INFO")
        return result
    except Exception as e:
        error_msg = f"Error creating histogram: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

@tool
def get_plot_recommendations(file_path: str) -> str:
    """Get recommendations for which plots work best with the data in the file."""
    try:
        df = load_file_as_dataframe(file_path)
        plot_generator = PlotGenerator(df)
        recommendations = plot_generator.get_plot_recommendations()
        
        if not recommendations:
            return "No specific plot recommendations available for this data."
        
        result = "Plot recommendations for your data:\n" + "\n".join(f"• {rec}" for rec in recommendations)
        log(f"Plot recommendations generated for {file_path}", "INFO")
        return result
    except Exception as e:
        error_msg = f"Error getting plot recommendations: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

@tool
def get_data_summary_for_plotting(file_path: str) -> str:
    """Get a summary of the data that's useful for choosing plots."""
    try:
        df = load_file_as_dataframe(file_path)
        
        # Basic info
        total_rows, total_cols = df.shape
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        summary = f"Data Summary for Plotting:\n"
        summary += f"• Total rows: {total_rows}, Total columns: {total_cols}\n"
        summary += f"• Numeric columns ({len(numeric_cols)}): {', '.join(numeric_cols) if numeric_cols else 'None'}\n"
        summary += f"• Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols) if categorical_cols else 'None'}\n"
        
        # Add info about categorical columns
        if categorical_cols:
            summary += f"\nCategorical column details:\n"
            for col in categorical_cols[:5]:  # Limit to first 5 columns
                unique_count = df[col].nunique()
                summary += f"• '{col}': {unique_count} unique values\n"
                if unique_count <= 10:
                    summary += f"  Values: {', '.join(map(str, df[col].value_counts().head().index.tolist()))}\n"
        
        # Add info about numeric columns
        if numeric_cols:
            summary += f"\nNumeric column ranges:\n"
            for col in numeric_cols[:5]:  # Limit to first 5 columns
                min_val = df[col].min()
                max_val = df[col].max()
                summary += f"• '{col}': {min_val:.2f} to {max_val:.2f}\n"
        
        log(f"Data summary generated for plotting from {file_path}", "INFO")
        return summary
    except Exception as e:
        error_msg = f"Error getting data summary: {str(e)}"
        log(error_msg, "ERROR")
        return error_msg

def get_visualization_tools():
    """Return all available visualization tools."""
    return [
        create_bar_plot,
        create_line_plot,
        create_pie_chart,
        create_histogram,
        get_plot_recommendations,
        get_data_summary_for_plotting
    ]