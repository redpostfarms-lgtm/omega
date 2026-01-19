@echo off
REM ========================================
REM PHASE 3: Start Docker Desktop
REM ========================================
REM

echo.
echo ========================================
echo PHASE 3: START DOCKER DESKTOP
echo ========================================
echo.
echo This script will:
echo   1. Launch Docker Desktop
echo   2. Wait for it to fully start
echo   3. Verify Docker is running
echo.
pause

echo.
echo [1/4] Starting Docker Desktop...
echo.
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo.
echo Docker Desktop is starting...
echo.
echo IMPORTANT: Wait for the GREEN icon in your system tray
echo            (bottom-right corner of Windows taskbar)
echo.
echo This may take 1-2 minutes...
echo.
pause

echo.
echo [2/4] Checking Docker status...
echo.
timeout /t 5 /nobreak

docker --version
if %errorlevel% neq 0 (
    echo.
    echo Docker command not found yet. Waiting longer...
    timeout /t 10 /nobreak
    docker --version
)

echo.
echo [3/4] Testing Docker daemon...
echo.
docker ps
if %errorlevel% neq 0 (
    echo.
    echo Docker daemon not ready yet.
    echo Please wait for the GREEN icon in system tray, then press any key...
    pause
    docker ps
)

echo.
echo [4/4] Docker Desktop is running!
echo.
echo Next steps:
echo   1. Configure Docker for WSL 2
echo   2. Run PHASE-4-CONFIGURE-DOCKER.bat
echo.
pause
