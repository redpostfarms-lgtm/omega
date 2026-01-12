@echo off
REM ONE-LINE DEPLOY bat for FEEDMASTER - FARMHUB FEED & NUTRITION CORE 2026
REM Creates necessary directories and starts FeedMaster.py

set FEEDMASTER_DIR=D:\RPF_BRAIN\FarmHub
set RECIPES_DIR=%FEEDMASTER_DIR%\feed_recipes

echo ============================================================
echo Deploying FEEDMASTER - FARMHUB FEED & NUTRITION CORE 2026
echo ============================================================

echo Creating directory structure...
mkdir "%FEEDMASTER_DIR%" >nul 2>&1
mkdir "%RECIPES_DIR%" >nul 2>&1

echo Starting FeedMaster.py...
start python "%FEEDMASTER_DIR%\FeedMaster.py"

echo FEEDMASTER is awake.
echo.
echo Voice commands now live:
echo   - FeedMaster, layers
echo   - FeedMaster, broiler recipe
echo   - FeedMaster, worm chow
echo   - FeedMaster, dairy cow
echo   - FeedMaster, beef
echo   - FeedMaster, status
echo.
echo Your livestock and worms now eat better than any farm in recorded history.
echo Zero chemicals. Zero guesswork. Maximum health, growth, and flavor.
echo.
echo The feed mill just became sentient.
echo.
pause

