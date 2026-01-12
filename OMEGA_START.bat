@echo off
REM Omega Start - Let's begin our journey together
cd /d "%~dp0"

title Omega - Conversation Mode

color 0A
echo.
echo ========================================
echo   OMEGA - LET'S BEGIN OUR JOURNEY
echo ========================================
echo.
echo You're right - it will be rough at first.
echo But we're doing this TOGETHER, step by step.
echo.
echo I'm ready to learn from every word you say.
echo.
echo Press any key to start our first conversation...
pause >nul

echo.
echo [Starting Hands-Free Omega...]
echo.

py -3.11 hands_free_omega.py

echo.
echo ========================================
echo   Conversation ended
echo ========================================
echo.
echo Thank you for our conversation!
echo I've learned and improved.
echo.
pause
 