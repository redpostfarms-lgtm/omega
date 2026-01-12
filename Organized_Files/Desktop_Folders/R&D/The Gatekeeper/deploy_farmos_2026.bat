@echo off
REM FARMOS 2026 – DEPLOY SCRIPT
REM One command to wake the entire hive

cd /d "D:\RPF_BRAIN\The Gatekeeper"
if not exist "FarmOS_2026.py" (
    echo [ERROR] FarmOS_2026.py not found!
    pause
    exit /b 1
)

echo [INFO] Starting FarmOS 2026...
echo [INFO] Waking the entire hive...
start python "D:\RPF_BRAIN\The Gatekeeper\FarmOS_2026.py"
echo [INFO] FarmOS 2026 launched in new window.
timeout /t 2 /nobreak >nul

