@echo off
REM Direct audio playback test
cd /d "%~dp0"

echo.
echo ========================================
echo   DIRECT AUDIO PLAYBACK TEST
echo ========================================
echo.

if not exist "test_simple.wav" (
    echo ERROR: test_simple.wav not found!
    echo Run: py -3.11 SIMPLE_TEST.py first
    pause
    exit /b 1
)

echo Playing audio with multiple methods...
echo.

echo [1] Opening with default player (should appear in taskbar)...
start "" "test_simple.wav"
timeout /t 2

echo [2] Trying Windows Media Player directly...
if exist "%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" (
    "%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" "test_simple.wav"
) else if exist "%ProgramFiles%\Windows Media Player\wmplayer.exe" (
    "%ProgramFiles%\Windows Media Player\wmplayer.exe" "test_simple.wav"
)

echo.
echo ========================================
echo   TROUBLESHOOTING
echo ========================================
echo.
echo If you still don't hear audio:
echo.
echo 1. Check Windows Volume:
echo    - Click speaker icon in system tray
echo    - Make sure volume is not muted
echo    - Try increasing volume
echo.
echo 2. Check Default Audio Device:
echo    - Right-click speaker icon
echo    - Select "Open Sound settings"
echo    - Check "Choose your output device"
echo.
echo 3. Test with another audio file:
echo    - Try playing clip_0001.wav (your voice sample)
echo    - If that works, TTS audio should work too
echo.
echo 4. Check if media player opened:
echo    - Look in taskbar for media player
echo    - Check if audio file opened
echo.
pause
