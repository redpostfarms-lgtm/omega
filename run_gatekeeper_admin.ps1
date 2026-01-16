# Gatekeeper Admin Launcher - PowerShell
# Automatically requests admin privileges and launches Gatekeeper System

param(
    [switch]$NoElevate = $false
)

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GATEKEEPER ADMIN LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $NoElevate) {
    Write-Host "Status: " -ForegroundColor Yellow -NoNewline
    Write-Host "[!] NOT RUNNING AS ADMINISTRATOR" -ForegroundColor Red
    Write-Host "`nAttempting to elevate privileges...`n"
    
    # Re-launch script as admin
    $scriptPath = $MyInvocation.MyCommand.Definition
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -NoElevate" -Verb RunAs
    exit
}

Write-Host "Status: " -ForegroundColor Green -NoNewline
Write-Host "[OK] Running as ADMINISTRATOR" -ForegroundColor Green

# Display environment info
Write-Host "`nEnvironment:"
Write-Host "  Workspace: $(Get-Location)"
Write-Host "  User: $env:USERNAME"
Write-Host "  Computer: $env:COMPUTERNAME"
Write-Host "  OS: $([System.Environment]::OSVersion)"

# Check Python
Write-Host "`nPython:"
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion"

Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETTING UP DIRECTORIES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

# Create critical directories
$dirsToCreate = @("logs", "data", "reports", "backups")
foreach ($dir in $dirsToCreate) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir"
    } else {
        Write-Host "  ✓ Exists: $dir"
    }
}

Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RUNNING ADMIN VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

# Run admin helper
python gatekeeper_admin_helper.py

Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LAUNCHING GATEKEEPER SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

# Launch main system
python gatekeeper_integration_module.py

Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SYSTEM SHUTDOWN" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nGatekeeper system has terminated. Logs available in: logs/gatekeeper_system.log`n"

Read-Host "Press Enter to exit"
