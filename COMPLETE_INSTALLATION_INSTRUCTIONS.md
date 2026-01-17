# 🚀 COMPLETE INSTALLATION INSTRUCTIONS

**Date:** January 17, 2026  
**System:** Omega Control System  
**Goal:** Install RGB, Audio, and GPU support

---

## ⚡ Quick Overview

You need to install **3 things**:

1. **OpenRGB** - Application to control RGB hardware
2. **FFmpeg** - Library for audio encoding  
3. **CUDA Toolkit** (Optional) - GPU acceleration

Estimated time: **30 minutes** (or **60 minutes** if adding GPU)

---

## 🎯 STEP 1: OPENRGB APPLICATION (Required - 5 minutes)

### What is OpenRGB?

Application that connects your computer to RGB hardware devices (fans, LEDs, etc.)

### Installation

1. **Download OpenRGB**
   - Visit: <https://openrgb.org/download>
   - Click: "Download OpenRGB v0.9x (Windows)"
   - Save the ZIP file

2. **Extract ZIP**
   - Right-click ZIP file → "Extract All"
   - Extract to: `C:\OpenRGB` (or any folder)

3. **Run OpenRGB**
   - In the extracted folder, find `OpenRGB.exe`
   - Double-click to run
   - Window should open showing detected devices
   - **IMPORTANT:** Keep this window open (minimize to system tray is fine)
   - This application must stay running for RGB to work

4. **Verify**
   - If you see RGB devices listed: ✓ Success
   - If no devices listed: Check USB cables to RGB headers

### Result

✓ OpenRGB.exe running in background  
✓ Communicates with RGB hardware  
✓ Ready for Python code to control

---

## 🎵 STEP 2: FFMPEG INSTALLATION (Required - 10 minutes)

### What is FFmpeg?

Library that encodes/decodes audio files (needed for TTS output)

### Choose ONE installation method

#### **Method A: Download & Manual Setup (Most Reliable)**

1. **Download FFmpeg**
   - Visit: <https://ffmpeg.org/download.html>
   - Find: "Windows builds by BtbN"
   - Click: Latest full build download
   - Filename: `ffmpeg-master-latest-win64-gpl.zip`
   - Download and save

2. **Extract FFmpeg**
   - Right-click ZIP → "Extract All"
   - Extract to: `C:\ffmpeg`
   - Result: `C:\ffmpeg\bin\` contains `ffmpeg.exe`

3. **Add to Windows PATH**
   - Press `Win + X` → Search: "Environment Variables"
   - Click: "Edit the system environment variables"
   - Click: "Environment Variables..." button
   - Under "System variables" → Select "Path" → Click "Edit"
   - Click "New" → Type: `C:\ffmpeg\bin`
   - Click OK on all windows
   - **Restart any open PowerShell/CMD windows**

4. **Verify**

   ```bash
   ffmpeg -version
   ```

   Should show FFmpeg version info (not "command not found")

#### **Method B: Using Package Manager (If available)**

```bash
# Using Chocolatey (if installed):
choco install ffmpeg

# Using WinGet (Windows 10+):
winget install ffmpeg

# Using Scoop (if installed):
scoop install ffmpeg
```text

### Result

✓ FFmpeg installed  
✓ Added to Windows PATH  
✓ `ffmpeg -version` works in terminal

---

## 🎮 STEP 3: CUDA TOOLKIT (Optional - GPU Acceleration)

### What is CUDA?

NVIDIA technology for GPU-accelerated computing (4-10x faster)

### ⚠️ Only needed if you have NVIDIA GPU

**First, check if you have a GPU:**

```bash
nvidia-smi
```text

- If shows GPU info → You have NVIDIA GPU, continue
- If "not found" → No NVIDIA GPU, skip this step
- If shows error → Install/update NVIDIA drivers first

### Installation (if you have GPU)

1. **Install/Update NVIDIA Drivers**
   - Visit: <https://nvidia.com/download/driverDetails.aspx>
   - Select your GPU model
   - Download latest driver
   - Install and restart

2. **Download CUDA Toolkit**
   - Visit: <https://developer.nvidia.com/cuda-toolkit>
   - Choose CUDA 12.1 (or 11.8 for older systems)
   - Select: Windows, x86_64, Local
   - Download installer

3. **Install CUDA**
   - Run installer as Administrator
   - Accept license
   - Click: "Custom Installation"
   - CHECK these:
     - ☑ CUDA Toolkit
     - ☑ NVIDIA cuDNN (included in CUDA 12.1+)
   - Use default paths
   - **After installation: RESTART YOUR COMPUTER**

4. **Reinstall PyTorch for CUDA**

   ```bash
   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Verify GPU

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```text

Should print: `CUDA: True`

### Result

✓ NVIDIA drivers updated  
✓ CUDA Toolkit installed  
✓ PyTorch configured for GPU  
✓ GPU acceleration enabled

---

## ✅ VERIFICATION - Test Everything

After completing steps above, run these commands:

### Test 1: OpenRGB

```bash
python -c "import openrgb_python; print('✓ OpenRGB Python OK')"
```text

### Test 2: FFmpeg

```bash
ffmpeg -version
```text

Should show FFmpeg version

### Test 3: Audio Libraries

```bash
python -c "import torchcodec; print('✓ torchcodec OK')"
python -c "from TTS.api import TTS; print('✓ TTS OK')"
```text

### Test 4: RGB Hardware Detection

```bash
python -c "from omega_rgb_advanced_controller import get_advanced_rgb_controller; status = get_advanced_rgb_controller().get_status(); print(f'RGB Method: {status.get(\"current_method\")}'); print(f'Available: {status.get(\"available_methods\")}')"
```text

**Success:** Should show `RGB Method: OpenRGB` (not `Simulated`)

### Test 5: GPU (if installed)

```bash
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```text

**Success:** Should show `CUDA Available: True` and your GPU name

### Test 6: Complete System

```bash
cd "h:\The Gatekeeper"
python test_rgb_system.py
```text

Should show: `✓ ALL TESTS PASSED`

---

## 🔍 Troubleshooting

### Problem: "ffmpeg not found"

**Solution:**

- Make sure FFmpeg extracted to correct path
- Check Windows PATH includes `C:\ffmpeg\bin`
- Restart terminal window
- Restart computer if PATH was added

### Problem: OpenRGB shows "No devices detected"

**Solution:**

- Check USB cables connected to motherboard RGB headers
- Enable RGB in BIOS (restart → press DEL → look for RGB/Aura settings)
- Update motherboard drivers
- Check in Device Manager for "USB" devices with errors

### Problem: RGB method still shows "Simulated"

**Solution:**

- Is OpenRGB.exe still running? Check taskbar
- Restart OpenRGB.exe
- Check if devices show in OpenRGB window
- If no devices in OpenRGB: hardware connection issue

### Problem: CUDA shows False

**Solution:**

- If you don't have NVIDIA GPU: That's expected, skip GPU steps
- If you have GPU but CUDA is False:
  - Verify NVIDIA drivers: `nvidia-smi`
  - Reinstall CUDA Toolkit
  - Restart computer
  - Reinstall PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu121`

---

## 📋 Installation Checklist

Mark these off as you complete them:

```text
REQUIRED:
□ Downloaded OpenRGB from https://openrgb.org/download
□ Extracted OpenRGB ZIP file
□ OpenRGB.exe is running in background
□ OpenRGB window shows RGB devices detected

□ Downloaded FFmpeg from https://ffmpeg.org/download.html
□ Extracted FFmpeg ZIP to C:\ffmpeg
□ Added C:\ffmpeg\bin to Windows PATH
□ Restarted terminal/PowerShell window
□ Verified: ffmpeg -version works

OPTIONAL (for GPU):
□ Checked: nvidia-smi shows GPU
□ Downloaded CUDA Toolkit 12.1
□ Installed CUDA Toolkit
□ Restarted computer (after CUDA install)
□ Reinstalled PyTorch with CUDA support

VERIFICATION:
□ Ran all 6 verification tests above
□ RGB Method shows "OpenRGB" (not "Simulated")
□ FFmpeg version displayed
□ Audio libraries load without error
□ (If GPU) CUDA shows True
□ test_rgb_system.py shows ALL TESTS PASSED
```text

---

## 🎉 Expected Results

### After completing everything

**RGB System:**

- ✓ OpenRGB.exe running in system tray
- ✓ RGB controller shows "OpenRGB" method
- ✓ Physical LED colors respond to commands
- ✓ Omega control panel RGB color picker works

**Audio System:**

- ✓ FFmpeg installed and in PATH
- ✓ TTS generates audio files successfully
- ✓ Audio playback works from Omega system
- ✓ No FFmpeg encoding errors

**GPU System (Optional):**

- ✓ CUDA detected and available
- ✓ torch.cuda.is_available() returns True
- ✓ System uses GPU for AI/audio tasks
- ✓ 4-10x performance boost on GPU-enabled operations

---

## ⏱️ Time Breakdown

- **OpenRGB:** 5 minutes
- **FFmpeg:** 10 minutes  
- **CUDA (optional):** 45 minutes (includes restart)
- **Testing:** 5 minutes

**Total:** ~20 minutes (or 65 minutes with GPU)

---

## 📞 Need Help?

### Quick Reference

- RGB Guide: `RGB_TROUBLESHOOTING_GUIDE.md`
- Audio Guide: `AUDIO_TROUBLESHOOT.md`
- GPU Guide: `GPU_HARDWARE_SPECIFICATION.md`
- Quick Fix: `QUICK_REFERENCE_CARD.txt`

### Run Diagnostics

```bash
python QUICK_DIAGNOSTICS.py
python COMPREHENSIVE_SYSTEM_DIAGNOSTICS.py
```text

---

## 🔗 Download Links

- **OpenRGB:** <https://openrgb.org/download>
- **FFmpeg:** <https://ffmpeg.org/download.html> (Windows builds by BtbN)
- **CUDA Toolkit:** <https://developer.nvidia.com/cuda-toolkit>
- **NVIDIA Drivers:** <https://nvidia.com/download/>
- **PyTorch:** <https://pytorch.org/get-started/locally/>

---

**Document:** Complete Installation Instructions  
**Date:** January 17, 2026  
**Status:** Ready to follow  
**Next Step:** Start with STEP 1 (OpenRGB download)
