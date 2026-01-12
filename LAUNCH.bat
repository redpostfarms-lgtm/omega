@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   LAUNCHING OMEGA SYSTEM
echo ========================================
echo.
echo Loading models (this may take a minute on first run)...
echo.
REM Try py first (Windows Python Launcher), then python
where py >nul 2>&1
if %errorlevel% equ 0 (
    py omega_full_brain.py
) else (
    python omega_full_brain.py
)
pause
