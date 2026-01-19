@echo off
REM ========================================
REM GATEKEEPER SETUP - START HERE
REM ========================================
REM
REM This is the master setup script.
REM Follow the phases in order.
REM

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║     🚀 GATEKEEPER DOCKER + WSL SETUP                         ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo SETUP PHASES:
echo.
echo   Phase 1: Enable WSL                    (5 min + restart)
echo   Phase 2: Setup Ubuntu                  (3 min)
echo   Phase 3: Start Docker Desktop          (2 min)
echo   Phase 4: Configure Docker for WSL      (2 min)
echo   Phase 5: Verify Installation           (2 min)
echo   Phase 6: Build Gatekeeper Stack        (10-15 min first time)
echo   Phase 7: Verify All Services           (1 min)
echo.
echo   TOTAL TIME: 25-30 minutes (first time)
echo   Future starts: ~2 minutes
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo CURRENT STATUS:
echo.

REM Check WSL
wsl --list --verbose >nul 2>&1
if %errorlevel% neq 0 (
    echo   WSL:              ✗ NOT INSTALLED
    echo   Docker Desktop:   ✗ NOT ACCESSIBLE
    echo   Containers:       ✗ NOT RUNNING
    echo.
    echo   START WITH: PHASE-1-ENABLE-WSL.bat
    echo               ^(Right-click → Run as Administrator^)
    goto :menu
)

echo   WSL:              ✓ INSTALLED

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   Docker Desktop:   ✗ NOT STARTED
    echo   Containers:       ✗ NOT RUNNING
    echo.
    echo   NEXT STEP: PHASE-3-START-DOCKER.bat
    goto :menu
)

echo   Docker Desktop:   ✓ RUNNING

REM Check containers
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo   Containers:       ✗ NOT RUNNING
    echo.
    echo   NEXT STEP: PHASE-6-BUILD-GATEKEEPER.bat
    goto :menu
)

set /a container_count=0
for /f %%i in ('docker ps -q ^| find /c /v ""') do set container_count=%%i

if %container_count% geq 5 (
    echo   Containers:       ✓ RUNNING ^(%container_count% containers^)
    echo.
    echo   ╔═══════════════════════════════════════════════╗
    echo   ║  🎉 ALL SYSTEMS RUNNING!                     ║
    echo   ╚═══════════════════════════════════════════════╝
    echo.
    echo   Service URLs:
    echo     • API:         http://localhost:8000
    echo     • API Docs:    http://localhost:8000/docs
    echo     • Jupyter:     http://localhost:8888
    echo     • Grafana:     http://localhost:3000
    echo     • Prometheus:  http://localhost:9090
    echo.
    echo   Common commands:
    echo     • View logs:   docker compose logs -f
    echo     • Stop all:    docker compose down
    echo     • Restart:     docker compose --profile development up -d
    echo.
    pause
    exit /b 0
) else (
    echo   Containers:       ⚠ PARTIAL ^(%container_count%/5 running^)
    echo.
    echo   NEXT STEP: PHASE-6-BUILD-GATEKEEPER.bat
)

:menu
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo PHASE SCRIPTS:
echo.
echo   [1] PHASE-1-ENABLE-WSL.bat       - Enable WSL ^(requires admin^)
echo   [2] PHASE-2-SETUP-UBUNTU.bat     - Setup Ubuntu
echo   [3] PHASE-3-START-DOCKER.bat     - Start Docker Desktop
echo   [4] PHASE-4-CONFIGURE-DOCKER.txt - Configure Docker ^(manual^)
echo   [5] PHASE-5-VERIFY.bat           - Verify installation
echo   [6] PHASE-6-BUILD-GATEKEEPER.bat - Build containers
echo   [7] PHASE-7-VERIFY-SERVICES.bat  - Verify services
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo DOCUMENTATION:
echo.
echo   • START_NOW.txt                  - Quick reference guide
echo   • COMPLETE_STARTUP_GUIDE.md      - Detailed walkthrough
echo   • GATE_AGENT_ACCESS.md           - Gate agent permissions
echo   • GATE_AGENT_HANDOFF.md          - Gate agent mission brief
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo Press any key to exit...
pause >nul
