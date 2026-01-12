# Create desktop shortcuts for wallet access
# Red Post Farms, LLC - Copyright (c) 2025-2026

$Desktop = [Environment]::GetFolderPath("Desktop")
$Gatekeeper = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "python"

Write-Host "Creating wallet access shortcuts on desktop..." -ForegroundColor Green

# Shortcut 1: View Wallets (GUI)
$bat1 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_wallet_quick_access.py
pause
"@
$bat1 | Out-File -FilePath "$Desktop\Omega - Wallet Access.bat" -Encoding ASCII

# Shortcut 2: View Wallets (CLI)
$bat2 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_wallet_access.py --show
pause
"@
$bat2 | Out-File -FilePath "$Desktop\Omega - View Wallets.bat" -Encoding ASCII

# Shortcut 3: Check Bitcoin Balance
$bat3 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_wallet_access.py --btc
pause
"@
$bat3 | Out-File -FilePath "$Desktop\Omega - Check Bitcoin.bat" -Encoding ASCII

# Shortcut 4: Check Ethereum Balance
$bat4 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_wallet_access.py --eth
pause
"@
$bat4 | Out-File -FilePath "$Desktop\Omega - Check Ethereum.bat" -Encoding ASCII

# Shortcut 5: Check Testnet Balance
$bat5 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_wallet_access.py --testnet
pause
"@
$bat5 | Out-File -FilePath "$Desktop\Omega - Check Testnet.bat" -Encoding ASCII

# Shortcut 6: Run Limbo Sweeper
$bat6 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_sweeper.py
pause
"@
$bat6 | Out-File -FilePath "$Desktop\Omega - Run Limbo Sweeper.bat" -Encoding ASCII

# Shortcut 7: View Results
$bat7 = @"
@echo off
cd /d "$Gatekeeper"
$Python limbo_sweeper_test_run.py --results
pause
"@
$bat7 | Out-File -FilePath "$Desktop\Omega - View Results.bat" -Encoding ASCII

# Shortcut 8: Wallet Folder
$bat8 = @"
@echo off
explorer "D:\RPF_BRAIN\Omega"
"@
$bat8 | Out-File -FilePath "$Desktop\Omega - Wallet Folder.bat" -Encoding ASCII

Write-Host ""
Write-Host "Shortcuts created on desktop:" -ForegroundColor Green
Write-Host "  - Omega - Wallet Access.bat (GUI)" -ForegroundColor Yellow
Write-Host "  - Omega - View Wallets.bat (CLI)" -ForegroundColor Yellow
Write-Host "  - Omega - Check Bitcoin.bat" -ForegroundColor Yellow
Write-Host "  - Omega - Check Ethereum.bat" -ForegroundColor Yellow
Write-Host "  - Omega - Check Testnet.bat" -ForegroundColor Yellow
Write-Host "  - Omega - Run Limbo Sweeper.bat" -ForegroundColor Yellow
Write-Host "  - Omega - View Results.bat" -ForegroundColor Yellow
Write-Host "  - Omega - Wallet Folder.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
