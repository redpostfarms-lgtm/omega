@echo off
REM Morning Initialization Batch Script
REM Runs the Python morning initialization system
REM Place this in your Windows startup folder or run manually each morning

title Morning Initialization - The Gatekeeper

cd /d "H:\The Gatekeeper"

echo.
echo ========================================
echo   STARTING MORNING INITIALIZATION
echo ========================================
echo.

REM Run the Python initialization script
python morning_initialization.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Morning initialization complete!
    echo.
    timeout /t 3
) else (
    echo.
    echo [WARNING] Initialization completed with warnings or errors.
    echo Check morning_init_status.json for details.
    echo.
    pause
)
