# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Soundboard - Sound Generation & Voice Manipulation System
# Quantum Web Scrub Enhanced - Research-Based Sound Synthesis

"""
Ω Omega Soundboard

Comprehensive sound generation and voice manipulation system:
- Sound synthesis (sine, square, sawtooth, noise, etc.)
- Voice modulation (pitch, formant, time, effects)
- Sound effects library
- Real-time audio processing
- Waveform recording and analysis
- Voice cloning and morphing

Research Sources:
- WaveNet Vocoder (DeepMind)
- NSynth (Google Magenta)
- librosa, soundfile, pydub
- Real-time audio processing techniques
"""

import sys
import io
import json
import time
import wave
import math
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable
from datetime import datetime
from collections import defaultdict

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

OMEGA_SOUNDBOARD_DIR = OMEGA_VOICE_DIR / 'soundboard'
OMEGA_SOUNDBOARD_DIR.mkdir(parents=True, exist_ok=True)

# Audio libraries
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Import quantum enhancements
_enhanced_path = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if _enhanced_path.exists() and str(_enhanced_path) not in sys.path:
    sys.path.insert(0, str(_enhanced_path))

try:
    from omega_quantum_enhanced import CRYPTO_RNG, HARDWARE_ENTROPY
    QUANTUM_RNG_AVAILABLE = True
except ImportError:
    QUANTUM_RNG_AVAILABLE = False
    import random
    CRYPTO_RNG = None
    HARDWARE_ENTROPY = None


class SoundSynthesizer:
    """Generate synthetic sounds - sine, square, sawtooth, noise, etc."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def sine_wave(self, frequency: float, duration: float, amplitude: float = 0.5, phase: float = 0.0):
        """Generate sine wave."""
        if not NUMPY_AVAILABLE:
            return None
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        return wave
    
    def square_wave(self, frequency: float, duration: float, amplitude: float = 0.5):
        """Generate square wave."""
        if not NUMPY_AVAILABLE:
            return None
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = amplitude * signal.square(2 * np.pi * frequency * t) if SCIPY_AVAILABLE else amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        return wave
    
    def sawtooth_wave(self, frequency: float, duration: float, amplitude: float = 0.5):
        """Generate sawtooth wave."""
        if not NUMPY_AVAILABLE:
            return None
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        if SCIPY_AVAILABLE:
            wave = amplitude * signal.sawtooth(2 * np.pi * frequency * t)
        else:
            wave = amplitude * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        return wave
    
    def triangle_wave(self, frequency: float, duration: float, amplitude: float = 0.5):
        """Generate triangle wave."""
        if not NUMPY_AVAILABLE:
            return None
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        if SCIPY_AVAILABLE:
            wave = amplitude * signal.sawtooth(2 * np.pi * frequency * t, 0.5)
        else:
            saw = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            wave = amplitude * (2 * np.abs(saw) - 1)
        return wave
    
    def white_noise(self, duration: float, amplitude: float = 0.1):
        """Generate white noise."""
        if not NUMPY_AVAILABLE:
            return None
        
        samples = int(self.sample_rate * duration)
        if QUANTUM_RNG_AVAILABLE and HARDWARE_ENTROPY:
            # Use quantum RNG for noise
            noise_bytes = HARDWARE_ENTROPY.get_entropy_bytes(samples * 2)
            noise = np.frombuffer(noise_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            noise = noise[:samples]  # Trim to exact length
        else:
            noise = np.random.randn(samples).astype(np.float32)
        
        return noise * amplitude
    
    def pink_noise(self, duration: float, amplitude: float = 0.1):
        """Generate pink noise (1/f noise)."""
        if not NUMPY_AVAILABLE:
            return None
        
        white = self.white_noise(duration, 1.0)
        if white is None:
            return None
        
        # Apply pink noise filter
        if SCIPY_AVAILABLE:
            # Simple pink noise filter
            b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
            a = [1, -2.494956002, 2.017265875, -0.522189400]
            pink = signal.lfilter(b, a, white)
        else:
            # Simplified pink noise
            pink = white * np.sqrt(np.abs(np.fft.fftfreq(len(white), 1/self.sample_rate)) + 1e-10)
            pink = np.real(np.fft.ifft(np.fft.fft(pink)))
        
        return pink * amplitude
    
    def tone_sequence(self, frequencies: List[float], durations: List[float], amplitude: float = 0.5):
        """Generate sequence of tones."""
        if not NUMPY_AVAILABLE:
            return None
        
        waves = []
        for freq, dur in zip(frequencies, durations):
            wave = self.sine_wave(freq, dur, amplitude)
            if wave is not None:
                waves.append(wave)
        
        if waves:
            return np.concatenate(waves)
        return None
    
    def chord(self, frequencies: List[float], duration: float, amplitude: float = 0.5):
        """Generate chord from multiple frequencies."""
        if not NUMPY_AVAILABLE:
            return None
        
        waves = []
        for freq in frequencies:
            wave = self.sine_wave(freq, duration, amplitude / len(frequencies))
            if wave is not None:
                waves.append(wave)
        
        if waves:
            return np.sum(waves, axis=0)
        return None


class VoiceModulator:
    """Advanced voice modulation - pitch, formant, time, effects."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def pitch_shift(self, audio, semitones: float):
        """Shift pitch without changing speed."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        if LIBROSA_AVAILABLE:
            try:
                return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=semitones)
            except Exception:
                pass
        
        # Fallback: simple resampling method
        if SCIPY_AVAILABLE:
            factor = 2 ** (semitones / 12.0)
            indices = np.round(np.arange(0, len(audio), 1/factor))
            indices = indices[indices < len(audio)].astype(int)
            return audio[indices]
        
        return audio
    
    def time_stretch(self, audio, rate: float):
        """Stretch time without changing pitch."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        if LIBROSA_AVAILABLE:
            try:
                return librosa.effects.time_stretch(audio, rate=rate)
            except Exception:
                pass
        
        # Fallback: simple resampling
        if SCIPY_AVAILABLE:
            indices = np.linspace(0, len(audio) - 1, int(len(audio) * rate))
            indices = indices.astype(int)
            return audio[indices]
        
        return audio
    
    def formant_shift(self, audio, shift: float):
        """Shift formants (vocal tract characteristics)."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        if LIBROSA_AVAILABLE:
            try:
                # Formant shifting using spectral manipulation
                stft = librosa.stft(audio)
                magnitude = np.abs(stft)
                phase = np.angle(stft)
                
                # Shift formants by modifying magnitude spectrum
                freqs = librosa.fft_frequencies(sr=self.sample_rate)
                shifted_freqs = freqs * (1 + shift)
                
                # Interpolate magnitude
                from scipy.interpolate import interp1d
                interp = interp1d(freqs, magnitude, axis=0, kind='linear', fill_value=0, bounds_error=False)
                shifted_magnitude = interp(shifted_freqs)
                
                # Reconstruct
                shifted_stft = shifted_magnitude * np.exp(1j * phase)
                return librosa.istft(shifted_stft)
            except Exception:
                pass
        
        return audio
    
    def add_reverb(self, audio, room_size: float = 0.5, damping: float = 0.5):
        """Add reverb effect."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        if SCIPY_AVAILABLE:
            try:
                # Simple reverb using delay and feedback
                delay_samples = int(self.sample_rate * 0.03 * room_size)  # 30ms base delay
                delay = np.zeros(delay_samples)
                output = np.zeros_like(audio)
                
                for i in range(len(audio)):
                    if i < delay_samples:
                        output[i] = audio[i]
                    else:
                        output[i] = audio[i] + delay[i - delay_samples] * damping
                        delay = np.roll(delay, 1)
                        delay[0] = output[i] * damping
                
                return output
            except Exception:
                pass
        
        return audio
    
    def add_chorus(self, audio, depth: float = 0.3, rate: float = 1.5):
        """Add chorus effect."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        try:
            # Chorus using modulated delay
            delay_samples = int(self.sample_rate * 0.01)  # 10ms delay
            output = np.zeros_like(audio)
            
            for i in range(len(audio)):
                delay_offset = int(delay_samples * (1 + depth * math.sin(2 * math.pi * rate * i / self.sample_rate)))
                if i >= delay_offset:
                    output[i] = audio[i] + audio[i - delay_offset] * 0.5
                else:
                    output[i] = audio[i]
            
            return output
        except Exception:
            return audio
    
    def add_vibrato(self, audio, depth: float = 0.02, rate: float = 5.0):
        """Add vibrato effect."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        try:
            # Vibrato using pitch modulation
            t = np.arange(len(audio)) / self.sample_rate
            pitch_mod = depth * np.sin(2 * np.pi * rate * t)
            
            # Apply pitch modulation
            output = np.zeros_like(audio)
            for i in range(len(audio)):
                source_idx = int(i * (1 + pitch_mod[i]))
                if source_idx < len(audio):
                    output[i] = audio[source_idx]
                else:
                    output[i] = audio[-1]
            
            return output
        except Exception:
            return audio
    
    def normalize(self, audio):
        """Normalize audio to [-1, 1] range."""
        if not NUMPY_AVAILABLE or audio is None:
            return audio
        
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio


class SoundEffectLibrary:
    """Library of sound effects for Omega."""
    
    def __init__(self, synthesizer: SoundSynthesizer):
        self.synth = synthesizer
        self.effects = {}
        self._initialize_effects()
    
    def _initialize_effects(self):
        """Initialize sound effect library."""
        # Notification sounds
        self.effects['notification'] = self._create_notification
        self.effects['alert'] = self._create_alert
        self.effects['success'] = self._create_success
        self.effects['error'] = self._create_error
        self.effects['warning'] = self._create_warning
        
        # UI sounds
        self.effects['click'] = self._create_click
        self.effects['beep'] = self._create_beep
        self.effects['chime'] = self._create_chime
        
        # Ambient sounds
        self.effects['ambient_hum'] = self._create_ambient_hum
        self.effects['pulse'] = self._create_pulse
    
    def _create_notification(self):
        """Create notification sound."""
        return self.synth.tone_sequence([800, 1000], [0.1, 0.1], 0.3)
    
    def _create_alert(self):
        """Create alert sound."""
        return self.synth.tone_sequence([1000, 800, 1000], [0.15, 0.15, 0.15], 0.5)
    
    def _create_success(self):
        """Create success sound."""
        return self.synth.tone_sequence([523, 659, 784], [0.2, 0.2, 0.3], 0.4)  # C major chord
    
    def _create_error(self):
        """Create error sound."""
        return self.synth.tone_sequence([200, 150], [0.2, 0.3], 0.5)
    
    def _create_warning(self):
        """Create warning sound."""
        return self.synth.tone_sequence([600, 500], [0.15, 0.15], 0.4)
    
    def _create_click(self):
        """Create click sound."""
        return self.synth.sine_wave(1000, 0.05, 0.2)
    
    def _create_beep(self):
        """Create beep sound."""
        return self.synth.sine_wave(440, 0.2, 0.3)
    
    def _create_chime(self):
        """Create chime sound."""
        return self.synth.chord([523, 659, 784, 1047], 0.5, 0.3)  # C major 7th
    
    def _create_ambient_hum(self):
        """Create ambient hum."""
        return self.synth.sine_wave(60, 2.0, 0.1)
    
    def _create_pulse(self):
        """Create pulse sound."""
        wave = self.synth.sine_wave(440, 0.5, 0.5)
        if wave is not None and NUMPY_AVAILABLE:
            # Add envelope
            envelope = np.linspace(0, 1, len(wave))
            envelope = envelope * np.flip(envelope)
            return wave * envelope
        return wave
    
    def get_effect(self, name: str):
        """Get sound effect by name."""
        if name in self.effects:
            return self.effects[name]()
        return None
    
    def list_effects(self):
        """List all available effects."""
        return list(self.effects.keys())


class VoiceRecorder:
    """Record and analyze voice waveforms."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.audio = None
        
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                print(f"PyAudio initialization error: {e}")
                self.audio = None
    
    def record(self, duration: float = 5.0):
        """Record audio from microphone."""
        if not self.audio or not NUMPY_AVAILABLE:
            print("Recording not available. Install: pip install pyaudio numpy")
            return None
        
        print(f"\n{'='*60}")
        print(f"RECORDING YOUR VOICE - {duration} seconds")
        print(f"{'='*60}")
        print("Speak now...")
        print()
        
        try:
            chunk_size = 1024
            format = pyaudio.paInt16
            channels = 1
            
            stream = self.audio.open(
                format=format,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            frames = []
            num_chunks = int(self.sample_rate / chunk_size * duration)
            
            for i in range(num_chunks):
                try:
                    data = stream.read(chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    # Progress indicator
                    if (i + 1) % max(1, num_chunks // 10) == 0:
                        progress = int((i + 1) / num_chunks * 100)
                        print(f"Recording: {progress}%", end='\r', flush=True)
                except Exception as e:
                    print(f"\nWarning during recording: {e}")
                    # Continue recording
            
            stream.stop_stream()
            stream.close()
            
            print("\nRecording complete!")
            
            # Convert to numpy array
            if not frames:
                print("No audio data captured")
                return None
            
            audio_data = b''.join(frames)
            if len(audio_data) == 0:
                print("Empty audio data")
                return None
            
            try:
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Remove DC offset and normalize
                audio_array = audio_array - np.mean(audio_array)
                max_val = np.max(np.abs(audio_array))
                if max_val > 0:
                    audio_array = audio_array / max_val * 0.95  # Leave headroom
                
                return audio_array
            except Exception as e:
                print(f"Audio conversion error: {e}")
                return None
            
        except KeyboardInterrupt:
            print("\n\nRecording interrupted by user")
            if 'stream' in locals():
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
            return None
        except Exception as e:
            print(f"Recording error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_recording(self, audio, filename: str):
        """Save recording to file."""
        if audio is None or not NUMPY_AVAILABLE:
            print("Cannot save: audio is None or numpy not available")
            return False
        
        try:
            # Ensure filename has .wav extension
            if not filename.endswith('.wav'):
                filename = filename + '.wav'
            
            filepath = OMEGA_SOUNDBOARD_DIR / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Normalize audio before saving
            max_val = np.max(np.abs(audio))
            if max_val > 1.0:
                audio = audio / max_val * 0.95  # Normalize and leave headroom
            
            if SOUNDFILE_AVAILABLE:
                sf.write(str(filepath), audio, self.sample_rate)
            else:
                # Fallback: use wave module
                audio_int16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
                with wave.open(str(filepath), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_int16.tobytes())
            
            print(f"Saved: {filepath}")
            return True
        except Exception as e:
            print(f"Save error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def analyze_waveform(self, audio) -> Dict[str, Any]:
        """Analyze voice waveform characteristics."""
        if audio is None or not NUMPY_AVAILABLE:
            return {"error": "Audio is None or numpy not available"}
        
        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            try:
                audio = np.array(audio, dtype=np.float32)
            except Exception:
                return {"error": "Could not convert audio to numpy array"}
        
        if len(audio) == 0:
            return {"error": "Empty audio"}
        
        try:
            analysis = {
                "duration": len(audio) / self.sample_rate,
                "sample_rate": self.sample_rate,
                "samples": len(audio),
                "max_amplitude": float(np.max(np.abs(audio))),
                "rms_amplitude": float(np.sqrt(np.mean(audio**2))),
                "zero_crossings": int(np.sum(np.diff(np.sign(audio)) != 0)),
            }
        except Exception as e:
            return {"error": f"Analysis error: {e}"}
        
        # Frequency analysis
        if SCIPY_AVAILABLE:
            try:
                # FFT for frequency analysis
                fft = np.fft.rfft(audio)
                freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
                magnitude = np.abs(fft)
                
                # Find dominant frequency
                dominant_idx = np.argmax(magnitude)
                analysis["dominant_frequency"] = float(freqs[dominant_idx])
                analysis["frequency_spectrum"] = {
                    "frequencies": freqs[:1000].tolist(),  # First 1000 bins
                    "magnitudes": magnitude[:1000].tolist()
                }
            except Exception:
                pass
        
        # Spectral features
        if LIBROSA_AVAILABLE:
            try:
                # Ensure audio is 1D
                if len(audio.shape) > 1:
                    audio = audio.flatten()
                
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)
                if spectral_centroid.size > 0:
                    analysis["spectral_centroid"] = float(spectral_centroid[0, 0])
                
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)
                if spectral_rolloff.size > 0:
                    analysis["spectral_rolloff"] = float(spectral_rolloff[0, 0])
                
                zcr = librosa.feature.zero_crossing_rate(audio)
                if zcr.size > 0:
                    analysis["zero_crossing_rate_librosa"] = float(np.mean(zcr[0]))
            except Exception as e:
                analysis["spectral_error"] = str(e)
        
        return analysis


class OmegaSoundboard:
    """Ω Omega Soundboard - Complete sound generation and manipulation system."""
    
    def __init__(self):
        self.sample_rate = 44100
        self.synthesizer = SoundSynthesizer(self.sample_rate)
        self.modulator = VoiceModulator(self.sample_rate)
        self.effects = SoundEffectLibrary(self.synthesizer)
        self.recorder = VoiceRecorder(self.sample_rate)
        
        self.sound_library = {}
        self.voice_library = {}
        self._load_libraries()
    
    def _load_libraries(self):
        """Load saved sounds and voices."""
        # Load sound library
        sound_lib_file = OMEGA_SOUNDBOARD_DIR / 'sound_library.json'
        if sound_lib_file.exists():
            try:
                with open(sound_lib_file, 'r', encoding='utf-8') as f:
                    self.sound_library = json.load(f)
            except Exception:
                pass
        
        # Load voice library
        voice_lib_file = OMEGA_SOUNDBOARD_DIR / 'voice_library.json'
        if voice_lib_file.exists():
            try:
                with open(voice_lib_file, 'r', encoding='utf-8') as f:
                    self.voice_library = json.load(f)
            except Exception:
                pass
    
    def _save_libraries(self):
        """Save sound and voice libraries."""
        try:
            sound_lib_file = OMEGA_SOUNDBOARD_DIR / 'sound_library.json'
            with open(sound_lib_file, 'w', encoding='utf-8') as f:
                json.dump(self.sound_library, f, indent=2)
            
            voice_lib_file = OMEGA_SOUNDBOARD_DIR / 'voice_library.json'
            with open(voice_lib_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_library, f, indent=2)
        except Exception:
            pass
    
    def record_user_voice(self, duration: float = 5.0) -> Optional[Dict[str, Any]]:
        """Record user's voice and analyze waveform."""
        print("=" * 80)
        print("Ω OMEGA VOICE RECORDING")
        print("=" * 80)
        
        if not PYAUDIO_AVAILABLE:
            print("\n⚠️  PyAudio not available. Cannot record.")
            print("Install with: pip install pyaudio")
            print("Or on Windows: pip install pipwin && pipwin install pyaudio")
            return None
        
        if not NUMPY_AVAILABLE:
            print("\n⚠️  NumPy not available. Cannot process audio.")
            print("Install with: pip install numpy")
            return None
        
        audio = self.recorder.record(duration)
        if audio is None:
            print("\n⚠️  Recording failed. Check microphone and try again.")
            return None
        
        # Check if audio has content
        if len(audio) == 0 or (NUMPY_AVAILABLE and np.max(np.abs(audio)) < 0.001):
            print("\n⚠️  No audio detected. Check microphone.")
            return None
        
        # Analyze waveform
        print("\nAnalyzing waveform...")
        analysis = self.recorder.analyze_waveform(audio)
        
        if "error" in analysis:
            print(f"\n⚠️  Analysis error: {analysis['error']}")
            return None
        
        # Save recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_voice_{timestamp}.wav"
        saved = self.recorder.save_recording(audio, filename)
        
        if not saved:
            print("\n⚠️  Could not save recording")
            return None
        
        # Store in voice library
        voice_id = f"user_voice_{timestamp}"
        self.voice_library[voice_id] = {
            "filename": filename,
            "analysis": analysis,
            "recorded_at": datetime.now().isoformat(),
            "duration": analysis.get("duration", 0),
            "max_amplitude": analysis.get("max_amplitude", 0),
            "dominant_frequency": analysis.get("dominant_frequency", 0)
        }
        self._save_libraries()
        
        print("\n" + "=" * 80)
        print("WAVEFORM ANALYSIS")
        print("=" * 80)
        print(f"Duration: {analysis.get('duration', 0):.2f}s")
        print(f"Max Amplitude: {analysis.get('max_amplitude', 0):.4f}")
        print(f"RMS Amplitude: {analysis.get('rms_amplitude', 0):.4f}")
        if 'dominant_frequency' in analysis:
            print(f"Dominant Frequency: {analysis['dominant_frequency']:.2f} Hz")
        if 'spectral_centroid' in analysis:
            print(f"Spectral Centroid: {analysis['spectral_centroid']:.2f} Hz")
        print("=" * 80)
        
        return {
            "audio": audio,
            "analysis": analysis,
            "voice_id": voice_id,
            "filename": filename
        }
    
    def generate_sound(self, sound_type: str, **kwargs):
        """Generate sound by type."""
        if not NUMPY_AVAILABLE:
            print("NumPy required for sound generation")
            return None
        
        try:
            if sound_type == "sine":
                return self.synthesizer.sine_wave(
                    kwargs.get("frequency", 440),
                    kwargs.get("duration", 1.0),
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type == "square":
                return self.synthesizer.square_wave(
                    kwargs.get("frequency", 440),
                    kwargs.get("duration", 1.0),
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type == "sawtooth":
                return self.synthesizer.sawtooth_wave(
                    kwargs.get("frequency", 440),
                    kwargs.get("duration", 1.0),
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type == "triangle":
                return self.synthesizer.triangle_wave(
                    kwargs.get("frequency", 440),
                    kwargs.get("duration", 1.0),
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type == "noise":
                noise_type = kwargs.get("noise_type", "white")
                if noise_type == "pink":
                    return self.synthesizer.pink_noise(
                        kwargs.get("duration", 1.0),
                        kwargs.get("amplitude", 0.1)
                    )
                else:
                    return self.synthesizer.white_noise(
                        kwargs.get("duration", 1.0),
                        kwargs.get("amplitude", 0.1)
                    )
            elif sound_type == "chord":
                frequencies = kwargs.get("frequencies", [440, 554, 659])  # A major
                return self.synthesizer.chord(
                    frequencies,
                    kwargs.get("duration", 1.0),
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type == "sequence":
                frequencies = kwargs.get("frequencies", [440, 554, 659])
                durations = kwargs.get("durations", [0.5, 0.5, 0.5])
                return self.synthesizer.tone_sequence(
                    frequencies,
                    durations,
                    kwargs.get("amplitude", 0.5)
                )
            elif sound_type in self.effects.list_effects():
                return self.effects.get_effect(sound_type)
            else:
                print(f"Unknown sound type: {sound_type}")
                print(f"Available types: sine, square, sawtooth, triangle, noise, chord, sequence")
                print(f"Available effects: {', '.join(self.effects.list_effects())}")
                return None
        except Exception as e:
            print(f"Sound generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def modulate_voice(self, audio, modulation: Dict[str, Any]):
        """Apply voice modulation."""
        if audio is None:
            return None
        
        if not NUMPY_AVAILABLE:
            return audio
        
        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            try:
                audio = np.array(audio, dtype=np.float32)
            except Exception:
                return None
        
        result = audio.copy()
        
        # Pitch shift
        if "pitch_shift" in modulation:
            result = self.modulator.pitch_shift(result, modulation["pitch_shift"])
        
        # Time stretch
        if "time_stretch" in modulation:
            result = self.modulator.time_stretch(result, modulation["time_stretch"])
        
        # Formant shift
        if "formant_shift" in modulation:
            result = self.modulator.formant_shift(result, modulation["formant_shift"])
        
        # Reverb
        if "reverb" in modulation:
            result = self.modulator.add_reverb(
                result,
                modulation["reverb"].get("room_size", 0.5),
                modulation["reverb"].get("damping", 0.5)
            )
        
        # Chorus
        if "chorus" in modulation:
            result = self.modulator.add_chorus(
                result,
                modulation["chorus"].get("depth", 0.3),
                modulation["chorus"].get("rate", 1.5)
            )
        
        # Vibrato
        if "vibrato" in modulation:
            result = self.modulator.add_vibrato(
                result,
                modulation["vibrato"].get("depth", 0.02),
                modulation["vibrato"].get("rate", 5.0)
            )
        
        # Normalize
        result = self.modulator.normalize(result)
        
        return result
    
    def play_sound(self, audio):
        """Play audio (if pyaudio available)."""
        if audio is None or not PYAUDIO_AVAILABLE or not NUMPY_AVAILABLE:
            print("Audio playback not available")
            return False
        
        try:
            # Normalize audio
            max_val = np.max(np.abs(audio))
            if max_val > 1.0:
                audio = audio / max_val * 0.8  # Normalize and leave headroom
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True
            )
            
            # Convert to float32 and ensure it's contiguous
            audio_float32 = np.ascontiguousarray(audio.astype(np.float32))
            
            # Write in chunks for better reliability
            chunk_size = 1024
            for i in range(0, len(audio_float32), chunk_size):
                chunk = audio_float32[i:i+chunk_size]
                stream.write(chunk.tobytes())
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
        except Exception as e:
            print(f"Playback error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_sound(self, audio, name: str):
        """Save generated sound."""
        if audio is None:
            return False
        
        try:
            filepath = OMEGA_SOUNDBOARD_DIR / f"{name}.wav"
            if SOUNDFILE_AVAILABLE:
                sf.write(str(filepath), audio, self.sample_rate)
            else:
                audio_int16 = (audio * 32767).astype(np.int16)
                with wave.open(str(filepath), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_int16.tobytes())
            
            self.sound_library[name] = {
                "filename": f"{name}.wav",
                "created_at": datetime.now().isoformat()
            }
            self._save_libraries()
            
            print(f"Sound saved: {filepath}")
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False


def main():
    """Main entry point for soundboard."""
    print("=" * 80)
    print("Ω OMEGA SOUNDBOARD - Sound Generation & Voice Manipulation")
    print("=" * 80)
    print()
    print("Capabilities:")
    print("  1. Record your voice waveform")
    print("  2. Generate synthetic sounds")
    print("  3. Apply voice modulation")
    print("  4. Create sound effects")
    print("  5. Manipulate and blend voices")
    print()
    
    soundboard = OmegaSoundboard()
    
    # Record user voice
    print("Ready to record your voice...")
    print("Starting recording in 2 seconds...")
    print("(Run with --auto to skip this prompt)")
    time.sleep(2)
    
    result = soundboard.record_user_voice(duration=5.0)
    
    if result:
        print("\n" + "=" * 80)
        print("VOICE RECORDED SUCCESSFULLY")
        print("=" * 80)
        print(f"Voice ID: {result['voice_id']}")
        print(f"Filename: {result['filename']}")
        print("\nYour voice waveform has been analyzed and saved.")
        print("Omega can now use this to improve its voice!")
    
    print("\n" + "=" * 80)
    print("SOUNDBOARD READY")
    print("=" * 80)
    print("\nAvailable sound effects:")
    for effect in soundboard.effects.list_effects():
        print(f"  - {effect}")
    
    print("\nOmega soundboard is ready to generate and manipulate sounds!")


if __name__ == '__main__':
    main()

