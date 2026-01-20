# LED App Launcher - PowerShell Version
# Tests each LED app by launching it directly

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  LED APP LAUNCHER - Testing All Apps" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$apps = @(
    @{Name="Aura Creator"; AppID="B9ECED6F.AURAC"},
    @{Name="LED's App!"; AppID="WellKnownSoftware"},
    @{Name="Magic Light BLE"; AppID="48425Shipwreck"},
    @{Name="Smart LED WiFi"; AppID="Rython.SmartLE"},
    @{Name="RGB bulb"; AppID="622PKar.RGBbul"},
    @{Name="DarkLights"; AppID="51518DarkProje"}
)

$counter = 1
foreach ($app in $apps) {
    Write-Host "[$counter/$($apps.Count)] Launching: $($app.Name)" -ForegroundColor Yellow
    Write-Host "    AppID: $($app.AppID)" -ForegroundColor Gray

    try {
        Start-Process "shell:AppsFolder\$($app.AppID)" -ErrorAction Stop
        Write-Host "    ✓ Launched successfully!`n" -ForegroundColor Green

        # Wait and ask for response
        Start-Sleep -Seconds 3

        Write-Host "    Did the LED respond? Check your USB LED strip!" -ForegroundColor Cyan
        $response = Read-Host "    [y=YES, n=NO, s=SKIP]"

        if ($response -eq 'y') {
            Write-Host "`n    🎉 SUCCESS! $($app.Name) CONTROLS THE LED!`n" -ForegroundColor Green
            # Continue testing others
        }

    } catch {
        Write-Host "    ✗ Failed to launch: $_`n" -ForegroundColor Red
    }

    $counter++
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Testing Complete" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
