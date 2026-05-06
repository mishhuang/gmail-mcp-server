@echo off
echo Starting Gmail API Server...
start "Gmail API Server" python api_server.py
echo.
echo Starting Gmail Frontend...
cd frontend
start "Gmail Frontend" npm run dev
cd ..
echo.
echo Services started:
echo   API:      http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
echo Press any key to stop both services...
pause >nul
taskkill /FI "WINDOWTITLE eq Gmail API Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Gmail Frontend*" /F >nul 2>&1
