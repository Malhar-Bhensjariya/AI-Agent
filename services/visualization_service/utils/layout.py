import matplotlib.pyplot as plt
import seaborn as sns

# Set global Seaborn theme
sns.set_theme(style="whitegrid")

def apply_default_layout(ax, title: str = "", xlabel: str = "", ylabel: str = "", rotate_xticks: bool = False):
    """
    Apply consistent styling to plots.
    """
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)

    if rotate_xticks:
        ax.tick_params(axis='x', labelrotation=45)

    plt.tight_layout()

def configure_figure(size=(8, 6), dpi=100):
    """
    Returns a figure and axis with standard size and DPI.
    """
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    return fig, ax
