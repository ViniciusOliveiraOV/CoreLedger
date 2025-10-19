@echo off
echo 🏦 CoreLedger Bank System Launcher
echo ================================
echo.

if "%1"=="" (
    echo Starting with default database...
    echo.
    .venv\Scripts\python.exe interactive_cli.py
) else (
    echo Starting with database: %1
    echo.
    .venv\Scripts\python.exe interactive_cli.py %1
)

echo.
pause