@echo off
REM GATEKEEPER - Complete System Setup
REM One-time setup script that configures everything

echo ============================================================
echo GATEKEEPER - Complete System Setup
echo ============================================================
echo.

cd /d "%~dp0"
set GATEKEEPER_DIR=%~dp0

echo [1/10] Creating directory structure...
if not exist "D:\RPF_BRAIN\Archived" mkdir "D:\RPF_BRAIN\Archived"
if not exist "D:\RPF_BRAIN\Archived\voiceprint" mkdir "D:\RPF_BRAIN\Archived\voiceprint"
if not exist "D:\RPF_BRAIN\Archived\voiceprint\tuned" mkdir "D:\RPF_BRAIN\Archived\voiceprint\tuned"
if not exist "D:\RPF_BRAIN\Archived\learning" mkdir "D:\RPF_BRAIN\Archived\learning"
if not exist "D:\RPF_BRAIN\Archived\voice_log" mkdir "D:\RPF_BRAIN\Archived\voice_log"
if not exist "D:\RPF_BRAIN\Archived\Grants" mkdir "D:\RPF_BRAIN\Archived\Grants"
if not exist "D:\RPF_BRAIN\Archived\Grants\ready_to_mail" mkdir "D:\RPF_BRAIN\Archived\Grants\ready_to_mail"
echo ✅ Directories created

echo.
echo [2/10] Priming the brain...
python "%GATEKEEPER_DIR%brain_prime.py"
if errorlevel 1 (
    echo ⚠️  Brain priming had issues (continuing)
) else (
    echo ✅ Brain primed
)

echo.
echo [3/10] Loading prompt bank...
python "%GATEKEEPER_DIR%prompt_bank.py"
if errorlevel 1 (
    echo ⚠️  Prompt bank had issues (continuing)
) else (
    echo ✅ Prompts loaded
)

echo.
echo [4/10] Voiceprint setup (REQUIRED)...
echo You will be prompted to speak your name...
python "%GATEKEEPER_DIR%voiceprint_auth.py"
if errorlevel 1 (
    echo ⚠️  Voiceprint setup failed - run manually later
) else (
    echo ✅ Voiceprint captured
)

echo.
echo [5/10] Voice tuning setup...
python "%GATEKEEPER_DIR%voice_tuner.py"
if errorlevel 1 (
    echo ⚠️  Voice tuning had issues (continuing)
) else (
    echo ✅ Voice tuned
)

echo.
echo [6/10] Initializing weekly growth baseline...
python "%GATEKEEPER_DIR%weekly_growth.py"
if errorlevel 1 (
    echo ⚠️  Growth baseline had issues (continuing)
) else (
    echo ✅ Growth baseline set
)

echo.
echo [7/10] Scheduling morning briefings...
call "%GATEKEEPER_DIR%schedule_briefing.bat"
if errorlevel 1 (
    echo ⚠️  Briefing schedule had issues (continuing)
) else (
    echo ✅ Morning briefings scheduled
)

echo.
echo [8/10] Scheduling weekly learning...
call "%GATEKEEPER_DIR%schedule_learning.bat"
if errorlevel 1 (
    echo ⚠️  Learning schedule had issues (continuing)
) else (
    echo ✅ Weekly learning scheduled
)

echo.
echo [9/10] Scheduling weekly growth loop...
call "%GATEKEEPER_DIR%schedule_growth.bat"
if errorlevel 1 (
    echo ⚠️  Growth schedule had issues (continuing)
) else (
    echo ✅ Weekly growth scheduled
)

echo.
echo [10/10] Verifying system integrity...
python "%GATEKEEPER_DIR%auto_heal.py" --verify
if errorlevel 1 (
    echo ⚠️  System verification found issues
) else (
    echo ✅ System verified
)

echo.
echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Optional next steps:
echo   1. Run max_out_pipelines.py to set all stats to 100%%
echo   2. Install Ollama for self-learning: https://ollama.ai/
echo   3. Install Kiwix for offline wiki: run install_offline_wiki.bat
echo   4. Add brain_wakeup.bat to Windows startup folder
echo.
echo The Gatekeeper is ready.
echo Say: "Hey, Gatekeeper, status"
echo.
pause

