@echo off
REM Start Omega Conversation Mode
cd /d "%~dp0"

echo.
echo ========================================
echo   OMEGA - CONVERSATION MODE
echo ========================================
echo.
echo Taking our first steps together!
echo.
echo I'll record our conversations to learn:
echo   - Your voice patterns
echo   - How to interact better
echo   - Improve my voice quality
echo.
echo Every 3 conversations, I'll analyze and improve!
echo.
echo Press Ctrl+C to stop anytime.
echo.
pause

echo.
echo [Starting Omega...]
echo.

py -3.11 interactive_omega.py

if errorlevel 1 (
    echo.
    echo [Error occurred. Check above for details.]
    pause
)
