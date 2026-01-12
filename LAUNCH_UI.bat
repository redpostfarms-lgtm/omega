@echo off
REM Launch Omega Control Panel Web Interface
cd /d "H:\The Gatekeeper"
echo ========================================
echo   OMEGA CONTROL PANEL - WEB INTERFACE
echo ========================================
echo.
echo Starting web interface...
echo Access at: http://localhost:5000
echo.
start http://localhost:5000
python omega_control_panel_web.py --port 5000
pause
