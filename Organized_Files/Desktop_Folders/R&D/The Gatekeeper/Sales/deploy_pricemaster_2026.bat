@echo off
REM PRICEMASTER 2026 – DEPLOY SCRIPT
REM One command to launch market intelligence

cd /d "D:\RPF_BRAIN\Sales"
if not exist "PriceMaster.py" (
    echo [ERROR] PriceMaster.py not found!
    pause
    exit /b 1
)

echo [INFO] Starting PriceMaster 2026...
echo [INFO] Market intelligence going live...
start python "D:\RPF_BRAIN\Sales\PriceMaster.py"
echo [INFO] PriceMaster 2026 launched in new window.
timeout /t 2 /nobreak >nul

