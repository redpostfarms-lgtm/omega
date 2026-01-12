@echo off
REM Automatic Python 3.11 Installation
echo.
echo ========================================
echo   INSTALLING PYTHON 3.11 AUTOMATICALLY
echo ========================================
echo.
echo This will attempt to install Python 3.11 using winget
echo.
pause

set PYLAUNCHER_ALLOW_INSTALL=1

REM Try to install via py launcher (may prompt for store)
echo Attempting installation via py launcher...
py -3.11 --version
if errorlevel 1 (
    echo.
    echo Attempting via winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    
    if errorlevel 1 (
        echo.
        echo ========================================
        echo AUTOMATIC INSTALLATION FAILED
        echo ========================================
        echo.
        echo Please install Python 3.11 manually:
        echo   1. Go to: https://www.python.org/downloads/release/python-31111/
        echo   2. Download Windows installer (64-bit)
        echo   3. Run installer
        echo   4. CHECK "Add Python 3.11 to PATH"
        echo   5. Complete installation
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Waiting for installation to complete...
timeout /t 5 /nobreak >nul

REM Verify installation
py -3.11 --version
if errorlevel 1 (
    echo.
    echo Python 3.11 not found after installation.
    echo Please restart your command prompt and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   PYTHON 3.11 INSTALLED!
echo ========================================
echo.
echo Now installing Omega dependencies...
cd /d "%~dp0"
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error installing dependencies.
    echo Try running: INSTALL_DEPS.bat
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
