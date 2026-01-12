@echo off
REM Install Omega Dependencies using Python 3.11
cd /d "%~dp0"

echo.
echo ========================================
echo   INSTALLING OMEGA DEPENDENCIES
echo ========================================
echo.
echo Current directory: %CD%
echo.

REM Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ========================================
    echo ERROR: Python 3.11 not found!
    echo ========================================
    echo.
    echo Please install Python 3.11 first:
    echo   1. Go to: https://www.python.org/downloads/release/python-31111/
    echo   2. Download Windows installer (64-bit)
    echo   3. Install with "Add to PATH" checked
    echo   4. Restart this command prompt
    echo   5. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✓ Python 3.11 found
py -3.11 --version
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo ✓ Found requirements.txt
echo.
echo Installing dependencies...
echo (This may take 5-10 minutes, downloading ~2GB)
echo.

REM Upgrade pip first
echo [1/2] Upgrading pip...
py -3.11 -m pip install --upgrade pip

REM Install dependencies
echo.
echo [2/2] Installing Omega dependencies...
py -3.11 -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Installation failed
    echo ========================================
    echo.
    echo Try running manually:
    echo   py -3.11 -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo You can now run Omega with:
echo   py -3.11 omega_full_brain.py
echo.
echo Or double-click: START_HERE.bat
echo.
pause
