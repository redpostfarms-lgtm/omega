@echo off
REM Final System Optimization Analyzer Launcher
REM Runs comprehensive scan, optimization, and analytics

echo.
echo ========================================
echo   Final System Optimization Analyzer
echo ========================================
echo.

cd /d "%~dp0"

REM Try py launcher first, fallback to python
py FINAL_SYSTEM_OPTIMIZATION_ANALYZER.py
if %errorlevel% neq 0 (
    python FINAL_SYSTEM_OPTIMIZATION_ANALYZER.py
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not run Python script
        echo Please ensure Python is installed and in PATH
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Analysis Complete
echo ========================================
echo.
echo Check the optimization_reports folder for results
echo.
pause
