@echo off
title Savory AI Bistro - Full Stack Culinary Intelligence
echo ======================================================================
echo          SAVORY AI BISTRO - FULL STACK RESTAURANT APPLICATION
echo          Powered by FastAPI, SQLite, and Culinary AI Intelligence
echo ======================================================================
echo.
cd /d "%~dp0backend"
echo [1/3] Activating Python Virtual Environment...
call venv\Scripts\activate.bat

echo [2/3] Starting Full-Stack Server on http://127.0.0.1:8000 ...
echo.
echo   * Web Application:        http://127.0.0.1:8000
echo   * Interactive API Docs:   http://127.0.0.1:8000/docs
echo   * Redoc Documentation:    http://127.0.0.1:8000/redoc
echo.
echo [3/3] Opening Savory AI Bistro in your default browser...
start http://127.0.0.1:8000

echo.
echo ----------------------------------------------------------------------
echo Default Demo Accounts:
echo   - Customer: jane@example.com      / password123
echo   - Admin:    admin@savorybistro.com / admin123
echo ----------------------------------------------------------------------
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
