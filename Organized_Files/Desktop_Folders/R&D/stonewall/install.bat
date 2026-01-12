@echo off
REM Stonewall VPN - Windows install script

echo ============================================================
echo STONEWALL VPN - Installation
echo ============================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install cryptography requests

REM Run setup
python -m stonewall.setup

echo.
echo Stonewall installed!
echo.
echo Usage:
echo   python -m stonewall.stonewall_core --init      # Start VPN
echo   python -m stonewall.stonewall_core --daemon    # Run as daemon
echo   python -m stonewall.stonewall_core --status    # Check status
echo   python -m stonewall.stonewall_core --stop      # Stop VPN
echo.
echo Your machine is ready to go dark.

