@echo off
REM ONE-LINE DEPLOY bat for MARKETING PLAYBOOK 2026
REM Creates necessary directories and starts Marketing_Playbook.py

set SALES_DIR=D:\RPF_BRAIN\Sales

echo ============================================================
echo Deploying MARKETING PLAYBOOK 2026
echo ============================================================

echo Creating directory structure...
mkdir "%SALES_DIR%" >nul 2>&1

echo Starting Marketing_Playbook.py...
start python "%SALES_DIR%\Marketing_Playbook.py"

echo MARKETING PLAYBOOK is awake.
echo You can now use commands: "Playbook, pitch tomatoes", "Playbook, sell beef", etc.
pause

