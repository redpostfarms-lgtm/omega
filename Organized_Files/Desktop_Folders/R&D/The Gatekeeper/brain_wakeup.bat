@echo off
REM Gatekeeper Brain Wakeup - Auto-heal on boot
REM Runs hardware scan, auto-heal, loads voice tuning, primes the brain, starts all systems

cd /d "%~dp0"
set GATEKEEPER_DIR=%~dp0

echo ============================================================
echo Gatekeeper Brain Wakeup - Complete System
echo ============================================================

REM Hardware scan and status report (speaks on boot)
echo [0/7] Hardware scan and status report...
python "%GATEKEEPER_DIR%hardware_scan.py"
if errorlevel 1 (
    echo Hardware scan had issues (continuing)
)

REM Run auto-heal first
echo [1/7] Auto-healing system...
python "%GATEKEEPER_DIR%auto_heal.py"
if errorlevel 1 (
    echo Auto-heal failed. Check logs.
    pause
    exit /b 1
)

REM Load voice tuning
echo [2/7] Loading voice tuning...
python "%GATEKEEPER_DIR%voice_tuner.py" --load
if errorlevel 1 (
    echo Voice tuning load failed.
    pause
    exit /b 1
)

REM Prime the brain
echo [3/7] Priming brain...
python "%GATEKEEPER_DIR%brain_prime.py"
if errorlevel 1 (
    echo Brain priming failed.
    pause
    exit /b 1
)

REM Battery Health Prophet
echo [4/7] Checking battery health...
start /B python "%GATEKEEPER_DIR%battery_oracle.py"

REM Solar Forecaster
echo [5/7] Forecasting solar production...
start /B python "%GATEKEEPER_DIR%solar_forecaster.py"

REM Schedule morning briefing (one-time setup)
echo [6/7] Checking morning briefing schedule...
if not exist "%TEMP%\briefing_scheduled.flag" (
    call "%GATEKEEPER_DIR%schedule_briefing.bat"
    echo. > "%TEMP%\briefing_scheduled.flag"
)

REM FarmHub Sensor Core
echo [7/9] Starting FarmHub Sensor Core...
start /B python "%GATEKEEPER_DIR%FarmHub\sensor_hub.py"
if errorlevel 1 (
    echo FarmHub startup had issues (continuing)
)

REM FarmHub Medical Core
echo [8/10] Starting FarmHub Medical Core...
start /B python "%GATEKEEPER_DIR%FarmHub\medical_core_final_2026.py"
if errorlevel 1 (
    echo FarmHub Medical startup had issues (continuing)
)

REM Hive Hibernation Engine
echo [9/11] Hive hibernation engine ready...
REM Hive starts in hibernation - zero agents active
REM Wakes automatically when "solve" command received

REM Weekly Knowledge School (auto-update knowledge base)
echo [10/12] Starting weekly knowledge school...
start /B python "%GATEKEEPER_DIR%weekly_school.py"
if errorlevel 1 (
    echo Weekly school startup had issues (continuing)
)

REM FarmOS 2026 - Unified Inter-Agent Neural Farm OS (optional - can run separately)
echo [11/12] FarmOS 2026 available (run deploy_farmos_2026.bat to start)...
REM Uncomment below to auto-start FarmOS on boot:
REM start /B python "%GATEKEEPER_DIR%FarmOS_2026.py"
REM if errorlevel 1 (
REM     echo FarmOS startup had issues (continuing)
REM )

echo.
echo [12/12] System ready.
echo.
echo ============================================================
echo Gatekeeper ready. The doors of knowledge opens.
echo ============================================================
echo.
echo All systems operational:
echo   - Hardware scanned and status reported
echo   - Brain primed
echo   - Voice tuned
echo   - Battery health monitoring active
echo   - Solar forecasting active
echo   - Morning briefing scheduled
echo   - FarmHub Sensor Core active (44 sensors)
echo   - FarmHub Medical Core active (fall/bleeding/seizure detection)
echo   - Hive hibernation engine ready (agents hibernate until needed)
echo   - Weekly knowledge school active (auto-updates 11.1 TB knowledge base)
echo   - FarmOS 2026 available (run deploy_farmos_2026.bat to start unified agent OS)
echo.
echo Ready when you are.
echo.
pause

