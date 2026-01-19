@echo off
REM ========================================
REM PHASE 6: Build and Start Gatekeeper
REM ========================================
REM

echo.
echo ========================================
echo PHASE 6: BUILD GATEKEEPER STACK
echo ========================================
echo.
echo This script will:
echo   1. Build Docker images for all services
echo   2. Start development environment
echo   3. Launch 5 containers (API, Redis, Prometheus, Grafana, Jupyter)
echo.
echo FIRST TIME: This will take 10-15 minutes
echo   - Downloads ~2GB of base images
echo   - Builds custom images
echo   - Starts all services
echo.
echo SUBSEQUENT RUNS: Only 1-2 minutes
echo.
pause

echo.
echo [1/6] Navigating to project directory...
echo.
cd /d "C:\Users\Drakalich\.claude-worktrees\The Gatekeeper\pedantic-kowalevski"
if %errorlevel% neq 0 (
    echo ERROR: Could not find project directory!
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo.
echo [2/6] Checking compose.yaml exists...
echo.
if not exist "compose.yaml" (
    echo ERROR: compose.yaml not found!
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)
echo ✓ Found compose.yaml

echo.
echo [3/6] Pulling base images...
echo.
docker compose pull
if %errorlevel% neq 0 (
    echo WARNING: Some images could not be pulled. Will build from scratch...
)

echo.
echo [4/6] Building Gatekeeper images...
echo.
echo This may take 10-15 minutes on first run...
echo.
docker compose --profile development build
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [5/6] Starting all services...
echo.
docker compose --profile development up -d
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [6/6] Waiting for services to be ready...
echo.
timeout /t 5 /nobreak

docker compose ps

echo.
echo ========================================
echo GATEKEEPER STACK IS RUNNING!
echo ========================================
echo.
echo Running containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Service URLs:
echo   • API:         http://localhost:8000
echo   • API Docs:    http://localhost:8000/docs
echo   • Health:      http://localhost:8000/health
echo   • Jupyter:     http://localhost:8888  (token: gatekeeper)
echo   • Grafana:     http://localhost:3000  (admin/gatekeeper)
echo   • Prometheus:  http://localhost:9090
echo.
echo Next step: Run PHASE-7-VERIFY-SERVICES.bat
echo.
pause
