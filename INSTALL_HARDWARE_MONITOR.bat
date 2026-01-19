@echo off
REM Omega Enhanced Hardware Monitoring - Installation Script
REM Installs Python.NET for LibreHardwareMonitor integration

echo ========================================
echo OMEGA HARDWARE MONITOR SETUP
echo ========================================
echo.
echo This will install Python.NET (pythonnet) for
echo LibreHardwareMonitor integration.
echo.
echo Requirements:
echo   - LibreHardwareMonitor installed at:
echo     C:\Program Files\LibreHardwareMonitor
echo.
echo   - LibreHardwareMonitor running as Administrator
echo.
pause

cd /d "%~dp0"

echo.
echo [1/3] Activating Python virtual environment...
call .venv311\Scripts\activate.bat

echo.
echo [2/3] Installing Python.NET...
pip install pythonnet

echo.
echo [3/3] Testing enhanced monitor...
python omega_hardware_monitor_enhanced.py

echo.
echo ========================================
echo INSTALLATION COMPLETE
echo ========================================
echo.
echo If you see "LibreHardwareMonitor: Active" above,
echo the integration is working!
echo.
echo If not, make sure:
echo   1. LibreHardwareMonitor is running
echo   2. It's running as Administrator
echo   3. It's installed at C:\Program Files\LibreHardwareMonitor
echo.
pause
