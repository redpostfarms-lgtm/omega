# Fixing TTS (Text-to-Speech) Issues

## Current Status
✅ TTS model loading works  
✅ Terms of service auto-acceptance fixed  
✅ PyTorch 2.6+ compatibility patch applied  
❌ torchcodec incompatibility with PyTorch 2.9.1 (blocks audio generation)

## The Problem
PyTorch 2.9.1 is too new and incompatible with the torchcodec library that TTS uses for audio decoding.

## The Solution

### Step 1: Free Disk Space
Your disk is currently full, which prevents downgrading PyTorch. Free up space by:
- Emptying the Recycle Bin
- Deleting temporary files (`%TEMP%`)
- Removing old downloads
- Uninstalling unused programs

**Need at least 2-3 GB free** for the PyTorch downgrade.

### Step 2: Downgrade PyTorch
Once you have free space, run:
```batch
py -3.11 -m pip install "torch<2.6.0" --upgrade
```

This will install PyTorch 2.5.x, which is compatible with TTS.

### Step 3: Verify Installation
Test TTS:
```batch
py -3.11 SIMPLE_TEST.py
```

You should hear "Hello, this is a test. Can you hear me?" if everything works.

### Step 4: Run Omega
Once TTS works, start Omega:
```batch
START_HERE.bat
```

## Alternative: If You Can't Downgrade PyTorch
If you can't free space, you'll need to:
1. Install FFmpeg with DLLs (for torchcodec)
2. Or wait for TTS/torchcodec to support PyTorch 2.9+

## Quick Check Script
Run `FIX_TTS.bat` to check your current status and get step-by-step guidance.
