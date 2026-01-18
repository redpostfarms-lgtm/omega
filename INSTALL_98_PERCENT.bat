@echo off
REM ============================================================
REM  Install Dependencies for 98% Completion
REM  Installs all advanced features packages
REM ============================================================

echo.
echo ============================================================
echo   INSTALL FOR 98%% SYSTEM COMPLETION
echo ============================================================
echo.

REM Check Python 3.11
echo [1/7] Checking Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo       ERROR - Python 3.11 not found!
    pause
    exit /b 1
)
echo       OK
echo.

REM Upgrade pip
echo [2/7] Upgrading pip...
py -3.11 -m pip install --upgrade pip --quiet
echo       COMPLETE
echo.

REM Install emotion detection
echo [3/7] Installing EMOTION DETECTION packages...
echo       (transformers, datasets, accelerate)
py -3.11 -m pip install transformers datasets accelerate --quiet
if errorlevel 1 (
    echo       WARNING - Some packages failed
) else (
    echo       COMPLETE
)
echo.

REM Install predictive health
echo [4/7] Installing PREDICTIVE HEALTH packages...
echo       (prophet, scikit-learn, pandas, statsmodels)
py -3.11 -m pip install prophet scikit-learn pandas statsmodels --quiet
if errorlevel 1 (
    echo       WARNING - Prophet may need C++ compiler
    echo       Install: https://visualstudio.microsoft.com/visual-cpp-build-tools/
) else (
    echo       COMPLETE
)
echo.

REM Install agent reasoning
echo [5/7] Installing AGENT REASONING packages...
echo       (langchain, langgraph, langchain-community)
py -3.11 -m pip install langchain langgraph langchain-community --quiet
if errorlevel 1 (
    echo       WARNING - Some packages failed
) else (
    echo       COMPLETE
)
echo.

REM Install notifications
echo [6/7] Installing NOTIFICATION packages...
echo       (jinja2, python-telegram-bot, discord.py, slack-sdk)
py -3.11 -m pip install jinja2 python-telegram-bot discord.py slack-sdk aiohttp --quiet
if errorlevel 1 (
    echo       WARNING - Some packages failed
) else (
    echo       COMPLETE
)
echo.

REM Install monitoring and packaging
echo [7/7] Installing MONITORING and PACKAGING...
echo       (grafana-client, elasticsearch, build, twine)
py -3.11 -m pip install grafana-client elasticsearch build twine hatchling --quiet
if errorlevel 1 (
    echo       WARNING - Some packages failed
) else (
    echo       COMPLETE
)
echo.

REM Summary
echo ============================================================
echo   INSTALLATION COMPLETE
echo ============================================================
echo.
echo  Packages installed for 98%% completion:
echo    - Emotion Detection: transformers, datasets
echo    - Predictive Health: prophet, scikit-learn
echo    - Agent Reasoning: langchain, langgraph
echo    - Notifications: telegram, discord, slack
echo    - Monitoring: grafana-client
echo    - Packaging: build, twine
echo.
echo  Next steps:
echo    1. Follow: ROADMAP_TO_98_PERCENT.md
echo    2. Implement 6 advanced features
echo    3. Run: pytest tests/ -v
echo    4. Deploy: docker-compose up -d
echo.
echo  Current completion: 91%% (with DevOps)
echo  Target completion: 98%% (with all features)
echo  Gap: 7%% (6 feature implementations)
echo.
echo ============================================================
echo.

pause
