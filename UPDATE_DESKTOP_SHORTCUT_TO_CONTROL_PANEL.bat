@echo off
REM Update Desktop Shortcut to Launch Control Panel UI
echo Updating Desktop Shortcut to Launch Control Panel...
echo.

cd /d "%~dp0"

REM Update shortcut to point to control panel
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Omega.lnk'); $Shortcut.TargetPath = '%CD%\START_CONTROL_PANEL.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Launch Omega Control Panel - User Interface'; $Shortcut.WindowStyle = 1; $Shortcut.Save(); Write-Host 'Shortcut updated successfully'"

if exist "%USERPROFILE%\Desktop\Omega.lnk" (
    echo.
    echo [SUCCESS] Desktop shortcut updated!
    echo Location: %USERPROFILE%\Desktop\Omega.lnk
    echo Target: START_CONTROL_PANEL.bat (Control Panel UI)
    echo.
    echo The shortcut now launches the Omega Control Panel UI.
    echo Double-click "Omega" on your Desktop to launch the control panel.
) else (
    echo.
    echo [ERROR] Desktop shortcut not found.
    echo Run CREATE_DESKTOP_SHORTCUT.bat first to create it.
)

pause
