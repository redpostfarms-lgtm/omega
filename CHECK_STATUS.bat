@echo off
REM Omega System Status Check
cd /d "%~dp0"

echo.
echo ========================================
echo   OMEGA SYSTEM STATUS CHECK
echo ========================================
echo.

echo 1. Python Versions Available:
py --list
echo.

echo 2. Python 3.11 Check:
py -3.11 --version 2>nul
if errorlevel 1 (
    echo    [X] Python 3.11 NOT installed
    echo    [ ] You need Python 3.11 to run Omega
) else (
    echo    [OK] Python 3.11 available
)
echo.

echo 3. Critical Files:
if exist "omega_full_brain.py" (
    echo    [OK] omega_full_brain.py
) else (
    echo    [X] omega_full_brain.py MISSING
)

if exist "requirements.txt" (
    echo    [OK] requirements.txt
) else (
    echo    [X] requirements.txt MISSING
)

if exist "rate_limiter.py" (
    echo    [OK] rate_limiter.py
) else (
    echo    [X] rate_limiter.py MISSING
)

if exist "START_HERE.bat" (
    echo    [OK] START_HERE.bat
) else (
    echo    [X] START_HERE.bat MISSING
)
echo.

echo 4. Dependencies Check:
echo    (Checking with Python 3.11...)
py -3.11 -c "import TTS" 2>nul
if errorlevel 1 (
    echo    [X] TTS NOT installed
) else (
    echo    [OK] TTS installed
)

py -3.11 -c "import torch" 2>nul
if errorlevel 1 (
    echo    [X] torch NOT installed
) else (
    echo    [OK] torch installed
)

py -3.11 -c "import sounddevice" 2>nul
if errorlevel 1 (
    echo    [X] sounddevice NOT installed
) else (
    echo    [OK] sounddevice installed
)

py -3.11 -c "import speech_recognition" 2>nul
if errorlevel 1 (
    echo    [X] speech_recognition NOT installed
) else (
    echo    [OK] speech_recognition installed
)
echo.

echo 5. Current Directory:
cd
echo    %CD%
echo.

echo ========================================
echo   SUMMARY
echo ========================================
echo.
echo Python versions found: 3.14, 3.13
echo Python 3.11 required for TTS: NOT INSTALLED
echo.
echo NEXT STEPS:
echo 1. Install Python 3.11 from python.org
echo 2. Run: INSTALL_DEPS.bat
echo 3. Run: py -3.11 omega_full_brain.py
echo.
pause
