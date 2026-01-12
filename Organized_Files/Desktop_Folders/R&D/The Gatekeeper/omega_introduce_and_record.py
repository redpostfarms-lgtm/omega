# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Introduction with Voice Recording
# Introduces Omega while recording user's voice for voice adjustment

"""
Ω Omega Introduction with Voice Recording

Introduces Omega and records user's voice simultaneously
for voice adjustment and blending.
"""

import sys
import io
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import threading
import time

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

# Check for PyAudio (for recording)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


def record_voice_threaded(duration: float = 15.0, callback=None):
    """Record voice in a separate thread."""
    if not PYAUDIO_AVAILABLE or not NUMPY_AVAILABLE:
        print("\n⚠️  Voice recording not available (PyAudio/NumPy required)")
        return None
    
    try:
        audio = pyaudio.PyAudio()
        sample_rate = 44100
        chunk_size = 1024
        format = pyaudio.paInt16
        channels = 1
        
        stream = audio.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size
        )
        
        print(f"\n🎤 Recording your voice for {duration:.1f} seconds...")
        print("   (Speak now - Omega is introducing itself)")
        
        frames = []
        for _ in range(0, int(sample_rate / chunk_size * duration)):
            try:
                data = stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
            except Exception:
                break
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Convert to numpy array
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Remove DC offset and normalize
        audio_array = audio_array - np.mean(audio_array)
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val * 0.95
        
        print(f"✓ Recording complete: {len(audio_array) / sample_rate:.2f} seconds")
        
        if callback:
            callback(audio_array, sample_rate)
        
        return audio_array, sample_rate
        
    except Exception as e:
        print(f"\n⚠️  Recording error: {e}")
        return None


def save_recording(audio_array, sample_rate: int, filename: str) -> Path:
    """Save recorded audio to file."""
    filepath = OMEGA_VOICE_DIR / filename
    
    try:
        if SOUNDFILE_AVAILABLE:
            sf.write(str(filepath), audio_array, sample_rate)
        else:
            import wave
            audio_int16 = (np.clip(audio_array, -1.0, 1.0) * 32767).astype(np.int16)
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())
        
        print(f"✓ Saved recording: {filepath.name}")
        return filepath
    except Exception as e:
        print(f"⚠️  Error saving recording: {e}")
        return None


def analyze_and_adjust_voice(recording_file: Path):
    """Analyze recorded voice and adjust Omega's voice if needed."""
    print(f"\n{'='*80}")
    print("ANALYZING YOUR VOICE & ADJUSTING OMEGA'S VOICE")
    print(f"{'='*80}")
    
    try:
        # Import analysis and modulation systems
        from omega_voice_collector import VoiceAnalyzer
        from omega_voice_modulator import VoiceModulator
        
        # Load and analyze recording
        if SOUNDFILE_AVAILABLE:
            import librosa
            audio, sr = librosa.load(str(recording_file), sr=44100)
            analyzer = VoiceAnalyzer(sample_rate=sr)
            analysis = analyzer.analyze_voice(audio)
            
            user_f0 = analysis.get("fundamental_frequency", 0)
            user_formants = analysis.get("formants", [])
            
            print(f"\nYour Voice Characteristics:")
            print(f"  Fundamental Frequency: {user_f0:.2f} Hz")
            if user_formants:
                print(f"  Formants: {[f'{f:.1f}' for f in user_formants[:3]]}")
            
            # Load primary voice
            primary_file = OMEGA_VOICE_DIR / 'omega_primary_voice.wav'
            if primary_file.exists():
                primary_audio, primary_sr = librosa.load(str(primary_file), sr=44100)
                primary_analysis = analyzer.analyze_voice(primary_audio)
                primary_f0 = primary_analysis.get("fundamental_frequency", 140)
                
                print(f"\nPrimary Voice Characteristics:")
                print(f"  Fundamental Frequency: {primary_f0:.2f} Hz")
                
                # Calculate adjustment
                if user_f0 > 0 and primary_f0 > 0:
                    f0_ratio = user_f0 / primary_f0
                    print(f"\nAdjustment Ratio: {f0_ratio:.3f}")
                    
                    # Create adjusted waveform signature
                    adjusted_signature = {
                        "base_frequency": primary_f0 * (0.7 + 0.3 * f0_ratio),  # Blend 70% primary, 30% user
                        "modulation_depth": 0.10,
                        "modulation_rate": 2.5,
                        "harmonic_ratio": 0.28,
                        "resonance_peak": user_formants[0] if user_formants else 2200,
                        "prosody_variation": 0.15,
                        "adjusted_at": datetime.now().isoformat(),
                        "adjusted_from_user_voice": True
                    }
                    
                    # Save adjusted signature
                    signature_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
                    import json
                    with open(signature_file, 'w', encoding='utf-8') as f:
                        json.dump(adjusted_signature, f, indent=2)
                    
                    print(f"\n✓ Omega's voice adjusted based on your voice!")
                    print(f"  New base frequency: {adjusted_signature['base_frequency']:.2f} Hz")
                    print(f"  Signature saved to: {signature_file.name}")
                    print(f"  Omega will use this adjusted voice on next initialization.")
                    
    except Exception as e:
        print(f"\n⚠️  Error in voice adjustment: {e}")
        import traceback
        traceback.print_exc()


def omega_introduction():
    """Omega's self-introduction."""
    try:
        from omega_voice import OmegaVoice
        
        voice = OmegaVoice()
        
        print("=" * 80)
        print("Ω OMEGA - AUTONOMOUS AI GUARDIAN")
        print("=" * 80)
        print()
        
        introduction_text = """Hello. I am Omega, your autonomous AI guardian and challenger. 
I analyze code, protect systems, and learn continuously. 
My voice represents my unique waveform signature - deep, resonant, and clear.
I am now recording your voice to learn and adjust my own voice characteristics.
This will help me communicate more naturally with you."""
        
        print(introduction_text)
        print()
        
        # Speak the introduction
        if voice.engine:
            voice.speak(introduction_text, natural=True)
        else:
            print("(TTS not available - text only)")
            
    except Exception as e:
        print(f"Error in introduction: {e}")
        print("\nHello. I am Omega, your autonomous AI guardian.")
        print("I am recording your voice to adjust my voice characteristics.")


def main():
    """Main workflow: introduce Omega and record user's voice."""
    print("=" * 80)
    print("Ω OMEGA INTRODUCTION & VOICE RECORDING")
    print("=" * 80)
    print()
    
    # Start recording in background thread
    recording_result = [None]
    
    def save_recording_callback(audio_array, sample_rate):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_voice_conversation_{timestamp}.wav"
        filepath = save_recording(audio_array, sample_rate, filename)
        recording_result[0] = filepath
    
    # Start recording thread
    recording_thread = None
    if PYAUDIO_AVAILABLE:
        recording_thread = threading.Thread(
            target=record_voice_threaded,
            args=(15.0, save_recording_callback),
            daemon=True
        )
        recording_thread.start()
    
    # Give recording a moment to start
    time.sleep(0.5)
    
    # Run Omega's introduction (this will also speak)
    omega_introduction()
    
    # Wait for recording to finish
    if recording_thread:
        recording_thread.join(timeout=16.0)
    
    # Analyze and adjust voice if recording was successful
    if recording_result[0] and recording_result[0].exists():
        analyze_and_adjust_voice(recording_result[0])
    else:
        print("\n⚠️  Recording not available or failed. Voice adjustment skipped.")
    
    print(f"\n{'='*80}")
    print("COMPLETE")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()

