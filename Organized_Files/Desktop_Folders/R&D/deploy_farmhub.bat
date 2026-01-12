@echo off
REM FARMHUB 2026 – DEPLOYMENT SCRIPT
REM One-click deployment of FarmHub with Quantum Module

echo ============================================================
echo FARMHUB 2026 – FINAL MASTER SYSTEM
echo Quantum + Vision + Audio + Medical + HR + Engineering
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if FarmHub file exists
if exist "The Gatekeeper\FarmHub\FarmHub_2026_Final.py" (
    echo [OK] FarmHub_2026_Final.py found
    set FARMHUB_PATH=The Gatekeeper\FarmHub\FarmHub_2026_Final.py
) else if exist "D:\RPF_BRAIN\FarmHub\FarmHub_2026_Final.py" (
    echo [OK] FarmHub_2026_Final.py found in D:\RPF_BRAIN
    set FARMHUB_PATH=D:\RPF_BRAIN\FarmHub\FarmHub_2026_Final.py
) else (
    echo [ERROR] FarmHub_2026_Final.py not found!
    echo Please ensure the file exists.
    pause
    exit /b 1
)

echo.
echo [1/3] Testing quantum module integration...
python test_farmhub_quantum.py
if errorlevel 1 (
    echo [WARNING] Quantum module test had issues (continuing anyway)
)

echo.
echo [2/3] Starting FarmHub 2026...
echo.
echo Available commands:
echo   quantum          - Quantum optimization (resource, energy, irrigation)
echo   harriet          - HR Director Assistant
echo   bob              - Farm Engineer
echo   apothecary       - Organic pest control
echo   feedmaster       - Livestock feed and nutrition
echo   medical          - Medical triage
echo   sales            - Sales and pricing
echo   status           - System status
echo   quit             - Exit
echo.
echo ============================================================
echo.

python "%FARMHUB_PATH%"

if errorlevel 1 (
    echo.
    echo [ERROR] FarmHub encountered an error
    pause
)
