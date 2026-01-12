@echo off
REM Test Omega's voice and show improvement cycle status
cd /d "%~dp0"

echo.
echo ========================================
echo   OMEGA VOICE TEST & IMPROVEMENT
echo ========================================
echo.

echo [1/3] Testing current voice quality...
py -3.11 SIMPLE_TEST.py

echo.
echo [2/3] Checking improvement cycle status...
py -3.11 improvement_cycle_manager.py

echo.
echo [3/3] Voice improvement system ready!
echo.
echo To start conversations with improvement cycles:
echo   TALK_WITH_OMEGA.bat
echo.
pause
