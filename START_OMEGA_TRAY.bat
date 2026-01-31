@echo off
REM ============================================================
REM   OMEGA WITH SYSTEM TRAY LAUNCHER
REM ============================================================
REM   Starts Omega with system tray icon
REM   - Minimizes to tray instead of closing
REM   - Click tray icon to restore window
REM   - Right-click tray for menu options
REM ============================================================

title Omega System Tray Launcher

echo.
echo ============================================================
echo   OMEGA WITH SYSTEM TRAY
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if pythonw exists (for silent background)
where pythonw >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Starting Omega with system tray ^(background mode^)...
    start "" pythonw OMEGA_WITH_TRAY.py
    echo.
    echo Omega is now running in the background.
    echo Look for the Omega icon in your system tray ^(bottom-right^).
    echo.
    timeout /t 5
) else (
    echo Starting Omega with system tray...
    python OMEGA_WITH_TRAY.py
)
