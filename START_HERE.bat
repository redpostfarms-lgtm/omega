@echo off
REM Navigate to the correct directory first
cd /d "D:\RPF_BRAIN\The Gatekeeper"

echo.
echo ========================================
echo   OMEGA SYSTEM - STARTING
echo ========================================
echo.
echo Current directory: %CD%
echo.

REM Check if we're in the right place
if not exist "omega_full_brain.py" (
    echo ERROR: omega_full_brain.py not found!
    echo Make sure you're in: D:\RPF_BRAIN\The Gatekeeper
    pause
    exit /b 1
)

echo ✓ Found Omega files
echo.
echo Loading models (this may take a minute on first run)...
echo Press Ctrl+C to stop at any time
echo.
echo ========================================
echo.

REM Try Python 3.11 first (required for TTS)
REM Omega is now operational - use operational startup
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Using: py -3.11 (Python 3.11 required for TTS)
        echo Starting Omega in operational mode...
        echo.
        py -3.11 omega_operational_startup.py
        goto :end
    )
)

REM Try default Python (may not work due to version)
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Python 3.11 not found!
    echo TTS requires Python 3.9-3.11
    echo.
    echo Please install Python 3.11 first:
    echo   1. Go to: https://www.python.org/downloads/release/python-31111/
    echo   2. Download Windows installer (64-bit)
    echo   3. Install with "Add to PATH" checked
    echo   4. Then run: py -3.11 omega_operational_startup.py
    echo.
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Using: python
    echo Starting Omega in operational mode...
    echo.
    python omega_operational_startup.py
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo Using: python3
    echo Starting Omega in operational mode...
    echo.
    python3 omega_operational_startup.py
    goto :end
)

echo.
echo ========================================
echo ERROR: Python not found!
echo ========================================
echo.
echo Python is not in your PATH or not installed.
echo.
echo Try one of these:
echo   1. Install Python from python.org
    echo   2. Use: py omega_operational_startup.py
echo   3. Use full path to Python.exe
echo.
pause
exit /b 1

:end

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Omega failed to start
    echo ========================================
    echo.
    echo Common issues:
    echo   1. Missing dependencies: pip install -r requirements.txt
    echo   2. Python not in PATH
    echo   3. Missing microphone
    echo.
    pause
    exit /b 1
)

pause
