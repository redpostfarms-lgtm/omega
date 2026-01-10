# omega_full_brain.py — Final Voice + Emotion Brain (2026)
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import os
import torch
import asyncio
import signal
import sys
from pathlib import Path
from rate_limiter import GOOGLE_SPEECH_LIMITER

# Load models lazily (first run downloads ~2 GB total)
tts = None
def get_tts():
    """Get TTS instance, loading if needed."""
    global tts
    if tts is None:
        # Accept TTS terms automatically
        import os
        os.environ['TTS_ACCEPT_TO_S'] = '1'
        tts = TTS('xtts_v2').to('cuda' if torch.cuda.is_available() else 'cpu')
    return tts

# Load emotion classifier (optional - gracefully handle if unavailable)
emotion_classifier = None
try:
    from speechbrain.pretrained import EmotionRecognition
    emotion_classifier = EmotionRecognition.from_hparams(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        savedir="pretrained_emotion"
    )
    print("✓ Emotion detection enabled")
except Exception as e:
    print(f"⚠ Emotion detection unavailable: {e}")
    print("   Continuing without emotion detection...")

def record_audio(duration=5, fs=16000):
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp_wav = "temp_input.wav"
    wavfile.write(temp_wav, fs, audio.flatten())
    return temp_wav

def detect_emotion(wav_file):
    """Detect emotion from audio file with error handling."""
    if emotion_classifier is None:
        return 'neutral'
    try:
        prediction = emotion_classifier.classify_file(wav_file)
        return prediction[2].lower() if len(prediction) > 2 else 'neutral'
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return 'neutral'

def omega_speak(text, emotion="neutral"):
    """Speak text with emotion-aware tone, non-blocking."""
    # Emotion-aware tone
    if emotion == "happy":
        text = f"😊 {text} Great news!"
    elif emotion == "angry":
        text = f"🔥 {text} Calm down, Wiley."
    elif emotion == "sad":
        text = f"😔 {text} I'm here."
    else:
        text = f"🧠 {text}"
    
    try:
        clip_path = Path('clip_0001.wav')
        if not clip_path.exists():
            print(f"Warning: {clip_path} not found, using default voice")
            clip_path = None
        
        get_tts().tts_to_file(
            text=text,
            speaker_wav=str(clip_path) if clip_path else None,
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
    
    print("OMEGA FULL BRAIN — VOICE + EMOTION — ALWAYS LISTENING")
    print("Press Ctrl+C to exit")
    
    while running:
        try:
            # Record audio (blocking, but necessary)
            loop = asyncio.get_event_loop()
            wav = await loop.run_in_executor(None, record_audio)
            
            try:
                # Speech recognition with rate limiting
                said = await recognize_speech_async(wav)
                print(f"Wiley: {said}")
                
                # Emotion detection (run in executor to avoid blocking)
                emotion = await loop.run_in_executor(None, detect_emotion, wav)
                print(f"Emotion detected: {emotion.upper()}")
                
                # Reply with emotion-aware tone
                reply = f"Gate says: {said}. I feel your {emotion}."
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