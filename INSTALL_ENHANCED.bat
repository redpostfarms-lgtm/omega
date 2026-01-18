@echo off
REM ============================================================
REM  Gatekeeper Enhanced Installation Script
REM  Installs all core and optional dependencies
REM ============================================================

echo.
echo ============================================================
echo   GATEKEEPER ENHANCED INSTALLATION
echo ============================================================
echo.

REM Check Python 3.11
echo [1/5] Checking Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 not found!
    echo Download from: https://www.python.org/downloads/release/python-31111/
    echo Make sure to check "Add Python 3.11 to PATH" during installation
    pause
    exit /b 1
)
echo       FOUND - OK
echo.

REM Upgrade pip
echo [2/5] Upgrading pip...
py -3.11 -m pip install --upgrade pip --quiet
echo       COMPLETE
echo.

REM Install core dependencies
echo [3/5] Installing CORE dependencies...
echo       (pyyaml, schedule, flask, black, ruff, etc.)
py -3.11 -m pip install pyyaml schedule flask waitress black ruff prometheus-client psutil win10toast --quiet
if errorlevel 1 (
    echo       WARNING: Some core packages failed to install
) else (
    echo       COMPLETE
)
echo.

REM Install optional dependencies
echo [4/5] Installing OPTIONAL dependencies...
set /p install_optional="Install optional packages (watchdog, pytest, sqlalchemy)? [Y/n]: "
if /i "%install_optional%"=="n" (
    echo       SKIPPED
) else (
    echo       Installing...
    py -3.11 -m pip install watchdog pytest pytest-asyncio sqlalchemy --quiet
    echo       COMPLETE
)
echo.

REM Install LLM integration
echo [5/5] Installing LLM integration...
set /p install_llm="Install local LLM support (Ollama, Langchain, ChromaDB)? [Y/n]: "
if /i "%install_llm%"=="n" (
    echo       SKIPPED
) else (
    echo       Installing... (this may take a few minutes)
    py -3.11 -m pip install ollama langchain langchain-community chromadb sentence-transformers --quiet
    echo       COMPLETE
)
echo.

REM Summary
echo ============================================================
echo   INSTALLATION COMPLETE
echo ============================================================
echo.
echo  Core dependencies: INSTALLED
if /i "%install_optional%"=="n" (
    echo  Optional dependencies: SKIPPED
) else (
    echo  Optional dependencies: INSTALLED
)
if /i "%install_llm%"=="n" (
    echo  LLM integration: SKIPPED
) else (
    echo  LLM integration: INSTALLED
)
echo.
echo  Next steps:
echo    1. Run: VERIFY_ENHANCED_INSTALL.bat
echo    2. Configure: config\gatekeeper_config.json
echo    3. Start: START_HERE.bat
echo.
echo ============================================================
echo.

pause
