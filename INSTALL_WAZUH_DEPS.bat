@echo off
REM Wazuh Integration Dependencies Installer
REM ==========================================
REM Installs Python dependencies for Wazuh integration features

echo ============================================================
echo Wazuh Integration Dependencies Installer
echo ============================================================
echo.

REM Find Python executable
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=py
    echo [OK] Python launcher found
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_EXE=python
        echo [OK] Python found
    ) else (
        echo [ERROR] Python not found. Please install Python 3.7+
        pause
        exit /b 1
    )
)

echo.
echo Using: %PYTHON_EXE%
echo.

REM Run installation script
"%PYTHON_EXE%" "%~dp0install_wazuh_dependencies.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation Complete
echo ============================================================
pause
