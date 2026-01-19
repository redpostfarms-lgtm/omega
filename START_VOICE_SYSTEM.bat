@echo off
REM Omega Voice System Launcher
REM Quick access to voice controls

cd /d "H:\The Gatekeeper"

:menu
cls
echo.
echo ===============================================
echo   OMEGA VOICE SYSTEM
echo ===============================================
echo.
echo   1. Interactive Mode
echo   2. Play Kit Voice
echo   3. Play Omega Warm Voice
echo   4. Demo All Voices
echo   5. System Status
echo   6. Exit
echo.
echo ===============================================
echo.

choice /c 123456 /n /m "Select option (1-6): "

if errorlevel 6 goto :end
if errorlevel 5 goto :status
if errorlevel 4 goto :demo
if errorlevel 3 goto :warm
if errorlevel 2 goto :kit
if errorlevel 1 goto :interactive

:interactive
python omega_voice_integration.py interactive
goto :menu

:kit
python omega_voice_integration.py play kit
pause
goto :menu

:warm
python omega_voice_integration.py play warm
pause
goto :menu

:demo
python omega_voice_integration.py demo
pause
goto :menu

:status
python omega_voice_integration.py status
pause
goto :menu

:end
echo.
echo Goodbye!
echo.
timeout /t 2 >nul
