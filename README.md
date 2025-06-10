# AI-Agent
## AIDA – AI-powered Intelligent Data Analyst

```text
aida/
├── backend/
│   ├── flask/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── agent_executor.py           # Routes task to specific agent
│   │   │   ├── tool_selector.py            # Gemini decides agent/tool ('a', 'b', etc.)
│   │   │   ├── editor_agent.py             # DF editing
│   │   │   ├── data_transform_agent.py     # Filtering, transformation, etc.
│   │   │   ├── visualization_agent.py      # Matplotlib/seaborn-based charts
│   │   │   └── chat_agent.py               # Default fallback agent for general queries
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── df_operator.py              # DF Langchain wrapper
│   │   │   ├── transformer_operator.py
│   │   │   └── visualize_operator.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py             # File reading/saving
│   │   │   ├── df_editor.py                # Core logic for DF edits
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
│   └── postgres/
│       ├── init.sql                        # Schema or seed data
│       └── docker-compose.yml              # Postgres service config
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