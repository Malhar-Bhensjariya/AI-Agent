
# AIDA – AI-powered Intelligent Data Analyst  

AIDA is a conversational AI platform designed to make data analysis seamless and accessible. Instead of writing complex queries or code, users can simply upload CSV files and interact with their data through natural language. Powered by modular AI agents, AIDA can clean, transform, analyze, and visualize datasets, making it useful for students, analysts, and professionals who want quick insights without diving deep into technical details. 
## Demo

✨ **Check out the live demo:** [Try it here!](https://ai-da-six.vercel.app/)
## Features  

#### 1. CSV Upload and File Handling  
- Upload **CSV files** directly through the interface.  
- Files are automatically processed into **pandas DataFrames** for analysis.  

#### 2. Intelligent Data Analysis  
- Powered by modular **AI Agents** (Gemini 2.0 Flash).  
- Supports:  
  - Missing value detection  
  - Outlier detection  
  - Statistical summaries  
  - Frequency counts  

#### 3. Interactive Data Editing  
- Perform operations such as filtering, grouping, transformations, and column edits.  
- The **Editor Agent** enables direct data manipulation without writing code.  

#### 4. Conversational Interface  
- A **chat-driven UI** (React + Vite) to interact with datasets.  
- Ask questions, request edits, or generate charts in plain English.  

## Run Locally

Clone the project

```bash
git clone https://github.com/Malhar-Bhensjariya/AI-Agent.git
```

Backend (Flask)
- Go to the backend directory

    ```bash
    cd AI-Agent/backend/flask
    ```
- Create a virtual environment

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/Mac
    venv\Scripts\activate      # On Windows
    ```
- Install dependencies

    ```bash
    pip install -r requirements.txt
    ```
- Start the Flask server

    ```bash
    python app.py
    ```

Frontend (React)

- Go to the frontend directory

    ```bash
    cd ../../frontend
    ```
- Install dependencies

    ```bash
    npm install
    ```

- Start the development server

    ```bash
    npm run dev
    ```

Environment Variables

- Flask .env

    ```bash
    GEMINI_API_KEY=your-gemini-api-key
    ```
- Install dependencies

    ```bash
    FLASK_API=http://localhost:5000
    ```
## Folder Structure


```text
aida/
├── backend/
│   ├── flask/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── agent_executor.py           # Routes task to specific agent
│   │   │   ├── tool_selector.py            # Gemini decides agent/tool ('a', 'b', etc.)
│   │   │   ├── editor_agent.py             # DF editing
│   │   │   ├── data_analyzer_agent.py      # Data analysis
│   │   │   ├── data_transform_agent.py     # Filtering, transformation, etc.
│   │   │   ├── visualization_agent.py      # Matplotlib/seaborn-based charts
│   │   │   └── chat_agent.py               # Default fallback agent for general queries
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── df_operator.py              # DF Langchain wrapper
│   │   │   ├── analyzer_operator.py
│   │   │   ├── transformer_operator.py
│   │   │   └── visualize_operator.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py             # File reading/saving
│   │   │   ├── df_editor.py                # Core logic for DF edits
│   │   │   ├── analyzer.py                 # Data analysis logic
│   │   │   ├── transformer.py              # Data manipulation logic
│   │   │   └── plot_generator.py           # Plot/chart generation
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── layout.py                   # Consistent styling for plots 
│   │   │   ├── logger.py                   # Logging utility
│   │   │   └── gemini_connector.py         # Connect with Gemini 2.0 flash and use it in agents
│   │   ├── uploads/                        # Uploaded files (CSV, Excel, etc.)
│   │   ├── static/
│   │   │   └── plots/                      # Saved plot images
│   │   ├── vectorstore/                    # (Optional) For future RAG/CAG
│   │   ├── .env                            # Gemini keys and config
│   │   ├── app.py                          # Flask entrypoint
│   │   └── requirements.txt
|
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── assets/     
│   │   ├── components/
│   │   │   ├── layout/ 
│   │   │   │   └── Sidebar.jsx
│   │   │   ├── chat/ 
│   │   │   │   ├── ChatBox.jsx
│   │   │   │   └── MessageBubble.jsx
│   │   │   ├── table/
│   │   │   │   └── TableView.jsx
│   │   │   ├── chart/
│   │   │   │   └── ChartView.jsx
│   │   │   └── common/
│   │   │       ├── Loader.jsx
│   │   │       └── ToggleSwitch.jsx
│   │   ├── context/
│   │   │   └── AppContext.js
│   │   ├── hooks/
│   │   │   ├── useAgentResponse.jsx
│   │   │   └── useUploadTask.js
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   └── LandingPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js
│   └── package.json
├── .env
├── .gitignore
└── README.md

```
