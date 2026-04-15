
# AIDA – AI-powered Intelligent Data Analyst  

AIDA is a conversational AI platform designed to make data analysis seamless and accessible. Instead of writing complex queries or code, users can simply upload CSV files and interact with their data through natural language. Powered by modular AI agents, AIDA can clean, transform, analyze, and visualize datasets, making it useful for students, analysts, and professionals who want quick insights without diving deep into technical details. 

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

Backend (Microservices)
- Go to the services directory

    ```bash
    cd AI-Agent/services
    ```
- Each service has its own Python virtual environment (`venv` folder).
  Run the install script to create and populate these environments:

    ```bash
    ../install_dependencies.sh   # or install_dependencies.bat on Windows
    ```

- Start all services using the helper script. It will automatically invoke
  the `python` binary from each service's `venv`, ensuring isolation:

    ```bash
    python start_all.py
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

- Services .env

    ```bash
    GEMINI_API_KEY=your-gemini-api-key
    MONGODB_URI=mongodb+srv://<db_username>:<db_password>@cluster0.kwb9l6o.mongodb.net/?appName=Cluster0
    JWT_SECRET_KEY=your-jwt-secret-key
    ```
- Frontend .env

    ```bash
    FLASK_API=http://localhost:5000
    ```
## Folder Structure


```text
aida/
├── services/
│   ├── main_service/                       # Main service (tool selector, agent executor, auth, uploads)
│   │   ├── app.py                          # Flask app for main service
│   │   ├── agent_executor.py               # Routes to microservices
│   │   ├── tool_selector.py                # Gemini decides agent
│   │   ├── tools/                          # File handling tools
│   │   ├── utils/                          # Shared utilities
│   │   ├── uploads/                        # Uploaded files
│   │   ├── static/                         # Static files (plots)
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   ├── editor_service/                     # Data editing microservice
│   │   ├── app.py
│   │   ├── editor_agent.py
│   │   ├── df_operator.py
│   │   ├── df_editor.py
│   │   ├── file_handler.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   ├── analyzer_service/                   # Data analysis microservice
│   │   ├── app.py
│   │   ├── data_analyzer_agent.py
│   │   ├── analyzer_operator.py
│   │   ├── analyzer.py
│   │   ├── file_handler.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   ├── transform_service/                  # Data transformation microservice
│   │   ├── app.py
│   │   ├── data_transform_agent.py
│   │   ├── transformer_operator.py
│   │   ├── transformer.py
│   │   ├── file_handler.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   ├── visualization_service/              # Visualization microservice
│   │   ├── app.py
│   │   ├── visualization_agent.py
│   │   ├── visualize_operator.py
│   │   ├── plot_generator.py
│   │   ├── file_handler.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   ├── chat_service/                       # Chat microservice
│   │   ├── app.py
│   │   ├── chat_agent.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── .env
│   │   └── venv/
│   └── start_all.py                        # Script to start all services
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
