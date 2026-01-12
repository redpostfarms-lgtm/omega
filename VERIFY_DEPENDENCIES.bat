@echo off
REM Gatekeeper System - Dependency Verification Batch File
REM Checks that all Python packages are installed

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

REM Run verification
"%PYTHON%" "%~dp0verify_dependencies.py"

pause
