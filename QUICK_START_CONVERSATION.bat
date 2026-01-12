@echo off
REM Quick start conversation with Omega - includes improvement cycles
cd /d "%~dp0"

echo.
echo ========================================
echo   TALK WITH OMEGA - IMPROVEMENT MODE
echo ========================================
echo.
echo Omega will:
echo   • Record our conversations
echo   • Improve voice every 3 cycles
echo   • Learn to interact better
echo   • Analyze voice patterns
echo.
echo Press Ctrl+C to stop
echo.
pause

py -3.11 interactive_omega.py
