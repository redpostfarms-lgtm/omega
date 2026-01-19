# Omega System Monitor - Scheduled Task Setup
# Runs every 15-20 minutes and monitors the entire Gatekeeper system

Write-Host "🔒 OMEGA SYSTEM MONITOR - SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Paths
$ProjectRoot = "H:\The Gatekeeper"
$MonitorScript = Join-Path $ProjectRoot "omega_system_monitor.py"
$PythonExe = (Get-Command python).Source
$TaskName = "OmegaSystemMonitor"
$LogDir = Join-Path $ProjectRoot "system_monitor_reports"

# Verify files exist
if (-not (Test-Path $MonitorScript)) {
    Write-Host "❌ Monitor script not found: $MonitorScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Monitor script found: $MonitorScript" -ForegroundColor Green
Write-Host "✅ Python executable: $PythonExe" -ForegroundColor Green
Write-Host ""

# Create log directory if it doesn't exist
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "✅ Created log directory: $LogDir" -ForegroundColor Green
}

# Remove existing task if it exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "🗑️  Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Write-Host ""
Write-Host "📅 Creating scheduled task..." -ForegroundColor Cyan

# Create the action (what to run)
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$MonitorScript`"" `
    -WorkingDirectory $ProjectRoot

# Create triggers (every 17 minutes - midpoint between 15-20)
$Trigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 17)

# Also trigger at system startup (after 2 minute delay)
$Trigger2 = New-ScheduledTaskTrigger -AtStartup
$Trigger2.Delay = "PT2M"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -MultipleInstances IgnoreNew

# Register the task
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger1, $Trigger2 `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Omega System Monitor - Checks health, dependencies, and auto-repairs issues every 15-20 minutes" | Out-Null

Write-Host "✅ Scheduled task created: $TaskName" -ForegroundColor Green
Write-Host ""

# Run the task immediately for the first time
Write-Host "▶️  Running initial scan..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName

# Wait a moment for it to start
Start-Sleep -Seconds 3

# Show task info
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ OMEGA SYSTEM MONITOR - ACTIVE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Task Name: $TaskName"
Write-Host "🔄 Frequency: Every 17 minutes (midpoint of 15-20 range)"
Write-Host "🚀 Startup: Runs 2 minutes after system boot"
Write-Host "📁 Reports: $LogDir"
Write-Host "📊 Dashboard: $LogDir\GATE_DASHBOARD.txt"
Write-Host ""
Write-Host "🎯 Monitored Components:"
Write-Host "   • Python packages (auto-install if missing)"
Write-Host "   • System tools (git, python, pip)"
Write-Host "   • Code syntax errors"
Write-Host "   • Git repository status"
Write-Host "   • C: drive space (auto-cleanup if low)"
Write-Host "   • CPU & RAM usage"
Write-Host ""
Write-Host "🔧 Auto-Repair Features:"
Write-Host "   • Installs missing Python packages"
Write-Host "   • Runs disk cleanup when C: < 15 GB"
Write-Host "   • Generates reports for Gate to review"
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To view current status:" -ForegroundColor Cyan
Write-Host "   Get-Content '$LogDir\GATE_DASHBOARD.txt'"
Write-Host ""
Write-Host "💡 To run manual scan:" -ForegroundColor Cyan
Write-Host "   python '$MonitorScript'"
Write-Host ""
Write-Host "💡 To view task status:" -ForegroundColor Cyan
Write-Host "   Get-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "💡 To disable monitoring:" -ForegroundColor Cyan
Write-Host "   Disable-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "💡 To remove monitoring:" -ForegroundColor Cyan
Write-Host "   Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
Write-Host ""

# Wait for initial scan to complete
Write-Host "⏳ Waiting for initial scan to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show the dashboard if it was created
$DashboardPath = Join-Path $LogDir "GATE_DASHBOARD.txt"
if (Test-Path $DashboardPath) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Get-Content $DashboardPath
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}
else {
    Write-Host "⏳ Dashboard will be available after first scan completes." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete! The Gatekeeper is now being monitored." -ForegroundColor Green
