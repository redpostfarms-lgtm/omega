# RED WAVE LED Test - PowerShell Version
# Enhanced with error handling, parameter validation, and progress tracking
[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Path to OpenRGB executable")]
    [ValidateScript({
            if (-not (Test-Path $_)) {
                throw "OpenRGB executable not found at path: $_"
            }
            return $true
        })]
    [string]$OpenRGBPath = "C:\Program Files\OpenRGB\OpenRGB.exe",

    [Parameter(HelpMessage = "Duration of wave pattern in seconds")]
    [ValidateRange(5, 60)]
    [int]$WaveDuration = 10,

    [Parameter(HelpMessage = "Timeout for OpenRGB commands in seconds")]
    [ValidateRange(1, 30)]
    [int]$CommandTimeout = 5
)

Write-Host "`n============================================================" -ForegroundColor Red
Write-Host "  RED WAVE LED TEST - Physical Hardware Control" -ForegroundColor Red
Write-Host "============================================================`n" -ForegroundColor Red

# Step 1: Check for AURA LED Controller with improved error handling
Write-Verbose "[1] Detecting AURA LED Controller..."
Write-Host "[1] Detecting AURA LED Controller..." -ForegroundColor Cyan

# Fixed Issue 1 (Low): Better device detection with multiple match handling
$auraDevices = Get-PnpDevice | Where-Object {
    $_.FriendlyName -like "*AURA*" -or $_.InstanceId -like "*VID_0B05*"
}

if ($auraDevices) {
    # Handle multiple devices - select first one
    $auraDevice = $auraDevices | Select-Object -First 1

    Write-Host "    ✓ Found: $($auraDevice.FriendlyName)" -ForegroundColor Green
    Write-Host "    Status: $($auraDevice.Status)" -ForegroundColor Green
    Write-Host "    Instance: $($auraDevice.InstanceId)" -ForegroundColor Gray

    if ($auraDevices.Count -gt 1) {
        Write-Verbose "Multiple AURA devices found. Using first match."
        Write-Host "    ℹ️ Note: $($auraDevices.Count) AURA devices detected, using first one" -ForegroundColor Yellow
    }
}
else {
    Write-Host "    ✗ AURA LED Controller not found" -ForegroundColor Red
    Write-Host "    Searched for: Devices with 'AURA' name or VID_0B05" -ForegroundColor Gray
    exit 1
}

# Step 2: Check for OpenRGB with security validation
Write-Verbose "[2] Validating OpenRGB..."
Write-Host "`n[2] Checking for OpenRGB..." -ForegroundColor Cyan
if (Test-Path $OpenRGBPath) {
    Write-Host "    ✓ OpenRGB found at: $OpenRGBPath" -ForegroundColor Green

    # Fixed Issue 3 (Medium): Security - Validate executable signature
    Write-Verbose "Validating OpenRGB executable signature..."
    try {
        $signature = Get-AuthenticodeSignature -FilePath $OpenRGBPath -ErrorAction Stop
        Write-Verbose "Signature status: $($signature.Status)"

        # Note: OpenRGB may not be signed, so we check but don't fail
        if ($signature.Status -eq 'Valid') {
            Write-Host "    ✓ Digital signature verified" -ForegroundColor Green
        }
        elseif ($signature.Status -eq 'NotSigned') {
            Write-Host "    ⚠️ OpenRGB executable is not digitally signed" -ForegroundColor Yellow
            Write-Host "    Continuing anyway (common for open-source tools)" -ForegroundColor Gray
        }
        else {
            Write-Warning "OpenRGB signature status: $($signature.Status). Proceeding with caution."
        }
    }
    catch {
        Write-Verbose "Could not verify signature: $_"
    }

    # Try to list devices with timeout
    Write-Verbose "Listing OpenRGB devices..."
    try {
        # Fixed Issue 1 (Medium): Add timeout for OpenRGB commands
        $job = Start-Job -ScriptBlock {
            param($path)
            & $path --list-devices 2>&1
        } -ArgumentList $OpenRGBPath

        $devices = Wait-Job $job -Timeout $CommandTimeout | Receive-Job
        Remove-Job $job -Force

        if ($devices) {
            Write-Host "`n    OpenRGB Devices:" -ForegroundColor Yellow
            Write-Host $devices
        }
    }
    catch {
        Write-Host "    ⚠️ Could not list OpenRGB devices: $_" -ForegroundColor Yellow
        Write-Verbose "Device listing error: $_"
    }

    # Try RED wave pattern
    Write-Host "`n[3] Attempting RED wave pattern via OpenRGB..." -ForegroundColor Cyan
    Write-Host "    Duration: $WaveDuration seconds" -ForegroundColor Gray
    Write-Host "    Command Timeout: $CommandTimeout seconds" -ForegroundColor Gray
    Write-Host "    Pattern: RED color pulse" -ForegroundColor Gray
    Write-Host ""

    $iterations = [int]($WaveDuration * 2) # 2 iterations per second

    for ($i = 0; $i -lt $iterations; $i++) {
        $intensity = [math]::Abs([math]::Sin($i * 0.3)) * 255
        $intensity = [int]$intensity

        # Set RED color
        $hexColor = ("{0:X2}0000" -f $intensity)

        # Fixed Issue 3 (Low): Add progress indication
        $percentComplete = [int](($i / $iterations) * 100)
        Write-Progress -Activity "Running RED wave pattern" `
            -Status "Wave $($i + 1)/$iterations - Intensity: $intensity" `
            -PercentComplete $percentComplete

        Write-Verbose "Setting color: #$hexColor (Intensity: $intensity)"
        Write-Host ("    Wave #{0:D2}: RED intensity {1:D3}/255 (#{2})" -f ($i + 1), $intensity, $hexColor) -ForegroundColor Red

        try {
            # Fixed Issue 1 (Medium): Execute with timeout
            $job = Start-Job -ScriptBlock {
                param($path, $color)
                & $path --color $color 2>&1 | Out-Null
            } -ArgumentList $OpenRGBPath, $hexColor

            $result = Wait-Job $job -Timeout $CommandTimeout
            Remove-Job $job -Force

            if (-not $result) {
                Write-Verbose "Command timed out after $CommandTimeout seconds"
                Write-Host "    ⚠️ Command timed out" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Verbose "Command error: $_"
            Write-Host "    ⚠️ Command failed: $_" -ForegroundColor Yellow
        }

        Start-Sleep -Milliseconds 500
    }

    Write-Progress -Activity "Running RED wave pattern" -Completed

}
else {
    Write-Host "    ✗ OpenRGB not found at: $OpenRGBPath" -ForegroundColor Red
    Write-Host "    Install from: https://openrgb.org" -ForegroundColor Gray
    Write-Host "    Or specify custom path with -OpenRGBPath parameter" -ForegroundColor Gray
    exit 1
}

Write-Host "`n============================================================" -ForegroundColor Red
Write-Host "  TEST COMPLETE" -ForegroundColor Red
Write-Host "============================================================`n" -ForegroundColor Red

Write-Host "Did you see RED waves on your LED hardware?" -ForegroundColor Yellow
Write-Host "  - Look at the physical LED strip on your tower" -ForegroundColor Gray
Write-Host "  - RED color should have pulsed/waved" -ForegroundColor Gray
