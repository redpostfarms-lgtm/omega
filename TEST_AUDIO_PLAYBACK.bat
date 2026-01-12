@echo off
REM Test audio playback with multiple methods
cd /d "%~dp0"

echo.
echo ========================================
echo   AUDIO PLAYBACK TEST
echo ========================================
echo.

if not exist "test_simple.wav" (
    echo ERROR: test_simple.wav not found!
    echo Generating new audio file...
    echo.
    py -3.11 SIMPLE_TEST.py
    if errorlevel 1 (
        echo Failed to generate audio
        pause
        exit /b 1
    )
)

echo [1/4] Checking audio file...
dir "test_simple.wav" | find "test_simple.wav"
echo.

echo [2/4] Method 1: Using Windows default player...
start "" "test_simple.wav"
timeout /t 3 >nul
echo   Opened with default player
echo.

echo [3/4] Method 2: Using PowerShell...
powershell -Command "Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object system.windows.media.mediaplayer; $mediaPlayer.open([uri]::new('%CD%\test_simple.wav')); $mediaPlayer.Play(); Start-Sleep -Seconds 5"
echo   Played with PowerShell MediaPlayer
echo.

echo [4/4] Method 3: Using Windows Media Player...
if exist "%ProgramFiles%\Windows Media Player\wmplayer.exe" (
    "%ProgramFiles%\Windows Media Player\wmplayer.exe" "test_simple.wav"
    echo   Opened with Windows Media Player
) else (
    echo   Windows Media Player not found
)
echo.

echo ========================================
echo   DID YOU HEAR THE AUDIO?
echo ========================================
echo.
echo If you heard audio from any method above, playback is working!
echo If not, check:
echo   1. Windows volume settings
echo   2. Audio device is connected and enabled
echo   3. Default audio device is set correctly
echo   4. Audio file is not corrupted
echo.
pause
