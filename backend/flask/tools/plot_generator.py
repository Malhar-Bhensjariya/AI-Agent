import pandas as pd
import numpy as np
import json
from utils.logger import log

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

    def _prepare_data_for_json(self, data):
        """Convert pandas/numpy data types to JSON-serializable types"""
        if isinstance(data, (pd.Series, np.ndarray)):
            return data.tolist()
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif pd.isna(data):
            return None
        return data

    def _get_chart_colors(self, count, chart_type='bar'):
        """Generate appropriate colors for charts"""
        if chart_type == 'pie':
            # Predefined colors for pie charts
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
            ]
            return colors[:count] if count <= len(colors) else colors * (count // len(colors) + 1)
        else:
            # Single color for bar/line charts
            return '#36A2EB'

    def generate_bar_plot(self, x_col: str, y_col: str, save_path: str = None):
        """Generate bar plot configuration for Chart.js"""
        try:
            self._validate_columns(x_col, y_col)

            # Prepare data - group by x_col and aggregate y_col
            if self.df[x_col].dtype in ['object', 'category']:
                # For categorical data, use mean aggregation
                grouped_data = self.df.groupby(x_col)[y_col].mean().reset_index()
            else:
                # For numeric x, use the data as is but limit to reasonable number of points
                if self.df[x_col].nunique() > 50:
                    log(f"Warning: Too many unique values in {x_col}, sampling 50 points", "WARNING")
                    sampled_df = self.df.sample(n=50).sort_values(x_col)
                    grouped_data = sampled_df[[x_col, y_col]]
                else:
                    grouped_data = self.df[[x_col, y_col]].sort_values(x_col)

            # Convert to JSON-serializable format
            labels = [self._prepare_data_for_json(val) for val in grouped_data[x_col]]
            values = [self._prepare_data_for_json(val) for val in grouped_data[y_col]]

            chart_config = {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': y_col,
                        'data': values,
                        'backgroundColor': self._get_chart_colors(len(values), 'bar'),
                        'borderColor': '#2E86AB',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'Bar Chart: {y_col} vs {x_col}'
                        },
                        'legend': {
                            'display': True
                        }
                    },
                    'scales': {
                        'x': {
                            'title': {
                                'display': True,
                                'text': x_col
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': y_col
                            }
                        }
                    }
                }
            }

            log(f"Bar plot configuration generated for {x_col} vs {y_col}", "INFO")
            return json.dumps(chart_config)

        except Exception as e:
            log(f"Error generating bar plot: {str(e)}", "ERROR")
            raise ValueError(f"Failed to generate bar plot: {str(e)}")

    def generate_line_plot(self, x_col: str, y_col: str, save_path: str = None):
        """Generate line plot configuration for Chart.js"""
        try:
            self._validate_columns(x_col, y_col)

            # Check if data is numeric for line plot
            if not pd.api.types.is_numeric_dtype(self.df[y_col]):
                log(f"Warning: Column '{y_col}' is not numeric, attempting conversion", "WARNING")
                try:
                    self.df[y_col] = pd.to_numeric(self.df[y_col], errors='coerce')
                except:
                    raise ValueError(f"Column '{y_col}' cannot be converted to numeric for line plot")

            # Sort by x column and limit data points for performance
            df_sorted = self.df.sort_values(x_col)
            if len(df_sorted) > 1000:
                log(f"Warning: Too many data points ({len(df_sorted)}), sampling 1000 points", "WARNING")
                step = len(df_sorted) // 1000
                df_sorted = df_sorted.iloc[::step]

            # Prepare data
            labels = [self._prepare_data_for_json(val) for val in df_sorted[x_col]]
            values = [self._prepare_data_for_json(val) for val in df_sorted[y_col]]

            chart_config = {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': y_col,
                        'data': values,
                        'borderColor': '#36A2EB',
                        'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                        'borderWidth': 2,
                        'fill': False,
                        'tension': 0.1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'Line Chart: {y_col} vs {x_col}'
                        },
                        'legend': {
                            'display': True
                        }
                    },
                    'scales': {
                        'x': {
                            'title': {
                                'display': True,
                                'text': x_col
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': y_col
                            }
                        }
                    },
                    'interaction': {
                        'intersect': False,
                        'mode': 'index'
                    }
                }
            }

            log(f"Line plot configuration generated for {x_col} vs {y_col}", "INFO")
            return json.dumps(chart_config)

        except Exception as e:
            log(f"Error generating line plot: {str(e)}", "ERROR")
            raise ValueError(f"Failed to generate line plot: {str(e)}")

    def generate_pie_chart(self, column: str, save_path: str = None, max_categories: int = 10):
        """Generate pie chart configuration for Chart.js"""
        try:
            self._validate_columns(column)

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

            # Prepare data
            labels = [str(label) for label in data_counts.index]
            values = [self._prepare_data_for_json(val) for val in data_counts.values]
            colors = self._get_chart_colors(len(values), 'pie')

            chart_config = {
                'type': 'pie',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': colors,
                        'borderColor': '#fff',
                        'borderWidth': 2
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'Pie Chart: {column}'
                        },
                        'legend': {
                            'display': True,
                            'position': 'right'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.label + ": " + context.parsed + " (" + ((context.parsed/context.dataset.data.reduce((a,b) => a+b, 0)) * 100).toFixed(1) + "%)"; }'
                            }
                        }
                    }
                }
            }

            log(f"Pie chart configuration generated for {column}", "INFO")
            return json.dumps(chart_config)

        except Exception as e:
            log(f"Error generating pie chart: {str(e)}", "ERROR")
            raise ValueError(f"Failed to generate pie chart: {str(e)}")

    def generate_histogram(self, column: str, bins: int = 30, save_path: str = None):
        """Generate histogram configuration for Chart.js"""
        try:
            self._validate_columns(column)

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

            # Create histogram bins
            hist_counts, bin_edges = np.histogram(data_to_plot, bins=bins)
            
            # Create bin labels (midpoint of each bin)
            bin_labels = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
            bin_labels = [round(label, 2) for label in bin_labels]

            chart_config = {
                'type': 'bar',
                'data': {
                    'labels': bin_labels,
                    'datasets': [{
                        'label': 'Frequency',
                        'data': [self._prepare_data_for_json(count) for count in hist_counts],
                        'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                        'borderColor': '#36A2EB',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'Histogram: {column}'
                        },
                        'legend': {
                            'display': True
                        }
                    },
                    'scales': {
                        'x': {
                            'title': {
                                'display': True,
                                'text': column
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': 'Frequency'
                            }
                        }
                    }
                }
            }

            log(f"Histogram configuration generated for {column}", "INFO")
            return json.dumps(chart_config)

        except Exception as e:
            log(f"Error generating histogram: {str(e)}", "ERROR")
            raise ValueError(f"Failed to generate histogram: {str(e)}")

    def generate_scatter_plot(self, x_col: str, y_col: str, save_path: str = None):
        """Generate scatter plot configuration for Chart.js"""
        try:
            self._validate_columns(x_col, y_col)

            # Ensure both columns are numeric
            for col in [x_col, y_col]:
                if not pd.api.types.is_numeric_dtype(self.df[col]):
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    except:
                        raise ValueError(f"Column '{col}' cannot be converted to numeric for scatter plot")

            # Limit data points for performance
            df_clean = self.df[[x_col, y_col]].dropna()
            if len(df_clean) > 1000:
                log(f"Warning: Too many data points ({len(df_clean)}), sampling 1000 points", "WARNING")
                df_clean = df_clean.sample(n=1000)

            # Prepare data as x,y coordinate pairs
            data_points = [
                {
                    'x': self._prepare_data_for_json(row[x_col]),
                    'y': self._prepare_data_for_json(row[y_col])
                }
                for _, row in df_clean.iterrows()
            ]

            chart_config = {
                'type': 'scatter',
                'data': {
                    'datasets': [{
                        'label': f'{y_col} vs {x_col}',
                        'data': data_points,
                        'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                        'borderColor': '#36A2EB',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'Scatter Plot: {y_col} vs {x_col}'
                        },
                        'legend': {
                            'display': True
                        }
                    },
                    'scales': {
                        'x': {
                            'title': {
                                'display': True,
                                'text': x_col
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': y_col
                            }
                        }
                    }
                }
            }

            log(f"Scatter plot configuration generated for {x_col} vs {y_col}", "INFO")
            return json.dumps(chart_config)

        except Exception as e:
            log(f"Error generating scatter plot: {str(e)}", "ERROR")
            raise ValueError(f"Failed to generate scatter plot: {str(e)}")

    def get_plot_recommendations(self):
        """Get recommendations for which plots work best with the current data"""
        recommendations = []
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            recommendations.append("Line plots and scatter plots work well with your numeric columns")
        
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