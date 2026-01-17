#!/usr/bin/env python3
import os
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ['TTS_ACCEPT_TO_S'] = '1'

print("[*] TTS Fix Test - Omega Voice System")
print("=" * 50)

print("\n[1/4] Checking Python & torch...")
import torch
print(f"  [OK] Python {sys.version.split()[0]}")
print(f"  [OK] PyTorch {torch.__version__}")
print(f"  [OK] CUDA available: {torch.cuda.is_available()}")

print("\n[2/4] Testing TTS model load...")
try:
    from TTS.api import TTS
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"  [LOAD] XTTS v2 on {device}...")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    print(f"  [OK] TTS model loaded successfully on {device}")
except Exception as e:
    print(f"  [ERROR] Error loading TTS: {e}")
    sys.exit(1)

print("\n[3/4] Testing audio generation...")
try:
    print("  [GENERATE] Creating audio file...")
    tts.tts_to_file(
        text="Hello, this is a test. Can you hear me? The gate is open.",
        file_path="test_tts_output.wav"
    )
    print("  [OK] Audio file generated successfully!")
except Exception as e:
    print(f"  [ERROR] Error generating audio: {e}")
    print(f"\n  ERROR TYPE: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4/4] Verifying output file...")
if os.path.exists("test_tts_output.wav"):
    size = os.path.getsize("test_tts_output.wav")
    print(f"  [OK] File created: test_tts_output.wav ({size} bytes)")
    print("\n" + "=" * 50)
    print("[SUCCESS] TTS SYSTEM IS WORKING!")
    print("=" * 50)
else:
    print("  [ERROR] No file created")
    sys.exit(1)

print("\n[Next] Run: python omega.py")
