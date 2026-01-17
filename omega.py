# omega.py — Omega Voice System with Dual Voice Cloning
"""
Omega AI Voice System - Uses dual voice cloning for optimal TTS
Supports both clip_0001.wav and omega_downloaded.wav as voice models
"""

from TTS.api import TTS
import os
import torch
import sys

os.environ['TTS_ACCEPT_TO_S'] = '1'

# Auto-pick GPU or CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load XTTS v2 model with voice cloning capabilities
print(f"[Omega] Initializing dual voice system on {device}...")
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
print("[Omega] Voice system ready")

# Detect available voice files
voice_files = []
for vf in ['clip_0001.wav', 'omega_downloaded.wav']:
    if os.path.exists(vf):
        size = os.path.getsize(vf) / (1024 * 1024)
        voice_files.append((vf, size))
        print(f"[Omega] Voice file available: {vf} ({size:.2f} MB)")

def omega_speak(text, voice_model=None, use_voice_clone=True):
    """
    Speak text using TTS with optional voice cloning.
    
    Args:
        text: Text to speak
        voice_model: Voice file to use ('clip_0001.wav' or 'omega_downloaded.wav')
        use_voice_clone: Use voice cloning (True by default)
    """
    try:
        # Auto-select voice if not specified
        if voice_model is None and voice_files:
            voice_model = voice_files[0][0]  # Use first available
        
        # Use voice cloning if available
        speaker_wav = None
        if use_voice_clone and voice_model and os.path.exists(voice_model):
            speaker_wav = voice_model
            print(f"[Omega] Voice cloning enabled with {voice_model}")
        
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language='en',
            file_path='response.wav'
        )
        
        # Non-blocking audio playback
        if sys.platform == 'win32':
            os.startfile('response.wav')
        elif sys.platform == 'darwin':
            os.system('open response.wav')
        else:
            os.system('xdg-open response.wav')
            
        print(f"[Omega] Spoke: {text[:50]}...")
        
    except Exception as e:
        print(f"[Omega ERROR] {e}")

# Test with dual voices
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("OMEGA DUAL VOICE SYSTEM - Multi-Voice Cloning Test")
    print("=" * 70 + "\n")
    
    test_lines = [
        "I have analyzed both voice profiles and created an optimal blend.",
        "My enhanced voice system now supports dual voice cloning.",
        "Selecting the best voice characteristics for perfect synthesis.",
    ]
    
    for i, line in enumerate(test_lines):
        # Alternate between voice files
        selected_voice = voice_files[i % len(voice_files)][0] if voice_files else None
        print(f"\n[Speaking] Using {selected_voice}: {line}")
        omega_speak(line, voice_model=selected_voice, use_voice_clone=True)
    
    print("\n" + "=" * 70)
    print("[Complete] Omega dual voice system test finished")
    print("=" * 70)
