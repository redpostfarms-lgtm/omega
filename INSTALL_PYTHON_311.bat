@echo off
REM Install Python 3.11 for Omega System
echo.
echo ========================================
echo   INSTALLING PYTHON 3.11
echo ========================================
echo.
echo This will install Python 3.11 using winget
echo.
pause

REM Try to install via winget
winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements

if errorlevel 1 (
    echo.
    echo ========================================
    echo WINGET INSTALL FAILED
    echo ========================================
    echo.
    echo Please install Python 3.11 manually:
    echo   1. Go to: https://www.python.org/downloads/release/python-31111/
    echo   2. Download Windows installer (64-bit)
    echo   3. Run installer
    echo   4. CHECK "Add Python 3.11 to PATH"
    echo   5. Install
    echo.
    echo Then run: py -3.11 --version
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   PYTHON 3.11 INSTALLED!
echo ========================================
echo.
echo Verifying installation...
py -3.11 --version

if errorlevel 1 (
    echo ERROR: Python 3.11 not found after installation
    echo You may need to restart your terminal
    pause
    exit /b 1
)

echo.
echo Now installing Omega dependencies...
cd /d "%~dp0"
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
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
pause
