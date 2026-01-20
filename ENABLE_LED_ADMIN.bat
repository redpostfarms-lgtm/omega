@echo off
echo.
echo ================================================================
echo   ENABLE WINRING0 DRIVER - Run OpenRGB as Administrator
echo ================================================================
echo.
echo This will allow OpenRGB to access I2C/SMBus for LED control
echo.

:: Stop any running OpenRGB instances
taskkill /F /IM OpenRGB.exe 2>nul

timeout /t 2 /nobreak >nul

:: Start OpenRGB as Administrator with server mode
echo Starting OpenRGB as Administrator...
powershell -Command "Start-Process 'C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe' -ArgumentList '--server' -Verb RunAs"

timeout /t 5 /nobreak >nul

echo.
echo ================================================================
echo   OpenRGB is now running with admin rights
echo ================================================================
echo.
echo Next: Check OpenRGB GUI for detected LED devices
echo If still 0 devices, you need to:
echo   1. Restart computer
echo   2. Enter BIOS (press DEL)
echo   3. Enable AURA LED / Onboard LED
echo   4. Save and restart
echo.
pause
