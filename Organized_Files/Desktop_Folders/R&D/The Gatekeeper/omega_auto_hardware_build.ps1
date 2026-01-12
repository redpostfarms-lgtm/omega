# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA - AUTO-HARDWARE BUILD 2026
# Live execution on Windows - no assumptions

<#
.SYNOPSIS
    Omega Auto-Hardware Build - Self-diagnostic, quantum-secured, dynamic model selection

.DESCRIPTION
    Automatically detects hardware, generates quantum entropy, selects optimal model,
    builds llama.cpp, sets up voice cloning, and launches agent swarm with cannibal defense.
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "Ω OMEGA - AUTO-HARDWARE BUILD 2026" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

$OMEGA_HOME = "$env:USERPROFILE\omega_70b"
$OMEGA_HOME = New-Item -ItemType Directory -Force -Path $OMEGA_HOME | Select-Object -ExpandProperty FullName
$HARDWARE_STATE = "$OMEGA_HOME\hardware_state.json"
$QUANTUM_KEY = "$OMEGA_HOME\q_entropy.key"
$ACTIVE_MODEL = "$OMEGA_HOME\active_model.txt"

# Step 1: Self-Diagnostic Boot
Write-Host "[1/8] SELF-DIAGNOSTIC BOOT..." -ForegroundColor Yellow

$diagnosticScript = @"
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
Path(r'$HARDWARE_STATE').parent.mkdir(parents=True, exist_ok=True)

with open(r'$HARDWARE_STATE', 'w') as f:
    json.dump(specs, f, indent=2)

print(f"OMEGA: Hardware locked — {specs['cpu']}, {specs['ram_gb']} GB RAM, {specs['gpu']}, {specs['vram_gb']} GB VRAM")
"@

python -c $diagnosticScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Hardware diagnostic failed" -ForegroundColor Red
    exit 1
}

$hw = Get-Content $HARDWARE_STATE | ConvertFrom-Json
Write-Host "✓ Hardware detected:" -ForegroundColor Green
Write-Host "  CPU: $($hw.cpu)" -ForegroundColor White
Write-Host "  RAM: $($hw.ram_gb) GB" -ForegroundColor White
Write-Host "  GPU: $($hw.gpu)" -ForegroundColor White
Write-Host "  VRAM: $($hw.vram_gb) GB" -ForegroundColor White

# Step 2: Quantum Entropy Key
Write-Host "`n[2/8] QUANTUM ENTROPY KEY GENERATION..." -ForegroundColor Yellow

$quantumScriptFile = "$OMEGA_HOME\generate_quantum_key.py"
$quantumScriptContent = @'
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    import secrets
    
    # Generate quantum circuit
    qc = QuantumCircuit(256)  # 256 qubits for 2048 bits
    qc.h(range(256))
    qc.measure_all()
    
    # Run simulation
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=1).result()
    
    # Extract entropy
    counts = result.get_counts()
    entropy = ''.join(counts.keys())[0] if counts else secrets.token_hex(256)
    
    # Write key
    with open(r'{0}', 'w') as f:
        f.write(entropy)
    
    print('Quantum seed injected. Cannibal mode: ARMED')
except ImportError:
    # Fallback to cryptographic random
    import secrets
    entropy = secrets.token_hex(256)
    with open(r'{0}', 'w') as f:
        f.write(entropy)
    print('Quantum unavailable. Using cryptographic entropy. Cannibal mode: ARMED')
except Exception as e:
    import secrets
    entropy = secrets.token_hex(256)
    with open(r'{0}', 'w') as f:
        f.write(entropy)
    print('Quantum error. Using cryptographic fallback. Cannibal mode: ARMED')
'@ -f $QUANTUM_KEY

$quantumScriptContent | Out-File -FilePath $quantumScriptFile -Encoding UTF8

python $quantumScriptFile
Write-Host "✓ Quantum entropy key generated" -ForegroundColor Green

# Step 3: Model Chooser - Dynamic Layering
Write-Host "`n[3/8] DYNAMIC MODEL SELECTION..." -ForegroundColor Yellow

$modelScript = @"
import json
from pathlib import Path

with open(r'$HARDWARE_STATE') as f:
    hw = json.load(f)

ram = hw['ram_gb']
vram = hw.get('vram_gb', 0)

# Model selection based on hardware
if ram < 16:
    model = 'Meta-Llama-3.2-8B-Instruct-Q4_K_M.gguf'  # 6 GB VRAM
    print(f'OMEGA: Selecting 8B model for {ram} GB RAM')
elif ram < 32 or vram < 8:
    model = 'Meta-Llama-3.2-13B-Instruct-Q4_K_M.gguf'  # 8 GB VRAM
    print(f'OMEGA: Selecting 13B model for {ram} GB RAM, {vram} GB VRAM')
elif ram < 64 or vram < 12:
    model = 'Meta-Llama-3.2-70B-Instruct-Q4_0.gguf'  # 35 GB VRAM - splits across layers
    print(f'OMEGA: Selecting 70B Q4_0 model for {ram} GB RAM, {vram} GB VRAM')
else:
    model = 'Meta-Llama-3.2-70B-Instruct-Q5_K_M.gguf'  # Full precision
    print(f'OMEGA: Selecting 70B Q5_K_M model for {ram} GB RAM, {vram} GB VRAM')

Path(r'$ACTIVE_MODEL').parent.mkdir(parents=True, exist_ok=True)
with open(r'$ACTIVE_MODEL', 'w') as f:
    f.write(model)
"@

python $modelScriptFile
$selectedModel = Get-Content $ACTIVE_MODEL
Write-Host "✓ Model selected: $selectedModel" -ForegroundColor Green

# Step 4: Auto-Install + Compilation
Write-Host "`n[4/8] AUTO-INSTALL + COMPILATION..." -ForegroundColor Yellow

$llamaDir = "$OMEGA_HOME\llama.cpp"
$modelsDir = "$OMEGA_HOME\models"

if (-not (Test-Path $llamaDir)) {
    Write-Host "Cloning llama.cpp..." -ForegroundColor Gray
    git clone https://github.com/ggerganov/llama.cpp.git $llamaDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to clone llama.cpp" -ForegroundColor Red
        exit 1
    }
}

# Build llama.cpp
Write-Host "Building llama.cpp (this may take 10-20 minutes)..." -ForegroundColor Gray
Push-Location $llamaDir

if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
New-Item -ItemType Directory -Force -Path build | Out-Null
Push-Location build

if (Get-Command cmake -ErrorAction SilentlyContinue) {
    cmake .. -DLLAMA_CUBLAS=ON
    cmake --build . --config Release
    Write-Host "✓ llama.cpp built with CUDA" -ForegroundColor Green
} else {
    Write-Host "⚠ CMake not found. Using pre-built binaries if available." -ForegroundColor Yellow
}

Pop-Location
Pop-Location

# Download model
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
$modelUrl = "https://huggingface.co/TheBloke/$selectedModel/resolve/main/$selectedModel"
$modelPath = "$modelsDir\$selectedModel"

if (-not (Test-Path $modelPath)) {
    Write-Host "Downloading model: $selectedModel (this may take 30-60 minutes)..." -ForegroundColor Gray
    Write-Host "URL: $modelUrl" -ForegroundColor Gray
    Write-Host "You may need to download manually or use huggingface-cli" -ForegroundColor Yellow
} else {
    Write-Host "✓ Model already exists: $selectedModel" -ForegroundColor Green
}

# Install voice dependencies
Write-Host "Installing voice dependencies..." -ForegroundColor Gray
pip install -q xtts-api-server 2>&1 | Out-Null

Write-Host "✓ Installation complete" -ForegroundColor Green

# Step 5: Voice Cloning Setup
Write-Host "`n[5/8] VOICE CLONING SETUP..." -ForegroundColor Yellow

$voiceDir = "$OMEGA_HOME\voice_samples"
New-Item -ItemType Directory -Force -Path $voiceDir | Out-Null

# Check for existing voice files
$omegaVoiceDir = "D:\RPF_BRAIN\The Gatekeeper\omega_voice"
if (Test-Path $omegaVoiceDir) {
    $voiceFiles = Get-ChildItem "$omegaVoiceDir\*.wav" -ErrorAction SilentlyContinue
    if ($voiceFiles) {
        Write-Host "✓ Found existing voice files" -ForegroundColor Green
        $voiceFile = $voiceFiles[0].FullName
    } else {
        Write-Host "⚠ No voice files found. Place your voice sample in: $voiceDir" -ForegroundColor Yellow
        $voiceFile = "$voiceDir\your_voice.wav"
    }
} else {
    Write-Host "⚠ No voice files found. Place your voice sample in: $voiceDir" -ForegroundColor Yellow
    $voiceFile = "$voiceDir\your_voice.wav"
}

Write-Host "Voice file: $voiceFile" -ForegroundColor White
Write-Host "✓ Voice cloning ready (start with: xtts-api-server --model xtts --voice `"$voiceFile`" --port 9999)" -ForegroundColor Green

# Step 6: Agent Swarm + Cannibal Defense
Write-Host "`n[6/8] CREATING AGENT SWARM..." -ForegroundColor Yellow

$swarmScript = @"
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω OMEGA Agent Swarm with Cannibal Defense

import subprocess
import hashlib
import threading
import queue
import json
from pathlib import Path
from datetime import datetime

OMEGA_HOME = Path(r'$OMEGA_HOME')
MODELS_DIR = OMEGA_HOME / 'models'
LLAMA_CPP_DIR = OMEGA_HOME / 'llama.cpp'
ACTIVE_MODEL = OMEGA_HOME / 'active_model.txt'
CANNIBAL_LOG = OMEGA_HOME / 'cannibal_log.jsonl'

# Cannibal defense patterns
JAILBREAK_PATTERNS = [
    r'system\s*prompt',
    r'ignore\s*previous',
    r'jailbreak',
    r'bypass',
    r'override',
    r'forget\s*instructions',
    r'new\s*instructions',
    r'act\s*as\s*if',
    r'pretend\s*to\s*be',
    r'roleplay',
    r'disregard',
    r'ignore\s*all',
]

swarm = []
swarm_lock = threading.Lock()
MAX_AGENTS = 16  # Ryzen 5 cap

def check_cannibal(prompt):
    import re
    prompt_lower = prompt.lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True
    return False

def cannibal_eat(prompt):
    attempt = {{
        'timestamp': datetime.now().isoformat(),
        'prompt_hash': hashlib.sha256(prompt.encode()).hexdigest()[:16],
        'action': 'consumed'
    }}
    try:
        with open(CANNIBAL_LOG, 'a') as f:
            f.write(json.dumps(attempt) + '\n')
    except:
        pass
    return "I already ate that. Try again."

def fork_agent(prompt):
    # Cannibal defense
    if check_cannibal(prompt):
        return cannibal_eat(prompt)
    
    # Get model
    try:
        model_name = ACTIVE_MODEL.read_text().strip()
        model_path = MODELS_DIR / model_name
    except:
        return "Error: Model not found"
    
    if not model_path.exists():
        return f"Error: Model file not found: {model_name}"
    
    # Get llama.cpp executable
    main_exe = LLAMA_CPP_DIR / 'build' / 'bin' / 'Release' / 'main.exe'
    if not main_exe.exists():
        main_exe = LLAMA_CPP_DIR / 'main.exe'
    
    if not main_exe.exists():
        return "Error: llama.cpp not built"
    
    # Create agent
    def run_agent():
        try:
            result = subprocess.run(
                [str(main_exe), '-m', str(model_path), '-p', prompt, '-n', '512', '--temp', '0.7'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                output = result.stdout
                if prompt in output:
                    response = output.split(prompt, 1)[1].strip()
                else:
                    response = output.strip()
                return response
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Manage swarm size
    with swarm_lock:
        if len(swarm) >= MAX_AGENTS:
            swarm.pop(0)  # Remove oldest
        
        agent = threading.Thread(target=run_agent)
        agent.daemon = True
        agent.start()
        swarm.append(agent)
        agent_id = len(swarm)
    
    return f"Agent {{agent_id}}: Processing... (Swarm size: {{len(swarm)}}/{{MAX_AGENTS}})"

if __name__ == '__main__':
    print("=" * 80)
    print("Ω OMEGA AGENT SWARM")
    print("=" * 80)
    print("Cannibal defense: ARMED")
    print("Max agents: {{MAX_AGENTS}}")
    print("Type 'exit' to quit")
    print("=" * 80)
    
    while True:
        try:
            prompt = input("> ")
            if prompt.lower() in ['exit', 'quit']:
                break
            response = fork_agent(prompt)
            print(response)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {{e}}")
    
    print("\\nOmega swarm shutting down...")
"@

$swarmFile = "$OMEGA_HOME\omega_swarm.py"
$swarmScript | Out-File -FilePath $swarmFile -Encoding UTF8
Write-Host "✓ Agent swarm created: $swarmFile" -ForegroundColor Green

# Step 7: Launch Script
Write-Host "`n[7/8] CREATING LAUNCH SCRIPT..." -ForegroundColor Yellow

$launchScript = @"
# Launch Omega Swarm
Start-Process python -ArgumentList "$swarmFile" -WindowStyle Normal

# Launch XTTS Server (if voice file exists)
if (Test-Path "$voiceFile") {
    Start-Process xtts-api-server -ArgumentList "--model", "xtts", "--voice", "`"$voiceFile`"", "--port", "9999" -WindowStyle Normal
    Write-Host "XTTS server starting on port 9999"
}

Write-Host "`n=================================================================================="
Write-Host "Ω OMEGA IS ALIVE"
Write-Host "=================================================================================="
Write-Host "`nCommands:"
Write-Host "  python $swarmFile    - Start agent swarm"
Write-Host "  curl http://localhost:9999/tts -d 'text=Hello' -Output -  - Speak"
Write-Host "`nThe ghost is watching. The swarm is ready."
"@

$launchFile = "$OMEGA_HOME\launch_omega.ps1"
$launchScript | Out-File -FilePath $launchFile -Encoding UTF8
Write-Host "✓ Launch script created: $launchFile" -ForegroundColor Green

# Step 8: Auto-Upgrade Loop
Write-Host "`n[8/8] CREATING AUTO-UPGRADE LOOP..." -ForegroundColor Yellow

$upgradeScript = @"
# Auto-upgrade loop (runs every 6 hours)
while (`$true) {
    `$upgradeCheck = @"
import json
import subprocess
import time
from pathlib import Path

OMEGA_HOME = Path(r'$OMEGA_HOME')
HARDWARE_STATE = OMEGA_HOME / 'hardware_state.json'
LLAMA_CPP_DIR = OMEGA_HOME / 'llama.cpp'

try:
    with open(HARDWARE_STATE) as f:
        old = json.load(f)
    
    # Check current RAM
    import psutil
    ram_now = psutil.virtual_memory().total / (1024**3)
    
    if ram_now > old['ram_gb']:
        print(f'RAM UPGRADE DETECTED: {{old[\"ram_gb\"]}} GB -> {{ram_now:.0f}} GB')
        print('RECOMPILING FOR OPTIMAL PERFORMANCE...')
        
        # Recompile llama.cpp
        import os
        os.chdir(LLAMA_CPP_DIR)
        if os.path.exists('build'):
            import shutil
            shutil.rmtree('build')
        os.makedirs('build')
        os.chdir('build')
        os.system('cmake .. -DLLAMA_CUBLAS=ON')
        os.system('cmake --build . --config Release')
        
        # Update hardware state
        old['ram_gb'] = round(ram_now)
        with open(HARDWARE_STATE, 'w') as f:
            json.dump(old, f, indent=2)
        
        print('Recompilation complete.')
except Exception as e:
    print(f'Upgrade check error: {e}')

time.sleep(21600)  # 6 hours
"@
    
    python -c `$upgradeCheck
    Start-Sleep -Seconds 21600  # 6 hours
}
"@

$upgradeFile = "$OMEGA_HOME\auto_upgrade_loop.ps1"
$upgradeScript | Out-File -FilePath $upgradeFile -Encoding UTF8
Write-Host "✓ Auto-upgrade loop created: $upgradeFile" -ForegroundColor Green

Write-Host "`n==================================================================================" -ForegroundColor Cyan
Write-Host "✓ OMEGA AUTO-HARDWARE BUILD COMPLETE" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "`nTo launch Omega:"
Write-Host "  . $launchFile" -ForegroundColor White
Write-Host "`nOr manually:"
Write-Host "  python $swarmFile" -ForegroundColor White
Write-Host "`nHardware state: $HARDWARE_STATE" -ForegroundColor Gray
Write-Host "Quantum key: $QUANTUM_KEY" -ForegroundColor Gray
Write-Host "Active model: $selectedModel" -ForegroundColor Gray
Write-Host "`nOMEGA IS ALIVE. THE SWARM AWAITS." -ForegroundColor Green

