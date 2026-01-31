@echo off
REM ============================================================
REM   REMOVE OMEGA FROM WINDOWS STARTUP
REM ============================================================

title Remove Omega from Windows Startup

echo.
echo ============================================================
echo   REMOVE OMEGA FROM WINDOWS STARTUP
echo ============================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Checking for Omega startup scripts...
echo.

set "FOUND=0"

for %%f in ("%STARTUP_FOLDER%\Omega*.bat" "%STARTUP_FOLDER%\omega*.bat") do (
    if exist "%%f" (
        echo Removing: %%f
        del "%%f"
        set "FOUND=1"
    )
)

if "%FOUND%"=="1" (
    echo.
    echo ============================================================
    echo   SUCCESS!
    echo ============================================================
    echo.
    echo Omega has been removed from Windows startup.
    echo.
) else (
    echo.
    echo No Omega startup scripts found.
    echo Omega was not configured to start with Windows.
    echo.
)

pause
