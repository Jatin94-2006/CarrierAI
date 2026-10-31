@echo off
title CareerAI Backend
cd /d "%~dp0backend"
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

