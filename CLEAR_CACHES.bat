@echo off
REM Clear caches to free up space (safer - just deletes)
cd /d "%~dp0"

echo.
echo ========================================
echo   CLEARING CACHES TO FREE UP SPACE
echo ========================================
echo.
echo WARNING: This will DELETE cache files.
echo They will be re-downloaded/regenerated when needed.
echo.
echo Caches to clear:
echo   1. Pip cache: 0.85 GB (safe to delete)
echo   2. Python __pycache__: ~small (safe to delete)
echo.
echo Total to free: ~1 GB
echo.
set /p CONFIRM="Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" exit /b

echo.
echo [1/2] Clearing pip cache...
py -3.11 -m pip cache purge
if %errorlevel% equ 0 (
    echo   [OK] Pip cache cleared
) else (
    echo   [WARNING] Pip cache clear failed or already empty
)

echo.
echo [2/2] Clearing Python __pycache__ directories...
cd /d "%~dp0"
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo   Deleting: %%d
        rmdir /s /q "%%d" 2>nul
    )
)

REM Also clear in user Python packages
for /d /r "%LOCALAPPDATA%\Programs\Python\Python311" %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
    )
)

echo.
echo ========================================
echo   DONE
echo ========================================
echo.
echo Next steps:
echo   1. Check free space on C: drive
echo   2. If enough space, downgrade PyTorch: py -3.11 -m pip install "torch^<2.6.0" --upgrade
echo.
pause
