# File Manager Launcher for Gatekeeper System
# PowerShell Version - Starts the file manager web server and opens the UI

param(
    [int]$Port = 5001,
    [string]$Host = "localhost"
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Gatekeeper File Manager v1.0" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ to continue" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Flask is installed
Write-Host ""
Write-Host "Checking for required packages..." -ForegroundColor Yellow

try {
    python -c "import flask" 2>&1 | Out-Null
    Write-Host "Flask is installed" -ForegroundColor Green
}
catch {
    Write-Host "Installing Flask and Flask-CORS..." -ForegroundColor Yellow
    pip install flask flask-cors
}

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Construct URLs
$apiUrl = "http://$Host`:$Port"
$uiUrl = "$apiUrl/file_manager_ui.html"

Write-Host ""
Write-Host "Starting File Manager Server..." -ForegroundColor Yellow
Write-Host "API Server: $apiUrl" -ForegroundColor Cyan
Write-Host "UI Address: $uiUrl" -ForegroundColor Cyan
Write-Host ""

# Wait a moment before opening browser
Start-Sleep -Seconds 1

# Open UI in default browser
Write-Host "Opening UI in default browser..." -ForegroundColor Yellow
Start-Process $uiUrl

# Start the server (this will block)
Write-Host ""
Write-Host "Starting server (press Ctrl+C to stop)..." -ForegroundColor Yellow
Write-Host ""

python gatekeeper_file_manager_web.py --host $Host --port $Port

Write-Host ""
Write-Host "File Manager stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
