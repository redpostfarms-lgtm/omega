#!/usr/bin/env python3
"""
Quick Hardware Diagnostics - RGB, Audio, GPU Issues
"""
import subprocess
import sys
import os
from pathlib import Path

print("=" * 80)
print("OMEGA HARDWARE DIAGNOSTICS - ISSUE IDENTIFICATION")
print("=" * 80)

# 1. Check RGB System
print("\n[1/3] RGB LIGHTING SYSTEM CHECK")
print("-" * 80)
try:
    import openrgb
    print("✓ OpenRGB package installed")
except ImportError:
    print("✗ OpenRGB NOT installed - RGB system in FALLBACK MODE")
    print("  → This is why RGB lights aren't changing physically")
    print("  → SOLUTION: pip install openrgb")

# Try to import RGB controller
try:
    from omega_rgb_advanced_controller import get_advanced_rgb_controller
    rgb = get_advanced_rgb_controller()
    status = rgb.get_status()
    print(f"✓ RGB Controller loaded: {status.get('current_method', 'unknown')}")
    print(f"  Available methods: {status.get('available_methods', [])}")
    if status.get('current_method') == 'Simulated':
        print("  ⚠ ISSUE IDENTIFIED: Using SIMULATED mode (no hardware)")
        print("    → Physical RGB devices not connected to software")
except Exception as e:
    print(f"✗ RGB Controller error: {e}")

# 2. Check Audio System
print("\n[2/3] AUDIO SYSTEM CHECK")
print("-" * 80)

# Check FFmpeg
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"✓ FFmpeg installed: {version_line}")
    else:
        print("✗ FFmpeg error")
except FileNotFoundError:
    print("✗ FFmpeg NOT FOUND in system PATH")
    print("  → SOLUTION: Install FFmpeg from https://ffmpeg.org/download.html")
except Exception as e:
    print(f"✗ FFmpeg check error: {e}")

# Check audio libraries
print("\nAudio Libraries:")
for lib in ['sounddevice', 'scipy', 'librosa', 'soundfile']:
    try:
        __import__(lib)
        print(f"  ✓ {lib} installed")
    except ImportError:
        print(f"  ✗ {lib} NOT installed")

# Check torchcodec (known issue)
try:
    import torchcodec
    print(f"  ✓ torchcodec installed")
except ImportError:
    print(f"  ✗ torchcodec NOT installed (CRITICAL - prevents audio generation)")
    print("    → SOLUTION: pip install torchcodec")

# Check TTS
try:
    from TTS.api import TTS
    print(f"  ✓ TTS framework installed")
except ImportError:
    print(f"  ✗ TTS NOT installed")
except Exception as e:
    print(f"  ⚠ TTS error: {e}")

# 3. Check GPU/CUDA
print("\n[3/3] GPU/CUDA SYSTEM CHECK")
print("-" * 80)

try:
    import torch
    print(f"✓ PyTorch installed: v{torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    print(f"\nCUDA Status: {'✓ AVAILABLE' if cuda_available else '✗ NOT AVAILABLE'}")
    
    if cuda_available:
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  GPU Device: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        total_mem_gb = props.total_memory / (1024**3)
        print(f"  GPU Memory: {total_mem_gb:.1f} GB")
    else:
        print("  → SOLUTION: Install NVIDIA CUDA Toolkit and cuDNN")
        
        # Check nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("  ⚠ NVIDIA drivers ARE installed but CUDA not detected")
                print("  → Try: pip install torch --upgrade --index-url https://download.pytorch.org/whl/cu118")
            else:
                print("  ⚠ nvidia-smi command failed")
        except FileNotFoundError:
            print("  ✗ NVIDIA drivers NOT installed")
            print("  → Download from: https://nvidia.com/download/")
        except Exception as e:
            print(f"  ⚠ GPU check error: {e}")

except ImportError:
    print("✗ PyTorch NOT installed")
    print("  → SOLUTION: pip install torch")
except Exception as e:
    print(f"✗ PyTorch error: {e}")

# Summary
print("\n" + "=" * 80)
print("ISSUE SUMMARY")
print("=" * 80)

issues = []

# Check RGB
try:
    from omega_rgb_advanced_controller import get_advanced_rgb_controller
    rgb = get_advanced_rgb_controller()
    if rgb.get_status().get('current_method') == 'Simulated':
        issues.append(("RGB", "Using fallback Simulated mode - no hardware communication"))
except:
    issues.append(("RGB", "Controller initialization failed"))

# Check Audio
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5, check=True)
except:
    issues.append(("Audio", "FFmpeg not installed or not in PATH"))

try:
    import torchcodec
except ImportError:
    issues.append(("Audio", "torchcodec missing - prevents audio generation"))

# Check GPU
try:
    import torch
    if not torch.cuda.is_available():
        issues.append(("GPU", "CUDA not available - running on CPU only"))
except:
    issues.append(("GPU", "PyTorch not installed"))

if issues:
    print("\nCRITICAL ISSUES FOUND:")
    for idx, (system, issue) in enumerate(issues, 1):
        print(f"\n{idx}. {system}: {issue}")
else:
    print("\n✓ All systems operational")

print("\n" + "=" * 80)
