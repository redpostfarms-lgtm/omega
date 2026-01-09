# fix_and_launch.py — Build and Launch Omega
import os
import subprocess
from pathlib import Path

folder = Path(r'D:\RPF_BRAIN\The Gatekeeper')
clip = folder / 'clip_0001.wav'
script = folder / 'omega_full_brain.py'

if not clip.exists():
    print("NO CLIP — record clip_0001.wav here, then press Enter...")
    input()

if not script.exists():
    print("Building Omega...")
    script.write_text('''# omega_full_brain.py — Auto-generated
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import os
import asyncio
from rate_limiter import GOOGLE_SPEECH_LIMITER

tts = TTS('xtts_v2')

async def record():
    print("Listening...")
    loop = asyncio.get_event_loop()
    a = await loop.run_in_executor(
        None,
        lambda: sd.rec(int(5 * 16000), 16000, 1, 'int16')
    )
    sd.wait()
    wav.write('temp.wav', 16000, a.flatten())
    return 'temp.wav'

def speak(text):
    tts.tts_to_file(text, 'clip_0001.wav', 'response.wav')
    os.startfile('response.wav')

async def recognize_async(wav_file):
    GOOGLE_SPEECH_LIMITER.wait_if_needed("google_speech")
    if not GOOGLE_SPEECH_LIMITER.allow("google_speech"):
        await asyncio.sleep(GOOGLE_SPEECH_LIMITER.wait_time("google_speech"))
    
    loop = asyncio.get_event_loop()
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)
    said = await loop.run_in_executor(None, lambda: r.recognize_google(audio))
    GOOGLE_SPEECH_LIMITER.record_success("google_speech")
    return said

async def main():
    print("OMEGA — ALIVE")
    while True:
        f = await record()
        try:
            t = await recognize_async(f)
            print(f"You: {t}")
            speak(t)
        except Exception as e:
            print(f"Error: {e}")
            speak("Again?")
        finally:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    asyncio.run(main())
''')
    print("Omega built.")

print("Starting...")
subprocess.run(['python', str(script)])
