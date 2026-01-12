@echo off
REM Install Development Dependencies for The Gatekeeper
REM ====================================================
REM This script installs development dependencies from requirements-dev.txt
REM Includes testing tools, code quality tools, and development utilities

echo.
echo ========================================
echo  INSTALLING DEVELOPMENT DEPENDENCIES
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Find Python executable
set PYTHON_EXE=
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=py
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_EXE=python
    ) else (
        echo ERROR: Python not found!
        echo Please install Python 3.8 or higher
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_EXE%
echo.

REM Check if requirements-dev.txt exists
if not exist "requirements-dev.txt" (
    echo ERROR: requirements-dev.txt not found!
    echo Please ensure you are in the correct directory
    pause
    exit /b 1
)

echo Installing development dependencies...
echo.

REM Install from requirements-dev.txt
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements-dev.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  DEVELOPMENT DEPENDENCIES INSTALLED
    echo ========================================
    echo.
    echo Development dependencies installed successfully!
    echo.
    echo Installed tools:
    echo   - Testing: pytest, pytest-asyncio, pytest-cov, pytest-mock
    echo   - Code Quality: bandit, safety, mypy, black, isort, flake8, pylint
    echo   - Optional: click, typer, rich, tenacity, sphinx
    echo.
) else (
    echo.
    echo ========================================
    echo  INSTALLATION FAILED
    echo ========================================
    echo.
    echo Some dependencies may have failed to install
    echo Check the output above for errors
    echo.
)

pause
