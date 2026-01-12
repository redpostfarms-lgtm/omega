@echo off
REM Omega Educational System Launcher
cd /d "%~dp0"

echo ========================================
echo   OMEGA EDUCATIONAL SYSTEM
echo   Comprehensive 100%% Proficiency Training
echo ========================================
echo.

echo Available Educational Systems:
echo.
echo [1] Knowledge Assessment
echo [2] Educational System Overview
echo [3] Hands-On Guidance System
echo [4] Educational Agents
echo [5] Full Educational Plan
echo.
echo Starting educational system...
echo.

python omega_educational_system.py
if errorlevel 1 (
    echo.
    echo [ERROR] Could not start educational system
    pause
    exit /b 1
)

echo.
echo ========================================
echo   EDUCATIONAL SYSTEM READY
echo ========================================
pause
