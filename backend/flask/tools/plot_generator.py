import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from flask_app.utils.layout import apply_default_layout, configure_figure
from flask_app.utils.logger import log

class PlotGenerator:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if df.empty:
            raise ValueError("DataFrame cannot be empty")
        self.df = df

    def _validate_columns(self, *columns):
        """Validate that columns exist in the DataFrame"""
        missing_cols = [col for col in columns if col not in self.df.columns]
        if missing_cols:
            available_cols = list(self.df.columns)
            raise ValueError(f"Columns {missing_cols} not found in data. Available columns: {available_cols}")

    def _validate_save_path(self, save_path: str):
        """Validate and prepare save path"""
        if save_path:
            # Create directory if it doesn't exist
            directory = os.path.dirname(save_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    raise ValueError(f"Cannot create directory {directory}: {str(e)}")
            
            # Check if file extension is valid
            valid_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.svg']
            if not any(save_path.lower().endswith(ext) for ext in valid_extensions):
                log(f"Warning: {save_path} may not have a valid image extension", "WARNING")

    def generate_bar_plot(self, x_col: str, y_col: str, save_path: str = None):
        """Generate a bar plot"""
        try:
            self._validate_columns(x_col, y_col)
            if save_path:
                self._validate_save_path(save_path)

            # Check if data is suitable for bar plot
            if self.df[x_col].dtype not in ['object', 'category'] and self.df[x_col].nunique() > 20:
                log(f"Warning: Column '{x_col}' has {self.df[x_col].nunique()} unique values, plot may be cluttered", "WARNING")

            fig, ax = configure_figure()
            
            # Handle potential issues with seaborn barplot
            try:
                sns.barplot(data=self.df, x=x_col, y=y_col, ax=ax)
            except Exception as e:
                # Fallback to matplotlib if seaborn fails
                log(f"Seaborn barplot failed, using matplotlib: {str(e)}", "WARNING")
                grouped_data = self.df.groupby(x_col)[y_col].mean()
                ax.bar(range(len(grouped_data)), grouped_data.values)
                ax.set_xticks(range(len(grouped_data)))
                ax.set_xticklabels(grouped_data.index)

            apply_default_layout(ax, title=f"Bar Plot: {y_col} vs {x_col}", xlabel=x_col, ylabel=y_col, rotate_xticks=True)

            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                log(f"Bar plot saved to {save_path}", "INFO")
                
            plt.close(fig)
            return f"Bar plot saved to {save_path}" if save_path else "Bar plot generated successfully"

        except Exception as e:
            log(f"Error generating bar plot: {str(e)}", "ERROR")
            if 'fig' in locals():
                plt.close(fig)
            raise ValueError(f"Failed to generate bar plot: {str(e)}")

    def generate_line_plot(self, x_col: str, y_col: str, save_path: str = None):
        """Generate a line plot"""
        try:
            self._validate_columns(x_col, y_col)
            if save_path:
                self._validate_save_path(save_path)

            # Check if data is numeric for line plot
            if not pd.api.types.is_numeric_dtype(self.df[y_col]):
                log(f"Warning: Column '{y_col}' is not numeric, attempting conversion", "WARNING")
                try:
                    self.df[y_col] = pd.to_numeric(self.df[y_col], errors='coerce')
                except:
                    raise ValueError(f"Column '{y_col}' cannot be converted to numeric for line plot")

            fig, ax = configure_figure()
            
            # Sort by x column for better line plot
            df_sorted = self.df.sort_values(x_col)
            
            try:
                sns.lineplot(data=df_sorted, x=x_col, y=y_col, ax=ax)
            except Exception as e:
                # Fallback to matplotlib if seaborn fails
                log(f"Seaborn lineplot failed, using matplotlib: {str(e)}", "WARNING")
                ax.plot(df_sorted[x_col], df_sorted[y_col])

            apply_default_layout(ax, title=f"Line Plot: {y_col} vs {x_col}", xlabel=x_col, ylabel=y_col)

            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                log(f"Line plot saved to {save_path}", "INFO")
                
            plt.close(fig)
            return f"Line plot saved to {save_path}" if save_path else "Line plot generated successfully"

        except Exception as e:
            log(f"Error generating line plot: {str(e)}", "ERROR")
            if 'fig' in locals():
                plt.close(fig)
            raise ValueError(f"Failed to generate line plot: {str(e)}")

    def generate_pie_chart(self, column: str, save_path: str = None, max_categories: int = 10):
        """Generate a pie chart"""
        try:
            self._validate_columns(column)
            if save_path:
                self._validate_save_path(save_path)

            # Get value counts and handle too many categories
            data_counts = self.df[column].value_counts()
            
            if len(data_counts) == 0:
                raise ValueError(f"Column '{column}' has no data to plot")
            
            if len(data_counts) > max_categories:
                log(f"Too many categories ({len(data_counts)}), showing top {max_categories}", "WARNING")
                top_categories = data_counts.head(max_categories)
                other_sum = data_counts.iloc[max_categories:].sum()
                if other_sum > 0:
                    top_categories['Others'] = other_sum
                data_counts = top_categories

            fig, ax = configure_figure(size=(8, 8))
            colors = sns.color_palette('pastel', len(data_counts))
            
            # Create pie chart with better formatting
            wedges, texts, autotexts = ax.pie(
                data_counts.values, 
                labels=data_counts.index, 
                autopct='%1.1f%%', 
                colors=colors, 
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            # Improve text visibility
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
            
            ax.set_title(f"Pie Chart: {column}", fontsize=14, fontweight='bold', pad=20)

            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                log(f"Pie chart saved to {save_path}", "INFO")
                
            plt.close(fig)
            return f"Pie chart saved to {save_path}" if save_path else "Pie chart generated successfully"

        except Exception as e:
            log(f"Error generating pie chart: {str(e)}", "ERROR")
            if 'fig' in locals():
                plt.close(fig)
            raise ValueError(f"Failed to generate pie chart: {str(e)}")

    def generate_histogram(self, column: str, bins: int = 30, save_path: str = None):
        """Generate a histogram for numeric data"""
        try:
            self._validate_columns(column)
            if save_path:
                self._validate_save_path(save_path)

            # Check if column is numeric
            if not pd.api.types.is_numeric_dtype(self.df[column]):
                try:
                    numeric_data = pd.to_numeric(self.df[column], errors='coerce')
                    if numeric_data.isnull().all():
                        raise ValueError(f"Column '{column}' contains no numeric data")
                    data_to_plot = numeric_data.dropna()
                except:
                    raise ValueError(f"Column '{column}' is not numeric and cannot be converted")
            else:
                data_to_plot = self.df[column].dropna()

            if len(data_to_plot) == 0:
                raise ValueError(f"No valid data found in column '{column}'")

            fig, ax = configure_figure()
            ax.hist(data_to_plot, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
            
            apply_default_layout(ax, title=f"Histogram: {column}", xlabel=column, ylabel='Frequency')

            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                log(f"Histogram saved to {save_path}", "INFO")
                
            plt.close(fig)
            return f"Histogram saved to {save_path}" if save_path else "Histogram generated successfully"

        except Exception as e:
            log(f"Error generating histogram: {str(e)}", "ERROR")
            if 'fig' in locals():
                plt.close(fig)
            raise ValueError(f"Failed to generate histogram: {str(e)}")

    def get_plot_recommendations(self):
        """Get recommendations for which plots work best with the current data"""
        recommendations = []
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            recommendations.append("Line plots work well with your numeric columns")
        
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            recommendations.append("Bar plots are recommended for categorical vs numeric data")
        
        for col in categorical_cols:
            unique_vals = self.df[col].nunique()
            if unique_vals <= 10:
                recommendations.append(f"Pie chart recommended for '{col}' ({unique_vals} categories)")
            elif unique_vals > 20:
                recommendations.append(f"'{col}' has too many categories ({unique_vals}) for pie chart")
        
        for col in numeric_cols:
            recommendations.append(f"Histogram recommended for '{col}' distribution")
        
        return recommendations