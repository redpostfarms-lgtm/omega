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
from pathlib import Path
from rate_limiter import GOOGLE_SPEECH_LIMITER

ROOT = Path(r'D:\RPF_BRAIN\The Gatekeeper')
CLIP = ROOT / 'clip_0001.wav'
MEMORY = ROOT / 'world_memory.map'

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
    if emotion_classifier is None:
        return 'neutral'
    try:
        pred = emotion_classifier.classify_file(wav)
        return pred[2].lower() if len(pred) > 2 else 'neutral'
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return 'neutral'

def play_audio_background(wav_file):
    """Play audio file in background without showing media player window."""
    if not Path(wav_file).exists():
        print(f"Audio file not found: {wav_file}")
        return
    
    try:
        if sys.platform == 'win32':
            # Use PowerShell MediaPlayer for hidden background playback
            # Escape path for PowerShell (replace backslashes and single quotes)
            # Use .format() instead of f-string to safely handle paths with curly braces
            abs_path = str(Path(wav_file).absolute()).replace('\\', '/').replace("'", "''")
            ps_cmd = '''
            Add-Type -AssemblyName presentationCore
            $mediaPlayer = New-Object system.windows.media.mediaplayer
            $mediaPlayer.open([uri]::new('file:///{0}'))
            $mediaPlayer.Volume = 1.0
            $mediaPlayer.Play()
            # Wait for playback to complete by polling Position vs NaturalDuration
            # Max 5 minutes timeout for safety (prevents infinite loops)
            $timeout = (Get-Date).AddMinutes(5)
            while ($mediaPlayer.Position -lt $mediaPlayer.NaturalDuration.TimeSpan -and (Get-Date) -lt $timeout) {{
                Start-Sleep -Milliseconds 100
            }}
            '''.format(abs_path)
            # Run PowerShell in background, hidden window
            subprocess.Popen(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else subprocess.DETACHED_PROCESS
            )
        else:
            # Linux/macOS: use background process with proper escaping
            import shlex
            safe_wav_file = shlex.quote(str(Path(wav_file).absolute()))
            if os.system('which ffplay > /dev/null 2>&1') == 0:
                os.system(f'ffplay -nodisp -autoexit {safe_wav_file} &')
            else:
                os.system(f'play {safe_wav_file} &')
    except Exception as e:
        print(f"Background audio playback error: {e}")
        # Fallback: try minimized window
        try:
            # Use shell=True with string command (not list) for Windows cmd
            cmd_str = f'start /min "" "{wav_file}"'
            subprocess.Popen(cmd_str, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        except Exception:
            # Fallback playback failed - audio may not play
            pass

# Speak with emotion tone
def omega_speak(text, emotion="neutral"):
    """Speak text with emotion-aware tone, using voice clone, non-blocking background playback."""
    # Always use voice clone for better quality
    if not CLIP.exists():
        print(f"Warning: {CLIP} not found, using default voice")
        speaker_wav = None
    else:
        speaker_wav = str(CLIP)
        print(f"[Using voice clone: {CLIP.name} for improved quality]")
    
    # Emotion-aware tone (text only, no emoji to avoid Unicode issues on Windows)
    emotion_prefix = {"happy": "[Happy] ", "angry": "[Angry] ", "sad": "[Sad] ", "neutral": ""}.get(emotion, "")
    text_with_emotion = emotion_prefix + text
    
    try:
        print(f"Generating speech: {text_with_emotion[:50]}...")
        get_tts().tts_to_file(
            text=text_with_emotion, 
            speaker_wav=speaker_wav,  # Always use voice clone if available
            language='en', 
            file_path='response.wav'
        )
        
        file_size = Path('response.wav').stat().st_size if Path('response.wav').exists() else 0
        print(f"[OK] Audio generated: response.wav ({file_size} bytes)")
        
        # Play audio in background without showing media player window
        print("[Playing audio in background - no window will appear]")
        play_audio_background('response.wav')
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