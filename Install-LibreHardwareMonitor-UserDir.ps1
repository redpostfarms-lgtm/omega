# Omega Hardware Monitor - User Directory Installation
# Installs LibreHardwareMonitor to user directory (no admin needed)

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  OMEGA - LibreHardwareMonitor Installation (User Mode)" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Install to user directory instead of Program Files
$installDir = Join-Path $env:USERPROFILE "LibreHardwareMonitor"
$dllPath = Join-Path $installDir "LibreHardwareMonitorLib.dll"

Write-Host "[1/1] Installing LibreHardwareMonitor..." -ForegroundColor Yellow
Write-Host "      Target: $installDir" -ForegroundColor Gray

if (Test-Path $dllPath) {
    Write-Host "      [OK] Already installed" -ForegroundColor Green
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
            if (Test-Path $extractPath) {
                Remove-Item $extractPath -Recurse -Force
            }
            
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
            Write-Host "      Extracted archive" -ForegroundColor Gray
            
            if (!(Test-Path $installDir)) {
                New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            }
            
            Copy-Item -Path "$extractPath\*" -Destination $installDir -Recurse -Force
            Write-Host "      [OK] Installed to: $installDir" -ForegroundColor Green
            
            # Cleanup
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
            
        }
        else {
            Write-Host "      [ERROR] No suitable release found on GitHub" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "      [ERROR] Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verification
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Check LibreHardwareMonitor DLL
Write-Host "[Test 1] LibreHardwareMonitor DLL..." -ForegroundColor Yellow
if (Test-Path $dllPath) {
    Write-Host "         [OK] LibreHardwareMonitorLib.dll found" -ForegroundColor Green
    Write-Host "         Location: $dllPath" -ForegroundColor Gray
}
else {
    Write-Host "         [ERROR] LibreHardwareMonitorLib.dll NOT FOUND" -ForegroundColor Red
}

# Check LibreHardwareMonitor executable
$exePath = Join-Path $installDir "LibreHardwareMonitor.exe"
Write-Host "`n[Test 2] LibreHardwareMonitor Application..." -ForegroundColor Yellow
if (Test-Path $exePath) {
    Write-Host "         [OK] LibreHardwareMonitor.exe found" -ForegroundColor Green
    Write-Host "         Location: $exePath" -ForegroundColor Gray
}
else {
    Write-Host "         [ERROR] LibreHardwareMonitor.exe NOT FOUND" -ForegroundColor Red
}

# Check pythonnet
Write-Host "`n[Test 3] Python.NET (pythonnet)..." -ForegroundColor Yellow
$venvPython = "H:/The Gatekeeper/.venv/Scripts/python.exe"
if (Test-Path $venvPython) {
    $result = & $venvPython -c "import clr; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "         [OK] Python.NET imports successfully" -ForegroundColor Green
    }
    else {
        Write-Host "         [ERROR] Python.NET import failed" -ForegroundColor Red
    }
}

# Test Omega hardware monitor with new path
Write-Host "`n[Test 4] Omega Hardware Monitor Integration..." -ForegroundColor Yellow
if (Test-Path $venvPython) {
    $testScript = "from omega_hardware_monitor_enhanced import OmegaHardwareMonitor; m = OmegaHardwareMonitor(); print('OK'); m.close()"
    $result = & $venvPython -c $testScript 2>&1
    if ($result -match "OK") {
        Write-Host "         [OK] Hardware monitor loads successfully" -ForegroundColor Green
    }
    else {
        Write-Host "         [WARNING] Hardware monitor test (see output below)" -ForegroundColor Yellow
        Write-Host "         $result" -ForegroundColor Gray
    }
}

# Next Steps
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

if (Test-Path $exePath) {
    Write-Host "1. Start LibreHardwareMonitor (as Administrator for full sensors):" -ForegroundColor Yellow
    Write-Host "   Start-Process '$exePath' -Verb RunAs`n" -ForegroundColor White
    Write-Host "   OR run without admin (limited sensors):" -ForegroundColor Yellow
    Write-Host "   Start-Process '$exePath'`n" -ForegroundColor White
}

Write-Host "2. Keep LibreHardwareMonitor running in background" -ForegroundColor Yellow

Write-Host "`n3. Update omega_hardware_monitor_enhanced.py with new path:" -ForegroundColor Yellow
Write-Host "   DLL path: $dllPath`n" -ForegroundColor White

Write-Host "4. Restart Omega web server:" -ForegroundColor Yellow
Write-Host "   python omega_control_panel_web.py --port 5000`n" -ForegroundColor White

Write-Host "5. Access dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost:5000`n" -ForegroundColor White

Write-Host "NOTE: For full CPU/Motherboard sensors, run LibreHardwareMonitor as Admin" -ForegroundColor Gray
Write-Host "`nInstallation complete!`n" -ForegroundColor Green
