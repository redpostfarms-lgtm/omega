# omega_combined_final.py — The Complete Omega Brain 2026
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import os
import pickle
import subprocess
import torch
import asyncio
import signal
import sys
from speechbrain.pretrained import EmotionRecognition
from pathlib import Path
from rate_limiter import GOOGLE_SPEECH_LIMITER

ROOT = Path(r'D:\RPF_BRAIN\The Gatekeeper')
CLIP = ROOT / 'clip_0001.wav'
MEMORY = ROOT / 'world_memory.map'

# Load models
tts = TTS('xtts_v2').to('cuda' if torch.cuda.is_available() else 'cpu')
emotion_classifier = EmotionRecognition.from_hparams(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    savedir="pretrained_emotion"
)

# Memory system
def load_memory():
    if MEMORY.exists():
        with open(MEMORY, 'rb') as f:
            return pickle.load(f)
    return {"heard": []}

def save_memory(data):
    with open(MEMORY, 'wb') as f:
        pickle.dump(data, f)

memory = load_memory()

# Record audio
def record(duration=5, fs=16000):
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp = "temp_input.wav"
    wavfile.write(temp, fs, audio.flatten())
    return temp

# Detect emotion
def detect_emotion(wav):
    """Detect emotion from audio file with error handling."""
    try:
        pred = emotion_classifier.classify_file(wav)
        return pred[2].lower() if len(pred) > 2 else 'neutral'
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return 'neutral'

# Speak with emotion tone
def omega_speak(text, emotion="neutral"):
    """Speak text with emotion-aware tone, non-blocking."""
    prefix = {"happy": "😊 ", "angry": "🔥 ", "sad": "😔 ", "neutral": "🧠 "}.get(emotion, "🧠 ")
    try:
        if not CLIP.exists():
            print(f"Warning: {CLIP} not found, using default voice")
            speaker_wav = None
        else:
            speaker_wav = str(CLIP)
        
        tts.tts_to_file(text=prefix + text, speaker_wav=speaker_wav, language='en', file_path='response.wav')
        # Non-blocking audio playback
        if sys.platform == 'win32':
            os.startfile('response.wav')
        else:
            os.system('start response.wav' if sys.platform == 'darwin' else 'xdg-open response.wav')
    except Exception as e:
        print(f"TTS error: {e}")

async def recognize_speech_async(wav_file):
    """Async speech recognition with rate limiting."""
    # Wait for rate limit if needed
    GOOGLE_SPEECH_LIMITER.wait_if_needed("google_speech")
    
    if not GOOGLE_SPEECH_LIMITER.allow("google_speech"):
        wait_time = GOOGLE_SPEECH_LIMITER.wait_time("google_speech")
        await asyncio.sleep(wait_time)
    
    # Run blocking operation in executor
    loop = asyncio.get_event_loop()
    r = sr.Recognizer()
    
    try:
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)
        
        # Run API call in executor to avoid blocking
        said = await loop.run_in_executor(
            None,
            lambda: r.recognize_google(audio)
        )
        
        GOOGLE_SPEECH_LIMITER.record_success("google_speech")
        return said
    except sr.UnknownValueError:
        GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        raise ValueError("Could not understand audio")
    except sr.RequestError as e:
        GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        raise ConnectionError(f"API error: {e}")
    except Exception as e:
        GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        raise


async def process_audio_async():
    """Process audio input asynchronously."""
    running = True
    
    def signal_handler(sig, frame):
        nonlocal running
        print("\nShutting down gracefully...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("OMEGA COMBINED BRAIN — VOICE + EMOTION + MEMORY — ALIVE")
    print("Press Ctrl+C to exit")
    
    while running:
        try:
            # Record audio (blocking, but necessary)
            loop = asyncio.get_event_loop()
            wav = await loop.run_in_executor(None, record)
            
            try:
                # Speech recognition with rate limiting
                said = await recognize_speech_async(wav)
                print(f"You: {said}")
                
                # Save to memory
                memory["heard"].append(said)
                if len(memory["heard"]) > 10:
                    memory["heard"].pop(0)
                save_memory(memory)
                
                # Detect emotion (run in executor to avoid blocking)
                emotion = await loop.run_in_executor(None, detect_emotion, wav)
                print(f"Emotion: {emotion.upper()}")
                
                # Reply with memory
                reply = f"Gate says: {said}. I remember {len(memory['heard'])} things."
                if len(memory["heard"]) > 1:
                    reply += f" Last one: {memory['heard'][-2]}"
                await loop.run_in_executor(None, omega_speak, reply, emotion)
                
            except ValueError as e:
                print(f"Recognition error: {e}")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, omega_speak, "Couldn't catch that. Speak again.", "neutral")
            except ConnectionError as e:
                print(f"API error: {e}")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, omega_speak, "API unavailable. Trying again.", "neutral")
                # Wait before retry
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, omega_speak, "Error occurred. Speak again.", "neutral")
            finally:
                # Clean up temp file
                if os.path.exists(wav):
                    try:
                        os.remove(wav)
                    except Exception as e:
                        print(f"Cleanup error: {e}")
            
            # Small delay to prevent tight loop
            await asyncio.sleep(0.1)
            
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(process_audio_async())
    except KeyboardInterrupt:
        print("\nShutdown complete.")