@echo off
REM Install Omega dependencies
cd /d "%~dp0"

echo.
echo ========================================
echo   INSTALLING OMEGA DEPENDENCIES
echo ========================================
echo.
echo This will install all required packages.
echo This may take 5-10 minutes (especially PyTorch ~2GB).
echo.
pause

echo.
echo Installing dependencies from requirements.txt...
echo.

REM Use py instead of python
py -m pip install --upgrade pip

py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Installation failed
    echo ========================================
    echo.
    echo Try running manually:
    echo   py -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo You can now run: START_HERE.bat
echo.
pause
