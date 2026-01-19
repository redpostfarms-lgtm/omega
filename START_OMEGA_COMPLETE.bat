@echo off
REM ========================================
REM OMEGA SYSTEM - COMPLETE LAUNCHER
REM ========================================

echo.
echo ========================================
echo    OMEGA SYSTEM - STARTING UP
echo ========================================
echo.

REM Check if web server is already running
echo [1/4] Checking for existing Omega server...
netstat -ano | findstr ":5000" >nul
if %errorlevel% equ 0 (
    echo [!] Omega server already running on port 5000
) else (
    echo [+] Starting Omega Control Panel...
    start "Omega Control Panel" /MIN .\.venv311\Scripts\python.exe omega_control_panel_web.py --port 5000
    timeout /t 3 /nobreak >nul
)

REM Open web interface
echo [2/4] Opening Omega Control Panel...
start http://localhost:5000

REM Test voice system
echo [3/4] Testing Omega voice system...
if exist speak_omega_voice.py (
    echo [+] Voice system ready
) else (
    echo [!] Voice system not found
)

REM Display status
echo [4/4] System Status:
echo.
echo   Web Interface: http://localhost:5000
echo   Mobile View:   http://localhost:5000/mobile
echo   Voice Test:    python speak_omega_voice.py
echo.
echo ========================================
echo    OMEGA SYSTEM - ONLINE
echo ========================================
echo.

pause
