# Omega Hardware Monitor - Installation Script
# Installs LibreHardwareMonitor and pythonnet

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  OMEGA - LibreHardwareMonitor Installation          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Install pythonnet
Write-Host "[1/2] Installing Python.NET (pythonnet)..." -ForegroundColor Yellow
$venvPip = "H:/The Gatekeeper/.venv/Scripts/pip.exe"
if (Test-Path $venvPip) {
    & $venvPip install pythonnet --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      ✓ pythonnet installed successfully`n" -ForegroundColor Green
    }
    else {
        Write-Host "      ✗ pythonnet installation failed`n" -ForegroundColor Red
    }
}
else {
    Write-Host "      ✗ Virtual environment not found`n" -ForegroundColor Red
}

# Step 2: Download and install LibreHardwareMonitor
Write-Host "[2/2] Installing LibreHardwareMonitor..." -ForegroundColor Yellow

$installDir = "C:\Program Files\LibreHardwareMonitor"
$dllPath = Join-Path $installDir "LibreHardwareMonitorLib.dll"

if (Test-Path $dllPath) {
    Write-Host "      ✓ Already installed at: $installDir" -ForegroundColor Green
    $dll = Get-Item $dllPath
    Write-Host "      Size: $($dll.Length) bytes | Modified: $($dll.LastWriteTime)" -ForegroundColor Gray
}
else {
    try {
        Write-Host "      Downloading from GitHub..." -ForegroundColor Gray
        $apiUrl = "https://api.github.com/repos/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest"
        $release = Invoke-RestMethod -Uri $apiUrl -UseBasicParsing
        $zipAsset = $release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        
        if ($zipAsset) {
            Write-Host "      Found: $($zipAsset.name)" -ForegroundColor Gray
            $zipPath = Join-Path $env:TEMP "LibreHardwareMonitor.zip"
            
            Invoke-WebRequest -Uri $zipAsset.browser_download_url -OutFile $zipPath -UseBasicParsing
            Write-Host "      Downloaded successfully" -ForegroundColor Gray
            
            $extractPath = Join-Path $env:TEMP "LibreHardwareMonitor_Extract"
            if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
            
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
            Write-Host "      Extracted archive" -ForegroundColor Gray
            
            if (!(Test-Path $installDir)) {
                New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            }
            
            Copy-Item -Path "$extractPath\*" -Destination $installDir -Recurse -Force
            Write-Host "      ✓ Installed to: $installDir" -ForegroundColor Green
            
            # Cleanup
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
            
        }
        else {
            Write-Host "      ✗ No suitable release found on GitHub" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "      ✗ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verification
Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  VERIFICATION                                        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check pythonnet
Write-Host "[Test 1] Python.NET (pythonnet)..." -ForegroundColor Yellow
$venvPython = "H:/The Gatekeeper/.venv/Scripts/python.exe"
if (Test-Path $venvPython) {
    $result = & $venvPython -c "import clr; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "         ✓ Python.NET imports successfully" -ForegroundColor Green
    }
    else {
        Write-Host "         ✗ Python.NET import failed" -ForegroundColor Red
        Write-Host "         $result" -ForegroundColor Gray
    }
}

# Check LibreHardwareMonitor DLL
Write-Host "`n[Test 2] LibreHardwareMonitor DLL..." -ForegroundColor Yellow
if (Test-Path $dllPath) {
    Write-Host "         ✓ LibreHardwareMonitorLib.dll found" -ForegroundColor Green
    Write-Host "         Location: $dllPath" -ForegroundColor Gray
}
else {
    Write-Host "         ✗ LibreHardwareMonitorLib.dll NOT FOUND" -ForegroundColor Red
}

# Check LibreHardwareMonitor executable
$exePath = Join-Path $installDir "LibreHardwareMonitor.exe"
Write-Host "`n[Test 3] LibreHardwareMonitor Application..." -ForegroundColor Yellow
if (Test-Path $exePath) {
    Write-Host "         ✓ LibreHardwareMonitor.exe found" -ForegroundColor Green
    Write-Host "         Location: $exePath" -ForegroundColor Gray
}
else {
    Write-Host "         ✗ LibreHardwareMonitor.exe NOT FOUND" -ForegroundColor Red
}

# Test Omega hardware monitor
Write-Host "`n[Test 4] Omega Hardware Monitor Integration..." -ForegroundColor Yellow
if (Test-Path $venvPython) {
    $testScript = "from omega_hardware_monitor_enhanced import OmegaHardwareMonitor; m = OmegaHardwareMonitor(); print('OK'); m.close()"
    $result = & $venvPython -c $testScript 2>&1
    if ($result -match "OK") {
        Write-Host "         ✓ Hardware monitor loads successfully" -ForegroundColor Green
    }
    else {
        Write-Host "         ⚠ Hardware monitor test (see output below)" -ForegroundColor Yellow
        Write-Host "         $result" -ForegroundColor Gray
    }
}

# Next Steps
Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NEXT STEPS                                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if (Test-Path $exePath) {
    Write-Host "1. Start LibreHardwareMonitor (as Administrator):" -ForegroundColor Yellow
    Write-Host "   Start-Process '$exePath' -Verb RunAs`n" -ForegroundColor White
}

Write-Host "2. Keep LibreHardwareMonitor running in background" -ForegroundColor Yellow

Write-Host "`n3. Restart Omega web server:" -ForegroundColor Yellow
Write-Host "   python omega_control_panel_web.py --port 5000`n" -ForegroundColor White

Write-Host "4. Access dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost:5000`n" -ForegroundColor White

Write-Host "NOTE: CPU/Motherboard sensors require Administrator rights" -ForegroundColor Gray
Write-Host "`nInstallation complete!`n" -ForegroundColor Green
