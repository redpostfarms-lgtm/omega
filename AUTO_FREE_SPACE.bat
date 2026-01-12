@echo off
REM Automated script to free up space - clears safe caches automatically
cd /d "%~dp0"

echo.
echo ========================================
echo   AUTO FREE SPACE SCRIPT
echo ========================================
echo.
echo This will automatically clear safe caches to free up space.
echo No user interaction needed.
echo.

REM Clear pip cache (safe to delete)
echo [1/2] Clearing pip cache...
py -3.11 -m pip cache purge >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Pip cache cleared (~0.85 GB freed)
) else (
    echo   [INFO] Pip cache already cleared or not found
)

REM Clear Python __pycache__ (safe to delete)
echo.
echo [2/2] Clearing Python __pycache__ directories...
set CLEARED=0
cd /d "%~dp0"
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
        set /a CLEARED+=1
    )
)

REM Also clear in user Python packages
for /d /r "%LOCALAPPDATA%\Programs\Python\Python311\Lib\site-packages" %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
        set /a CLEARED+=1
    )
)

if %CLEARED% gtr 0 (
    echo   [OK] Cleared %CLEARED% __pycache__ directories
) else (
    echo   [INFO] No __pycache__ directories found
)

echo.
echo ========================================
echo   AUTOMATIC CLEANUP COMPLETE
echo ========================================
echo.
echo Next: Check if you have enough space for PyTorch downgrade
echo.
echo If you need more space, manually move TTS cache:
echo   1. Run as Admin: MOVE_TTS_CACHE.bat
echo   2. OR copy: xcopy "%LOCALAPPDATA%\tts" "D:\RPF_BRAIN\_CACHE\tts" /E /I
echo.
echo Then downgrade PyTorch:
echo   py -3.11 -m pip install "torch^<2.6.0" --upgrade
echo.
pause
