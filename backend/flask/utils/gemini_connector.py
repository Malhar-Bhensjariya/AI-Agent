# gemini_connector.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_app.utils.logger import log  # Adjust path based on your structure

load_dotenv()

# Load API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment.")

# Configure Gemini
genai.configure(api_key=api_key)

# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Generation config
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192
}


def get_response(prompt: str, history: list = None) -> str:
    """
    Sends a prompt to Gemini and returns the response text.
    
    Args:
        prompt (str): User input or query.
        history (list): Optional list of prior messages (for chat context).
    
    Returns:
        str: Gemini's response.
    """
    try:
        chat = model.start_chat(history=history or [])
        response = chat.send_message(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        log(f"Gemini response error: {e}", level="ERROR")
        return "Gemini couldn't process your request."


def get_raw_model():
    """
    Returns the raw generative model instance (for tool-based agents).
    """
    return model
