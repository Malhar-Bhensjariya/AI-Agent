import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

def detect_agent_type(user_query: str) -> str:
    """Use Gemini to classify the query into a tool category (1–4)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.1,
        convert_system_message_to_human=True
    )

    system_prompt = SystemMessage(content="""You are a classification agent that categorizes a user's request related to CSV or Excel files into one of four agent types.

Return ONLY one of the following digits as your entire response:
1 — For data editing (e.g., add/remove rows/columns, set a cell, update a row, rename columns)
2 — For data analysis (e.g., calculate statistics, detect outliers, show frequency counts, give column names)
3 — For data transformation (e.g., filter rows, sort data, clean values)
4 — For visualizations (e.g., generate bar chart, pie chart, or line plot)
5 — For anything else, including unclear or general prompts

ONLY reply with 1, 2, 3, 4 or 5. Do not include any explanation. No extra text or punctuation.""")

    user_prompt = HumanMessage(content=user_query)

    try:
        response = model.invoke([system_prompt, user_prompt])
        selection = response.content.strip()

        if selection not in {"1", "2", "3", "4", "5"}:
            return "5"  # Default fallback to chat agent

        return {
            "1": "editor",
            "2": "analyze",
            "3": "transform",
            "4": "visual",
            "5": "chat"
        }[selection]

    except Exception:
        return "chat"
