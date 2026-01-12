@echo off
REM ONE-LINE DEPLOY bat for SALESHUB 2026
REM Creates necessary directories and starts SalesHub.py

set SALES_DIR=D:\RPF_BRAIN\Sales

echo ============================================================
echo Deploying SALESHUB 2026 - Marketing Agent
echo ============================================================

echo Creating directory structure...
mkdir "%SALES_DIR%" >nul 2>&1

echo Starting SalesHub.py...
start python "%SALES_DIR%\SalesHub.py"

echo SALESHUB is awake.
echo You can now use commands: "SalesHub, pitch tomatoes", "SalesHub, sell beef", etc.
pause

