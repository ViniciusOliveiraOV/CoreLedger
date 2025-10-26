@echo off
echo.
echo ============================================
echo   CoreLedger Real-Time Dashboard Setup
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Starting API Server...
start "CoreLedger API" cmd /k ".venv\Scripts\python.exe start_api.py"

echo [2/4] Waiting for API to initialize...
timeout /t 5 /nobreak >nul

echo [3/4] Installing React dependencies...
cd frontend
call npm install

echo [4/4] Starting React frontend...
start "CoreLedger Dashboard" cmd /k "npm start"

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo API Server: http://localhost:8000
echo Dashboard: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul