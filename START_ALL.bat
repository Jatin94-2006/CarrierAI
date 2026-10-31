@echo off
title CareerAI Final Unified Launcher
echo Starting Backend (Port 8000)...
start "CareerAI Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend (Port 3000)...
start "CareerAI Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both servers launched:
echo Frontend: http://127.0.0.1:3000
echo Backend:  http://127.0.0.1:8000

