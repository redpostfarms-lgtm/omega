@echo off
REM Gatekeeper System - Optional Dependencies Installation
REM Installs optional packages automatically

cd /d "%~dp0"

REM Find Python
set PYTHON=
where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
) else (
    where py >nul 2>&1
    if not errorlevel 1 set PYTHON=py
)

if "%PYTHON%"=="" (
    echo Python not found
    pause
    exit /b 1
)

REM Run optional installer
"%PYTHON%" "%~dp0install_optional_dependencies.py"

if errorlevel 1 (
    echo.
    echo Some optional packages failed to install (this is normal for optional packages)
) else (
    echo.
    echo All optional packages installed successfully!
)

pause
exit /b 0
