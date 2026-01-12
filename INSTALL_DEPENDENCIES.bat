@echo off
REM Gatekeeper System - Dependency Installation Batch File
REM Installs all required dependencies automatically

echo.
echo ================================================================================
echo GATEKEEPER SYSTEM - DEPENDENCY INSTALLATION
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Find Python executable (try multiple methods)
set PYTHON_EXE=
where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_EXE=py
    ) else (
        REM Try common Python installation paths
        if exist "C:\Python311\python.exe" set PYTHON_EXE=C:\Python311\python.exe
        if exist "C:\Python310\python.exe" set PYTHON_EXE=C:\Python310\python.exe
        if exist "C:\Python39\python.exe" set PYTHON_EXE=C:\Python39\python.exe
        if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
        if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    )
)

REM Check if Python was found
if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found: %PYTHON_EXE%
"%PYTHON_EXE%" --version

echo.
echo [INFO] Starting dependency installation...
echo.

REM Run the Python installer using explicit executable path
"%PYTHON_EXE%" "%~dp0install_all_dependencies.py"

REM Check exit code
if errorlevel 1 (
    echo.
    echo [WARNING] Some dependencies failed to install
    echo Please check the output above for errors
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] Dependency installation completed successfully!
    echo.
)

pause
exit /b 0
