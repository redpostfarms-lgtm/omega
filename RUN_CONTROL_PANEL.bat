@echo off
REM Run Control Panel - Batch File
echo ================================================================================
echo OMEGA CONTROL PANEL
echo ================================================================================
echo.
cd /d "%~dp0"
python START_CONTROL_PANEL_FIXED.py
if errorlevel 1 (
    echo.
    echo ERROR: Control panel failed to start
    echo Check error messages above
    pause
)
