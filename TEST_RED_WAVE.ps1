# RED WAVE LED Test - PowerShell Version
Write-Host "`n============================================================" -ForegroundColor Red
Write-Host "  RED WAVE LED TEST - Physical Hardware Control" -ForegroundColor Red
Write-Host "============================================================`n" -ForegroundColor Red

# Step 1: Check for AURA LED Controller
Write-Host "[1] Detecting AURA LED Controller..." -ForegroundColor Cyan
$auraDevice = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*AURA*" -or $_.InstanceId -like "*VID_0B05*" }

if ($auraDevice) {
    Write-Host "    ✓ Found: $($auraDevice.FriendlyName)" -ForegroundColor Green
    Write-Host "    Status: $($auraDevice.Status)" -ForegroundColor Green
    Write-Host "    Instance: $($auraDevice.InstanceId)" -ForegroundColor Gray
}
else {
    Write-Host "    ✗ AURA LED Controller not found" -ForegroundColor Red
    exit
}

# Step 2: Check for OpenRGB
Write-Host "`n[2] Checking for OpenRGB..." -ForegroundColor Cyan
$openrgbPath = "C:\Program Files\OpenRGB\OpenRGB.exe"
if (Test-Path $openrgbPath) {
    Write-Host "    ✓ OpenRGB found at: $openrgbPath" -ForegroundColor Green

    # Try to list devices
    try {
        $devices = & $openrgbPath --list-devices 2>&1
        Write-Host "`n    OpenRGB Devices:" -ForegroundColor Yellow
        Write-Host $devices
    }
    catch {
        Write-Host "    ⚠️ Could not list OpenRGB devices" -ForegroundColor Yellow
    }

    # Try RED wave pattern
    Write-Host "`n[3] Attempting RED wave pattern via OpenRGB..." -ForegroundColor Cyan
    Write-Host "    Duration: 10 seconds" -ForegroundColor Gray
    Write-Host "    Pattern: RED color pulse" -ForegroundColor Gray
    Write-Host ""

    for ($i = 0; $i -lt 20; $i++) {
        $intensity = [math]::Abs([math]::Sin($i * 0.3)) * 255
        $intensity = [int]$intensity

        # Set RED color
        $hexColor = ("{0:X2}0000" -f $intensity)
        Write-Host ("    Wave #{0:D2}: RED intensity {1:D3}/255 (#{2})" -f ($i + 1), $intensity, $hexColor) -ForegroundColor Red

        try {
            & $openrgbPath --color $hexColor 2>&1 | Out-Null
        }
        catch {
            Write-Host "    ⚠️ Command failed" -ForegroundColor Yellow
        }

        Start-Sleep -Milliseconds 500
    }

}
else {
    Write-Host "    ✗ OpenRGB not found" -ForegroundColor Red
    Write-Host "    Install from: https://openrgb.org" -ForegroundColor Gray
}

Write-Host "`n============================================================" -ForegroundColor Red
Write-Host "  TEST COMPLETE" -ForegroundColor Red
Write-Host "============================================================`n" -ForegroundColor Red

Write-Host "Did you see RED waves on your LED hardware?" -ForegroundColor Yellow
Write-Host "  - Look at the physical LED strip on your tower" -ForegroundColor Gray
Write-Host "  - RED color should have pulsed/waved" -ForegroundColor Gray
