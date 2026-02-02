import os
import pandas as pd
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(uploaded_file, upload_dir: str) -> str:
    """
    Save the uploaded file to upload_dir if valid.
    Returns the saved file path or raises ValueError.
    """
    if uploaded_file.filename == '':
        raise ValueError("No selected file")

    if not allowed_file(uploaded_file.filename):
        raise ValueError(f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    filename = secure_filename(uploaded_file.filename)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    uploaded_file.save(file_path)
    return file_path

def load_file_as_dataframe(file_path: str) -> pd.DataFrame:
    """
    Load a saved file (CSV, XLS, XLSX) into a pandas DataFrame.
    Preserves column order as they appear in the file.
    """
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        # Explicitly preserve column order with encoding specification
        return pd.read_csv(file_path, encoding='utf-8')
    elif ext in ('xls', 'xlsx'):
        # Use openpyxl engine for better consistency
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file extension: .{ext}")