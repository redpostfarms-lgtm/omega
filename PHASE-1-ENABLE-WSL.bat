@echo off
REM ========================================
REM PHASE 1: Enable WSL and Install Ubuntu
REM ========================================
REM
REM RIGHT-CLICK THIS FILE AND SELECT "RUN AS ADMINISTRATOR"
REM

echo.
echo ========================================
echo PHASE 1: ENABLE WSL
echo ========================================
echo.
echo This script will:
echo   1. Enable WSL feature on Windows
echo   2. Install WSL 2 kernel
echo   3. Install Ubuntu as default distribution
echo   4. Restart your computer when done
echo.
echo IMPORTANT: Save all your work before proceeding!
echo.
pause

echo.
echo [1/4] Enabling Windows Subsystem for Linux...
echo.
wsl --install

echo.
echo [2/4] Checking installation status...
echo.
wsl --status

echo.
echo ========================================
echo INSTALLATION COMPLETE
echo ========================================
echo.
echo Your computer needs to restart to complete the installation.
echo.
echo After restart:
echo   1. Ubuntu will launch automatically (or launch from Start Menu)
echo   2. Create a username and password when prompted
echo   3. Then proceed to Phase 2
echo.
echo Press any key to RESTART NOW (or close this window to restart later)
pause

echo.
echo [3/4] Restarting computer in 10 seconds...
echo Press Ctrl+C to cancel
echo.
shutdown /r /t 10

echo.
echo [4/4] Computer will restart in 10 seconds...
