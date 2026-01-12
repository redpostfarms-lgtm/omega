@echo off
REM QUANTUM SALESBOT 2026 – DEPLOY SCRIPT
REM One command to rule them all

cd /d "D:\RPF_BRAIN\Sales"
if not exist "QuantumSalesBot.py" (
    echo [ERROR] QuantumSalesBot.py not found!
    pause
    exit /b 1
)

echo [INFO] Starting Quantum SalesBot 2026...
start python "D:\RPF_BRAIN\Sales\QuantumSalesBot.py"
echo [INFO] Quantum SalesBot launched in new window.
timeout /t 2 /nobreak >nul

