@echo off
REM Comprehensive script to free up space and move files
cd /d "%~dp0"

echo.
echo ========================================
echo   FREE UP SPACE UTILITY
echo ========================================
echo.

REM Check disk space
echo Checking disk space...
for /f "tokens=3" %%a in ('dir C:\ /-c ^| find "bytes free"') do set CFREE=%%a
for /f "tokens=3" %%a in ('dir D:\ /-c ^| find "bytes free"') do set DFREE=%%a

echo   C: drive free: %CFREE% bytes (~%CFREE:~0,-9% GB)
echo   D: drive free: %DFREE% bytes (~%DFREE:~0,-9% GB)
echo.

echo Options:
echo   1. Clear caches (pip, __pycache__) - frees ~1 GB
echo   2. Move TTS cache to D: drive - frees ~1.75 GB
echo   3. Both - frees ~2.75 GB total
echo   4. Exit
echo.
set /p CHOICE="Choose option (1-4): "

if "%CHOICE%"=="1" (
    call CLEAR_CACHES.bat
) else if "%CHOICE%"=="2" (
    call MOVE_CACHES.bat
) else if "%CHOICE%"=="3" (
    call CLEAR_CACHES.bat
    echo.
    echo Press any key to continue with moving caches...
    pause >nul
    call MOVE_CACHES.bat
) else (
    exit /b
)

echo.
echo ========================================
echo   CHECKING NEW DISK SPACE
echo ========================================
echo.
for /f "tokens=3" %%a in ('dir C:\ /-c ^| find "bytes free"') do set NEWCFREE=%%a
echo   C: drive now has: %NEWCFREE% bytes free
echo.

if %NEWCFREE% gtr 2000000000 (
    echo [OK] You now have enough space!
    echo.
    echo Next: Downgrade PyTorch
    echo   py -3.11 -m pip install "torch^<2.6.0" --upgrade
    echo.
) else (
    echo [WARNING] Still low on space. Try:
    echo   1. Empty Recycle Bin
    echo   2. Delete temp files: del /q /s %TEMP%\*.*
    echo   3. Uninstall unused programs
    echo.
)

pause
