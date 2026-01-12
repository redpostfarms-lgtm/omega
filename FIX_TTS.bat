@echo off
REM Fix TTS issues - Check status and guide fix
cd /d "%~dp0"

echo.
echo ========================================
echo   TTS FIX UTILITY
echo ========================================
echo.

REM Check disk space
echo [1/3] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set freespace=%%a
echo   Free space: %freespace% bytes
echo.

REM Check Python version
echo [2/3] Checking Python...
py -3.11 --version 2>nul
if errorlevel 1 (
    echo   ERROR: Python 3.11 not found!
    echo   Please install Python 3.11
    pause
    exit /b 1
)
echo   Python 3.11 found
echo.

REM Check PyTorch version
echo [3/3] Checking PyTorch...
py -3.11 -c "import torch; print('PyTorch version:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo   ERROR: PyTorch not installed!
    echo   Run: py -3.11 -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo   DIAGNOSIS
echo ========================================
echo.
echo Issue: PyTorch 2.9.1 is incompatible with torchcodec
echo.
echo SOLUTION:
echo   1. Free up disk space (delete old files, empty Recycle Bin)
echo   2. Run: py -3.11 -m pip install "torch^<2.6.0" --upgrade
echo   3. Test: py -3.11 SIMPLE_TEST.py
echo.
pause
