@echo off
REM Test installation and run Omega
cd /d "%~dp0"

echo.
echo ========================================
echo   TESTING INSTALLATION
echo ========================================
echo.

echo Testing TTS...
py -3.11 -c "import TTS; print('✓ TTS works!')"
if errorlevel 1 (
    echo ✗ TTS not working
    pause
    exit /b 1
)

echo Testing speechbrain...
py -3.11 -c "import speechbrain; print('✓ speechbrain works!')"
if errorlevel 1 (
    echo ✗ speechbrain not working
    pause
    exit /b 1
)

echo Testing rate_limiter...
py -3.11 -c "from rate_limiter import GOOGLE_SPEECH_LIMITER; print('✓ rate_limiter works!')"
if errorlevel 1 (
    echo ✗ rate_limiter not working
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ALL TESTS PASSED!
echo ========================================
echo.
echo Starting Omega...
echo.
pause

py -3.11 omega_full_brain.py

pause
