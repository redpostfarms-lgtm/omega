@echo off
REM ============================================================
REM  Start Omega Web IDE
REM  Browser-based development environment
REM ============================================================

echo.
echo ============================================================
echo   OMEGA WEB IDE LAUNCHER
echo ============================================================
echo.

REM Check Python
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 not found
    echo.
    pause
    exit /b 1
)

REM Check Flask
py -3.11 -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask not installed
    echo Install: py -3.11 -m pip install flask waitress
    echo.
    pause
    exit /b 1
)

echo  Starting Web IDE...
echo  Press Ctrl+C to stop
echo.
echo  Opening http://localhost:5000 in your browser...
echo.
echo ============================================================
echo.

REM Start IDE (will open browser automatically)
start http://localhost:5000
py -3.11 omega_web_ide.py

pause
