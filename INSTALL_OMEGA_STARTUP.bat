@echo off
REM ============================================================
REM   INSTALL OMEGA TO WINDOWS STARTUP
REM ============================================================
REM   This script adds Omega to Windows startup folder
REM   so it starts automatically when you log in.
REM ============================================================

title Install Omega to Windows Startup

echo.
echo ============================================================
echo   INSTALL OMEGA TO WINDOWS STARTUP
echo ============================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "OMEGA_DIR=%~dp0"
set "STARTUP_SCRIPT=%STARTUP_FOLDER%\Omega_Startup.bat"

echo Current Omega directory: %OMEGA_DIR%
echo Startup folder: %STARTUP_FOLDER%
echo.

echo Creating startup script...

REM Create the startup batch file
(
echo @echo off
echo REM Omega System Tray - Auto-start on Windows login
echo cd /d "%OMEGA_DIR%"
echo start "" /B pythonw OMEGA_WITH_TRAY.py
) > "%STARTUP_SCRIPT%"

if exist "%STARTUP_SCRIPT%" (
    echo.
    echo ============================================================
    echo   SUCCESS!
    echo ============================================================
    echo.
    echo Omega has been added to Windows startup.
    echo.
    echo Created: %STARTUP_SCRIPT%
    echo.
    echo What happens now:
    echo   - When you log in to Windows, Omega will start automatically
    echo   - Look for the Omega icon in your system tray (bottom-right)
    echo   - Click the icon to show the control panel
    echo   - Right-click for more options
    echo.
    echo To remove from startup:
    echo   - Run REMOVE_OMEGA_STARTUP.bat
    echo   - Or delete: %STARTUP_SCRIPT%
    echo.
) else (
    echo.
    echo ============================================================
    echo   ERROR!
    echo ============================================================
    echo.
    echo Failed to create startup script.
    echo Please run this batch file as Administrator.
    echo.
)

pause
