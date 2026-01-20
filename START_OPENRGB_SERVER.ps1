# Start OpenRGB Server (as Administrator)
# Improved version with process checking and port verification

param (
    [string]$OpenRGBPath = "C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe",
    [int]$Port = 6742
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param ([string]$Title)
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "============================================================`n" -ForegroundColor Cyan
}

function Write-Status {
    param ([string]$Message, [string]$Color = "Gray")
    Write-Host "  $Message" -ForegroundColor $Color
}

function Write-Success {
    param ([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param ([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

Write-Header "Starting OpenRGB Server"

# 1. Validate Path
if (!(Test-Path $OpenRGBPath)) {
    Write-ErrorMsg "OpenRGB executable not found at: $OpenRGBPath"
    Write-Status "Please check the path and try again." "Yellow"
    exit 1
}

# 2. Check if already running
$processName = [System.IO.Path]::GetFileNameWithoutExtension($OpenRGBPath)
$runningProcess = Get-Process -Name $processName -ErrorAction SilentlyContinue

if ($runningProcess) {
    Write-Status "OpenRGB process found (PID: $($runningProcess.Id))." "Yellow"
    
    # Check if port is listening
    $isListening = $false
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connections) { $isListening = $true }
    } catch {
        # Ignore errors checking port
    }

    if ($isListening) {
        Write-Success "OpenRGB Server is already listening on port $Port."
        Write-Header "Ready for LED control!"
        exit 0
    } else {
        Write-Status "Process is running but port $Port is not listening." "Yellow"
        Write-Status "Restarting OpenRGB in server mode..." "Yellow"
        Stop-Process -Id $runningProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# 3. Start Process
Write-Status "Starting OpenRGB server as Administrator..." "Yellow"
Write-Status "(Required for I2C/SMBus access to AURA LED Controller)" "Gray"

try {
    # Start as admin in server mode
    $argList = "--server", "--server-port $Port"
    Start-Process -FilePath $OpenRGBPath -ArgumentList $argList -Verb RunAs -WindowStyle Minimized
    
    # 4. Wait for startup and verify
    Write-Status "Waiting for server to initialize..." "Gray"
    
    $retries = 10
    $connected = $false
    
    for ($i = 1; $i -le $retries; $i++) {
        Start-Sleep -Seconds 1
        try {
            $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
            if ($connections) {
                $connected = $true
                break
            }
        } catch {
            # Ignore
        }
    }

    if ($connected) {
        Write-Success "OpenRGB server started successfully."
        Write-Status "Port: $Port" "Gray"
        Write-Status "Mode: Server (SDK enabled)" "Gray"
        
        Write-Header "Ready for LED control!"
        
        Write-Host "Next: Run the RED WAVE test" -ForegroundColor Cyan
        Write-Host "    cd 'H:\The Gatekeeper'" -ForegroundColor White
        Write-Host "    python test_openrgb_red_wave.py`n" -ForegroundColor White
    } else {
        Write-ErrorMsg "OpenRGB started but the server port ($Port) is not listening yet."
        Write-Status "It might still be initializing. Please check the OpenRGB window." "Yellow"
    }

} catch {
    Write-ErrorMsg "Failed to start OpenRGB: $_"
    exit 1
}
