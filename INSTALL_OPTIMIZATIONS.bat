@echo off
REM Install optimization dependencies
cd /d "%~dp0"

echo.
echo ========================================
echo   INSTALLING OPTIMIZATION DEPENDENCIES
echo ========================================
echo.

echo [Installing faster-whisper for offline speech recognition...]
py -3.11 -m pip install faster-whisper

echo.
echo [Installing aiofiles for async file operations...]
py -3.11 -m pip install aiofiles

echo.
echo ========================================
echo   OPTIMIZATION DEPENDENCIES INSTALLED
echo ========================================
echo.
echo Ready to use optimized Omega!
echo Run: py -3.11 hands_free_omega_optimized.py
echo.
pause
