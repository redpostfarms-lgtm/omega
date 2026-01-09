# omega.py — Simple Omega Voice Test
from TTS.api import TTS
import os
import torch
import sys

# Auto-pick GPU or CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load XTTS v2 model
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)

def omega_speak(text):
    """Speak text using TTS."""
    try:
        clip_path = 'clip_0001.wav'
        speaker_wav = clip_path if os.path.exists(clip_path) else None
        
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language='en',
            file_path='response.wav'
        )
        # Non-blocking audio playback
        if sys.platform == 'win32':
            os.startfile('response.wav')
        else:
            os.system('start response.wav' if sys.platform == 'darwin' else 'xdg-open response.wav')
    except Exception as e:
        print(f"TTS error: {e}")

# Test — your voice speaks back
if __name__ == "__main__":
    omega_speak('Hey Wiley. Gate\'s open. Worms are singing. Coffee\'s cold.')
