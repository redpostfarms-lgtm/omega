@echo off
REM Gatekeeper Admin Launcher - Windows Batch
REM Automatically requests admin privileges and launches Gatekeeper

setlocal enabledelayedexpansion

title Gatekeeper Admin System

echo.
echo ========================================
echo   GATEKEEPER ADMIN LAUNCHER
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Status: [OK] Running as ADMINISTRATOR
    echo.
) else (
    echo Status: [!] NOT RUNNING AS ADMIN
    echo.
    echo Attempting to elevate privileges...
    echo.
    
    REM Re-run script with admin privileges
    powershell -Command "Start-Process cmd -ArgumentList '/c %0' -Verb RunAs"
    exit /b
)

REM Set working directory
cd /d "%~dp0"

echo Workspace: %CD%
echo Python: 
python --version

echo.
echo ========================================
echo   INITIALIZING GATEKEEPER SYSTEM
echo ========================================
echo.

REM Create critical directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "reports" mkdir reports
if not exist "backups" mkdir backups

echo Directories: OK
echo.

REM Run admin helper
echo Running admin verification...
python gatekeeper_admin_helper.py

echo.
echo ========================================
echo   LAUNCHING GATEKEEPER
echo ========================================
echo.

REM Launch main system
python gatekeeper_integration_module.py

pause
