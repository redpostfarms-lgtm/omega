@echo off
cls
echo ===============================================
echo     OMEGA SWARM - Launch Options
echo ===============================================
echo.
echo Choose your setup:
echo.
echo [1] Local Network Only (Default - No setup needed)
echo     - Same Wi-Fi required
echo     - Fast, direct connection
echo     - IP: 10.0.0.26:5002
echo.
echo [2] External Access via Tunnel (Setup required)
echo     - Works from anywhere
echo     - Requires ngrok token
echo     - Run: python setup_tunnel.py setup
echo.
echo [3] Configure ngrok Token (For later use)
echo.
echo [Q] Quit
echo.
echo ===============================================
choice /c 123Q /n /m "Select option: "

if errorlevel 4 goto :EOF
if errorlevel 3 goto configure
if errorlevel 2 goto tunnel
if errorlevel 1 goto local

:local
echo.
echo Starting OMEGA Swarm (Local Network Mode)...
echo.
start /B .\.venv\Scripts\python.exe omega_swarm_server.py
timeout /t 2 /nobreak >nul
start http://10.0.0.26:5002
echo.
echo Server running on http://10.0.0.26:5002
echo Scan QR codes with phones on the same Wi-Fi
echo.
echo Press Ctrl+C in the Python terminal to stop
pause
goto :EOF

:tunnel
echo.
echo Starting tunnel mode...
python setup_tunnel.py status
echo.
echo Starting ngrok tunnel...
start /B python setup_tunnel.py start
timeout /t 3 /nobreak >nul
echo.
echo Starting OMEGA server...
start /B .\.venv\Scripts\python.exe omega_swarm_server.py
timeout /t 2 /nobreak >nul
start http://10.0.0.26:5002
echo.
echo Tunnel active! QR codes will use public URL
echo Check http://127.0.0.1:4040 for ngrok dashboard
echo.
pause
goto :EOF

:configure
echo.
echo Opening tunnel setup...
echo.
python setup_tunnel.py setup
echo.
pause
goto :EOF
