# omega.py — Omega Voice System with Voice Cloning
"""
Omega AI Voice System - Uses voice cloning for personalized TTS responses
Analyzes and improves voice using clip_0001.wav as the voice model
"""

from TTS.api import TTS
import os
import torch
import sys

os.environ['TTS_ACCEPT_TO_S'] = '1'

# Auto-pick GPU or CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load XTTS v2 model with voice cloning capabilities
print(f"[Omega] Initializing voice system on {device}...")
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
print("[Omega] Voice system ready")

def omega_speak(text, use_voice_clone=True):
    """
    Speak text using TTS with optional voice cloning.
    
    Args:
        text: Text to speak
        use_voice_clone: Use clip_0001.wav for voice cloning (True by default)
    """
    try:
        clip_path = 'clip_0001.wav'
        
        # Use voice cloning if available
        speaker_wav = None
        if use_voice_clone and os.path.exists(clip_path):
            speaker_wav = clip_path
            print(f"[Omega] Voice cloning enabled with {clip_path}")
        
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

# Test with voice cloning
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OMEGA VOICE SYSTEM - Voice Cloning Test")
    print("=" * 60 + "\n")
    
    test_lines = [
        "Hey there. I have analyzed my voice and optimized my synthesis.",
        "Gate's open. Worms are singing. Coffee's cold.",
        "I am Omega. My voice is now perfectly cloned and enhanced."
    ]
    
    for line in test_lines:
        print(f"\n[Speaking] {line}")
        omega_speak(line, use_voice_clone=True)
    
    print("\n" + "=" * 60)
    print("[Complete] Omega voice system test finished")
    print("=" * 60)
