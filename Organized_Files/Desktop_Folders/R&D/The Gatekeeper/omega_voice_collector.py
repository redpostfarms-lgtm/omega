# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Collector - Extract & Analyze Voices from Multiple Sources
# Quantum Worldwide Scrub Enhanced

"""
Ω Omega Voice Collector

Extracts and analyzes voices from:
- YouTube videos
- Audiobooks
- TikTok/X videos
- Podcasts
- Audio files

Then blends them with your voice to create Omega's unique voice.
"""

import sys
import io
import json
import time
import wave
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from urllib.parse import urlparse, parse_qs

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

VOICE_SOURCES_DIR = OMEGA_VOICE_DIR / 'voice_sources'
VOICE_SOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Audio libraries
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# YouTube extraction
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from pytube import YouTube
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

# Voice activity detection
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False


class VoiceExtractor:
    """Extract audio from various sources."""
    
    def __init__(self):
        self.sample_rate = 16000  # Standard for voice analysis
    
    def extract_from_youtube(self, url: str, output_dir: Path = None) -> Optional[Path]:
        """Extract audio from YouTube video."""
        if not YT_DLP_AVAILABLE:
            print("yt-dlp not available. Install with: pip install yt-dlp")
            return None
        
        if output_dir is None:
            output_dir = VOICE_SOURCES_DIR
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Extracting audio from: {url}")
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Change extension to .wav
                wav_file = Path(filename).with_suffix('.wav')
                
                if wav_file.exists():
                    print(f"✓ Audio extracted: {wav_file}")
                    return wav_file
                else:
                    print(f"✗ Audio extraction failed")
                    return None
                    
        except Exception as e:
            print(f"Error extracting from YouTube: {e}")
            return None
    
    def extract_from_file(self, filepath: Path) -> Optional[np.ndarray]:
        """Extract audio from file."""
        if not NUMPY_AVAILABLE:
            return None
        
        try:
            if LIBROSA_AVAILABLE:
                audio, sr = librosa.load(str(filepath), sr=self.sample_rate)
                return audio
            elif SOUNDFILE_AVAILABLE:
                audio, sr = sf.read(str(filepath))
                if len(audio.shape) > 1:
                    audio = audio[:, 0]  # Take first channel
                # Resample if needed
                if sr != self.sample_rate:
                    from scipy import signal
                    num_samples = int(len(audio) * self.sample_rate / sr)
                    audio = signal.resample(audio, num_samples)
                return audio
            else:
                # Fallback: use wave module
                with wave.open(str(filepath), 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    return audio
        except Exception as e:
            print(f"Error extracting from file: {e}")
            return None


class VoiceAnalyzer:
    """Analyze voice characteristics from audio."""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def analyze_voice(self, audio: np.ndarray) -> Dict[str, Any]:
        """Comprehensive voice analysis."""
        if not NUMPY_AVAILABLE or audio is None or len(audio) == 0:
            return {"error": "Invalid audio"}
        
        analysis = {
            "duration": len(audio) / self.sample_rate,
            "sample_rate": self.sample_rate,
            "samples": len(audio),
        }
        
        # Basic characteristics
        analysis["max_amplitude"] = float(np.max(np.abs(audio)))
        analysis["rms_amplitude"] = float(np.sqrt(np.mean(audio**2)))
        
        # Fundamental frequency (pitch)
        analysis["fundamental_frequency"] = self._extract_f0(audio)
        
        # Formants (vocal tract resonances)
        analysis["formants"] = self._extract_formants(audio)
        
        # Spectral characteristics
        if LIBROSA_AVAILABLE:
            try:
                analysis["spectral_centroid"] = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)))
                analysis["spectral_rolloff"] = float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)))
                analysis["zero_crossing_rate"] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
                analysis["mfcc"] = np.mean(librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13), axis=1).tolist()
            except Exception:
                pass
        
        # Prosody (rhythm, stress patterns)
        analysis["prosody"] = self._analyze_prosody(audio)
        
        # Energy distribution
        analysis["energy_distribution"] = self._analyze_energy(audio)
        
        return analysis
    
    def _extract_f0(self, audio: np.ndarray) -> float:
        """Extract fundamental frequency."""
        if not SCIPY_AVAILABLE:
            return 0.0
        
        try:
            # Autocorrelation method
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks
            peaks = signal.find_peaks(autocorr, height=np.max(autocorr) * 0.3)[0]
            
            if len(peaks) > 1:
                period = peaks[1] - peaks[0]
                if period > 0:
                    freq = self.sample_rate / period
                    # Human voice range: 80-300 Hz
                    return float(max(80.0, min(300.0, freq)))
            
            # Fallback: FFT method
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
            magnitude = np.abs(fft)
            
            # Focus on voice range
            voice_range = (freqs >= 80) & (freqs <= 300)
            if np.any(voice_range):
                voice_magnitude = magnitude[voice_range]
                voice_freqs = freqs[voice_range]
                dominant_idx = np.argmax(voice_magnitude)
                return float(voice_freqs[dominant_idx])
            
            return 140.0  # Default
        except Exception:
            return 140.0
    
    def _extract_formants(self, audio: np.ndarray) -> List[float]:
        """Extract formant frequencies (F1, F2, F3)."""
        if not SCIPY_AVAILABLE:
            return [0.0, 0.0, 0.0]
        
        try:
            # LPC (Linear Predictive Coding) for formants
            # Simplified: find peaks in spectral envelope
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
            magnitude = np.abs(fft)
            
            # Typical formant ranges:
            # F1: 300-1000 Hz (vowel openness)
            # F2: 800-3000 Hz (vowel frontness)
            # F3: 2000-4000 Hz (vowel rounding)
            
            formants = []
            for low, high in [(300, 1000), (800, 3000), (2000, 4000)]:
                formant_range = (freqs >= low) & (freqs <= high)
                if np.any(formant_range):
                    formant_magnitude = magnitude[formant_range]
                    formant_freqs = freqs[formant_range]
                    peak_idx = np.argmax(formant_magnitude)
                    formants.append(float(formant_freqs[peak_idx]))
                else:
                    formants.append(0.0)
            
            return formants if len(formants) == 3 else [0.0, 0.0, 0.0]
        except Exception:
            return [0.0, 0.0, 0.0]
    
    def _analyze_prosody(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze prosody (rhythm, stress patterns)."""
        if not NUMPY_AVAILABLE:
            return {}
        
        try:
            # Energy envelope
            frame_length = int(0.025 * self.sample_rate)  # 25ms frames
            hop_length = int(0.010 * self.sample_rate)  # 10ms hop
            
            energy = []
            for i in range(0, len(audio) - frame_length, hop_length):
                frame = audio[i:i+frame_length]
                energy.append(np.sum(frame**2))
            
            energy = np.array(energy)
            
            # Prosody characteristics
            prosody = {
                "energy_mean": float(np.mean(energy)),
                "energy_std": float(np.std(energy)),
                "energy_variation": float(np.std(energy) / (np.mean(energy) + 1e-10)),
                "tempo": self._estimate_tempo(energy)
            }
            
            return prosody
        except Exception:
            return {}
    
    def _estimate_tempo(self, energy: np.ndarray) -> float:
        """Estimate speech tempo from energy envelope."""
        if len(energy) < 2:
            return 0.0
        
        try:
            # Find peaks in energy (stressed syllables)
            peaks = signal.find_peaks(energy, height=np.mean(energy) * 1.2)[0]
            
            if len(peaks) > 1:
                # Average time between peaks
                intervals = np.diff(peaks)
                avg_interval = np.mean(intervals)
                # Convert to beats per minute (assuming 10ms hop)
                tempo = 60.0 / (avg_interval * 0.010)
                return float(tempo)
            
            return 0.0
        except Exception:
            return 0.0
    
    def _analyze_energy(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze energy distribution across frequency bands."""
        if not NUMPY_AVAILABLE:
            return {}
        
        try:
            # Frequency bands: low, mid, high
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
            magnitude = np.abs(fft)
            
            low_band = (freqs >= 80) & (freqs <= 500)
            mid_band = (freqs >= 500) & (freqs <= 2000)
            high_band = (freqs >= 2000) & (freqs <= 8000)
            
            low_energy = np.sum(magnitude[low_band]) if np.any(low_band) else 0.0
            mid_energy = np.sum(magnitude[mid_band]) if np.any(mid_band) else 0.0
            high_energy = np.sum(magnitude[high_band]) if np.any(high_band) else 0.0
            
            total_energy = low_energy + mid_energy + high_energy
            
            return {
                "low_energy": float(low_energy / (total_energy + 1e-10)),
                "mid_energy": float(mid_energy / (total_energy + 1e-10)),
                "high_energy": float(high_energy / (total_energy + 1e-10))
            }
        except Exception:
            return {}


class MultiVoiceBlender:
    """Blend multiple voices into one unique voice."""
    
    def __init__(self):
        self.voice_library = {}
        self._load_library()
    
    def _load_library(self):
        """Load voice library."""
        lib_file = OMEGA_VOICE_DIR / 'multi_voice_library.json'
        if lib_file.exists():
            try:
                with open(lib_file, 'r', encoding='utf-8') as f:
                    self.voice_library = json.load(f)
            except Exception:
                pass
    
    def _save_library(self):
        """Save voice library."""
        lib_file = OMEGA_VOICE_DIR / 'multi_voice_library.json'
        try:
            with open(lib_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_library, f, indent=2)
        except Exception:
            pass
    
    def add_voice(self, voice_id: str, analysis: Dict[str, Any], source: str = "unknown"):
        """Add voice to library."""
        self.voice_library[voice_id] = {
            "analysis": analysis,
            "source": source,
            "added_at": datetime.now().isoformat()
        }
        self._save_library()
    
    def blend_voices(self, voice_ids: List[str], weights: List[float] = None) -> Dict[str, Any]:
        """Blend multiple voices with weights."""
        if not voice_ids:
            return {}
        
        if weights is None:
            weights = [1.0 / len(voice_ids)] * len(voice_ids)
        
        if len(weights) != len(voice_ids):
            weights = [1.0 / len(voice_ids)] * len(voice_ids)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Get voice analyses
        voices = []
        for vid in voice_ids:
            if vid in self.voice_library:
                voices.append(self.voice_library[vid]["analysis"])
        
        if not voices:
            return {}
        
        # Blend characteristics
        blended = {}
        
        # Blend fundamental frequency
        if all("fundamental_frequency" in v for v in voices):
            f0_values = [v["fundamental_frequency"] for v in voices]
            blended["fundamental_frequency"] = sum(f * w for f, w in zip(f0_values, weights))
        
        # Blend formants
        if all("formants" in v and len(v["formants"]) == 3 for v in voices):
            formant_arrays = [np.array(v["formants"]) for v in voices]
            blended_formants = np.zeros(3)
            for formants, weight in zip(formant_arrays, weights):
                blended_formants += formants * weight
            blended["formants"] = blended_formants.tolist()
        
        # Blend energy distribution
        if all("energy_distribution" in v for v in voices):
            energy_keys = ["low_energy", "mid_energy", "high_energy"]
            blended_energy = {}
            for key in energy_keys:
                values = [v["energy_distribution"].get(key, 0.0) for v in voices]
                blended_energy[key] = sum(v * w for v, w in zip(values, weights))
            blended["energy_distribution"] = blended_energy
        
        # Blend prosody
        if all("prosody" in v for v in voices):
            prosody_keys = ["energy_mean", "energy_std", "energy_variation", "tempo"]
            blended_prosody = {}
            for key in prosody_keys:
                values = [v["prosody"].get(key, 0.0) for v in voices]
                blended_prosody[key] = sum(v * w for v, w in zip(values, weights))
            blended["prosody"] = blended_prosody
        
        # Blend spectral centroid
        if all("spectral_centroid" in v for v in voices):
            centroid_values = [v["spectral_centroid"] for v in voices]
            blended["spectral_centroid"] = sum(c * w for c, w in zip(centroid_values, weights))
        
        return blended


class OmegaVoiceCollector:
    """Main system for collecting and blending voices."""
    
    def __init__(self):
        self.extractor = VoiceExtractor()
        self.analyzer = VoiceAnalyzer()
        self.blender = MultiVoiceBlender()
    
    def collect_from_youtube(self, url: str) -> Optional[str]:
        """Collect voice from YouTube video."""
        print(f"\n{'='*80}")
        print(f"COLLECTING VOICE FROM YOUTUBE")
        print(f"{'='*80}")
        print(f"URL: {url}")
        
        # Extract audio
        audio_file = self.extractor.extract_from_youtube(url)
        if not audio_file:
            return None
        
        # Load and analyze
        audio = self.extractor.extract_from_file(audio_file)
        if audio is None:
            return None
        
        # Analyze voice
        print("\nAnalyzing voice...")
        analysis = self.analyzer.analyze_voice(audio)
        
        # Save to library
        voice_id = f"youtube_{int(time.time())}"
        self.blender.add_voice(voice_id, analysis, source=f"youtube:{url}")
        
        print(f"\n✓ Voice collected: {voice_id}")
        print(f"  Fundamental Frequency: {analysis.get('fundamental_frequency', 0):.2f} Hz")
        print(f"  Formants: {analysis.get('formants', [])}")
        
        return voice_id
    
    def collect_from_file(self, filepath: Path, source_name: str = "file") -> Optional[str]:
        """Collect voice from audio file."""
        print(f"\n{'='*80}")
        print(f"COLLECTING VOICE FROM FILE")
        print(f"{'='*80}")
        print(f"File: {filepath}")
        
        # Load and analyze
        audio = self.extractor.extract_from_file(filepath)
        if audio is None:
            return None
        
        # Analyze voice
        print("\nAnalyzing voice...")
        analysis = self.analyzer.analyze_voice(audio)
        
        # Save to library
        voice_id = f"{source_name}_{int(time.time())}"
        self.blender.add_voice(voice_id, analysis, source=str(filepath))
        
        print(f"\n✓ Voice collected: {voice_id}")
        print(f"  Fundamental Frequency: {analysis.get('fundamental_frequency', 0):.2f} Hz")
        print(f"  Formants: {analysis.get('formants', [])}")
        
        return voice_id
    
    def create_omega_voice(self, voice_ids: List[str], user_voice_id: str = None, weights: List[float] = None) -> Dict[str, Any]:
        """Create Omega's blended voice."""
        print(f"\n{'='*80}")
        print(f"CREATING OMEGA'S BLENDED VOICE")
        print(f"{'='*80}")
        
        # Include user voice if provided
        all_voice_ids = voice_ids.copy()
        if user_voice_id and user_voice_id not in all_voice_ids:
            all_voice_ids.append(user_voice_id)
        
        # Adjust weights if user voice added
        if weights and user_voice_id:
            # Give user voice 30% weight
            user_weight = 0.3
            remaining_weight = 0.7
            adjusted_weights = [w * remaining_weight for w in weights]
            adjusted_weights.append(user_weight)
        elif user_voice_id:
            # Equal weights except user gets 30%
            n = len(voice_ids)
            adjusted_weights = [0.7 / n] * n + [0.3]
        else:
            adjusted_weights = weights
        
        # Blend voices
        blended = self.blender.blend_voices(all_voice_ids, adjusted_weights)
        
        # Save Omega's voice profile
        omega_profile = {
            "voice_id": "omega_blended",
            "blended_from": all_voice_ids,
            "weights": adjusted_weights,
            "characteristics": blended,
            "created_at": datetime.now().isoformat()
        }
        
        profile_file = OMEGA_VOICE_DIR / 'omega_blended_voice.json'
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(omega_profile, f, indent=2)
        except Exception:
            pass
        
        print(f"\n✓ Omega's voice created!")
        print(f"  Blended from {len(all_voice_ids)} voices")
        if user_voice_id:
            print(f"  Including your voice ({user_voice_id})")
        print(f"  Profile saved: {profile_file}")
        
        return omega_profile


def main():
    """Main entry point."""
    print("=" * 80)
    print("Ω OMEGA VOICE COLLECTOR")
    print("=" * 80)
    print()
    print("Collect voices from:")
    print("  - YouTube videos")
    print("  - Audio files")
    print("  - Your recordings")
    print()
    print("Then blend them to create Omega's unique voice!")
    print()
    
    collector = OmegaVoiceCollector()
    
    print("Ready to collect voices.")
    print("Use the methods:")
    print("  collector.collect_from_youtube(url)")
    print("  collector.collect_from_file(filepath)")
    print("  collector.create_omega_voice(voice_ids, user_voice_id)")


if __name__ == '__main__':
    main()

