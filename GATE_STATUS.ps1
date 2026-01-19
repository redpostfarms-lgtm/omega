# Gate Status Check - Quick access to system monitor dashboard
# Run this anytime to see current system health

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🔒 THE GATEKEEPER - QUICK STATUS CHECK                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$DashboardPath = "H:\The Gatekeeper\system_monitor_reports\GATE_DASHBOARD.txt"
$StatusFile = "H:\The Gatekeeper\system_monitor_reports\current_status.json"

# Check if monitoring is active
$Task = Get-ScheduledTask -TaskName "OmegaSystemMonitor" -ErrorAction SilentlyContinue

if ($Task) {
    $TaskState = $Task.State
    Write-Host "📋 Monitor Status: $TaskState" -ForegroundColor $(if ($TaskState -eq "Running") { "Green" } elseif ($TaskState -eq "Ready") { "Yellow" } else { "Red" })

    $LastRunInfo = Get-ScheduledTaskInfo -TaskName "OmegaSystemMonitor"
    if ($LastRunInfo.LastRunTime) {
        Write-Host "⏰ Last Run: $($LastRunInfo.LastRunTime)" -ForegroundColor Gray
        Write-Host "▶️  Next Run: $($LastRunInfo.NextRunTime)" -ForegroundColor Gray
    }
}
else {
    Write-Host "⚠️  System Monitor NOT INSTALLED" -ForegroundColor Red
    Write-Host "   Run: .\SETUP_SYSTEM_MONITOR.ps1" -ForegroundColor Yellow
}

Write-Host ""

# Show dashboard
if (Test-Path $DashboardPath) {
    Get-Content $DashboardPath
}
else {
    Write-Host "⚠️  Dashboard not found. Monitor may not have run yet." -ForegroundColor Yellow
    Write-Host "   Running manual scan..." -ForegroundColor Cyan
    Write-Host ""

    python "H:\The Gatekeeper\omega_system_monitor.py"
}

Write-Host ""
Write-Host "💡 Quick Commands:" -ForegroundColor Cyan
Write-Host "   • Manual scan: python 'H:\The Gatekeeper\omega_system_monitor.py'" -ForegroundColor Gray
Write-Host "   • View JSON: Get-Content '$StatusFile' | ConvertFrom-Json | ConvertTo-Json -Depth 10" -ForegroundColor Gray
Write-Host "   • Run now: Start-ScheduledTask -TaskName OmegaSystemMonitor" -ForegroundColor Gray
Write-Host ""
