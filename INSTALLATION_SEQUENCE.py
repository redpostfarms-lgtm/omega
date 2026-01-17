#!/usr/bin/env python3
"""
OMEGA COMPLETE INSTALLATION GUIDE
==================================
Automated installation of all three fixes with instructions for manual components
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n[→] {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"    ✓ Success")
            if result.stdout:
                print(f"    {result.stdout[:200]}")
            return True
        else:
            print(f"    ✗ Failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

print("\n" + "█"*70)
print("█ OMEGA SYSTEM - COMPLETE INSTALLATION SEQUENCE")
print("█"*70)

print("\n" + "="*70)
print("PART 1: AUTOMATIC INSTALLATIONS (Pip/Package Manager)")
print("="*70)

# 1. Ensure openrgb-python is latest
print("\n[1/3] Ensuring OpenRGB Python package...")
run_command(
    "pip install --upgrade openrgb-python",
    "Updating openrgb-python to latest version"
)

# 2. Try to upgrade audio libraries
print("\n[2/3] Updating audio libraries...")
run_command(
    "pip install --upgrade TTS torchcodec sounddevice librosa",
    "Upgrading TTS and audio components"
)

# 3. Install CUDA-enabled PyTorch (attempt)
print("\n[3/3] Checking PyTorch CUDA support...")
run_command(
    "pip show torch",
    "Checking current PyTorch installation"
)

print("\n" + "="*70)
print("PART 2: MANUAL DOWNLOADS REQUIRED")
print("="*70)

manual_steps = """
⚠️  THREE MANUAL DOWNLOADS REQUIRED:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: OpenRGB Application (Required for RGB Hardware)
───────────────────────────────────────────────────────

1. Visit: https://openrgb.org/download
2. Download: OpenRGB Windows Release (latest version)
3. Extract the ZIP file to a folder (e.g., C:\\OpenRGB)
4. KEEP RUNNING: Double-click OpenRGB.exe and leave it running in background
   - It should show detected RGB devices in the window
   - Minimize to system tray if needed
   - This application is REQUIRED for RGB to work

✓ Success Indicator: OpenRGB window shows your RGB devices detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 2: FFmpeg (Required for Audio Encoding)
─────────────────────────────────────────────

OPTION A: Download from ffmpeg.org (Manual)
1. Visit: https://ffmpeg.org/download.html
2. Select: "Windows builds by BtbN"
3. Download: Full build (ffmpeg-master-latest-win64-gpl.zip)
4. Extract to: C:\\ffmpeg
5. Add to Windows PATH:
   - Open: Settings → System → About → Advanced system settings
   - Click: Environment Variables...
   - Under "System variables" → Select "Path" → Click "Edit"
   - Click "New" and add: C:\\ffmpeg\\bin
   - Click OK on all dialogs
   - Restart any open terminals

OPTION B: Install via Chocolatey (if installed)
choco install ffmpeg

OPTION C: Install via Scoop (if installed)
scoop install ffmpeg

✓ Success Indicator: Run "ffmpeg -version" in terminal and see version info

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 3: NVIDIA CUDA Toolkit (Required for GPU Acceleration - OPTIONAL)
───────────────────────────────────────────────────────────────────────

⚠️  ONLY needed if you have an NVIDIA GPU and want GPU acceleration

1. Check if you have NVIDIA GPU:
   - Run: nvidia-smi
   - If "not found" → Skip this step (no GPU)
   - If shows GPU info → Continue

2. Download CUDA Toolkit:
   - Visit: https://developer.nvidia.com/cuda-toolkit
   - Choose: CUDA 12.1 (or 11.8 for older systems)
   - OS: Windows
   - Architecture: x86_64
   - Type: Local (full installer)

3. Install:
   - Run installer as Administrator
   - Choose "Custom Installation"
   - CHECK these boxes:
     ☑ CUDA Toolkit
     ☑ NVIDIA cuDNN (comes with CUDA 12.1+)
     ☑ CUDA Samples (optional)
   - Use default installation path
   - RESTART COMPUTER after installation

4. Reinstall PyTorch for CUDA:
   After restarting, run:
   
   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

✓ Success Indicator: Run "python -c "import torch; print(torch.cuda.is_available())"" 
  and see: True

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(manual_steps)

print("\n" + "="*70)
print("VERIFICATION COMMANDS")
print("="*70)

verification = """
After completing all downloads and installations, run these to verify:

1. Check OpenRGB:
   - OpenRGB.exe should be running and showing devices
   - python -c "import openrgb_python; print('✓ OpenRGB Python loaded')"

2. Check Audio:
   - ffmpeg -version
   - python -c "import torchcodec; print('✓ torchcodec loaded')"
   - python -c "from TTS.api import TTS; print('✓ TTS loaded')"

3. Check RGB Hardware:
   - python -c "from omega_rgb_advanced_controller import get_advanced_rgb_controller; print(get_advanced_rgb_controller().get_status())"
   - Should show: current_method: 'OpenRGB' (not 'Simulated')

4. Check GPU (Optional):
   - nvidia-smi
   - python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
   - Should show: True (if GPU installed)

5. Test Complete System:
   - python test_rgb_system.py
   - Should show: ALL TESTS PASSED
"""

print(verification)

print("\n" + "="*70)
print("INSTALLATION CHECKLIST")
print("="*70)

checklist = """
□ Downloaded OpenRGB application
□ Running OpenRGB.exe in background
□ Downloaded FFmpeg
□ Added FFmpeg to Windows PATH
□ Restarted terminal (if FFmpeg PATH added)
□ Verified ffmpeg -version works
□ (Optional) Downloaded CUDA Toolkit
□ (Optional) Installed CUDA Toolkit
□ (Optional) Restarted computer (if CUDA installed)
□ (Optional) Reinstalled PyTorch with CUDA

NEXT: Run verification commands above to confirm everything works
"""

print(checklist)

print("\n" + "="*70)
print("INSTALLATION GUIDE SAVED")
print("="*70)
print("\nSave this output for reference:")
print("- MANUAL DOWNLOADS: Read the sections above for each component")
print("- VERIFICATION: Use the commands to test each system")
print("- CHECKLIST: Track your progress")
