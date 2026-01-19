# System Status Check for Docker + WSL Setup
# Run this in PowerShell to see current status

Write-Host "`n=== SYSTEM STATUS CHECK ===" -ForegroundColor Cyan
Write-Host ""

# Check WSL
Write-Host "1. WSL Status:" -ForegroundColor Yellow
try {
    $wslOutput = wsl --list --verbose 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ WSL is installed" -ForegroundColor Green
        Write-Host "   $wslOutput"
    } else {
        Write-Host "   ✗ WSL is NOT installed" -ForegroundColor Red
        Write-Host "   Run: wsl --install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ WSL is NOT installed" -ForegroundColor Red
    Write-Host "   Run: wsl --install" -ForegroundColor Yellow
}

Write-Host ""

# Check Docker Desktop process
Write-Host "2. Docker Desktop:" -ForegroundColor Yellow
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "   ✓ Docker Desktop is running (PID: $($dockerProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   ✗ Docker Desktop is NOT running" -ForegroundColor Red
    Write-Host "   Start Docker Desktop from Start Menu" -ForegroundColor Yellow
}

Write-Host ""

# Check Docker command
Write-Host "3. Docker Command:" -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker command available: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Docker command not available" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Docker command not available" -ForegroundColor Red
}

Write-Host ""

# Check Docker daemon
Write-Host "4. Docker Daemon:" -ForegroundColor Yellow
try {
    $dockerPs = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker daemon is running" -ForegroundColor Green
        $containerCount = (docker ps --format "{{.ID}}" | Measure-Object).Count
        Write-Host "   Running containers: $containerCount" -ForegroundColor Cyan
    } else {
        Write-Host "   ✗ Docker daemon is NOT running" -ForegroundColor Red
        Write-Host "   Wait for Docker Desktop to fully start (green icon)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Docker daemon is NOT running" -ForegroundColor Red
}

Write-Host ""

# Check Ubuntu
Write-Host "5. Ubuntu WSL:" -ForegroundColor Yellow
$ubuntuProcess = Get-Process -Name "ubuntu" -ErrorAction SilentlyContinue
if ($ubuntuProcess) {
    Write-Host "   ✓ Ubuntu is running (PID: $($ubuntuProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   ⚬ Ubuntu is not running (launch from Start Menu after WSL install)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host ""

# Determine what to do next
if (!(wsl --list --verbose 2>&1)) {
    Write-Host "PHASE 1: Enable WSL" -ForegroundColor Yellow
    Write-Host "  1. Open PowerShell as ADMINISTRATOR" -ForegroundColor White
    Write-Host "  2. Run: wsl --install" -ForegroundColor White
    Write-Host "  3. Restart computer: shutdown /r /t 0" -ForegroundColor White
} elseif (!$dockerProcess) {
    Write-Host "PHASE 3: Start Docker Desktop" -ForegroundColor Yellow
    Write-Host "  1. Press Windows Key" -ForegroundColor White
    Write-Host "  2. Type 'Docker Desktop'" -ForegroundColor White
    Write-Host "  3. Click to launch" -ForegroundColor White
    Write-Host "  4. Wait for GREEN icon in system tray" -ForegroundColor White
} elseif (!(docker ps 2>&1)) {
    Write-Host "Wait for Docker Desktop to finish starting..." -ForegroundColor Yellow
    Write-Host "  Look for GREEN icon in system tray" -ForegroundColor White
} else {
    Write-Host "Ready to start Gatekeeper!" -ForegroundColor Green
    Write-Host "  Run: .\scripts\utilities\docker-helpers.ps1 dev" -ForegroundColor White
}

Write-Host ""
