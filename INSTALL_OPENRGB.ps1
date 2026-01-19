# OpenRGB Installer for LED Control
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  OpenRGB Installation - LED Hardware Control" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "OpenRGB allows control of RGB lighting across different brands." -ForegroundColor Gray
Write-Host "Including your ASUS AURA LED Controller.`n" -ForegroundColor Gray

# Check if already installed
$openrgbPath = "C:\Program Files\OpenRGB\OpenRGB.exe"
if (Test-Path $openrgbPath) {
    Write-Host "✓ OpenRGB is already installed!" -ForegroundColor Green
    Write-Host "  Location: $openrgbPath`n" -ForegroundColor Gray
    exit
}

Write-Host "[1] Downloading OpenRGB..." -ForegroundColor Yellow
$downloadUrl = "https://openrgb.org/releases/release_0.9/OpenRGB_0.9_Windows_64_b5f46e3.zip"
$downloadPath = "$env:TEMP\OpenRGB.zip"
$extractPath = "C:\Program Files\OpenRGB"

try {
    # Download
    Write-Host "    Downloading from openrgb.org..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "    ✓ Download complete`n" -ForegroundColor Green

    # Extract
    Write-Host "[2] Installing to Program Files..." -ForegroundColor Yellow
    if (!(Test-Path $extractPath)) {
        New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
    }

    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    Write-Host "    ✓ Installation complete`n" -ForegroundColor Green

    # Cleanup
    Remove-Item $downloadPath -Force

    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  ✅ OpenRGB INSTALLED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "============================================================`n" -ForegroundColor Green

    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: .\TEST_RED_WAVE.ps1" -ForegroundColor White
    Write-Host "  2. Watch your tower LEDs for RED waves!`n" -ForegroundColor White

}
catch {
    Write-Host "`n❌ Installation failed: $_" -ForegroundColor Red
    Write-Host "`nManual installation:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://openrgb.org/downloads.html" -ForegroundColor Gray
    Write-Host "  2. Download Windows 64-bit version" -ForegroundColor Gray
    Write-Host "  3. Extract to C:\Program Files\OpenRGB" -ForegroundColor Gray
}
