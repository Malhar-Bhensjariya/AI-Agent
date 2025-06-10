# utils/logger.py
import datetime

def log(message: str, level: str = "INFO") -> None:
    """
    Logs a message to the console with a timestamp and level.

    Args:
        message (str): The log message.
        level (str): Severity level ("INFO", "ERROR", etc.).
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
