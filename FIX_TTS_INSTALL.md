# Fix TTS Installation Issue

## Problem
TTS installation failed because it requires **Microsoft Visual C++ 14.0 or greater** to compile.

## Solution Options

### Option 1: Install Microsoft C++ Build Tools (Recommended)
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "C++ build tools" workload
4. Install (this is ~6GB)
5. Restart your computer
6. Then run: `py -3.11 -m pip install TTS`

### Option 2: Try Installing Pre-built Wheel
Sometimes pre-built wheels are available:
```cmd
py -3.11 -m pip install TTS --only-binary :all:
```text

### Option 3: Alternative TTS Library
We could modify Omega to use a different TTS library that doesn't require compilation, but this would require code changes.

## Current Status
✅ Python 3.11 installed
✅ Most dependencies installed (torch, sounddevice, numpy, scipy, etc.)
❌ TTS failed to install (needs C++ build tools)

## Quick Install Command (After installing C++ Build Tools)
```cmd
py -3.11 -m pip install TTS
```text

---

**Recommendation:** Install Microsoft C++ Build Tools, then retry TTS installation.
