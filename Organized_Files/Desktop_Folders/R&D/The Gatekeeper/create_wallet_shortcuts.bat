@echo off
REM Create desktop shortcuts for wallet access
REM Red Post Farms, LLC - Copyright (c) 2025-2026

set "DESKTOP=%USERPROFILE%\Desktop"
set "GATEKEEPER=%~dp0"
set "PYTHON=python"

echo Creating wallet access shortcuts on desktop...

REM Shortcut 1: View Wallets
echo [InternetShortcut] > "%DESKTOP%\Omega - View Wallets.url"
echo URL=file:///%GATEKEEPER:~0,-1%/limbo_wallet_access.py >> "%DESKTOP%\Omega - View Wallets.url"
echo IconFile=%GATEKEEPER%limbo_wallet_access.py >> "%DESKTOP%\Omega - View Wallets.url"

REM Create batch file for wallet viewer
echo @echo off > "%DESKTOP%\Omega - View Wallets.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - View Wallets.bat"
echo %PYTHON% limbo_wallet_access.py --show >> "%DESKTOP%\Omega - View Wallets.bat"
echo pause >> "%DESKTOP%\Omega - View Wallets.bat"

REM Shortcut 2: Check Bitcoin Balance
echo @echo off > "%DESKTOP%\Omega - Check Bitcoin.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - Check Bitcoin.bat"
echo %PYTHON% limbo_wallet_access.py --btc >> "%DESKTOP%\Omega - Check Bitcoin.bat"
echo pause >> "%DESKTOP%\Omega - Check Bitcoin.bat"

REM Shortcut 3: Check Ethereum Balance
echo @echo off > "%DESKTOP%\Omega - Check Ethereum.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - Check Ethereum.bat"
echo %PYTHON% limbo_wallet_access.py --eth >> "%DESKTOP%\Omega - Check Ethereum.bat"
echo pause >> "%DESKTOP%\Omega - Check Ethereum.bat"

REM Shortcut 4: Check Testnet Balance
echo @echo off > "%DESKTOP%\Omega - Check Testnet.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - Check Testnet.bat"
echo %PYTHON% limbo_wallet_access.py --testnet >> "%DESKTOP%\Omega - Check Testnet.bat"
echo pause >> "%DESKTOP%\Omega - Check Testnet.bat"

REM Shortcut 5: Run Limbo Sweeper
echo @echo off > "%DESKTOP%\Omega - Run Limbo Sweeper.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - Run Limbo Sweeper.bat"
echo %PYTHON% limbo_sweeper.py >> "%DESKTOP%\Omega - Run Limbo Sweeper.bat"
echo pause >> "%DESKTOP%\Omega - Run Limbo Sweeper.bat"

REM Shortcut 6: View Results
echo @echo off > "%DESKTOP%\Omega - View Results.bat"
echo cd /d "%GATEKEEPER%" >> "%DESKTOP%\Omega - View Results.bat"
echo %PYTHON% limbo_sweeper_test_run.py --results >> "%DESKTOP%\Omega - View Results.bat"
echo pause >> "%DESKTOP%\Omega - View Results.bat"

REM Shortcut 7: Wallet Folder (opens wallet directory)
echo @echo off > "%DESKTOP%\Omega - Wallet Folder.bat"
echo explorer "D:\RPF_BRAIN\Omega" >> "%DESKTOP%\Omega - Wallet Folder.bat"

echo.
echo Shortcuts created on desktop:
echo   - Omega - View Wallets.bat
echo   - Omega - Check Bitcoin.bat
echo   - Omega - Check Ethereum.bat
echo   - Omega - Check Testnet.bat
echo   - Omega - Run Limbo Sweeper.bat
echo   - Omega - View Results.bat
echo   - Omega - Wallet Folder.bat
echo.
pause
