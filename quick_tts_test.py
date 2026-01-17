#!/usr/bin/env python3
"""Quick TTS Test - No fancy symbols"""
import os
import sys

os.environ['TTS_ACCEPT_TO_S'] = '1'

print("\n=== TTS FIX TEST ===\n")

# Test 1: Python and PyTorch
print("[1] Checking imports...")
try:
    import torch
    print(f"    PyTorch: {torch.__version__}")
    print(f"    CUDA: {torch.cuda.is_available()}")
except Exception as e:
    print(f"    ERROR: {e}")
    sys.exit(1)

# Test 2: TTS Import
print("[2] Loading TTS library...")
try:
    from TTS.api import TTS
    print("    TTS library loaded")
except Exception as e:
    print(f"    ERROR: {e}")
    sys.exit(1)

# Test 3: Load model
print("[3] Loading TTS model (may take 1-2 minutes)...")
try:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    print(f"    Model loaded on {device}")
except Exception as e:
    print(f"    ERROR loading model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Generate audio
print("[4] Generating audio...")
try:
    tts.tts_to_file(
        text="The gate is open.",
        file_path="test_tts_output.wav"
    )
    print("    Audio generated!")
except Exception as e:
    print(f"    ERROR generating audio: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify
print("[5] Verifying file...")
if os.path.exists("test_tts_output.wav"):
    size = os.path.getsize("test_tts_output.wav")
    print(f"    File created: {size} bytes")
    print("\n=== SUCCESS! TTS IS WORKING ===\n")
else:
    print("    ERROR: File not created")
    sys.exit(1)
