@echo off
REM File Manager Launcher for Gatekeeper System
REM Starts the file manager web server and opens the UI

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===============================================
echo Gatekeeper File Manager v1.0
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ to continue
    pause
    exit /b 1
)

echo Starting File Manager Server...
echo.

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask flask-cors
)

REM Start the server
echo Launching on http://localhost:5001
echo.
start http://localhost:5001/file_manager_ui.html
python gatekeeper_file_manager_web.py --host 0.0.0.0 --port 5001

pause
