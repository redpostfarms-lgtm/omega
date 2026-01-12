@echo off
REM Omega Operational Startup - Standalone Operational System
cd /d "%~dp0"

REM Set console to UTF-8 for Unicode support
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   OMEGA - OPERATIONAL STARTUP
echo ========================================
echo.

REM Try Python 3.11 first
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Starting Omega in operational mode...
        echo.
        py -3.11 omega_operational_startup.py
        goto :end
    )
)

REM Try default Python
python omega_operational_startup.py

:end
pause
