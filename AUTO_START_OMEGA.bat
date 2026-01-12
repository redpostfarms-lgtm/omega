@echo off
REM Auto-start Omega - No clicks needed, just runs automatically
cd /d "%~dp0"

title Omega - Hands-Free Conversation (Auto-Started)

color 0B
cls

echo.
echo ========================================
echo   OMEGA - AUTO-STARTING
echo ========================================
echo.
echo Starting hands-free conversation...
echo Omega will greet everyone and start asking questions automatically.
echo No clicks needed - just speak when ready!
echo.
echo [Press Ctrl+C to stop at any time]
echo.
timeout /t 2 /nobreak >nul

py -3.11 hands_free_omega.py

pause
