# OpenRGB Installation and Setup
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  OpenRGB Installation - Full LED Control" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$downloadUrl = "https://openrgb.org/releases/release_0.9/OpenRGB_0.9_Windows_64_b5f46e3.zip"
$downloadPath = "$env:TEMP\OpenRGB.zip"
$extractPath = "C:\Program Files\OpenRGB"
$exePath = "$extractPath\OpenRGB.exe"

Write-Host "[1] Downloading OpenRGB..." -ForegroundColor Yellow
Write-Host "    URL: $downloadUrl" -ForegroundColor Gray

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "    ✓ Downloaded to: $downloadPath`n" -ForegroundColor Green

    Write-Host "[2] Installing to Program Files..." -ForegroundColor Yellow

    if (!(Test-Path $extractPath)) {
        New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
    }

    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    Write-Host "    ✓ Extracted to: $extractPath`n" -ForegroundColor Green

    # Cleanup
    Remove-Item $downloadPath -Force

    Write-Host "[3] Installing Python API..." -ForegroundColor Yellow
    python -m pip install openrgb-python --quiet
    Write-Host "    ✓ openrgb-python installed`n" -ForegroundColor Green

    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  ✅ OpenRGB INSTALLED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "============================================================`n" -ForegroundColor Green

    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Close Armoury Crate (optional but recommended)" -ForegroundColor White
    Write-Host "  2. Run: python test_openrgb_red_wave.py" -ForegroundColor White
    Write-Host "  3. Watch your LED for RED waves!`n" -ForegroundColor White

    # Start OpenRGB in server mode
    Write-Host "[4] Starting OpenRGB in server mode..." -ForegroundColor Yellow
    Start-Process -FilePath $exePath -ArgumentList "--server" -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "    ✓ OpenRGB server running (SDK port 6742)`n" -ForegroundColor Green

}
catch {
    Write-Host "`n❌ Installation failed: $_" -ForegroundColor Red
    Write-Host "`nManual installation:" -ForegroundColor Yellow
    Write-Host "  1. Download: $downloadUrl" -ForegroundColor Gray
    Write-Host "  2. Extract to: $extractPath" -ForegroundColor Gray
    Write-Host "  3. Run: $exePath --server" -ForegroundColor Gray
}
