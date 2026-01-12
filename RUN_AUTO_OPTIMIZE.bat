@echo off
REM Auto Optimize Applications - Batch Wrapper
echo ================================================================================
echo AUTO APP OPTIMIZATION
echo ================================================================================
echo.
cd /d "%~dp0"
python AUTO_SELECT_AND_OPTIMIZE.py
echo.
echo ================================================================================
pause
