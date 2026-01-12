@echo off
REM Start Voice Improvement System
cd /d "%~dp0"

echo.
echo ========================================
echo   OMEGA VOICE IMPROVEMENT SYSTEM
echo ========================================
echo.
echo This system will:
echo   1. Find free audio resources
echo   2. Record our conversations
echo   3. Analyze voice characteristics
echo   4. Improve TTS voice quality
echo.
pause

echo.
echo [1/3] Finding free audio resources...
py -3.11 audio_resource_finder.py
pause

echo.
echo [2/3] Starting interactive conversation...
echo        (This will record our conversations)
py -3.11 interactive_omega.py
pause

echo.
echo [3/3] Analyzing voice characteristics...
py -3.11 voice_improvement_analyzer.py
pause

echo.
echo Voice improvement session complete!
pause
