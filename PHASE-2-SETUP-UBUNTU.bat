@echo off
REM ========================================
REM PHASE 2: Setup Ubuntu (After Restart)
REM ========================================
REM
REM Run this AFTER computer restarts from Phase 1
REM

echo.
echo ========================================
echo PHASE 2: SETUP UBUNTU
echo ========================================
echo.
echo This script will:
echo   1. Launch Ubuntu terminal
echo   2. Guide you through initial setup
echo   3. Update Ubuntu packages
echo   4. Install essential development tools
echo.
pause

echo.
echo [1/3] Launching Ubuntu...
echo.
echo When Ubuntu opens, you will be asked to:
echo   - Enter new UNIX username (recommended: gate)
echo   - Enter new password
echo   - Confirm password
echo.
echo Press any key to launch Ubuntu...
pause

start ubuntu.exe

echo.
echo [2/3] After creating your Ubuntu user...
echo.
echo Copy and paste these commands into the Ubuntu terminal:
echo.
echo   sudo apt update
echo   sudo apt upgrade -y
echo   sudo apt install -y git curl wget build-essential
echo.
echo [3/3] After Ubuntu setup is complete...
echo.
echo Proceed to PHASE-3-START-DOCKER.bat
echo.
pause
