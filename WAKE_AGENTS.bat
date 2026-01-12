@echo off
REM Wake up Omega's learning agents
cd /d "%~dp0"

echo.
echo ========================================
echo   WAKING OMEGA LEARNING AGENTS
echo ========================================
echo.

py -3.11 omega_agent_council.py

echo.
pause
