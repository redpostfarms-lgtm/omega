@echo off
REM FARMHUB OS 2026 - DEPLOYMENT SCRIPT
REM Run once after save

cd /d D:\RPF_BRAIN\FarmHub

echo ============================================================
echo FARMHUB OS 2026 - DEPLOYMENT
echo ============================================================
echo.

echo Creating directory structure...
if not exist "models" mkdir "models"
if not exist "forms" mkdir "forms"
if not exist "cad" mkdir "cad"

echo.
echo Starting FarmHub OS...
echo.

python master_farmhub.py

pause

