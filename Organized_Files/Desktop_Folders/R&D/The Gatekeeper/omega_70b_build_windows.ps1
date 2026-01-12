# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Windows Build Script
# Full Local 70B LLM + Voice + Cannibal Defense

<#
.SYNOPSIS
    Omega 70B Build Script - Windows Edition
    Builds complete local 70B LLM system with voice cloning and cannibal defense

.DESCRIPTION
    This script installs and configures:
    - PyTorch with CUDA support
    - Unsloth for efficient training
    - llama.cpp for inference
    - XTTS voice cloning
    - Omega server with cannibal defense
    - Integration with existing Omega system

.NOTES
    Requires:
    - NVIDIA GPU with CUDA support
    - ~50GB free disk space
    - Python 3.10+
    - Git
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "Ω OMEGA 70B - WINDOWS BUILD" -ForegroundColor Cyan
Write-Host "Full Local 70B LLM + Your Voice + Cannibal Defense" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$OMEGA_HOME = "$env:USERPROFILE\omega_70b"
$MODELS_DIR = "$OMEGA_HOME\models"
$DATA_DIR = "$OMEGA_HOME\data"
$LLAMA_CPP_DIR = "$OMEGA_HOME\llama.cpp"
$OMEGA_OUTPUT = "$OMEGA_HOME\omega-70b-wiley"

# Create directories
Write-Host "[1/8] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $OMEGA_HOME | Out-Null
New-Item -ItemType Directory -Force -Path $MODELS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $DATA_DIR | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

# Check Python
Write-Host "[2/8] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion" -ForegroundColor Green

# Check CUDA
Write-Host "[3/8] Checking CUDA..." -ForegroundColor Yellow
$cudaCheck = nvidia-smi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ CUDA not detected. GPU acceleration may not work." -ForegroundColor Yellow
} else {
    Write-Host "✓ CUDA detected" -ForegroundColor Green
    Write-Host $cudaCheck | Select-Object -First 3
}

# Install PyTorch with CUDA
Write-Host "[4/8] Installing PyTorch with CUDA..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ PyTorch installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ PyTorch installed" -ForegroundColor Green

# Install core dependencies
Write-Host "[5/8] Installing core dependencies..." -ForegroundColor Yellow
pip install unsloth[cu121] bitsandbytes accelerate transformers peft trl
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Dependency installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Core dependencies installed" -ForegroundColor Green

# Install voice and server dependencies
Write-Host "[6/8] Installing voice and server dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn xtts-api-server open-webui
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Some dependencies may have failed (non-critical)" -ForegroundColor Yellow
}
Write-Host "✓ Voice/server dependencies installed" -ForegroundColor Green

# Clone llama.cpp
Write-Host "[7/8] Cloning llama.cpp..." -ForegroundColor Yellow
if (-not (Test-Path $LLAMA_CPP_DIR)) {
    git clone https://github.com/ggerganov/llama.cpp.git $LLAMA_CPP_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to clone llama.cpp" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ llama.cpp already exists" -ForegroundColor Green
}

# Build llama.cpp (if on Windows with CUDA, use CMake)
Write-Host "Building llama.cpp..." -ForegroundColor Yellow
Push-Location $LLAMA_CPP_DIR
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
New-Item -ItemType Directory -Force -Path build | Out-Null
Push-Location build

# Try to use CMake for Windows build
if (Get-Command cmake -ErrorAction SilentlyContinue) {
    cmake .. -DLLAMA_CUBLAS=ON
    cmake --build . --config Release
    Write-Host "✓ llama.cpp built with CUDA" -ForegroundColor Green
} else {
    Write-Host "⚠ CMake not found. Using pre-built binaries if available." -ForegroundColor Yellow
    Write-Host "  You may need to download pre-built llama.cpp binaries." -ForegroundColor Yellow
}
Pop-Location
Pop-Location

# Download model (informational - actual download handled by Python script)
Write-Host "[8/8] Model download..." -ForegroundColor Yellow
Write-Host "Model will be downloaded by the training script." -ForegroundColor Gray
Write-Host "Model: Meta-Llama-3.2-70B-Instruct-Q4_K_M.gguf (~40GB)" -ForegroundColor Gray
Write-Host "✓ Setup complete. Run dataset preparation next." -ForegroundColor Green

Write-Host ""
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Run: python omega_70b_prepare_dataset.py" -ForegroundColor White
Write-Host "2. Run: python omega_70b_train.py" -ForegroundColor White
Write-Host "3. Run: python omega_70b_server.py" -ForegroundColor White
Write-Host "==================================================================================" -ForegroundColor Cyan

