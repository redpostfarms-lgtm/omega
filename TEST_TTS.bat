@echo off
REM Simple TTS test - navigate to correct folder first
cd /d "%~dp0"

echo.
echo ========================================
echo   TESTING TTS SYSTEM
echo ========================================
echo.
echo Current directory: %CD%
echo.

if not exist "SIMPLE_TEST.py" (
    echo ERROR: SIMPLE_TEST.py not found!
    echo Make sure you're in: D:\RPF_BRAIN\The Gatekeeper
    pause
    exit /b 1
)

echo Running TTS test...
echo This will download the model on first run (may take a few minutes)
echo.
pause

py -3.11 SIMPLE_TEST.py

echo.
pause
