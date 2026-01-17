#!/usr/bin/env python3
"""Verify all installations and show current system status"""

import sys
import subprocess
from pathlib import Path

def check_rgb():
    """Check RGB system status"""
    print("\n" + "="*60)
    print("RGB SYSTEM CHECK")
    print("="*60)
    
    try:
        import openrgb_python
        print("✓ openrgb-python installed")
    except ImportError:
        print("✗ openrgb-python NOT installed")
        return False
    
    try:
        from omega_rgb_advanced_controller import get_advanced_rgb_controller
        rgb = get_advanced_rgb_controller()
        status = rgb.get_status()
        current_method = status.get('current_method', 'Unknown')
        print(f"✓ RGB Controller loaded")
        print(f"  Current Method: {current_method}")
        print(f"  Available Methods: {status.get('available_methods', [])}")
        
        if current_method == 'Simulated':
            print("  ⚠ WARNING: Using Simulated (fallback) mode")
            print("  → OpenRGB service needs to be running")
        else:
            print(f"  ✓ Hardware control active via {current_method}")
        return True
    except Exception as e:
        print(f"✗ RGB Controller error: {e}")
        return False

def check_audio():
    """Check audio system"""
    print("\n" + "="*60)
    print("AUDIO SYSTEM CHECK")
    print("="*60)
    
    libs_ok = True
    
    # Check TTS
    try:
        from TTS.api import TTS
        print("✓ TTS library installed")
    except ImportError:
        print("✗ TTS NOT installed")
        libs_ok = False
    
    # Check torchcodec
    try:
        import torchcodec
        print("✓ torchcodec installed")
    except ImportError:
        print("✗ torchcodec NOT installed")
        libs_ok = False
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg installed")
        else:
            print("✗ FFmpeg error")
            libs_ok = False
    except FileNotFoundError:
        print("✗ FFmpeg NOT found in PATH")
        libs_ok = False
    except Exception as e:
        print(f"✗ FFmpeg check error: {e}")
        libs_ok = False
    
    # Check audio libraries
    for lib in ['sounddevice', 'scipy', 'librosa', 'soundfile']:
        try:
            __import__(lib)
            print(f"✓ {lib} installed")
        except ImportError:
            print(f"✗ {lib} NOT installed")
    
    return libs_ok

def check_gpu():
    """Check GPU/CUDA"""
    print("\n" + "="*60)
    print("GPU/CUDA CHECK")
    print("="*60)
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} installed")
        
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"✓ CUDA AVAILABLE")
            print(f"  Version: {torch.version.cuda}")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            try:
                props = torch.cuda.get_device_properties(0)
                mem_gb = props.total_memory / (1024**3)
                print(f"  Memory: {mem_gb:.1f} GB")
            except:
                pass
            return True
        else:
            print(f"✗ CUDA NOT available (CPU-only mode)")
            print(f"  → System running on CPU")
            return False
    except ImportError:
        print("✗ PyTorch NOT installed")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "█"*60)
    print("█ OMEGA SYSTEM INSTALLATION VERIFICATION")
    print("█"*60)
    
    rgb_ok = check_rgb()
    audio_ok = check_audio()
    gpu_ok = check_gpu()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    status = []
    if rgb_ok:
        status.append("✓ RGB System Ready")
    else:
        status.append("✗ RGB System Issue")
    
    if audio_ok:
        status.append("✓ Audio System Ready")
    else:
        status.append("✗ Audio System Issue")
    
    if gpu_ok:
        status.append("✓ GPU Acceleration Ready")
    else:
        status.append("✗ GPU/CUDA Not Available")
    
    for s in status:
        print(s)
    
    print("="*60)
    
    # Recommendations
    if not rgb_ok:
        print("\nRGB FIX NEEDED:")
        print("1. Ensure openrgb-python is installed: pip install openrgb-python")
        print("2. Download OpenRGB.exe from https://openrgb.org/download")
        print("3. Run OpenRGB.exe and keep it running in background")
    
    if not audio_ok:
        print("\nAUDIO FIX NEEDED:")
        print("1. Install FFmpeg")
        print("2. Ensure TTS is installed: pip install TTS")
    
    if not gpu_ok:
        print("\nGPU FIX NEEDED:")
        print("1. Install NVIDIA drivers from nvidia.com")
        print("2. Install CUDA Toolkit 12.1")
        print("3. Reinstall PyTorch: pip install torch --index-url https://download.pytorch.org/whl/cu121")

if __name__ == "__main__":
    main()
