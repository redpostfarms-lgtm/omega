# Setup Omega Resource Optimizer - Auto-runs to keep memory optimized
# Enforces GPU/CPU priority processing strategy

$pythonPath = "C:\Users\Drakalich\AppData\Local\Programs\Python\Python311\python.exe"
$scriptPath = "H:\The Gatekeeper\omega_resource_optimizer.py"
$taskName = "OmegaResourceOptimizer"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   OMEGA RESOURCE OPTIMIZER SETUP" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python exists
if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please update the path in this script" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK Python found: $pythonPath" -ForegroundColor Green
Write-Host "OK Script found: $scriptPath" -ForegroundColor Green
Write-Host ""

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory "H:\The Gatekeeper"

# Create triggers: Every 20 minutes + at startup
$trigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 20)
$trigger2 = New-ScheduledTaskTrigger -AtStartup -RandomDelay (New-TimeSpan -Minutes 2)

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

# Create principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest

# Register the task
Write-Host "Creating scheduled task..." -ForegroundColor Yellow
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger1, $trigger2 -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "OK Task created successfully" -ForegroundColor Green
Write-Host ""

# Run initial optimization
Write-Host "Running initial optimization..." -ForegroundColor Yellow
Write-Host ""
& $pythonPath $scriptPath
Write-Host ""

# Show task info
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "   OMEGA RESOURCE OPTIMIZER ACTIVE" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "   - Runs every 20 minutes automatically"
Write-Host "   - Runs 2 minutes after system startup"
Write-Host "   - Enforces GPU [60 percent] + CPU [40 percent] processing"
Write-Host "   - Limits RAM to 512 MB cache"
Write-Host "   - Triggers cleanup when memory above 80 percent"
Write-Host ""
Write-Host "Strategy:" -ForegroundColor Cyan
Write-Host "   - GPU Priority: 60 percent"
Write-Host "   - CPU Usage: 40 percent"
Write-Host "   - RAM Cache Limit: 512 MB"
Write-Host "   - Memory Threshold: 85 percent"
Write-Host "   - Aggressive Cleanup: above 80 percent"
Write-Host ""
Write-Host "Logs:" -ForegroundColor Cyan
Write-Host "   H:\The Gatekeeper\system_monitor_reports\resource_optimizer_log.txt"
Write-Host ""
Write-Host "Next automatic run in 20 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check status:" -ForegroundColor Gray
Write-Host "  Get-ScheduledTask -TaskName OmegaResourceOptimizer" -ForegroundColor Gray
Write-Host ""
Write-Host "To run manually:" -ForegroundColor Gray
Write-Host "  python omega_resource_optimizer.py" -ForegroundColor Gray
Write-Host ""
