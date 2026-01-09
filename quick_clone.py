# quick_clone.py — Quick voice clone test
from TTS.api import TTS
import os
import sys

tts = TTS('xtts_v2')

try:
    clip_path = 'clip_0001.wav'
    if not os.path.exists(clip_path):
        print(f"Warning: {clip_path} not found, using default voice")
        clip_path = None
    
    tts.tts_to_file(
        text="Hey Wiley. Gate's open. Worms are singing. Coffee's cold.",
        speaker_wav=clip_path,
        language='en',
        file_path='omega_now.wav'
    )
    
    # Non-blocking audio playback
    if sys.platform == 'win32':
        os.startfile('omega_now.wav')
    else:
        os.system('start omega_now.wav' if sys.platform == 'darwin' else 'xdg-open omega_now.wav')
    
    print("Alive.")
except Exception as e:
    print(f"Error: {e}")
