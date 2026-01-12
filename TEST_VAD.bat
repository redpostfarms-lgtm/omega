@echo off
REM Quick test of Voice Activity Detection
cd /d "%~dp0"

echo.
echo ========================================
echo   TESTING VOICE ACTIVITY DETECTION
echo ========================================
echo.
echo This will test if I can detect when you speak.
echo.
echo Instructions:
echo   1. I'll start listening
echo   2. Say something (anything)
echo   3. Stop speaking
echo   4. I'll tell you if I detected your speech
echo.
pause

py -3.11 -c "import sounddevice as sd; import numpy as np; import time; print('Listening for 5 seconds... Speak now!'); audio = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='float32'); sd.wait(); energy = np.sqrt(np.mean(audio**2)); print(f'Average energy: {energy:.4f}'); print('SPEECH DETECTED!' if energy > 0.015 else 'No speech detected (might need to adjust threshold)')"

pause
