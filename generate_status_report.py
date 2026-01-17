#!/usr/bin/env python3
"""Installation Status Report - Write directly to file"""

import sys
import subprocess
from pathlib import Path
import json

output = []

def log(msg):
    """Log message to output list"""
    output.append(msg)
    print(msg)  # Also print
    
# Start
log("\n" + "█"*70)
log("█ OMEGA SYSTEM INSTALLATION STATUS REPORT")
log("█"*70)

# Check each component
log("\n[1/4] Checking Python Packages...")
log("-"*70)

packages_ok = True

# Check openrgb-python
try:
    import openrgb_python
    log(f"✓ openrgb-python installed")
except ImportError:
    log(f"✗ openrgb-python NOT found")
    packages_ok = False

# Check torch
try:
    import torch
    log(f"✓ PyTorch {torch.__version__} installed")
except ImportError:
    log(f"✗ PyTorch NOT found")
    packages_ok = False

# Check torchcodec
try:
    import torchcodec
    log(f"✓ torchcodec installed")
except ImportError:
    log(f"✗ torchcodec NOT found")
    packages_ok = False

# Check TTS
try:
    from TTS.api import TTS
    log(f"✓ TTS framework installed")
except ImportError:
    log(f"✗ TTS NOT found")
    packages_ok = False

log("\n[2/4] Checking RGB System...")
log("-"*70)

rgb_ok = False
try:
    from omega_rgb_advanced_controller import get_advanced_rgb_controller
    rgb = get_advanced_rgb_controller()
    status = rgb.get_status()
    current_method = status.get('current_method', 'Unknown')
    log(f"✓ RGB Controller loaded")
    log(f"  Current Method: {current_method}")
    log(f"  Available: {status.get('available_methods', [])}")
    
    if current_method != 'Simulated':
        log(f"  ✓ HARDWARE CONTROL ACTIVE")
        rgb_ok = True
    else:
        log(f"  ⚠ Using Simulated mode (need OpenRGB service)")
except Exception as e:
    log(f"✗ RGB Controller error: {e}")

log("\n[3/4] Checking Audio System...")
log("-"*70)

audio_ok = True

# FFmpeg
try:
    result = subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, text=True, timeout=2)
    if result.returncode == 0:
        log(f"✓ FFmpeg installed")
    else:
        log(f"✗ FFmpeg error")
        audio_ok = False
except FileNotFoundError:
    log(f"✗ FFmpeg NOT in PATH")
    audio_ok = False
except Exception as e:
    log(f"✗ FFmpeg check failed: {e}")
    audio_ok = False

log("\n[4/4] Checking GPU/CUDA...")
log("-"*70)

gpu_ok = False
try:
    import torch
    cuda_available = torch.cuda.is_available()
    
    if cuda_available:
        log(f"✓ CUDA AVAILABLE")
        log(f"  Version: {torch.version.cuda}")
        log(f"  Device: {torch.cuda.get_device_name(0)}")
        try:
            props = torch.cuda.get_device_properties(0)
            mem_gb = props.total_memory / (1024**3)
            log(f"  Memory: {mem_gb:.1f} GB")
        except:
            pass
        gpu_ok = True
    else:
        log(f"✗ CUDA NOT available (CPU-only)")
except Exception as e:
    log(f"✗ GPU check error: {e}")

# Summary
log("\n" + "="*70)
log("SUMMARY")
log("="*70)

status_lines = [
    ("RGB System", rgb_ok),
    ("Audio System", audio_ok),
    ("GPU/CUDA", gpu_ok),
    ("Python Packages", packages_ok)
]

for system, ok in status_lines:
    symbol = "✓" if ok else "✗"
    log(f"{symbol} {system}: {'Ready' if ok else 'Needs Setup'}")

log("="*70)

# Write to file
report_file = Path("INSTALLATION_STATUS_REPORT.txt")
with open(report_file, 'w') as f:
    f.write('\n'.join(output))

log(f"\n✓ Report saved to: {report_file}")
