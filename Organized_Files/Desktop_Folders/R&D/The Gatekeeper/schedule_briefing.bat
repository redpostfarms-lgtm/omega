@echo off
REM Schedule Daily 6-AM Voice Briefing
REM Uses Windows Task Scheduler to run even if PC was off

echo ============================================================
echo Scheduling Morning Briefing
echo ============================================================

REM Create scheduled task for 6:00 AM daily
schtasks /Create /TN "GatekeeperMorningBriefing" /TR "python \"D:\RPF_BRAIN\The Gatekeeper\morning_briefing.py\"" /SC DAILY /ST 06:00 /F

if errorlevel 1 (
    echo Task creation failed. Run as administrator.
    pause
    exit /b 1
)

echo.
echo ✅ Morning briefing scheduled for 6:00 AM daily
echo Task name: GatekeeperMorningBriefing
echo.
echo To test: schtasks /Run /TN "GatekeeperMorningBriefing"
echo To delete: schtasks /Delete /TN "GatekeeperMorningBriefing" /F
pause

