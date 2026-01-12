#!/usr/bin/env python3
# Simple TTS test - no emotion, just speak
import os
import sys
from pathlib import Path
import threading
import time

# Accept TTS terms - set env var AND mock input
os.environ['TTS_ACCEPT_TO_S'] = '1'

# Auto-answer 'y' to any TTS prompts
import builtins
original_input = builtins.input
def mock_input(prompt=''):
    # Always return 'y' during TTS loading (TTS prompts during model download)
    print('y')  # Print the answer for visibility
    return 'y'

# Patch input BEFORE importing TTS
builtins.input = mock_input

print("Loading TTS model (first time downloads ~2GB)...")
print("Please wait, this may take a few minutes...")
print("Auto-accepting TTS terms of service...\n")

try:
    import torch
    # Patch torch.load to use weights_only=False for TTS compatibility with PyTorch 2.6+
    original_load = torch.load
    def patched_load(*args, **kwargs):
        # Remove weights_only if it exists, then set to False
        kwargs.pop('weights_only', None)
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
    
    from TTS.api import TTS
    
    # Use full model path
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cpu')
finally:
    # Restore original input
    builtins.input = original_input
print("[OK] TTS model loaded\n")

# Test text
test_text = "Hello, this is a test. Can you hear me?"
print(f"Generating speech: {test_text}")

# Always use voice clone for better quality
clip_path = Path('clip_0001.wav')
speaker_wav = str(clip_path) if clip_path.exists() else None

if speaker_wav:
    print(f"[Using voice clone: {speaker_wav} for better quality]")
else:
    print("[WARNING] clip_0001.wav not found - using default voice")

try:
    print(f"Generating speech with voice clone...")
    tts.tts_to_file(
        text=test_text,
        speaker_wav=speaker_wav,  # Use voice clone
        language='en',
        file_path='test_simple.wav'
    )
except RuntimeError as e:
    if 'torchcodec' in str(e).lower() or 'libtorchcodec' in str(e).lower():
        print(f"[WARNING] torchcodec error: {e}")
        print("[INFO] This is a known issue. Try:")
        print("  1. Free disk space")
        print("  2. Downgrade PyTorch: py -3.11 -m pip install 'torch<2.6.0'")
        print("  3. Or install FFmpeg with DLLs")
        sys.exit(1)
    else:
        raise

print(f"[OK] Audio file created: test_simple.wav")

# Play audio in background without showing media player
def play_background(wav_file):
    """Play audio in background without showing window."""
    if not Path(wav_file).exists():
        print(f"[ERROR] Audio file not created: {wav_file}")
        return
    
    try:
        if sys.platform == 'win32':
            # Use PowerShell MediaPlayer (hidden)
            import subprocess
            ps_cmd = f'''
            Add-Type -AssemblyName presentationCore
            $mp = New-Object system.windows.media.mediaplayer
            $mp.open([uri]::new('{Path(wav_file).absolute().as_uri()}'))
            $mp.Play()
            Start-Sleep -Seconds 10
            '''
            subprocess.Popen(
                ['powershell', '-Command', ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            os.system(f'ffplay -nodisp -autoexit {wav_file} &')
    except Exception as e:
        print(f"Background playback error: {e}, trying fallback...")
        try:
            os.startfile(wav_file)
        except:
            pass

print("[OK] Playing audio in background (no window)...")
play_background('test_simple.wav')

print("\n[OK] TTS is working! Audio should be playing in the background.")
print("If you don't hear it, check Windows volume settings.")
