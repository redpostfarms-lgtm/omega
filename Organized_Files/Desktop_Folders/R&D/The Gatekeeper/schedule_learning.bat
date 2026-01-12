@echo off
REM Schedule Weekly Self-Learning
REM Runs every Monday at 3 AM

echo ============================================================
echo Scheduling Weekly Self-Learning
echo ============================================================

REM Create scheduled task for Monday 3:00 AM
schtasks /Create /TN "GatekeeperSelfLearning" /TR "python \"D:\RPF_BRAIN\The Gatekeeper\self_learn.py\" --weekly" /SC WEEKLY /D MON /ST 03:00 /F

if errorlevel 1 (
    echo Task creation failed. Run as administrator.
    pause
    exit /b 1
)

echo.
echo ✅ Weekly self-learning scheduled
echo Task name: GatekeeperSelfLearning
echo Schedule: Every Monday at 3:00 AM
echo.
echo To test: schtasks /Run /TN "GatekeeperSelfLearning"
echo To delete: schtasks /Delete /TN "GatekeeperSelfLearning" /F
echo.
echo Note: Requires Ollama installed and llama3 model downloaded
echo Install: https://ollama.ai/
pause

