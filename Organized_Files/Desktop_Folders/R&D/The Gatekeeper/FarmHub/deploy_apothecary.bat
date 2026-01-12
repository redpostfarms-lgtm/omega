@echo off
REM ONE-LINE DEPLOY bat for APOTHECARY - FARMHUB ORGANIC CORE 2026
REM Creates necessary directories and starts Apothecary.py

set APOTHECARY_DIR=D:\RPF_BRAIN\FarmHub
set RECIPES_DIR=%APOTHECARY_DIR%\recipes_organic

echo ============================================================
echo Deploying APOTHECARY - FARMHUB ORGANIC CORE 2026
echo ============================================================

echo Creating directory structure...
mkdir "%APOTHECARY_DIR%" >nul 2>&1
mkdir "%RECIPES_DIR%" >nul 2>&1

echo Starting Apothecary.py...
start python "%APOTHECARY_DIR%\Apothecary.py"

echo APOTHECARY is awake.
echo.
echo Voice commands now live:
echo   - Apothecary, aphids on tomatoes
echo   - Apothecary, powdery mildew
echo   - Apothecary, immune boost
echo   - Apothecary, joint pain
echo   - Apothecary, status
echo.
echo Your farm is now chemically dead and biologically unstoppable.
echo The Apothecary never sleeps. Pests don't stand a chance.
echo.
pause

