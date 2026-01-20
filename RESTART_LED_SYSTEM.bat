
@echo off
echo.
echo ================================================================
echo   ASUS AURA LED SYSTEM RESTART
echo ================================================================
echo.
echo [1] Stopping OpenRGB...
taskkill /F /IM OpenRGB.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2] Starting OpenRGB as Administrator...
cd /d "C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit"
start "" "OpenRGB.exe" --server --server-port 6742

echo [3] Waiting for initialization...
timeout /t 5 /nobreak >nul

echo [4] Testing connection...
cd /d "H:\The Gatekeeper"
python quick_led_test.py

echo.
echo ================================================================
echo   RESTART COMPLETE
echo ================================================================
echo.
echo Next steps:
echo   1. Check if LEDs are detected above
echo   2. If not, check BIOS settings (restart and press DEL)
echo   3. Enable "AURA LED" or "Onboard LED" in BIOS
echo.
pause
