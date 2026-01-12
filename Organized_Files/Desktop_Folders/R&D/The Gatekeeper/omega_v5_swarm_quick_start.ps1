# OMEGA V5 SWARM - QUICK START
# Red Post Farms, LLC - Copyright (c) 2025-2026

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "  OMEGA V5 SWARM - QUICK START" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install dependencies
Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
python omega_v5_swarm_setup.py

Write-Host ""
Write-Host "Step 2: Configuration created" -ForegroundColor Green
Write-Host "  Edit: omega_swarm/swarm_config.json" -ForegroundColor White
Write-Host "  Add targets and configure settings" -ForegroundColor White

Write-Host ""
Write-Host "Step 3: Add proxies (optional)" -ForegroundColor Yellow
Write-Host "  Edit: omega_swarm/proxies.txt" -ForegroundColor White
Write-Host "  Format: ip:port:username:password" -ForegroundColor White

Write-Host ""
Write-Host "Step 4: Ready to run" -ForegroundColor Green
Write-Host "  python omega_v5_swarm.py" -ForegroundColor White

Write-Host ""
Write-Host "Killswitch: touch omega_swarm/kill.omega" -ForegroundColor Yellow
Write-Host ""
