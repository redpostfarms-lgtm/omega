@echo off
REM ================================================================
REM OMEGA - LibreHardwareMonitor Installation Script
REM ================================================================
REM This script will:
REM 1. Download LibreHardwareMonitor from GitHub
REM 2. Install Python.NET (pythonnet)
REM 3. Verify installation
REM ================================================================

echo.
echo ================================================================
echo OMEGA HARDWARE MONITORING - INSTALLATION
echo ================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as administrator!
    echo Some features may require admin rights later.
    echo.
)

REM Set installation directory
set "INSTALL_DIR=C:\Program Files\LibreHardwareMonitor"
set "DOWNLOAD_DIR=%TEMP%\LibreHardwareMonitor"

echo [1/5] Checking existing installation...
if exist "%INSTALL_DIR%\LibreHardwareMonitorLib.dll" (
    echo [OK] LibreHardwareMonitor already installed at %INSTALL_DIR%
    goto :skip_download
)

echo [NOT FOUND] LibreHardwareMonitor not installed
echo.

echo [2/5] Downloading LibreHardwareMonitor from GitHub...
echo Repository: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
echo.

REM Create download directory
if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%"

REM Download latest release using PowerShell
powershell -Command "try { $releases = Invoke-RestMethod -Uri 'https://api.github.com/repos/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest'; $asset = $releases.assets | Where-Object { $_.name -like '*net472*.zip' } | Select-Object -First 1; if ($asset) { Write-Host 'Downloading:' $asset.name; Invoke-WebRequest -Uri $asset.browser_download_url -OutFile '%DOWNLOAD_DIR%\LibreHardwareMonitor.zip'; Write-Host 'Download complete!'; exit 0 } else { Write-Host 'No suitable release found'; exit 1 } } catch { Write-Host 'Error downloading:' $_.Exception.Message; exit 1 }"

if %errorLevel% neq 0 (
    echo [ERROR] Download failed!
    echo Please download manually from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases
    pause
    exit /b 1
)

echo [3/5] Extracting LibreHardwareMonitor...
powershell -Command "Expand-Archive -Path '%DOWNLOAD_DIR%\LibreHardwareMonitor.zip' -DestinationPath '%DOWNLOAD_DIR%\extracted' -Force"

if %errorLevel% neq 0 (
    echo [ERROR] Extraction failed!
    pause
    exit /b 1
)

echo [4/5] Installing to %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
xcopy "%DOWNLOAD_DIR%\extracted\*" "%INSTALL_DIR%\" /E /I /Y >nul

if %errorLevel% neq 0 (
    echo [ERROR] Installation failed!
    echo You may need to run this script as Administrator
    pause
    exit /b 1
)

echo [OK] LibreHardwareMonitor installed successfully!

REM Cleanup
echo Cleaning up temporary files...
rd /s /q "%DOWNLOAD_DIR%" 2>nul

:skip_download

echo.
echo [5/5] Installing Python dependencies...
echo.

REM Activate virtual environment if exists
if exist ".venv311\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv311\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Installing pythonnet (Python.NET)...
python -m pip install --upgrade pip
python -m pip install pythonnet

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install pythonnet!
    echo Try manually: pip install pythonnet
    pause
    exit /b 1
)

echo [OK] Python dependencies installed!
echo.

echo ================================================================
echo VERIFYING INSTALLATION
echo ================================================================
echo.

REM Verify LibreHardwareMonitor DLL exists
if exist "%INSTALL_DIR%\LibreHardwareMonitorLib.dll" (
    echo [OK] LibreHardwareMonitorLib.dll found
) else (
    echo [ERROR] LibreHardwareMonitorLib.dll NOT FOUND!
    echo Expected location: %INSTALL_DIR%\LibreHardwareMonitorLib.dll
)

REM Test Python.NET import
python -c "import clr; print('[OK] Python.NET (clr) imports successfully')" 2>nul
if %errorLevel% neq 0 (
    echo [ERROR] Python.NET import failed!
)

REM Test hardware monitor
echo.
echo Testing Omega Hardware Monitor...
python omega_hardware_monitor_enhanced.py >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Hardware monitor test passed!
) else (
    echo [WARNING] Hardware monitor test had issues
    echo This may be normal if LibreHardwareMonitor isn't running
)

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo Next steps:
echo 1. Run LibreHardwareMonitor as Administrator:
echo    "%INSTALL_DIR%\LibreHardwareMonitor.exe"
echo.
echo 2. Keep it running in the background
echo.
echo 3. Restart your Omega web server:
echo    python omega_control_panel_web.py --port 5000
echo.
echo 4. Access dashboard: http://localhost:5000
echo.
echo Note: Some motherboard sensors require running as Administrator
echo.
pause
