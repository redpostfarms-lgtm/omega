# Complete Installation & Fix Guide

**For:** RGB Lights, Audio System, and GPU Acceleration  
**Date:** January 17, 2026  
**Version:** 1.0 - Complete Step-by-Step

---

## 🎯 Your Three Main Problems

### Problem 1: RGB Lights Don't Change Physically

**Install:** OpenRGB software + Python package

### Problem 2: Audio Generation Fails (FFmpeg Error)

**Install:** FFmpeg + torchcodec library

### Problem 3: GPU Not Working (CPU-only)

**Install:** NVIDIA drivers + CUDA Toolkit + PyTorch

---

## ⚡ QUICK START (5-10 minutes for RGB only)

If you ONLY want RGB lights to work:

```bash
# Step 1: Install OpenRGB Python library
pip install openrgb

# Step 2: Download OpenRGB application from:
# https://openrgb.org/download
# Run OpenRGB.exe and keep it running

# Step 3: Test
python -c "from omega_rgb_advanced_controller import get_advanced_rgb_controller; print(get_advanced_rgb_controller().get_status())"
```

If you see `'current_method': 'OpenRGB'` → **✓ FIXED**

---

## 📋 FULL FIX (Everything - 60-90 minutes including downloads)

### FIX #1: RGB LIGHTS (5 minutes)

#### Step 1a: Install OpenRGB Python Library

```bash
# Open PowerShell or Command Prompt
# Navigate to your project folder
cd "h:\The Gatekeeper"

# Install via pip
pip install openrgb
```

**Expected output:**

```
Successfully installed openrgb-0.x.x
```

#### Step 1b: Download OpenRGB Application

1. Visit: <https://openrgb.org/download>
2. Download for Windows (the latest version)
3. Extract the ZIP file to a folder
4. Right-click `OpenRGB.exe` → "Pin to Taskbar" (optional)

#### Step 1c: Start OpenRGB Service

1. Find and double-click `OpenRGB.exe`
2. Window should open showing detected RGB devices
3. Keep it running in background (don't close)
4. Note: It will run in system tray if you minimize it

#### Step 1d: Test RGB Connection

```bash
# In Python or PowerShell
python -c "
from omega_rgb_advanced_controller import get_advanced_rgb_controller
rgb = get_advanced_rgb_controller()
status = rgb.get_status()
print(f'Method: {status[\"current_method\"]}')
print(f'Devices: {status[\"available_methods\"]}')
"
```

**Success Indicators:**

- `'current_method': 'OpenRGB'` (not 'Simulated')
- Multiple devices listed
- RGB window shows detected devices

**If Still Not Working:**

- Check OpenRGB window → Are devices showing?
- If no devices: USB cable not connected
- If devices shown: Try setting color with Python:

  ```python
  rgb.set_rgb_color(255, 0, 0)  # Red
  # Check if physical LEDs change color
  ```

---

### FIX #2: AUDIO SYSTEM (10 minutes)

#### Step 2a: Install FFmpeg

**Option A: Using WinGet (Easiest, Windows 10/11)**

```bash
# Open PowerShell as Administrator
winget install ffmpeg

# Should show:
# Found FFmpeg [FFmpeg.FFmpeg] version 6.0
# Successfully installed
```

**Option B: Using Chocolatey**

```bash
# If you have Chocolatey installed
choco install ffmpeg
```

**Option C: Manual Installation (If above don't work)**

1. Download: <https://ffmpeg.org/download.html>
2. Choose: Windows Builds → Full Build (recommended)
3. Extract to: `C:\ffmpeg`
4. Add to Windows PATH:
   - Search: "Environment Variables"
   - Click: "Edit the system environment variables"
   - Click: "Environment Variables..." button
   - Under "System variables" → Select "Path" → Click "Edit"
   - Click: "New" and add: `C:\ffmpeg\bin`
   - Click OK on all dialogs
   - Restart any open terminals

#### Step 2b: Verify FFmpeg Installation

```bash
ffmpeg -version

# Should show:
# ffmpeg version 6.0 Copyright (c) 2000-2023
```

If "ffmpeg is not recognized":

- FFmpeg not installed or not in PATH
- If installed: Restart command prompt and try again
- If still fails: Check PATH environment variable

#### Step 2c: Fix torchcodec Library

```bash
# Remove old version
pip uninstall torchcodec -y

# Install fresh (without cache)
pip install torchcodec --no-cache-dir
```

#### Step 2d: Test Audio System

```bash
# Test in Python
python -c "
try:
    import torchcodec
    print('✓ torchcodec working')
except ImportError:
    print('✗ torchcodec still broken')
"

# Try generating audio
python -c "
from TTS.api import TTS

model = TTS(model_name='tts_models/en/ljspeech/tacotron2-DDC', gpu=False)
model.tts_to_file('Hello world, testing audio', 'test.wav')
print('✓ Audio file created')
"
```

**Success Indicator:** `test.wav` file created in current directory

---

### FIX #3: GPU ACCELERATION (30-60 minutes)

#### Step 3a: Check if NVIDIA GPU Exists

```bash
# Method 1: Check command
nvidia-smi

# If shows GPU info: GPU present ✓
# If "not recognized": GPU not detected or drivers missing
```

#### Step 3b: Install NVIDIA GPU Drivers

**If nvidia-smi command worked:**

- GPU drivers are already installed
- Skip to Step 3c

**If nvidia-smi command failed:**

1. Visit: <https://nvidia.com/download/driverDetails.aspx>
2. Select:
   - **Product Type:** GeForce (most common)
   - **Product:** Your GPU model (RTX 3060, GTX 1080, etc.)
   - **OS:** Windows 10 or Windows 11
   - **Architecture:** 64-bit (most likely)
3. Download driver
4. Run installer
5. Restart computer
6. Verify: `nvidia-smi` should work now

**How to find your GPU model:**

- Look in Device Manager (search: devmgmt.msc)
- Under "Display adapters" → NVIDIA device

#### Step 3c: Install CUDA Toolkit

1. Visit: <https://developer.nvidia.com/cuda-toolkit>
2. Download CUDA 12.1 (or 11.8 if older system)
3. Choose:
   - **OS:** Windows
   - **Architecture:** x86_64 (64-bit)
   - **Version:** Local (downloads full installer) or Network
4. Run installer
   - Accept license
   - Click "Custom Installation"
   - Make sure these are CHECKED:
     - ☑ CUDA Toolkit
     - ☑ Graphics Driver (or leave unchecked if already installed)
     - ☑ cuDNN
5. Complete installation
6. **Restart Computer** (Important!)

#### Step 3d: Verify CUDA Installation

```bash
# Check CUDA compiler is installed
nvcc --version

# Should show:
# nvcc: NVIDIA (R) Cuda compiler driver
# Cuda compilation tools, release 12.1
# Build cuda_12.1.r12.1/compiler.33018258_0
```

#### Step 3e: Reinstall PyTorch with CUDA Support

```bash
# Remove old PyTorch
pip uninstall torch torchvision torchaudio -y

# Install NEW PyTorch with CUDA support
# Choose based on your CUDA version:

# For CUDA 11.8 (older systems):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1 (newer systems):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# This will take a few minutes...
```

#### Step 3f: Test CUDA Installation

```bash
# Test in Python
python -c "
import torch

print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    print('✓ GPU IS WORKING')
else:
    print('✗ GPU NOT working - check steps above')
"
```

**Success Indicator:**

```
PyTorch: 2.x.x+cu121
CUDA Available: True
GPU: NVIDIA GeForce RTX 3060 (or your GPU)
Memory: 12.0 GB
✓ GPU IS WORKING
```

---

## 🔍 VERIFICATION CHECKLIST

After installing everything:

- [ ] **RGB System**
  - [ ] OpenRGB.exe running in background
  - [ ] `get_advanced_rgb_controller().get_status()['current_method']` shows 'OpenRGB'
  - [ ] Can set RGB color and see physical LED changes
  
- [ ] **Audio System**
  - [ ] `ffmpeg -version` works
  - [ ] `import torchcodec` works in Python
  - [ ] Can generate audio files without FFmpeg errors
  
- [ ] **GPU System**
  - [ ] `nvidia-smi` shows GPU info
  - [ ] `nvcc --version` works
  - [ ] `torch.cuda.is_available()` returns True
  - [ ] GPU memory shows correctly

---

## 🆘 TROUBLESHOOTING

### Problem: "openrgb command not found" after installation

**Solution:**

```bash
# Reinstall in current Python environment
python -m pip install --force-reinstall openrgb
```

### Problem: "ffmpeg is not recognized"

**Solution:**

1. Make sure FFmpeg installed with `winget install ffmpeg`
2. Restart command prompt/PowerShell
3. If still fails: Manually add to PATH (see Option C in Step 2a)

### Problem: "CUDA not available" after installation

**Most Common Cause:** PyTorch installed BEFORE CUDA

**Solution:**

```bash
# Uninstall torch first
pip uninstall torch torchvision torchaudio -y

# Restart Python environment

# Install AFTER CUDA installed
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Problem: RGB Still in "Simulated" Mode

**Check:**

1. Is OpenRGB.exe running? (check taskbar)
2. Are devices shown in OpenRGB window?
3. Are USB cables connected to motherboard?

**Fix:**

- Restart OpenRGB application
- Try different USB port (if RGB is external)
- Check device drivers in Device Manager

### Problem: GPU Memory Full

**Solution:**

```python
# Force CPU mode temporarily
import torch
torch.cuda.empty_cache()  # Clear GPU memory

# Or run tasks on CPU
device = 'cpu'  # Use CPU instead of 'cuda'
```

---

## 📊 EXPECTED RESULTS

### After All Fixes Complete

```
OMEGA SYSTEM STATUS
═══════════════════════════════════════════

✓ RGB SYSTEM
  • Status: OpenRGB active
  • Devices: 4 detected
  • Current Mode: Hardware control (not simulated)
  • Physical LEDs: Responding to color changes

✓ AUDIO SYSTEM
  • FFmpeg: Installed and working
  • TTS: Generating audio files successfully
  • Audio Encoding: torchcodec operational
  • Playback: All audio files playing correctly

✓ GPU SYSTEM
  • CUDA: Available and initialized
  • GPU: NVIDIA RTX 3060 (12.0 GB)
  • Performance: 4-10x faster on GPU tasks
  • Acceleration: Enabled system-wide

═══════════════════════════════════════════
```

---

## 📞 IF YOU GET STUCK

Run this diagnostic to see current status:

```bash
cd "h:\The Gatekeeper"
python QUICK_DIAGNOSTICS.py
```

This will show:

- Which systems are working ✓
- Which systems have issues ✗
- What needs to be installed

---

## 🎉 FINAL NOTES

1. **OpenRGB needs to stay running** - It must be active for RGB to work
2. **Restart after CUDA install** - CUDA requires system restart
3. **GPU makes things fast** - But system works fine on CPU too
4. **All installations are optional** - Each system works independently

**Priority Order for Installation:**

1. RGB (quickest, most noticeable)
2. Audio (enables voice features)
3. GPU (speeds up processing)

---

**Guide Version:** 1.0  
**Last Updated:** January 17, 2026  
**Status:** Complete and ready to follow
