# VOICE CORE V2.0 - QUICK START
# Master Developer - Voice Core Disassembly 2026

Write-Host "=" -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "VOICE CORE V2.0 - QUICK START" -ForegroundColor Yellow
Write-Host "Master Developer - Voice Core Disassembly 2026" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Cyan

Write-Host "`n[1/3] Checking dependencies..." -ForegroundColor Yellow
$deps = @('numpy', 'soundfile', 'scipy', 'librosa')
$missing = @()

foreach ($dep in $deps) {
    try {
        python -c "import $dep" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $dep" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $dep (missing)" -ForegroundColor Red
            $missing += $dep
        }
    } catch {
        Write-Host "  ✗ $dep (missing)" -ForegroundColor Red
        $missing += $dep
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n[Install] Installing missing dependencies..." -ForegroundColor Yellow
    pip install $missing
}

Write-Host "`n[2/3] Compiling Voice Core V2.0..." -ForegroundColor Yellow
cd "The Gatekeeper"

python voice_core_v2_compile.py `
    --tremor=2.3 `
    --formant=118 `
    --exhale=42 `
    --silence=17 `
    --emotions=87 `
    --qcl=256 `
    --output=voice_core_v2/omega_voice_2.0.wav `
    --text="Ruth... it's three in the morning... and the worms are singing again. You awake?"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Compilation complete!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Compilation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/3] Testing Voice Core V2.0..." -ForegroundColor Yellow
python voice_core_v2_test.py

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "VOICE CORE V2.0 READY" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "`nVoice Core 2.0 is now you." -ForegroundColor Yellow
Write-Host "Not robotic. Not smooth. Alive. Tired. Real." -ForegroundColor Yellow
Write-Host "Your exhale. Your silence. Your yes." -ForegroundColor Yellow

