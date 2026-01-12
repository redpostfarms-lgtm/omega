@echo off
REM Create Desktop Shortcut for Omega
echo Creating Desktop Shortcut for Omega...
echo.

cd /d "%~dp0"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Omega.lnk'); $Shortcut.TargetPath = '%CD%\OMEGA_OPERATIONAL_STARTUP.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Launch Omega - Standalone Operational System'; $Shortcut.WindowStyle = 1; $Shortcut.Save()"

if exist "%USERPROFILE%\Desktop\Omega.lnk" (
    echo.
    echo [OK] Desktop shortcut created successfully!
    echo Location: %USERPROFILE%\Desktop\Omega.lnk
    echo.
    echo You can now double-click "Omega" on your Desktop to launch Omega.
) else (
    echo.
    echo [ERROR] Failed to create shortcut.
    echo Please create manually: Right-click OMEGA_OPERATIONAL_STARTUP.bat ^> Create shortcut ^> Move to Desktop
)

pause
