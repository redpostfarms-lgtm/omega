@echo off
echo Creating Desktop Shortcut for Omega...
echo.

cd /d "%~dp0"

REM Create shortcut using PowerShell
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Omega.lnk'); $Shortcut.TargetPath = '%CD%\OMEGA_OPERATIONAL_STARTUP.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Launch Omega - Standalone Operational System'; $Shortcut.WindowStyle = 1; $Shortcut.Save(); Write-Host 'Shortcut created successfully at: %USERPROFILE%\Desktop\Omega.lnk'"

if exist "%USERPROFILE%\Desktop\Omega.lnk" (
    echo.
    echo [SUCCESS] Desktop shortcut created!
    echo Location: %USERPROFILE%\Desktop\Omega.lnk
    echo.
    echo You can now double-click "Omega" on your Desktop to launch Omega.
    echo.
) else (
    echo.
    echo [ERROR] Failed to create shortcut.
    echo.
    echo Manual creation:
    echo   1. Navigate to: %CD%
    echo   2. Right-click: OMEGA_OPERATIONAL_STARTUP.bat
    echo   3. Select: Create shortcut
    echo   4. Move shortcut to Desktop
    echo   5. Rename to: Omega
    echo.
)

pause
