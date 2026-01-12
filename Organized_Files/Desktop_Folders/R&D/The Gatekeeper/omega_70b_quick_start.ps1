# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Quick Start Script
# One-command setup and launch

<#
.SYNOPSIS
    Omega 70B Quick Start - Complete setup and launch

.DESCRIPTION
    This script runs the complete Omega 70B setup:
    1. Builds environment
    2. Prepares dataset
    3. Starts training (if needed)
    4. Launches server
    5. Integrates voice

.PARAMETER SkipBuild
    Skip the build step (if already built)

.PARAMETER SkipTraining
    Skip training (if model already exists)

.PARAMETER VoiceOnly
    Only start voice integration (assumes server is running)
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipTraining,
    [switch]$VoiceOnly
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "Ω OMEGA 70B - QUICK START" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

$GATE = Split-Path -Parent $MyInvocation.MyCommand.Path
$OMEGA_HOME = "$env:USERPROFILE\omega_70b"
$MODEL_FILE = "$OMEGA_HOME\models\omega-70b-wiley.gguf"

# Step 1: Build (unless skipped)
if (-not $SkipBuild -and -not $VoiceOnly) {
    Write-Host "[1/5] Building environment..." -ForegroundColor Yellow
    & "$GATE\omega_70b_build_windows.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Build failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/5] Build skipped" -ForegroundColor Gray
}

# Step 2: Prepare dataset (unless voice only)
if (-not $VoiceOnly) {
    Write-Host "[2/5] Preparing dataset..." -ForegroundColor Yellow
    python "$GATE\omega_70b_prepare_dataset.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Dataset preparation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/5] Dataset preparation skipped" -ForegroundColor Gray
}

# Step 3: Train (if model doesn't exist and not skipped)
if (-not $SkipTraining -and -not $VoiceOnly) {
    if (-not (Test-Path $MODEL_FILE)) {
        Write-Host "[3/5] Training model..." -ForegroundColor Yellow
        Write-Host "This will take ~4 hours. Starting training..." -ForegroundColor Gray
        python "$GATE\omega_70b_train.py"
        
        # Note: Actual training happens in separate script
        Write-Host "Training script created. Run it manually:" -ForegroundColor Yellow
        Write-Host "  python $OMEGA_HOME\train_omega.py" -ForegroundColor White
        Write-Host ""
        Write-Host "After training, run merge:" -ForegroundColor Yellow
        Write-Host "  python $GATE\omega_70b_merge.py" -ForegroundColor White
    } else {
        Write-Host "[3/5] Model already exists - skipping training" -ForegroundColor Green
    }
} else {
    Write-Host "[3/5] Training skipped" -ForegroundColor Gray
}

# Step 4: Start server (if model exists)
if (Test-Path $MODEL_FILE) {
    Write-Host "[4/5] Starting Omega 70B server..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "$GATE\omega_70b_server.py" -WindowStyle Normal
    Write-Host "✓ Server starting in new window" -ForegroundColor Green
    Start-Sleep -Seconds 3
} else {
    Write-Host "[4/5] Model not found - cannot start server" -ForegroundColor Yellow
    Write-Host "  Complete training first, then run this script again" -ForegroundColor Gray
}

# Step 5: Voice integration
Write-Host "[5/5] Setting up voice integration..." -ForegroundColor Yellow
Start-Process python -ArgumentList "$GATE\omega_70b_voice_integration.py" -WindowStyle Normal
Write-Host "✓ Voice integration starting in new window" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "✓ OMEGA 70B QUICK START COMPLETE" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server: http://localhost:8000" -ForegroundColor White
Write-Host "Voice:  http://localhost:9999" -ForegroundColor White
Write-Host ""
Write-Host "Test with:" -ForegroundColor Yellow
Write-Host '  python -c "import requests; print(requests.post(''http://localhost:8000/v1/chat/completions'', json={''messages'':[{''role'':''user'',''content'':''Hello Omega''}]}).json())"' -ForegroundColor Gray

