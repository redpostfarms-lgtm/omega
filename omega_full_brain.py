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
import subprocess
import time
from pathlib import Path
from rate_limiter import GOOGLE_SPEECH_LIMITER
from omega_monitoring import increment_counter, record_histogram, log_event

# Patch torch.load for PyTorch 2.6+ compatibility with TTS
try:
    original_load = torch.load
    def patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = patched_load
except Exception:
    # If torch isn't imported yet, skip (will patch in get_tts)
    pass

# Load models lazily (first run downloads ~2 GB total)
tts = None
def get_tts():
    """Get TTS instance, loading if needed."""
    global tts
    if tts is None:
        print("Loading TTS model (first time will download ~2GB, please wait)...")
        # Accept TTS terms automatically
        import os
        os.environ['TTS_ACCEPT_TO_S'] = '1'
        
        # Patch torch.load for PyTorch 2.6+ compatibility (if not already patched)
        try:
            if torch.load != patched_load:
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    if 'weights_only' not in kwargs:
                        kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)
                torch.load = patched_load
        except Exception:
            # Patch failed - will try again later
            pass
        
        try:
            # Use the full model path that TTS expects
            tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cuda' if torch.cuda.is_available() else 'cpu')
            print("[OK] TTS model loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load TTS model: {e}")
            if 'torchcodec' in str(e).lower() or 'libtorchcodec' in str(e).lower():
                print("[INFO] This is a PyTorch 2.6+ compatibility issue.")
                print("      Try: py -3.11 -m pip install 'torch<2.6.0'")
            raise
    return tts

# Load emotion classifier (optional - gracefully handle if unavailable)
emotion_classifier = None
try:
    from speechbrain.pretrained import EmotionRecognition
    emotion_classifier = EmotionRecognition.from_hparams(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        savedir="pretrained_emotion"
    )
    print("[OK] Emotion detection enabled")
except Exception as e:
    print(f"[WARNING] Emotion detection unavailable: {e}")
    print("   Continuing without emotion detection...")
    emotion_classifier = None  # Make sure it's set to None if failed

# Load advanced emotion detector (wav2vec2 - better accuracy)
advanced_emotion_detector = None
try:
    from omega_emotion_advanced import get_emotion_detector
    advanced_emotion_detector = get_emotion_detector()
    if advanced_emotion_detector.available:
        print("[OK] Advanced emotion detection enabled (wav2vec2)")
    else:
        print("[INFO] Advanced emotion detection unavailable - using basic")
        advanced_emotion_detector = None
except Exception as e:
    print(f"[INFO] Advanced emotion detection not loaded: {e}")
    advanced_emotion_detector = None

def record_audio(duration=5, fs=16000):
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp_wav = "temp_input.wav"
    wavfile.write(temp_wav, fs, audio.flatten())
    return temp_wav

def detect_emotion(wav_file):
    """
    Detect emotion from audio file with error handling.
    Uses advanced wav2vec2 model if available, fallback to basic.
    """
    # Try advanced detector first (better accuracy)
    if advanced_emotion_detector is not None:
        try:
            result = advanced_emotion_detector.detect_from_file(wav_file)
            if result and result.confidence > 0.5:
                print(f"[Advanced] Detected: {result.emotion} ({result.confidence:.1%})")
                return result.emotion
        except Exception as e:
            print(f"Advanced emotion detection error: {e}")

    # Fallback to basic emotion classifier
    if emotion_classifier is None:
        return 'neutral'
    try:
        prediction = emotion_classifier.classify_file(wav_file)
        detected = prediction[2].lower() if len(prediction) > 2 else 'neutral'
        print(f"[Basic] Detected: {detected}")
        return detected
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

def omega_speak(text, emotion="neutral"):
    """Speak text with emotion-aware tone, using voice clone, non-blocking background playback."""
    # Always use voice clone for better quality
    clip_path = Path('clip_0001.wav')
    speaker_wav = str(clip_path) if clip_path.exists() else None

    if speaker_wav:
        print(f"[Using voice clone: {clip_path.name} for improved quality]")
    else:
        print("[WARNING] clip_0001.wav not found - using default voice")

    # Emotion-aware tone (text only, no emoji to avoid Unicode issues on Windows)
    emotion_prefix = {"happy": "[Happy] ", "angry": "[Angry] ", "sad": "[Sad] ", "neutral": ""}.get(emotion, "")
    text_with_emotion = emotion_prefix + text

    try:
        print(f"Generating speech: {text_with_emotion[:50]}...")

        # Start timing TTS generation
        start_time = time.time()

        tts_instance = get_tts()
        tts_instance.tts_to_file(
            text=text_with_emotion,
            speaker_wav=speaker_wav,  # Always use voice clone if available
            language='en',
            file_path='response.wav'
        )

        # Record TTS generation metrics
        duration = time.time() - start_time
        increment_counter('tts_generation_total')
        record_histogram('tts_generation_duration', duration)
        log_event('tts_generation', level='info', duration=duration, emotion=emotion, text_length=len(text))

        file_size = Path('response.wav').stat().st_size if Path('response.wav').exists() else 0
        print(f"[OK] Audio generated: response.wav ({file_size} bytes, {duration:.2f}s)")

        # Play audio in background without showing media player window
        print("[Playing audio in background - no window will appear]")
        play_audio_background('response.wav')
    except Exception as e:
        print(f"TTS error: {e}")
        # Record TTS error
        increment_counter('tts_generation_errors')
        log_event('tts_error', level='error', error=str(e))
        import traceback
        traceback.print_exc()

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

    # Start timing speech recognition
    start_time = time.time()

    try:
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)

        # Run API call in executor to avoid blocking
        said = await loop.run_in_executor(
            None,
            lambda: r.recognize_google(audio)
        )

        # Record successful recognition metrics
        duration = time.time() - start_time
        increment_counter('speech_recognition_total')
        record_histogram('speech_recognition_duration', duration)
        log_event('speech_recognition', level='info', duration=duration, text_length=len(said))

        GOOGLE_SPEECH_LIMITER.record_success("google_speech")
        return said
    except sr.UnknownValueError:
        # Record recognition error
        duration = time.time() - start_time
        increment_counter('speech_recognition_errors')
        log_event('speech_recognition_error', level='warning', error='UnknownValueError', duration=duration)

        GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        raise ValueError("Could not understand audio")
    except sr.RequestError as e:
        # Record API error
        duration = time.time() - start_time
        increment_counter('speech_recognition_errors')
        log_event('speech_recognition_error', level='error', error=f'RequestError: {e}', duration=duration)

        GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        raise ConnectionError(f"API error: {e}")
    except Exception as e:
        # Record generic error
        duration = time.time() - start_time
        increment_counter('speech_recognition_errors')
        log_event('speech_recognition_error', level='error', error=str(e), duration=duration)

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