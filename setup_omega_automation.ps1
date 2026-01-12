# Setup-OmegaAutomation.ps1
# Run this script as Administrator to set up Omega Automation via Task Scheduler
# Usage: .\setup_omega_automation.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Omega Automation Setup ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$taskName = "OmegaAutomation"
$scriptPath = "D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"
$workingDir = "D:\RPF_BRAIN\The Gatekeeper"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Find Python
try {
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    Write-Host "Found Python: $pythonPath" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python or add it to PATH" -ForegroundColor Yellow
    exit 1
}

# Verify script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Script not found: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Script path: $scriptPath" -ForegroundColor Green
Write-Host ""

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Existing task removed" -ForegroundColor Green
}

# Create task action
Write-Host "Creating task action..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "-u `"$scriptPath`"" -WorkingDirectory $workingDir

# Create task trigger (at startup)
Write-Host "Creating task trigger (at startup)..." -ForegroundColor Cyan
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create task principal (run with highest privileges)
Write-Host "Creating task principal (run with highest privileges)..." -ForegroundColor Cyan
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest -LogonType ServiceAccount

# Create task settings
Write-Host "Creating task settings..." -ForegroundColor Cyan
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false

# Register the task
Write-Host "Registering scheduled task..." -ForegroundColor Cyan
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Omega Multi-AI Automation System" | Out-Null
    Write-Host "Task registered successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to register task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Task Name: $taskName" -ForegroundColor Cyan
Write-Host "Task Status: $(Get-ScheduledTask -TaskName $taskName | Select-Object -ExpandProperty State)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the task manually:" -ForegroundColor Yellow
Write-Host "  schtasks /run /tn `"$taskName`"" -ForegroundColor White
Write-Host ""
Write-Host "To create a desktop shortcut:" -ForegroundColor Yellow
Write-Host "  Right-click Desktop > New > Shortcut" -ForegroundColor White
Write-Host "  Target: schtasks /run /tn `"$taskName`"" -ForegroundColor White
Write-Host ""
