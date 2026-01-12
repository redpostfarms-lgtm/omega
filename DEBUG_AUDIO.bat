@echo off
REM Debug audio playback issue
cd /d "%~dp0"

echo.
echo ========================================
echo   DEBUGGING AUDIO PLAYBACK
echo ========================================
echo.

echo 1. Testing TTS with simple test script...
echo    This will download the model on first run (may take time)
echo.
py -3.11 SIMPLE_TEST.py

echo.
echo 2. Checking if test_audio.wav exists...
if exist "test_audio.wav" (
    echo [OK] test_audio.wav exists
    echo.
    echo 3. Trying to play test_audio.wav...
    start test_audio.wav
    timeout /t 2 /nobreak >nul
    echo Did you hear the audio?
) else (
    echo [ERROR] test_audio.wav not created
    echo Check error messages above
)

echo.
echo 4. Checking Windows audio settings...
echo Please verify:
echo   - Your speakers/headphones are connected
echo   - Windows volume is not muted
echo   - Default playback device is set correctly

echo.
pause
