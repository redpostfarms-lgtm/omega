@echo off
REM SETUP MORNING STARTUP - Adds to Windows Startup
REM Run this once to enable auto-startup on boot

echo ============================================================
echo ELARA - SETUP MORNING STARTUP
echo ============================================================
echo.

REM Get startup folder
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Check if shortcut already exists
if exist "%STARTUP%\Morning Startup.lnk" (
    echo [INFO] Morning startup already configured.
    echo [INFO] Removing old shortcut...
    del "%STARTUP%\Morning Startup.lnk"
)

REM Create shortcut
echo [1/3] Creating startup shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP%\Morning Startup.lnk'); $Shortcut.TargetPath = '%~dp0morning_startup.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Arguments = 'silent'; $Shortcut.Description = 'Morning Startup - Full Scan and Diagnosis'; $Shortcut.Save()"

if errorlevel 1 (
    echo [ERROR] Failed to create shortcut.
    pause
    exit /b 1
)

echo [OK] Shortcut created.
echo.

REM Create flag files for optional auto-start features
echo [2/3] Creating configuration flags...

REM Swarm auto-start flag (create if doesn't exist)
if not exist "swarm_auto_start.flag" (
    echo. > "swarm_auto_start.flag"
    echo [OK] Created swarm_auto_start.flag
)

REM Games auto-start flag (create if doesn't exist)
if not exist "games_auto_start.flag" (
    echo. > "games_auto_start.flag"
    echo [OK] Created games_auto_start.flag
)

echo.
echo [3/3] Setup complete!
echo.
echo ============================================================
echo MORNING STARTUP CONFIGURED
echo ============================================================
echo.
echo System will run full scan and diagnosis on every boot.
echo.
echo To disable: Delete shortcut from:
echo   %STARTUP%
echo.
echo Optional features (enable/disable by creating/deleting flags):
echo   - swarm_auto_start.flag  (Auto-start agent swarm)
echo   - games_auto_start.flag  (Game framework ready)
echo.
pause

