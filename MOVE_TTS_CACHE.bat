@echo off
REM Move TTS cache and create symlink so TTS still finds it
cd /d "%~dp0"

echo.
echo ========================================
echo   MOVING TTS CACHE TO D: DRIVE
echo ========================================
echo.
echo This will:
echo   1. Move TTS cache from C: to D:
echo   2. Create a symlink so TTS still finds it
echo   3. Free ~1.75 GB on C: drive
echo.

pause

REM Check admin rights (needed for symlinks)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] This script needs Administrator rights to create symlinks.
    echo Please run as Administrator (right-click -^> Run as administrator)
    echo.
    pause
    exit /b 1
)

set TTS_SOURCE=%LOCALAPPDATA%\tts
set TTS_TARGET=D:\RPF_BRAIN\_CACHE\tts
set TTS_BACKUP=%TTS_SOURCE%.backup

if not exist "%TTS_SOURCE%" (
    echo [INFO] TTS cache not found at %TTS_SOURCE%
    echo        Nothing to move.
    pause
    exit /b 0
)

echo [1/4] Creating target directory...
if not exist "D:\RPF_BRAIN\_CACHE" mkdir "D:\RPF_BRAIN\_CACHE"
if not exist "%TTS_TARGET%" mkdir "%TTS_TARGET%"

echo [2/4] Moving TTS cache...
echo   From: %TTS_SOURCE%
echo   To: %TTS_TARGET%
xcopy "%TTS_SOURCE%\*" "%TTS_TARGET%\" /E /I /Y /H

if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy TTS cache
    pause
    exit /b 1
)

echo [3/4] Creating backup of original...
if exist "%TTS_BACKUP%" rmdir /s /q "%TTS_BACKUP%"
move "%TTS_SOURCE%" "%TTS_BACKUP%"

echo [4/4] Creating symlink...
mklink /D "%TTS_SOURCE%" "%TTS_TARGET%"

if %errorlevel% equ 0 (
    echo.
    echo [OK] TTS cache moved successfully!
    echo.
    echo TTS will now use: %TTS_TARGET%
    echo Symlink created at: %TTS_SOURCE%
    echo.
    echo You can delete the backup after verifying TTS works:
    echo   %TTS_BACKUP%
    echo.
) else (
    echo.
    echo [ERROR] Failed to create symlink. Restoring original...
    if exist "%TTS_BACKUP%" (
        move "%TTS_BACKUP%" "%TTS_SOURCE%"
    )
    echo [INFO] Original TTS cache restored.
    echo.
    echo Alternative: Just copy (don't move) the cache
    echo   - TTS will use new location on D:
    echo   - Original cache can be deleted manually later
    echo.
)

pause
