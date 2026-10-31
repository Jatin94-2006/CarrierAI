@echo off
title Agent 3 - Course Suggestion Server
color 0A
echo.
echo  ============================================
echo    Agent 3 - Course Suggestion Server
echo    AI Career Guidance Platform
echo  ============================================
echo.

set PYTHON=C:\Users\bhavi\AppData\Local\Programs\Python\Python312\python.exe

echo [1/3] Checking Python...
"%PYTHON%" --version
if errorlevel 1 (
    echo ERROR: Python not found at expected location.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing required packages (first time only)...
"%PYTHON%" -m pip install fastapi uvicorn python-dotenv httpx pydantic --quiet

echo.
echo [3/3] Starting FastAPI server on http://localhost:8000
echo.
echo  Dashboard:  Open agent3\demo\index.html in your browser
echo  API Docs:   http://localhost:8000/docs
echo  Health:     http://localhost:8000/health
echo.
echo  Press CTRL+C to stop the server.
echo.

cd /d "%~dp0"
"%PYTHON%" -m uvicorn main:app --reload --port 8000
pause
