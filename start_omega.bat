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
REM Try py first (Windows Python Launcher), then python
where py >nul 2>&1
if %errorlevel% equ 0 (
    py omega_full_brain.py
) else (
    python omega_full_brain.py
)
if errorlevel 1 (
    echo.
    echo ERROR: Omega failed to start
    echo Check error messages above
    pause
)
