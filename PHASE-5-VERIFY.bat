@echo off
REM ========================================
REM PHASE 5: Verify Installation
REM ========================================
REM

echo.
echo ========================================
echo PHASE 5: VERIFY INSTALLATION
echo ========================================
echo.
echo This script will verify that:
echo   1. WSL is installed and running
echo   2. Docker is accessible from Windows
echo   3. Docker is accessible from WSL
echo   4. All systems are ready for container build
echo.
pause

echo.
echo [1/5] Checking WSL installation...
echo.
wsl --list --verbose
if %errorlevel% neq 0 (
    echo.
    echo ERROR: WSL is not installed!
    echo Please run PHASE-1-ENABLE-WSL.bat first.
    pause
    exit /b 1
)

echo.
echo [2/5] Checking Docker version...
echo.
docker --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker command not found!
    echo Please run PHASE-3-START-DOCKER.bat first.
    pause
    exit /b 1
)

echo.
echo [3/5] Checking Docker Compose version...
echo.
docker compose version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker Compose not available!
    echo Please ensure Docker Desktop is fully started.
    pause
    exit /b 1
)

echo.
echo [4/5] Testing Docker daemon...
echo.
docker ps
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker daemon is not running!
    echo Please start Docker Desktop and wait for green icon.
    pause
    exit /b 1
)

echo.
echo [5/5] Running Docker hello-world test...
echo.
docker run --rm hello-world
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker test failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! ALL SYSTEMS READY
echo ========================================
echo.
echo ✓ WSL is installed and running
echo ✓ Docker is accessible
echo ✓ Docker Compose is available
echo ✓ Docker daemon is running
echo ✓ Docker test passed
echo.
echo READY TO BUILD GATEKEEPER CONTAINERS!
echo.
echo Next step: Run PHASE-6-BUILD-GATEKEEPER.bat
echo.
pause
