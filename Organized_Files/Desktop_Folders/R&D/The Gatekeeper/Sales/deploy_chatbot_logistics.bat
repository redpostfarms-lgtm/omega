@echo off
REM ONE-LINE DEPLOY bat for SALESBOT + LOGISTICS HUB 2026
REM Creates necessary directories and starts ChatbotLogistics.py

set SALES_DIR=D:\RPF_BRAIN\Sales
set LABELS_DIR=%SALES_DIR%\labels

echo ============================================================
echo Deploying SALESBOT + LOGISTICS HUB 2026
echo ============================================================

echo Creating directory structure...
mkdir "%SALES_DIR%" >nul 2>&1
mkdir "%LABELS_DIR%" >nul 2>&1

echo Starting ChatbotLogistics.py...
start python "%SALES_DIR%\ChatbotLogistics.py"

echo SALESBOT + LOGISTICS HUB is awake.
echo You can now use commands: "SalesBot, order 10 lb castings", etc.
echo Webhook listening on localhost:3001 (optional)
pause

