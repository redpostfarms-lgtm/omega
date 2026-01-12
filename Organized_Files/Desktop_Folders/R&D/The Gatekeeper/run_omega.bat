@echo off
REM Ω Omega Master Integration - Command Prompt Entry Point
REM Red Post Farms, LLC - 2026

cd /d "%~dp0"

echo ============================================================
echo Ω OMEGA MASTER INTEGRATION
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run Omega Master Integration
if "%1"=="" (
    echo Running full analysis...
    python omega_master_integration.py --full
) else if "%1"=="--omega" (
    echo Running Omega tests only...
    python omega_master_integration.py --omega
) else if "%1"=="--quantum-scrub" (
    echo Running Quantum Worldwide Scrub only...
    python omega_master_integration.py --quantum-scrub
) else if "%1"=="--status" (
    echo Showing status...
    python omega_master_integration.py --status
) else if "%1"=="--help" (
    python omega_master_integration.py --help
) else (
    echo Running with arguments: %*
    python omega_master_integration.py %*
)

if errorlevel 1 (
    echo.
    echo ERROR: Omega execution failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Omega execution complete
echo ============================================================
pause
