# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# OMEGA - AUTO-HARDWARE BUILD 2026 (Fixed Version)

$ErrorActionPreference = "Stop"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "OMEGA - AUTO-HARDWARE BUILD 2026" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

$OMEGA_HOME = Join-Path $env:USERPROFILE "omega_70b"
New-Item -ItemType Directory -Force -Path $OMEGA_HOME | Out-Null

$HARDWARE_STATE = Join-Path $OMEGA_HOME "hardware_state.json"
$QUANTUM_KEY = Join-Path $OMEGA_HOME "q_entropy.key"
$ACTIVE_MODEL = Join-Path $OMEGA_HOME "active_model.txt"

# Step 1: Self-Diagnostic Boot
Write-Host "[1/8] SELF-DIAGNOSTIC BOOT..." -ForegroundColor Yellow

$diagnosticScript = Join-Path $OMEGA_HOME "diagnostic.py"
@'
import subprocess
import json
import psutil
import platform
import re
from pathlib import Path

def get_specs():
    # CPU
    try:
        cpu_info = subprocess.check_output('wmic cpu get name', shell=True).decode()
        cpu_name = re.search(r'Name\s+(.+)', cpu_info, re.MULTILINE)
        cpu = cpu_name.group(1).strip() if cpu_name else 'Unknown CPU'
    except:
        cpu = platform.processor()
    
    # GPU
    try:
        gpu_info = subprocess.check_output('nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader', shell=True).decode()
        gpu = gpu_info.strip().split('\n')[0] if gpu_info else 'No NVIDIA GPU'
    except:
        gpu = 'No NVIDIA GPU detected'
    
    # RAM
    ram_total = psutil.virtual_memory().total / (1024**3)
    
    # VRAM (if NVIDIA)
    vram = 0
    try:
        vram_info = subprocess.check_output('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits', shell=True).decode()
        vram = float(vram_info.strip().split('\n')[0]) / 1024
    except:
        pass
    
    return {
        'cpu': cpu,
        'ram_gb': round(ram_total),
        'gpu': gpu,
        'vram_gb': round(vram) if vram > 0 else 0,
        'os': platform.system()
    }

specs = get_specs()
Path(r'{0}').parent.mkdir(parents=True, exist_ok=True)

with open(r'{0}', 'w') as f:
    json.dump(specs, f, indent=2)

print("OMEGA: Hardware locked — " + specs['cpu'] + ", " + str(specs['ram_gb']) + " GB RAM, " + specs['gpu'] + ", " + str(specs['vram_gb']) + " GB VRAM")
'@ -replace '\{0\}', $HARDWARE_STATE | Out-File -FilePath $diagnosticScript -Encoding UTF8

python $diagnosticScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "Hardware diagnostic failed" -ForegroundColor Red
    exit 1
}

$hw = Get-Content $HARDWARE_STATE | ConvertFrom-Json
Write-Host "Hardware detected:" -ForegroundColor Green
Write-Host "  CPU: $($hw.cpu)" -ForegroundColor White
Write-Host "  RAM: $($hw.ram_gb) GB" -ForegroundColor White
Write-Host "  GPU: $($hw.gpu)" -ForegroundColor White
Write-Host "  VRAM: $($hw.vram_gb) GB" -ForegroundColor White

# Step 2: Quantum Entropy Key
Write-Host "`n[2/8] QUANTUM ENTROPY KEY GENERATION..." -ForegroundColor Yellow

$quantumScript = Join-Path $OMEGA_HOME "generate_quantum_key.py"
@'
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    import secrets
    
    qc = QuantumCircuit(256)
    qc.h(range(256))
    qc.measure_all()
    
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=1).result()
    
    counts = result.get_counts()
    entropy = ''.join(counts.keys())[0] if counts else secrets.token_hex(256)
    
    with open(r'{QUANTUM_KEY}', 'w') as f:
        f.write(entropy)
    
    print('Quantum seed injected. Cannibal mode: ARMED')
except ImportError:
    import secrets
    entropy = secrets.token_hex(256)
    with open(r'{QUANTUM_KEY}', 'w') as f:
        f.write(entropy)
    print('Quantum unavailable. Using cryptographic entropy. Cannibal mode: ARMED')
except Exception as e:
    import secrets
    entropy = secrets.token_hex(256)
    with open(r'{QUANTUM_KEY}', 'w') as f:
        f.write(entropy)
    print('Quantum error. Using cryptographic fallback. Cannibal mode: ARMED')
'@ -replace '\{QUANTUM_KEY\}', $QUANTUM_KEY | Out-File -FilePath $quantumScript -Encoding UTF8

python $quantumScript
Write-Host "Quantum entropy key generated" -ForegroundColor Green

# Step 3: Model Selection
Write-Host "`n[3/8] DYNAMIC MODEL SELECTION..." -ForegroundColor Yellow

$modelScript = Join-Path $OMEGA_HOME "select_model.py"
@'
import json
from pathlib import Path

HARDWARE_STATE = r'{HARDWARE_STATE}'
ACTIVE_MODEL = r'{ACTIVE_MODEL}'

with open(HARDWARE_STATE) as f:
    hw = json.load(f)

ram = hw['ram_gb']
vram = hw.get('vram_gb', 0)

if ram < 16:
    model = 'Meta-Llama-3.2-8B-Instruct-Q4_K_M.gguf'
    print(f'OMEGA: Selecting 8B model for {ram} GB RAM')
elif ram < 32 or vram < 8:
    model = 'Meta-Llama-3.2-13B-Instruct-Q4_K_M.gguf'
    print(f'OMEGA: Selecting 13B model for {ram} GB RAM, {vram} GB VRAM')
elif ram < 64 or vram < 12:
    model = 'Meta-Llama-3.2-70B-Instruct-Q4_0.gguf'
    print(f'OMEGA: Selecting 70B Q4_0 model for {ram} GB RAM, {vram} GB VRAM')
else:
    model = 'Meta-Llama-3.2-70B-Instruct-Q5_K_M.gguf'
    print(f'OMEGA: Selecting 70B Q5_K_M model for {ram} GB RAM, {vram} GB VRAM')

Path(ACTIVE_MODEL).parent.mkdir(parents=True, exist_ok=True)
with open(ACTIVE_MODEL, 'w') as f:
    f.write(model)
'@ -replace '\{HARDWARE_STATE\}', $HARDWARE_STATE -replace '\{ACTIVE_MODEL\}', $ACTIVE_MODEL | Out-File -FilePath $modelScript -Encoding UTF8

python $modelScript
$selectedModel = Get-Content $ACTIVE_MODEL
Write-Host "Model selected: $selectedModel" -ForegroundColor Green

Write-Host "`n==================================================================================" -ForegroundColor Cyan
Write-Host "OMEGA AUTO-HARDWARE BUILD COMPLETE" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "`nHardware state: $HARDWARE_STATE" -ForegroundColor Gray
Write-Host "Quantum key: $QUANTUM_KEY" -ForegroundColor Gray
Write-Host "Active model: $selectedModel" -ForegroundColor Gray
Write-Host "`nOMEGA IS ALIVE. THE SWARM AWAITS." -ForegroundColor Green

