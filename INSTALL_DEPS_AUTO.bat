@echo off
REM Gatekeeper System - Automatic Dependency Installation
REM No prompts, fully automatic

cd /d "%~dp0"

REM Try to find Python
set PYTHON=
for %%P in (python py C:\Python311\python.exe C:\Python310\python.exe C:\Python39\python.exe) do (
    "%%P" --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON=%%P
        goto :found
    )
)

:found
if "%PYTHON%"=="" (
    echo Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Run installer directly
"%PYTHON%" "%~dp0install_all_dependencies.py"

if errorlevel 1 exit /b 1
exit /b 0
