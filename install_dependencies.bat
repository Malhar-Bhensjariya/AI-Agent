@echo off
setlocal enabledelayedexpansion
REM AI Agent Services - Dependency Installation Script (Windows)
REM This script installs all dependencies for all microservices

echo 🚀 Starting AI Agent Services Dependency Installation
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo [INFO] Python version:
python --version
echo [INFO] Node.js version:
node --version

REM Get the directory where the script is located
set "BASE_DIR=%~dp0"
echo [INFO] Working directory: %BASE_DIR%

REM Services to install
set SERVICES=main_service editor_service analyzer_service transform_service visualization_service chat_service auth_service

REM Install Python dependencies for each service
echo [INFO] Installing Python dependencies for all services...

for %%s in (%SERVICES%) do (
    set "SERVICE_DIR=%BASE_DIR%services\%%s"

    if exist "!SERVICE_DIR!" (
        echo [INFO] Installing dependencies for %%s...

        REM Create virtual environment if it doesn't exist
        if not exist "!SERVICE_DIR!\venv" (
            echo [INFO] Creating virtual environment for %%s...
            python -m venv "!SERVICE_DIR!\venv"
        )

        REM Activate virtual environment and install dependencies
        call "!SERVICE_DIR!\venv\Scripts\activate.bat"

        if exist "!SERVICE_DIR!\requirements.txt" (
            python -m pip install --upgrade pip
            pip install -r "!SERVICE_DIR!\requirements.txt"
            if !errorlevel! equ 0 (
                echo [SUCCESS] Dependencies installed for %%s
            ) else (
                echo [ERROR] Failed to install dependencies for %%s
            )
        ) else (
            echo [WARNING] No requirements.txt found for %%s
        )

        call deactivate
    ) else (
        echo [WARNING] Service directory !SERVICE_DIR! not found
    )
)

REM Install frontend dependencies
echo [INFO] Installing frontend dependencies...

if exist "%BASE_DIR%frontend" (
    cd "%BASE_DIR%frontend"

    if exist "package.json" (
        npm install

        if %errorlevel% equ 0 (
            echo [SUCCESS] Frontend dependencies installed
        ) else (
            echo [ERROR] Failed to install frontend dependencies
        )
    ) else (
        echo [WARNING] No package.json found in frontend directory
    )
) else (
    echo [WARNING] Frontend directory not found
)

REM Create .env files if they don't exist
echo [INFO] Setting up environment files...

REM Main service .env
if not exist "%BASE_DIR%services\main_service\.env" (
    echo FLASK_ENV=development> "%BASE_DIR%services\main_service\.env"
    echo FLASK_DEBUG=True>> "%BASE_DIR%services\main_service\.env"
    echo PORT=5000>> "%BASE_DIR%services\main_service\.env"
    echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production>> "%BASE_DIR%services\main_service\.env"
    echo MONGODB_URI=mongodb://localhost:27017/aida_db>> "%BASE_DIR%services\main_service\.env"
    echo [SUCCESS] Created .env for main_service
)

REM Auth service .env
if not exist "%BASE_DIR%services\auth_service\.env" (
    echo FLASK_ENV=development> "%BASE_DIR%services\auth_service\.env"
    echo FLASK_DEBUG=True>> "%BASE_DIR%services\auth_service\.env"
    echo PORT=5006>> "%BASE_DIR%services\auth_service\.env"
    echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production>> "%BASE_DIR%services\auth_service\.env"
    echo MONGODB_URI=mongodb://localhost:27017/aida_db>> "%BASE_DIR%services\auth_service\.env"
    echo [SUCCESS] Created .env for auth_service
)

REM Other services .env
set counter=1
for %%s in (editor_service analyzer_service transform_service visualization_service chat_service) do (
    set /a port=5000 + counter
    if not exist "%BASE_DIR%services\%%s\.env" (
        echo FLASK_ENV=development> "%BASE_DIR%services\%%s\.env"
        echo FLASK_DEBUG=True>> "%BASE_DIR%services\%%s\.env"
        echo PORT=!port!>> "%BASE_DIR%services\%%s\.env"
        echo [SUCCESS] Created .env for %%s
    )
    set /a counter+=1
)

REM Frontend .env
if not exist "%BASE_DIR%frontend\.env" (
    echo VITE_FLASK_API=http://localhost:5000> "%BASE_DIR%frontend\.env"
    echo [SUCCESS] Created .env for frontend
)

REM Create uploads directories
echo [INFO] Creating uploads directories...
for %%s in (main_service editor_service analyzer_service transform_service visualization_service chat_service auth_service) do (
    if not exist "%BASE_DIR%services\%%s\uploads" (
        mkdir "%BASE_DIR%services\%%s\uploads"
        echo [SUCCESS] Created uploads directory for %%s
    )
)

REM Create static directories for services that need them
if not exist "%BASE_DIR%services\main_service\static\plots" (
    mkdir "%BASE_DIR%services\main_service\static\plots"
    echo [SUCCESS] Created static/plots directory for main_service
)

REM Final instructions
echo.
echo ==================================================
echo [SUCCESS] All dependencies installed successfully!
echo.
echo Next steps:
echo 1. Make sure MongoDB is running locally or update MONGODB_URI in .env files
echo 2. Start all services: python services\start_all.py
echo 3. Start frontend: cd frontend ^& npm run dev
echo 4. Open http://localhost:5173 in your browser
echo.
echo Service URLs:
echo - Main Service: http://localhost:5000
echo - Auth Service: http://localhost:5006
echo - Editor Service: http://localhost:5001
echo - Analyzer Service: http://localhost:5002
echo - Transform Service: http://localhost:5003
echo - Visualization Service: http://localhost:5004
echo - Chat Service: http://localhost:5005
echo - Frontend: http://localhost:5173
echo.
echo [WARNING] Remember to change JWT_SECRET_KEY and MONGODB_URI for production!
echo.
pause