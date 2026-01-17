# Python Version Issue

## Problem
You have Python 3.14.2 installed, but the TTS library requires Python 3.9-3.11.

## Solution Options

### Option 1: Install TTS without version check (may work)
```cmd
cd "D:\RPF_BRAIN\The Gatekeeper"
py -m pip install TTS --no-deps
py -m pip install torch sounddevice numpy scipy speech_recognition librosa noisereduce pydub soundfile
```text

### Option 2: Use Python 3.11 (Recommended)
1. Download Python 3.11 from python.org
2. Install it (check "Add to PATH")
3. Use `py -3.11` to run with Python 3.11:
   ```cmd
   py -3.11 -m pip install -r requirements.txt
   py -3.11 omega_full_brain.py
   ```

### Option 3: Create a virtual environment with Python 3.11
```cmd
py -3.11 -m venv omega_env
omega_env\Scripts\activate
pip install -r requirements.txt
python omega_full_brain.py
```text

## Quick Fix (Try This First)
Run this command:
```cmd
cd "D:\RPF_BRAIN\The Gatekeeper"
py -m pip install TTS torch sounddevice numpy scipy SpeechRecognition librosa noisereduce pydub soundfile speechbrain --no-deps
```text

Then try running Omega again.
