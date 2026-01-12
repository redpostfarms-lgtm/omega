# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Learner - Continuous Learning from Your Voice
# Listens, learns, improves pronunciation and waveform

import sys
import io
import json
import time
import wave
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import deque

# Set UTF-8 encoding for Windows console
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

# Audio libraries
try:
    import pyaudio
    import numpy as np
    PYAUDIO_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    NUMPY_AVAILABLE = False
    np = None

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ContinuousVoiceLearner:
    """Continuously learn from your voice to improve Omega's pronunciation and waveform."""
    
    def __init__(self):
        self.audio = None
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        
        self.is_listening = False
        self.learning_data = {
            "samples": [],
            "pronunciations": {},
            "waveform_improvements": [],
            "learned_at": []
        }
        self.learning_file = OMEGA_VOICE_DIR / 'omega_voice_learning.json'
        self.waveform_library_file = OMEGA_VOICE_DIR / 'waveform_library.json'
        
        self._load_learning_data()
        
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                print(f"PyAudio initialization error: {e}")
                self.audio = None
    
    def _load_learning_data(self):
        """Load previous learning data."""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data.update(json.load(f))
                print(f"✓ Loaded {len(self.learning_data.get('samples', []))} previous voice samples")
            except Exception:
                pass
        
        # Load waveform library
        self.waveform_library = {}
        if self.waveform_library_file.exists():
            try:
                with open(self.waveform_library_file, 'r', encoding='utf-8') as f:
                    self.waveform_library = json.load(f)
                print(f"✓ Loaded waveform library: {len(self.waveform_library)} entries")
            except Exception:
                pass
    
    def _save_learning_data(self):
        """Save learning data."""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2)
            
            with open(self.waveform_library_file, 'w', encoding='utf-8') as f:
                json.dump(self.waveform_library, f, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def detect_speech(self, audio_chunk) -> bool:
        """Detect if audio chunk contains speech."""
        if not NUMPY_AVAILABLE:
            return False
        
        try:
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Calculate energy
            energy = np.mean(np.abs(audio_float))
            
            # Speech threshold (adjust based on your environment)
            return energy > 0.01
        except:
            return False
    
    def analyze_pronunciation(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze pronunciation patterns from audio."""
        if not NUMPY_AVAILABLE:
            return {}
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Remove silence
            threshold = 0.01
            mask = np.abs(audio_float) > threshold
            if np.sum(mask) == 0:
                return {}
            
            audio_clean = audio_float[mask]
            
            # Analyze pronunciation characteristics
            analysis = {
                "duration": len(audio_clean) / self.sample_rate,
                "energy": float(np.mean(np.abs(audio_clean))),
                "pitch": self._extract_pitch(audio_clean),
                "formants": self._extract_formants(audio_clean),
                "spectral_centroid": self._spectral_centroid(audio_clean),
                "zero_crossing_rate": self._zero_crossing_rate(audio_clean),
                "mfcc_features": self._extract_mfcc_simple(audio_clean)
            }
            
            return analysis
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_pitch(self, audio) -> float:
        """Extract pitch using autocorrelation."""
        if not SCIPY_AVAILABLE:
            return 140.0
        
        try:
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            peaks = signal.find_peaks(autocorr, height=np.max(autocorr) * 0.3)[0]
            
            if len(peaks) > 1:
                period = peaks[1] - peaks[0]
                if period > 0:
                    freq = self.sample_rate / period
                    return max(80.0, min(300.0, float(freq)))
            return 140.0
        except:
            return 140.0
    
    def _extract_formants(self, audio) -> List[float]:
        """Extract formant frequencies."""
        if not SCIPY_AVAILABLE:
            return []
        
        try:
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            mask = (freqs > 300) & (freqs < 4000)
            if np.any(mask):
                peaks = signal.find_peaks(magnitude[mask], height=np.max(magnitude[mask]) * 0.3)[0]
                formants = [abs(float(freqs[mask][p])) for p in peaks[:3]]
                return formants
            return []
        except:
            return []
    
    def _spectral_centroid(self, audio) -> float:
        """Calculate spectral centroid (brightness)."""
        if not NUMPY_AVAILABLE:
            return 2000.0
        
        try:
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            positive_freqs = freqs[:len(freqs)//2]
            positive_mag = magnitude[:len(magnitude)//2]
            
            if np.sum(positive_mag) > 0:
                centroid = np.sum(positive_freqs * positive_mag) / np.sum(positive_mag)
                return abs(float(centroid))
            return 2000.0
        except:
            return 2000.0
    
    def _zero_crossing_rate(self, audio) -> float:
        """Calculate zero crossing rate (voiced/unvoiced detection)."""
        if not NUMPY_AVAILABLE:
            return 0.1
        
        try:
            zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2.0 * len(audio))
            return float(zcr)
        except:
            return 0.1
    
    def _extract_mfcc_simple(self, audio) -> List[float]:
        """Simple MFCC-like features for pronunciation."""
        if not NUMPY_AVAILABLE:
            return []
        
        try:
            # Simplified: energy in different frequency bands
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Frequency bands
            bands = [
                (0, 500),      # Low
                (500, 1500),   # Mid-low
                (1500, 3000),  # Mid-high
                (3000, 8000)   # High
            ]
            
            features = []
            for low, high in bands:
                mask = (freqs > low) & (freqs < high)
                if np.any(mask):
                    energy = np.sum(magnitude[mask])
                    features.append(float(energy))
                else:
                    features.append(0.0)
            
            return features
        except:
            return []
    
    def learn_from_sample(self, audio_data: bytes, text: Optional[str] = None):
        """Learn from a voice sample."""
        if not audio_data:
            return
        
        # Analyze pronunciation
        analysis = self.analyze_pronunciation(audio_data)
        
        if "error" in analysis:
            return
        
        # Store sample
        timestamp = datetime.now().isoformat()
        sample = {
            "timestamp": timestamp,
            "analysis": analysis,
            "text": text,
            "duration": analysis.get("duration", 0)
        }
        
        self.learning_data["samples"].append(sample)
        self.learning_data["learned_at"].append(timestamp)
        
        # Keep last 100 samples
        if len(self.learning_data["samples"]) > 100:
            self.learning_data["samples"] = self.learning_data["samples"][-100:]
            self.learning_data["learned_at"] = self.learning_data["learned_at"][-100:]
        
        # Update waveform library
        self._update_waveform_library(analysis)
        
        # Save learning
        self._save_learning_data()
        
        print(f"✓ Learned from voice sample ({analysis.get('duration', 0):.2f}s)")
    
    def _update_waveform_library(self, analysis: Dict[str, Any]):
        """Update waveform library with new characteristics."""
        # Average characteristics over time
        if "average_pitch" not in self.waveform_library:
            self.waveform_library["average_pitch"] = []
        if "average_formants" not in self.waveform_library:
            self.waveform_library["average_formants"] = []
        if "average_spectral_centroid" not in self.waveform_library:
            self.waveform_library["average_spectral_centroid"] = []
        
        # Add new data
        if "pitch" in analysis:
            self.waveform_library["average_pitch"].append(analysis["pitch"])
            # Keep last 50 values
            if len(self.waveform_library["average_pitch"]) > 50:
                self.waveform_library["average_pitch"] = self.waveform_library["average_pitch"][-50:]
        
        if "formants" in analysis and analysis["formants"]:
            self.waveform_library["average_formants"].append(analysis["formants"])
            if len(self.waveform_library["average_formants"]) > 50:
                self.waveform_library["average_formants"] = self.waveform_library["average_formants"][-50:]
        
        if "spectral_centroid" in analysis:
            self.waveform_library["average_spectral_centroid"].append(analysis["spectral_centroid"])
            if len(self.waveform_library["average_spectral_centroid"]) > 50:
                self.waveform_library["average_spectral_centroid"] = self.waveform_library["average_spectral_centroid"][-50:]
    
    def get_improved_waveform(self) -> Dict[str, Any]:
        """Get improved waveform based on learned characteristics."""
        improved = {
            "base_frequency": 140.0,
            "modulation_depth": 0.08,
            "modulation_rate": 2.2,
            "harmonic_ratio": 0.25,
            "resonance_peak": 2200.0,
            "prosody_variation": 0.12
        }
        
        # Calculate averages from learned data
        if self.waveform_library.get("average_pitch"):
            avg_pitch = np.mean(self.waveform_library["average_pitch"])
            improved["base_frequency"] = float(avg_pitch)
        
        if self.waveform_library.get("average_spectral_centroid"):
            avg_centroid = np.mean(self.waveform_library["average_spectral_centroid"])
            improved["resonance_peak"] = float(avg_centroid)
        
        # Update modulation based on learned variation
        if len(self.learning_data["samples"]) > 5:
            pitches = [s["analysis"].get("pitch", 140) for s in self.learning_data["samples"][-10:] if "pitch" in s.get("analysis", {})]
            if pitches:
                pitch_variation = np.std(pitches) / (np.mean(pitches) + 1e-10)
                improved["modulation_depth"] = min(0.15, max(0.05, float(pitch_variation)))
        
        return improved
    
    def start_listening(self, duration: Optional[float] = None):
        """Start continuous listening and learning."""
        if not self.audio:
            print("❌ PyAudio not available. Cannot listen.")
            return
        
        if self.is_listening:
            print("Already listening...")
            return
        
        self.is_listening = True
        print("\n" + "=" * 80)
        print("Ω OMEGA VOICE LEARNER - LISTENING")
        print("=" * 80)
        print("\nOmega is now listening and learning from your voice.")
        print("Press Ctrl+C to stop, or speak naturally.")
        print("Omega will capture and learn from your speech patterns.\n")
        
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            audio_buffer = deque(maxlen=int(self.sample_rate / self.chunk_size * 2))  # 2 second buffer
            speech_detected = False
            speech_start = None
            speech_buffer = []
            
            start_time = time.time()
            
            while self.is_listening:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_buffer.append(data)
                    
                    # Detect speech
                    if self.detect_speech(data):
                        if not speech_detected:
                            speech_detected = True
                            speech_start = time.time()
                            speech_buffer = []
                            print("🎤 Speech detected...")
                        
                        speech_buffer.append(data)
                    else:
                        # End of speech - process if we have enough
                        if speech_detected and len(speech_buffer) > 0:
                            speech_duration = time.time() - speech_start
                            if speech_duration > 0.5:  # At least 0.5 seconds
                                audio_data = b''.join(speech_buffer)
                                self.learn_from_sample(audio_data)
                            
                            speech_buffer = []
                            speech_detected = False
                    
                    # Check duration limit
                    if duration and (time.time() - start_time) > duration:
                        break
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error during listening: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Listening error: {e}")
        finally:
            self.is_listening = False
            print("\n" + "=" * 80)
            print("LISTENING STOPPED")
            print("=" * 80)
            print(f"\n✓ Learned from {len(self.learning_data['samples'])} voice samples")
            
            # Generate improved waveform
            improved = self.get_improved_waveform()
            print("\nImproved Waveform Characteristics:")
            for key, value in improved.items():
                print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
            
            # Save improved waveform
            improved_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
            try:
                with open(improved_file, 'w', encoding='utf-8') as f:
                    json.dump(improved, f, indent=2)
                print(f"\n✓ Improved waveform saved to: {improved_file}")
            except Exception as e:
                print(f"Error saving improved waveform: {e}")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        print("Stopping voice learning...")


def main():
    """Main voice learning interface."""
    print("=" * 80)
    print("Ω OMEGA VOICE LEARNER")
    print("=" * 80)
    print("\nOmega learns from your voice to improve pronunciation and waveform.")
    print("\nOptions:")
    print("1. Listen continuously (press Ctrl+C to stop)")
    print("2. Listen for specific duration")
    print("3. View learning statistics")
    print("4. Generate improved waveform")
    
    if not PYAUDIO_AVAILABLE:
        print("\n❌ PyAudio not available. Install with: pip install pyaudio")
        return
    
    if not NUMPY_AVAILABLE:
        print("\n❌ NumPy not available. Install with: pip install numpy")
        return
    
    learner = ContinuousVoiceLearner()
    
    print("\n" + "=" * 80)
    choice = input("\nEnter choice (1-4, or press Enter for continuous): ").strip()
    
    if choice == "2":
        duration = float(input("Duration in seconds: "))
        learner.start_listening(duration=duration)
    elif choice == "3":
        print(f"\nLearning Statistics:")
        print(f"  Samples collected: {len(learner.learning_data.get('samples', []))}")
        print(f"  Waveform library entries: {len(learner.waveform_library)}")
        if learner.learning_data.get('samples'):
            print(f"  Last learned: {learner.learning_data['learned_at'][-1]}")
    elif choice == "4":
        improved = learner.get_improved_waveform()
        print("\nImproved Waveform:")
        for key, value in improved.items():
            print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
    else:
        # Default: continuous listening
        learner.start_listening()


if __name__ == '__main__':
    main()

