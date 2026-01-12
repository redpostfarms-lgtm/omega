@echo off
REM Update Desktop Shortcut Icon
echo Updating Desktop Shortcut Icon...
echo.

cd /d "%~dp0"

REM Check if icon file exists
if not exist "omega_icon.ico" (
    echo [ERROR] omega_icon.ico not found!
    echo.
    echo Please create the icon first:
    echo   1. Save Omega logo image to: images\omega_logo_red_gold_wreath.png
    echo   2. Run: python CREATE_OMEGA_ICON.py
    echo.
    pause
    exit /b 1
)

REM Update shortcut to use icon
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Omega.lnk'); $Shortcut.IconLocation = '%CD%\omega_icon.ico,0'; $Shortcut.Save(); Write-Host 'Shortcut icon updated successfully'"

if exist "%USERPROFILE%\Desktop\Omega.lnk" (
    echo.
    echo [SUCCESS] Desktop shortcut icon updated!
    echo Location: %USERPROFILE%\Desktop\Omega.lnk
    echo Icon: omega_icon.ico
    echo.
    echo The desktop shortcut now uses the Omega icon.
) else (
    echo.
    echo [ERROR] Desktop shortcut not found.
    echo Run CREATE_DESKTOP_SHORTCUT.bat first to create it.
)

pause
