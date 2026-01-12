@echo off
REM Schedule Weekly 5-Min Growth Loop
REM Runs every Wednesday at 10:24 PM

echo ============================================================
echo Scheduling Weekly Growth Loop
echo ============================================================

REM First, run initialization if needed
python "D:\RPF_BRAIN\The Gatekeeper\weekly_growth.py"
if errorlevel 1 (
    echo Initialization failed.
    pause
    exit /b 1
)

REM Create scheduled task for Wednesday 22:24
schtasks /Create /TN "GatekeeperWeeklyGrowth" /TR "python \"D:\RPF_BRAIN\The Gatekeeper\weekly_growth.py\" --weekly" /SC WEEKLY /D WED /ST 22:24 /F

if errorlevel 1 (
    echo Task creation failed. Run as administrator.
    pause
    exit /b 1
)

echo.
echo ✅ Weekly growth loop scheduled
echo Task name: GatekeeperWeeklyGrowth
echo Schedule: Every Wednesday at 10:24 PM
echo.
echo To test: schtasks /Run /TN "GatekeeperWeeklyGrowth"
echo To delete: schtasks /Delete /TN "GatekeeperWeeklyGrowth" /F
echo.
echo The loop will show pipeline deltas and ask for approval.
pause

