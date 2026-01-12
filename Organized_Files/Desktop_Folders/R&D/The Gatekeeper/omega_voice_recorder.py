# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Recorder & Analyzer
# Records, analyzes, and blends your voice with Omega's

import sys
import io
import json
import time
import wave
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Union
from datetime import datetime

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

# Audio recording libraries
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


class VoiceRecorder:
    """Record voice and analyze waveform."""
    
    def __init__(self):
        self.audio = None
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                print(f"PyAudio initialization error: {e}")
                self.audio = None
    
    def record(self, duration: float = 5.0) -> Optional[bytes]:
        """Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as bytes, or None if recording failed
        """
        if not self.audio:
            print("PyAudio not available. Cannot record.")
            return None
        
        print(f"\nRecording for {duration} seconds...")
        print("Speak now...")
        
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            print("Recording complete.")
            return b''.join(frames)
            
        except Exception as e:
            print(f"Recording error: {e}")
            return None
    
    def save_recording(self, audio_data: bytes, filename: str) -> Path:
        """Save recorded audio to WAV file."""
        filepath = OMEGA_VOICE_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            
            print(f"Recording saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving recording: {e}")
            return None


class VoiceAnalyzer:
    """Analyze voice waveform characteristics."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def analyze_waveform(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze voice waveform and extract characteristics.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dictionary with voice characteristics
        """
        if not NUMPY_AVAILABLE:
            return {"error": "NumPy not available"}
        
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Remove silence
            audio_float = self._remove_silence(audio_float)
            
            if len(audio_float) == 0:
                return {"error": "No audio detected"}
            
            # Analyze characteristics
            analysis = {
                "base_frequency": self._extract_fundamental_frequency(audio_float),
                "harmonic_ratio": self._analyze_harmonics(audio_float),
                "modulation_depth": self._analyze_modulation(audio_float),
                "modulation_rate": self._analyze_modulation_rate(audio_float),
                "resonance_peak": self._find_resonance_peak(audio_float),
                "attack_time": self._analyze_attack(audio_float),
                "decay_time": self._analyze_decay(audio_float),
                "sustain_level": self._analyze_sustain(audio_float),
                "release_time": self._analyze_release(audio_float),
                "prosody_variation": self._analyze_prosody(audio_float),
                "energy_distribution": self._analyze_energy(audio_float),
                "formants": self._extract_formants(audio_float)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _remove_silence(self, audio, threshold: float = 0.01):
        """Remove silence from audio."""
        if not NUMPY_AVAILABLE:
            return audio
        
        # Find non-silent regions
        mask = np.abs(audio) > threshold
        indices = np.where(mask)[0]
        
        if len(indices) == 0:
            return audio
        
        # Return audio with silence removed
        return audio[indices[0]:indices[-1]+1]
    
    def _extract_fundamental_frequency(self, audio) -> float:
        """Extract fundamental frequency (pitch) using autocorrelation."""
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return 140.0  # Default
        
        try:
            # Autocorrelation to find pitch
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks
            peaks = signal.find_peaks(autocorr, height=np.max(autocorr) * 0.3)[0]
            
            if len(peaks) > 1:
                # Fundamental frequency from first significant peak
                period = peaks[1] - peaks[0] if len(peaks) > 1 else peaks[0]
                if period > 0:
                    freq = self.sample_rate / period
                    # Clamp to human voice range (80-300 Hz)
                    return max(80.0, min(300.0, freq))
            
            return 140.0  # Default
        except:
            return 140.0
    
    def _analyze_harmonics(self, audio) -> float:
        """Analyze harmonic content."""
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return 0.25
        
        try:
            # FFT to get frequency spectrum
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            
            # Find fundamental and harmonics
            fundamental_idx = np.argmax(magnitude[:len(magnitude)//2])
            fundamental_mag = magnitude[fundamental_idx]
            
            # Look for harmonics (2x, 3x fundamental)
            harmonic2_idx = fundamental_idx * 2
            harmonic3_idx = fundamental_idx * 3
            
            if harmonic2_idx < len(magnitude):
                harmonic2_mag = magnitude[harmonic2_idx]
                harmonic_ratio = harmonic2_mag / fundamental_mag if fundamental_mag > 0 else 0
                return min(0.5, max(0.0, harmonic_ratio))
            
            return 0.25
        except:
            return 0.25
    
    def _analyze_modulation(self, audio) -> float:
        """Analyze amplitude modulation (vibrato/tremolo)."""
        if not NUMPY_AVAILABLE:
            return 0.08
        
        try:
            # Envelope detection
            envelope = np.abs(audio)
            
            # Smooth envelope
            window_size = int(self.sample_rate * 0.01)  # 10ms window
            if window_size > 0:
                envelope_smooth = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
            else:
                envelope_smooth = envelope
            
            # Calculate modulation depth
            if len(envelope_smooth) > 0:
                modulation = np.std(envelope_smooth) / (np.mean(envelope_smooth) + 1e-10)
                return min(0.2, max(0.0, modulation))
            
            return 0.08
        except:
            return 0.08
    
    def _analyze_modulation_rate(self, audio) -> float:
        """Analyze modulation rate (vibrato frequency)."""
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return 2.2
        
        try:
            envelope = np.abs(audio)
            window_size = int(self.sample_rate * 0.01)
            if window_size > 0:
                envelope_smooth = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
            else:
                envelope_smooth = envelope
            
            # FFT of envelope to find modulation frequency
            fft = np.fft.fft(envelope_smooth)
            freqs = np.fft.fftfreq(len(envelope_smooth), 1/self.sample_rate)
            
            # Find peak in modulation range (1-5 Hz for vibrato)
            mask = (freqs > 1) & (freqs < 5)
            if np.any(mask):
                peak_idx = np.argmax(np.abs(fft[mask]))
                mod_rate = freqs[mask][peak_idx]
                return max(1.0, min(5.0, abs(mod_rate)))
            
            return 2.2
        except:
            return 2.2
    
    def _find_resonance_peak(self, audio) -> float:
        """Find resonance/formant peak frequency."""
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return 2200.0
        
        try:
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Look for peak in formant range (1000-4000 Hz)
            mask = (freqs > 1000) & (freqs < 4000)
            if np.any(mask):
                peak_idx = np.argmax(magnitude[mask])
                peak_freq = freqs[mask][peak_idx]
                return abs(peak_freq)
            
            return 2200.0
        except:
            return 2200.0
    
    def _analyze_attack(self, audio) -> float:
        """Analyze attack time."""
        if not NUMPY_AVAILABLE:
            return 0.05
        
        try:
            envelope = np.abs(audio)
            max_val = np.max(envelope)
            threshold = max_val * 0.1
            
            # Find when signal reaches 10% of max
            attack_idx = np.where(envelope > threshold)[0]
            if len(attack_idx) > 0:
                attack_time = attack_idx[0] / self.sample_rate
                return min(0.2, max(0.01, attack_time))
            
            return 0.05
        except:
            return 0.05
    
    def _analyze_decay(self, audio) -> float:
        """Analyze decay time."""
        if not NUMPY_AVAILABLE:
            return 0.2
        
        try:
            envelope = np.abs(audio)
            max_val = np.max(envelope)
            peak_idx = np.argmax(envelope)
            
            # Find decay to 70% of max
            threshold = max_val * 0.7
            decay_region = envelope[peak_idx:]
            decay_idx = np.where(decay_region < threshold)[0]
            
            if len(decay_idx) > 0:
                decay_time = decay_idx[0] / self.sample_rate
                return min(0.5, max(0.05, decay_time))
            
            return 0.2
        except:
            return 0.2
    
    def _analyze_sustain(self, audio) -> float:
        """Analyze sustain level."""
        if not NUMPY_AVAILABLE:
            return 0.75
        
        try:
            envelope = np.abs(audio)
            # Middle 50% of signal
            start = len(envelope) // 4
            end = 3 * len(envelope) // 4
            sustain_region = envelope[start:end]
            
            if len(sustain_region) > 0:
                sustain_level = np.mean(sustain_region) / (np.max(envelope) + 1e-10)
                return min(0.9, max(0.3, sustain_level))
            
            return 0.75
        except:
            return 0.75
    
    def _analyze_release(self, audio) -> float:
        """Analyze release time."""
        if not NUMPY_AVAILABLE:
            return 0.15
        
        try:
            envelope = np.abs(audio)
            max_val = np.max(envelope)
            
            # Find release from 70% to 10%
            threshold_high = max_val * 0.7
            threshold_low = max_val * 0.1
            
            high_idx = np.where(envelope > threshold_high)[0]
            low_idx = np.where(envelope < threshold_low)[0]
            
            if len(high_idx) > 0 and len(low_idx) > 0:
                release_start = high_idx[-1]
                release_end = low_idx[low_idx > release_start]
                if len(release_end) > 0:
                    release_time = (release_end[0] - release_start) / self.sample_rate
                    return min(0.5, max(0.05, release_time))
            
            return 0.15
        except:
            return 0.15
    
    def _analyze_prosody(self, audio) -> float:
        """Analyze prosody variation."""
        if not NUMPY_AVAILABLE:
            return 0.12
        
        try:
            # Analyze energy variation over time
            window_size = int(self.sample_rate * 0.1)  # 100ms windows
            if window_size > 0:
                energy = []
                for i in range(0, len(audio) - window_size, window_size):
                    window = audio[i:i+window_size]
                    energy.append(np.mean(np.abs(window)))
                
                if len(energy) > 1:
                    variation = np.std(energy) / (np.mean(energy) + 1e-10)
                    return min(0.3, max(0.0, variation))
            
            return 0.12
        except:
            return 0.12
    
    def _analyze_energy(self, audio) -> Dict[str, float]:
        """Analyze energy distribution across frequency bands."""
        if not NUMPY_AVAILABLE:
            return {}
        
        try:
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Frequency bands
            bands = {
                "low": (80, 300),      # Fundamental
                "mid": (300, 2000),    # Formants
                "high": (2000, 8000)   # Harmonics
            }
            
            energy_dist = {}
            for band_name, (low, high) in bands.items():
                mask = (freqs > low) & (freqs < high)
                if np.any(mask):
                    energy_dist[band_name] = float(np.sum(magnitude[mask]))
            
            return energy_dist
        except:
            return {}
    
    def _extract_formants(self, audio) -> list:
        """Extract formant frequencies."""
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return []
        
        try:
            # LPC analysis for formants
            # Simplified: find peaks in spectrum
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Find peaks in formant range (300-4000 Hz)
            mask = (freqs > 300) & (freqs < 4000)
            if np.any(mask):
                peaks = signal.find_peaks(magnitude[mask], height=np.max(magnitude[mask]) * 0.3)[0]
                formants = [abs(freqs[mask][p]) for p in peaks[:3]]  # Top 3 formants
                return formants
            
            return []
        except:
            return []


class VoiceBlender:
    """Blend your voice characteristics with Omega's voice."""
    
    def __init__(self):
        self.omega_voice_file = OMEGA_VOICE_DIR / 'omega_waveform.json'
        self.user_voice_file = OMEGA_VOICE_DIR / 'user_voice_analysis.json'
        self.blended_voice_file = OMEGA_VOICE_DIR / 'blended_voice.json'
    
    def blend_voices(self, user_analysis: Dict[str, Any], blend_ratio: float = 0.5) -> Dict[str, Any]:
        """Blend user voice with Omega's voice.
        
        Args:
            user_analysis: User voice characteristics
            blend_ratio: 0.0 = all Omega, 1.0 = all user, 0.5 = 50/50 blend
            
        Returns:
            Blended voice characteristics
        """
        # Load Omega's current signature
        omega_signature = {
            "base_frequency": 140.0,
            "modulation_depth": 0.08,
            "modulation_rate": 2.2,
            "harmonic_ratio": 0.25,
            "attack_time": 0.05,
            "decay_time": 0.2,
            "sustain_level": 0.75,
            "release_time": 0.15,
            "resonance_peak": 2200.0,
            "prosody_variation": 0.12
        }
        
        if self.omega_voice_file.exists():
            try:
                with open(self.omega_voice_file, 'r', encoding='utf-8') as f:
                    omega_signature.update(json.load(f))
            except:
                pass
        
        # Blend characteristics
        blended = {}
        for key in omega_signature:
            if key in user_analysis and not isinstance(user_analysis[key], (dict, list)):
                omega_val = omega_signature.get(key, 0)
                user_val = user_analysis.get(key, omega_val)
                blended[key] = omega_val * (1 - blend_ratio) + user_val * blend_ratio
            else:
                blended[key] = omega_signature[key]
        
        # Add user-specific characteristics
        if "formants" in user_analysis:
            blended["formants"] = user_analysis["formants"]
        if "energy_distribution" in user_analysis:
            blended["energy_distribution"] = user_analysis["energy_distribution"]
        
        blended["blend_ratio"] = blend_ratio
        blended["created_at"] = datetime.now().isoformat()
        
        # Save blended voice
        try:
            with open(self.blended_voice_file, 'w', encoding='utf-8') as f:
                json.dump(blended, f, indent=2)
            print(f"\nBlended voice saved to: {self.blended_voice_file}")
        except Exception as e:
            print(f"Error saving blended voice: {e}")
        
        return blended


def main():
    """Main recording and analysis workflow."""
    print("=" * 80)
    print("Ω OMEGA VOICE RECORDER & ANALYZER")
    print("=" * 80)
    print("\nThis will:")
    print("1. Record your voice (5 seconds)")
    print("2. Analyze the waveform")
    print("3. Blend it with Omega's voice")
    print("4. Create a hybrid voice")
    
    if not PYAUDIO_AVAILABLE:
        print("\n❌ PyAudio not available. Install with: pip install pyaudio")
        return
    
    if not NUMPY_AVAILABLE:
        print("\n❌ NumPy not available. Install with: pip install numpy")
        return
    
    # Record voice
    recorder = VoiceRecorder()
    audio_data = recorder.record(duration=5.0)
    
    if not audio_data:
        print("\n❌ Recording failed.")
        return
    
    # Save recording
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    recording_file = recorder.save_recording(audio_data, f"user_voice_{timestamp}.wav")
    
    # Analyze voice
    print("\n" + "=" * 80)
    print("ANALYZING YOUR VOICE...")
    print("=" * 80)
    
    analyzer = VoiceAnalyzer()
    analysis = analyzer.analyze_waveform(audio_data)
    
    if "error" in analysis:
        print(f"\n❌ Analysis error: {analysis['error']}")
        return
    
    # Save analysis
    analysis_file = OMEGA_VOICE_DIR / f"user_voice_analysis_{timestamp}.json"
    try:
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n✓ Analysis saved to: {analysis_file}")
    except Exception as e:
        print(f"Error saving analysis: {e}")
    
    # Display analysis
    print("\nYour Voice Characteristics:")
    print("-" * 80)
    for key, value in analysis.items():
        if not isinstance(value, (dict, list)):
            print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
    
    # Blend voices
    print("\n" + "=" * 80)
    print("BLENDING WITH OMEGA'S VOICE...")
    print("=" * 80)
    
    blender = VoiceBlender()
    blended = blender.blend_voices(analysis, blend_ratio=0.5)
    
    print("\nBlended Voice Characteristics:")
    print("-" * 80)
    for key, value in blended.items():
        if not isinstance(value, (dict, list)) and key != "created_at":
            print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✓ VOICE BLENDING COMPLETE")
    print("=" * 80)
    print("\nOmega's voice has been updated with your characteristics.")
    print("The hybrid voice is saved and ready to use.")


if __name__ == '__main__':
    main()

