@echo off
REM ========================================
REM PHASE 7: Verify All Services
REM ========================================
REM

echo.
echo ========================================
echo PHASE 7: VERIFY ALL SERVICES
echo ========================================
echo.
echo This script will verify that all services are:
echo   1. Running
echo   2. Accessible
echo   3. Responding correctly
echo.
pause

echo.
echo [1/7] Checking running containers...
echo.
docker ps --format "table {{.Names}}\t{{.Status}}"
echo.

set /a container_count=0
for /f %%i in ('docker ps -q ^| find /c /v ""') do set container_count=%%i

echo Found %container_count% running containers
echo Expected: 5 containers (gatekeeper, redis, prometheus, grafana, jupyter)
echo.

if %container_count% lss 5 (
    echo WARNING: Not all containers are running!
    echo.
    echo Check logs with: docker compose logs
    pause
)

echo.
echo [2/7] Testing API health endpoint...
echo.
curl -f http://localhost:8000/health
if %errorlevel% neq 0 (
    echo.
    echo ERROR: API health check failed!
    echo The API may still be starting up. Wait 30 seconds and try again.
    pause
) else (
    echo.
    echo ✓ API is healthy
)

echo.
echo [3/7] Testing API documentation...
echo.
curl -s http://localhost:8000/docs ^| find "Swagger" >nul
if %errorlevel% neq 0 (
    echo WARNING: Could not verify API docs
) else (
    echo ✓ API docs are accessible
)

echo.
echo [4/7] Testing Prometheus...
echo.
curl -s http://localhost:9090/-/ready
if %errorlevel% neq 0 (
    echo WARNING: Prometheus may not be ready yet
) else (
    echo ✓ Prometheus is ready
)

echo.
echo [5/7] Testing Grafana...
echo.
curl -s http://localhost:3000/api/health ^| find "ok" >nul
if %errorlevel% neq 0 (
    echo WARNING: Grafana may not be ready yet
) else (
    echo ✓ Grafana is healthy
)

echo.
echo [6/7] Testing Jupyter...
echo.
curl -s http://localhost:8888 ^| find "Jupyter" >nul
if %errorlevel% neq 0 (
    echo WARNING: Jupyter may not be accessible yet
) else (
    echo ✓ Jupyter is accessible
)

echo.
echo [7/7] Opening services in browser...
echo.
echo Opening API documentation...
start http://localhost:8000/docs

timeout /t 2 /nobreak

echo Opening Jupyter Lab...
start http://localhost:8888

timeout /t 2 /nobreak

echo Opening Grafana...
start http://localhost:3000

echo.
echo ========================================
echo VERIFICATION COMPLETE!
echo ========================================
echo.
echo All services should now be open in your browser:
echo.
echo   ✓ API Docs:   http://localhost:8000/docs
echo   ✓ Jupyter:    http://localhost:8888  (token: gatekeeper)
echo   ✓ Grafana:    http://localhost:3000  (admin/gatekeeper)
echo.
echo Additional services:
echo   • API:        http://localhost:8000
echo   • Health:     http://localhost:8000/health
echo   • Prometheus: http://localhost:9090
echo.
echo ========================================
echo FINAL STEPS
echo ========================================
echo.
echo 1. Update VSCode settings to enable Docker UI
echo    - Open settings.json
echo    - Uncomment Docker configuration lines
echo    - Change docker.showExplorer to true
echo    - Reload VSCode window
echo.
echo 2. View container logs:
echo    docker compose logs -f
echo.
echo 3. Stop services when done:
echo    docker compose down
echo.
echo 4. Restart services later:
echo    docker compose --profile development up -d
echo.
echo ========================================
echo SETUP COMPLETE! 🎉
echo ========================================
echo.
pause
