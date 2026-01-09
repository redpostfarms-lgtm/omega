@echo off
REM Omega System Startup Script for Windows
cd /d "%~dp0"
echo.
echo ========================================
echo   OMEGA SYSTEM - STARTING
echo ========================================
echo.
echo Starting Omega Full Brain (Voice + Emotion)...
echo Press Ctrl+C to stop
echo.
python omega_full_brain.py
if errorlevel 1 (
    echo.
    echo ERROR: Omega failed to start
    echo Check error messages above
    pause
)
