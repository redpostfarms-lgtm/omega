@echo off
REM MORNING STARTUP - Windows batch script
REM Runs full scan and diagnosis on boot, then continues

cd /d "%~dp0"

echo ============================================================
echo ELARA - MORNING STARTUP
echo ============================================================
echo.

REM Run morning startup Python script
python morning_startup.py

if errorlevel 1 (
    echo.
    echo [ERROR] Startup sequence failed.
    pause
    exit /b 1
)

echo.
echo [OK] Morning startup complete.
echo.

REM Keep window open if run manually
if not "%1"=="silent" (
    pause
)

