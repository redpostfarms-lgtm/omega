@echo off
REM ============================================================
REM   OMEGA SILENT BACKGROUND LAUNCHER
REM ============================================================
REM   Version: 1.0
REM   Purpose: Launch Omega services silently in the background
REM            with no visible console window.
REM
REM   USAGE:
REM     1. Direct execution (will show briefly then hide):
REM        OMEGA_SILENT_LAUNCHER.bat
REM
REM     2. Via Task Scheduler (recommended - truly invisible):
REM        - Create task with trigger: At logon / At startup
REM        - Action: Start program -> wscript.exe
REM        - Arguments: "OMEGA_SILENT_LAUNCHER.vbs"
REM        - Or use the included .vbs wrapper
REM
REM     3. Via shortcut with hidden window:
REM        - Create shortcut to this .bat
REM        - Properties -> Run: Minimized
REM
REM   LOGS:
REM     All output logged to: logs\omega_service.log
REM
REM   FEATURES:
REM     - Silent background execution
REM     - Auto-restart on process failure
REM     - Survives reboots via Task Scheduler
REM     - No admin privileges required (unless services need them)
REM ============================================================

REM === CONFIGURATION ===
set "OMEGA_DIR=%~dp0"
set "LOG_DIR=%OMEGA_DIR%logs"
set "LOG_FILE=%LOG_DIR%\omega_service.log"
set "PID_FILE=%LOG_DIR%\omega.pid"
set "PYTHON_EXE=pythonw"
set "RESTART_DELAY=10"
set "MAX_RESTARTS=5"

REM === INITIALIZE ===
cd /d "%OMEGA_DIR%"

REM Create logs directory if not exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM === LOGGING FUNCTION (via label) ===
REM Logs timestamp + message to log file
call :LOG "=============================================="
call :LOG "OMEGA SILENT LAUNCHER STARTING"
call :LOG "Directory: %OMEGA_DIR%"
call :LOG "Time: %DATE% %TIME%"
call :LOG "=============================================="

REM === CHECK PYTHON ===
where pythonw >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :LOG "ERROR: pythonw not found, trying python"
    set "PYTHON_EXE=python"
)

REM === LAUNCH OMEGA SYSTEM TRAY (Primary Service) ===
call :LOG "Starting Omega System Tray..."
start "" /B "%PYTHON_EXE%" "%OMEGA_DIR%OMEGA_WITH_TRAY.py" >> "%LOG_FILE%" 2>&1

REM === LAUNCH OMEGA OPERATIONAL STARTUP (Secondary Service) ===
call :LOG "Starting Omega Operational Startup..."
start "" /B "%PYTHON_EXE%" "%OMEGA_DIR%omega_operational_startup.py" >> "%LOG_FILE%" 2>&1

REM === WATCHDOG LOOP ===
REM Monitor processes and restart if they die
call :LOG "Watchdog monitoring active"

set "RESTART_COUNT=0"

:WATCHDOG_LOOP
    REM Wait before checking
    timeout /t 60 /nobreak >nul 2>&1

    REM Check if OMEGA_WITH_TRAY is running
    tasklist /FI "WINDOWTITLE eq Omega*" 2>nul | find /I "python" >nul
    if %ERRORLEVEL% NEQ 0 (
        REM Process not found, check restart count
        set /a RESTART_COUNT+=1

        if %RESTART_COUNT% GEQ %MAX_RESTARTS% (
            call :LOG "ERROR: Max restarts (%MAX_RESTARTS%) reached. Stopping watchdog."
            goto :END
        )

        call :LOG "WARNING: Omega process not found. Restarting... (Attempt %RESTART_COUNT%/%MAX_RESTARTS%)"
        timeout /t %RESTART_DELAY% /nobreak >nul 2>&1
        start "" /B "%PYTHON_EXE%" "%OMEGA_DIR%OMEGA_WITH_TRAY.py" >> "%LOG_FILE%" 2>&1
    ) else (
        REM Process is running, reset restart count
        set "RESTART_COUNT=0"
    )

    goto :WATCHDOG_LOOP

:END
call :LOG "Omega Silent Launcher terminated"
exit /b 0

REM === LOG SUBROUTINE ===
:LOG
    echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
    goto :eof
