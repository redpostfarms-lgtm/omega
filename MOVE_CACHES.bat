@echo off
REM Move large caches from C: to D: to free up space
cd /d "%~dp0"

echo.
echo ========================================
echo   MOVING CACHES TO FREE UP SPACE
echo ========================================
echo.
echo Current disk space:
echo   C: drive - 1.18 GB free (ALMOST FULL!)
echo   D: drive - 572 GB free (plenty of space)
echo   G: drive - 888 GB free (tons of space)
echo.
echo Found caches to move:
echo   1. TTS model cache: 1.75 GB on C:
echo   2. Pip cache: 0.85 GB on C:
echo.
echo Total to free: ~2.6 GB
echo.

pause

REM Set target drive (use D: since project is there)
set TARGET_DRIVE=D:
set TARGET_BASE=%TARGET_DRIVE%\RPF_BRAIN\_CACHE

echo [1/3] Creating target directory...
if not exist "%TARGET_BASE%" mkdir "%TARGET_BASE%"

REM Move TTS cache
echo.
echo [2/3] Moving TTS cache (1.75 GB)...
set TTS_SOURCE=%LOCALAPPDATA%\tts
set TTS_TARGET=%TARGET_BASE%\tts

if exist "%TTS_SOURCE%" (
    echo   From: %TTS_SOURCE%
    echo   To: %TTS_TARGET%
    if not exist "%TTS_TARGET%" mkdir "%TTS_TARGET%"
    
    REM Copy (safer than move)
    xcopy "%TTS_SOURCE%\*" "%TTS_TARGET%\" /E /I /Y
    
    if %errorlevel% equ 0 (
        echo   [OK] Copied TTS cache
        echo   [INFO] Original cache still at: %TTS_SOURCE%
        echo   [INFO] You can delete it after verifying TTS works
    ) else (
        echo   [ERROR] Failed to copy TTS cache
    )
) else (
    echo   [SKIP] TTS cache not found
)

REM Move pip cache (or just clear it - it's safe to delete)
echo.
echo [3/3] Handling pip cache (0.85 GB)...
set PIP_CACHE=%LOCALAPPDATA%\pip\Cache

if exist "%PIP_CACHE%" (
    echo   Pip cache found at: %PIP_CACHE%
    echo   [INFO] Pip cache is safe to delete - packages will re-download if needed
    echo   [INFO] To clear it: py -3.11 -m pip cache purge
    echo.
    set /p CLEAR_PIP="Clear pip cache now? (Y/N): "
    if /i "%CLEAR_PIP%"=="Y" (
        py -3.11 -m pip cache purge
        echo   [OK] Pip cache cleared
    )
) else (
    echo   [SKIP] Pip cache not found
)

echo.
echo ========================================
echo   DONE
echo ========================================
echo.
echo Next steps:
echo   1. Test if TTS still works (it should use the new location)
echo   2. If working, delete old cache: %TTS_SOURCE%
echo   3. Free space on C: should now be ~3.8 GB
echo   4. Downgrade PyTorch: py -3.11 -m pip install "torch^<2.6.0" --upgrade
echo.
pause
