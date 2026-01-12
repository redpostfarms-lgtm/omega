@echo off
REM GATEKEEPER - START BUILDING
REM Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved

echo ============================================================
echo GATEKEEPER - START BUILDING
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Verifying system...
python build_system.py

echo.
echo [2/3] Creating projects directory...
if not exist "projects" mkdir "projects"
echo ✅ Projects directory ready

echo.
echo [3/3] Ready to build!
echo.
echo Available commands:
echo   Voice: "Hey, Gatekeeper, write [project description]"
echo   Direct: python gatekeeper_fusion.py "[project description]"
echo.
echo Example projects:
echo   1. "write a quantum-safe BMS in Rust"
echo   2. "create a solar MPPT controller in Python"
echo   3. "build a farm automation hub with Rust and Python"
echo.
echo All outputs saved to: Archived\fusion_outputs\
echo.
echo The doors of knowledge opens. Gatekeeper is ready to build.
echo.
pause

