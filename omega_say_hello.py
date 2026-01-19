import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from omega_full_brain import get_tts, play_audio_background

print("\n[Omega] Generating greeting...")
tts = get_tts()

greeting = "Hello! I'm Omega. I'm ready for hands-free conversation. Voice security is active, and I'm here to learn and improve with you."

print(f"[Omega] {greeting}\n")

tts.tts_to_file(
    text=greeting,
    speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
    language='en',
    file_path='response.wav'
)

print("[Playing greeting in background...]")
play_audio_background('response.wav')

print("\n[OK] Omega has greeted you! Listen for the audio.")
print("[The audio plays in the background - no window will appear]\n")
