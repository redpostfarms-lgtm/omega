from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import os
import pickle
import torch
import asyncio
import signal
import sys
from pathlib import Path
from rate_limiter import GOOGLE_SPEECH_LIMITER

tts = TTS('xtts_v2').to('cuda' if torch.cuda.is_available() else 'cpu')
MEMORY_FILE = Path('memory.map')

def load_memory():
    """Load memory from file."""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Memory load error: {e}")
    return {'heard': []}

def save_memory(m):
    """Save memory to file."""
    try:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'wb') as f:
            pickle.dump(m, f)
    except Exception as e:
        print(f"Memory save error: {e}")

memory = load_memory()

def record():
    """Record audio from microphone."""
    print('Listening...')
    try:
        audio = sd.rec(
            frames=int(5 * 16000),
            samplerate=16000,
            channels=1,
            device=None,  # Use default device
            dtype='int16'
        )
        sd.wait()
        wavfile.write('temp.wav', 16000, audio.flatten())
        return 'temp.wav'
    except Exception as e:
        print(f"Recording error: {e}")
        raise

def speak(text):
    """Speak text, non-blocking."""
    try:
        clip_path = Path('clip_0001.wav')
        speaker_wav = str(clip_path) if clip_path.exists() else None
        
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            file_path='out.wav'
        )
        if sys.platform == 'win32':
            os.startfile('out.wav')
        else:
            os.system('start out.wav' if sys.platform == 'darwin' else 'xdg-open out.wav')
    except Exception as e:
        print(f"TTS error: {e}")

async def recognize_speech_async(wav_file):
    """Async speech recognition with rate limiting."""
    GOOGLE_SPEECH_LIMITER.wait_if_needed("google_speech")
    
    if not GOOGLE_SPEECH_LIMITER.allow("google_speech"):
        wait_time = GOOGLE_SPEECH_LIMITER.wait_time("google_speech")
        await asyncio.sleep(wait_time)
    
    loop = asyncio.get_event_loop()
    r = sr.Recognizer()
    
    try:
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)
        
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
    
    print('OMEGA — YOUR VOICE — ALIVE')
    print("Press Ctrl+C to exit")
    
    while running:
        try:
            loop = asyncio.get_event_loop()
            wav = await loop.run_in_executor(None, record)
            
            try:
                said = await recognize_speech_async(wav)
                print(f'You: {said}')
                
                memory['heard'].append(said)
                if len(memory['heard']) > 10:
                    memory['heard'].pop(0)
                save_memory(memory)
                
                reply = f"Gate heard: {said}. I remember {len(memory['heard'])} things."
                if len(memory['heard']) > 1:
                    reply += f" Last: {memory['heard'][-2]}"
                
                await loop.run_in_executor(None, speak, reply)
                
            except ValueError as e:
                print(f'Miss: {e}')
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, speak, "Say again.")
            except ConnectionError as e:
                print(f"API error: {e}")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, speak, "API unavailable. Trying again.")
                await asyncio.sleep(2)
            except Exception as e:
                print(f'Error: {e}')
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, speak, "Error occurred. Speak again.")
            finally:
                if os.path.exists(wav):
                    try:
                        os.remove(wav)
                    except Exception as e:
                        print(f"Cleanup error: {e}")
            
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
