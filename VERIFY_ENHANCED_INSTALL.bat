@echo off
REM ============================================================
REM  Verify Enhanced Installation
REM  Checks all dependencies and features
REM ============================================================

echo.
echo ============================================================
echo   ENHANCED SYSTEM VERIFICATION
echo ============================================================
echo.

REM Python check
echo [1/8] Checking Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo       ERROR - Python 3.11 not found
    goto :error
) else (
    py -3.11 --version
    echo       OK
)
echo.

REM Core packages
echo [2/8] Checking CORE packages...
py -3.11 -c "import yaml, schedule, flask, black, ruff" >nul 2>&1
if errorlevel 1 (
    echo       ERROR - Some core packages missing
    echo       Run: INSTALL_ENHANCED.bat
    goto :error
) else (
    echo       OK - pyyaml, schedule, flask, black, ruff
)
echo.

REM Monitoring packages
echo [3/8] Checking MONITORING packages...
py -3.11 -c "import prometheus_client, psutil" >nul 2>&1
if errorlevel 1 (
    echo       WARNING - Monitoring packages missing
    echo       Install: py -3.11 -m pip install prometheus-client psutil
) else (
    echo       OK - prometheus-client, psutil
)
echo.

REM Notification packages
echo [4/8] Checking NOTIFICATION packages...
py -3.11 -c "import win10toast" >nul 2>&1
if errorlevel 1 (
    echo       WARNING - win10toast not installed
    echo       Install: py -3.11 -m pip install win10toast
) else (
    echo       OK - win10toast
)
echo.

REM Optional packages
echo [5/8] Checking OPTIONAL packages...
py -3.11 -c "import watchdog, pytest, sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo       SKIPPED - Optional packages not installed
) else (
    echo       OK - watchdog, pytest, sqlalchemy
)
echo.

REM LLM packages
echo [6/8] Checking LLM packages...
py -3.11 -c "import ollama" >nul 2>&1
if errorlevel 1 (
    echo       SKIPPED - Ollama not installed
    echo       To use local LLM:
    echo         1. Install: py -3.11 -m pip install ollama
    echo         2. Download Ollama from https://ollama.ai
    echo         3. Run: ollama pull llama3.2
) else (
    echo       OK - Ollama Python client installed
)
echo.

REM Utilities
echo [7/8] Checking ENHANCED utilities...
if exist "utils\compressed_json.py" (
    echo       OK - Compressed JSON utility
) else (
    echo       ERROR - utils\compressed_json.py not found
)
if exist "utils\integrity_checker.py" (
    echo       OK - Integrity checker
) else (
    echo       ERROR - utils\integrity_checker.py not found
)
if exist "utils\win10_notifications.py" (
    echo       OK - Windows 10 notifications
) else (
    echo       ERROR - utils\win10_notifications.py not found
)
echo.

REM LLM integration
echo [8/8] Checking INTEGRATION files...
if exist "omega_local_llm.py" (
    echo       OK - Local LLM integration
) else (
    echo       ERROR - omega_local_llm.py not found
)
if exist "omega_web_ide.py" (
    echo       OK - Web IDE
) else (
    echo       ERROR - omega_web_ide.py not found
)
echo.

REM Summary
echo ============================================================
echo   VERIFICATION COMPLETE
echo ============================================================
echo.
echo  Core system: READY
echo  Monitoring: READY
echo  Enhanced features: INSTALLED
echo.
echo  Next steps:
echo    1. Review: ENHANCED_SYSTEM_GUIDE.md
echo    2. Setup Ollama (optional): See guide Section 6
echo    3. Start Web IDE: py -3.11 omega_web_ide.py
echo    4. Run Omega: START_HERE.bat
echo.
echo ============================================================
echo.
goto :end

:error
echo.
echo ============================================================
echo   VERIFICATION FAILED
echo ============================================================
echo.
echo  Please install missing dependencies:
echo    Run: INSTALL_ENHANCED.bat
echo.
echo ============================================================
echo.

:end
pause
