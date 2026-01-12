@echo off
REM Quick start - Talk with Omega and record conversations
cd /d "%~dp0"

echo.
echo ========================================
echo   TALK WITH OMEGA - CONVERSATION MODE
echo ========================================
echo.
echo I'll record our conversation to improve my voice!
echo Press Ctrl+C to stop.
echo.
pause

py -3.11 interactive_omega.py
