@echo off
echo Copying UI Screenshots to Desktop...
echo.

cd /d "%~dp0"
set "IMAGES_DIR=images"
set "DESKTOP=%USERPROFILE%\Desktop"
set "DEST=%DESKTOP%\Omega_UI_Images"

if not exist "%DEST%" mkdir "%DEST%"

copy "%IMAGES_DIR%\CONTROL PANEL FOR omega.png" "%DEST%\" >nul 2>&1 && echo Copied: CONTROL PANEL FOR omega.png
copy "%IMAGES_DIR%\omega_logo_red_gold_wreath.png" "%DEST%\" >nul 2>&1 && echo Copied: omega_logo_red_gold_wreath.png
copy "%IMAGES_DIR%\omega_logo_red_gold_wreath.ico" "%DEST%\" >nul 2>&1 && echo Copied: omega_logo_red_gold_wreath.ico
copy "%IMAGES_DIR%\OIP.jpg" "%DEST%\" >nul 2>&1 && echo Copied: OIP.jpg
copy "%IMAGES_DIR%\OIP.jfif" "%DEST%\" >nul 2>&1 && echo Copied: OIP.jfif
copy "%IMAGES_DIR%\omega symbol.jfif" "%DEST%\" >nul 2>&1 && echo Copied: omega symbol.jfif

echo.
echo Done! Images copied to: %DEST%
echo.
pause
