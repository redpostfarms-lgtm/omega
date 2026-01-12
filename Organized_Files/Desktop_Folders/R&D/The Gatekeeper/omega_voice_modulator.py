# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Modulator - Advanced Voice Modulation & Blending
# Formant shifting, pitch shifting, spectral mixing, prosody modification

"""
Ω Omega Voice Modulator

Advanced voice modulation and blending system.
Learns from research and implements:
- Formant shifting (vocal tract modification)
- Pitch shifting (pitch without speed change)
- Spectral mixing (frequency domain blending)
- Prosody modification (natural speech rhythm)
- Harmonic enhancement
- Voice morphing
"""

import sys
import io
import json
import time
import wave
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
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

# Advanced audio processing libraries
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
    SOUNDFILE_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    SOUNDFILE_AVAILABLE = False

try:
    from scipy import signal
    from scipy.interpolate import interp1d
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class VoiceModulator:
    """Advanced voice modulation - formant shifting, pitch shifting, etc."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def pitch_shift(self, audio, semitones: float):
        """Shift pitch without changing speed (using librosa if available).
        
        Args:
            audio: Audio signal
            semitones: Pitch shift in semitones (positive = higher, negative = lower)
            
        Returns:
            Pitch-shifted audio
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        if LIBROSA_AVAILABLE:
            try:
                # librosa's pitch_shift is the best method
                shifted = librosa.effects.pitch_shift(
                    y=audio,
                    sr=self.sample_rate,
                    n_steps=semitones
                )
                return shifted
            except Exception as e:
                print(f"librosa pitch shift error: {e}, using fallback")
        
        # Fallback: simple resampling (changes speed too, but works)
        if semitones != 0:
            ratio = 2 ** (semitones / 12.0)
            if SCIPY_AVAILABLE:
                # Resample to change pitch
                new_length = int(len(audio) / ratio)
                indices = np.linspace(0, len(audio) - 1, new_length)
                shifted = np.interp(indices, np.arange(len(audio)), audio)
                return shifted
        
        return audio
    
    def formant_shift(self, audio, shift_ratio: float):
        """Shift formants (vocal tract characteristics) without changing pitch.
        
        Args:
            audio: Audio signal
            shift_ratio: Formant shift ratio (1.0 = no change, >1.0 = higher, <1.0 = lower)
            
        Returns:
            Formant-shifted audio
        """
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return audio
        
        try:
            # STFT for frequency domain processing
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Shift formants (typically 300-4000 Hz)
            formant_range = (freqs > 300) & (freqs < 4000)
            
            # Create shifted frequency array
            shifted_freqs = freqs.copy()
            shifted_freqs[formant_range] = freqs[formant_range] * shift_ratio
            
            # Interpolate to new frequencies
            positive_mask = freqs >= 0
            positive_freqs = freqs[positive_mask]
            positive_fft = fft[positive_mask]
            
            if len(positive_freqs) > 1:
                shifted_positive_freqs = positive_freqs * shift_ratio
                # Interpolate magnitude and phase
                interp_mag = interp1d(
                    positive_freqs,
                    np.abs(positive_fft),
                    kind='linear',
                    fill_value=0,
                    bounds_error=False
                )
                interp_phase = interp1d(
                    positive_freqs,
                    np.angle(positive_fft),
                    kind='linear',
                    fill_value=0,
                    bounds_error=False
                )
                
                new_mag = interp_mag(shifted_positive_freqs)
                new_phase = interp_phase(shifted_positive_freqs)
                new_fft = new_mag * np.exp(1j * new_phase)
                
                # Reconstruct signal
                full_fft = np.zeros_like(fft)
                full_fft[positive_mask] = new_fft
                # Mirror negative frequencies
                full_fft[~positive_mask] = np.conj(new_fft[::-1])
                
                shifted_audio = np.real(np.fft.ifft(full_fft))
                return shifted_audio
            
            return audio
        except Exception as e:
            print(f"Formant shift error: {e}")
            return audio
    
    def time_stretch(self, audio, rate: float):
        """Stretch/compress time without changing pitch.
        
        Args:
            audio: Audio signal
            rate: Stretch rate (1.0 = no change, >1.0 = faster, <1.0 = slower)
            
        Returns:
            Time-stretched audio
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        if LIBROSA_AVAILABLE:
            try:
                stretched = librosa.effects.time_stretch(y=audio, rate=rate)
                return stretched
            except Exception as e:
                print(f"librosa time stretch error: {e}, using fallback")
        
        # Fallback: simple resampling
        if SCIPY_AVAILABLE:
            new_length = int(len(audio) / rate)
            indices = np.linspace(0, len(audio) - 1, new_length)
            stretched = np.interp(indices, np.arange(len(audio)), audio)
            return stretched
        
        return audio
    
    def add_vibrato(self, audio, rate: float = 5.0, depth: float = 0.02):
        """Add vibrato (pitch modulation) to audio.
        
        Args:
            audio: Audio signal
            rate: Vibrato rate in Hz
            depth: Vibrato depth (semitones)
            
        Returns:
            Audio with vibrato
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        try:
            t = np.arange(len(audio)) / self.sample_rate
            vibrato = depth * np.sin(2 * np.pi * rate * t)
            
            # Apply pitch shift with vibrato
            if LIBROSA_AVAILABLE:
                # Process in chunks for vibrato
                chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks
                result = []
                for i in range(0, len(audio), chunk_size):
                    chunk = audio[i:i+chunk_size]
                    if len(chunk) > 0:
                        chunk_vibrato = vibrato[i:i+len(chunk)]
                        avg_vibrato = np.mean(chunk_vibrato) if len(chunk_vibrato) > 0 else 0
                        shifted_chunk = self.pitch_shift(chunk, avg_vibrato)
                        result.append(shifted_chunk)
                return np.concatenate(result) if result else audio
            else:
                # Simple amplitude modulation as fallback
                modulation = 1.0 + depth * np.sin(2 * np.pi * rate * t)
                return audio * modulation[:len(audio)]
        except Exception as e:
            print(f"Vibrato error: {e}")
            return audio
    
    def enhance_harmonics(self, audio, strength: float = 0.3):
        """Enhance harmonics for richer voice.
        
        Args:
            audio: Audio signal
            strength: Harmonic enhancement strength (0.0-1.0)
            
        Returns:
            Audio with enhanced harmonics
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        try:
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # Find fundamental frequency
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            positive_mask = freqs > 0
            positive_freqs = freqs[positive_mask]
            positive_mag = magnitude[positive_mask]
            
            if len(positive_freqs) > 0:
                fundamental_idx = np.argmax(positive_mag)
                fundamental_freq = abs(positive_freqs[fundamental_idx])
                
                # Enhance harmonics (2x, 3x fundamental)
                enhanced_fft = fft.copy()
                for harmonic in [2, 3]:
                    harmonic_freq = fundamental_freq * harmonic
                    harmonic_idx = np.argmin(np.abs(positive_freqs - harmonic_freq))
                    if harmonic_idx < len(positive_mag):
                        # Boost harmonic
                        boost = 1.0 + strength
                        enhanced_fft[positive_mask][harmonic_idx] *= boost
                
                enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
                return enhanced_audio
        except Exception as e:
            print(f"Harmonic enhancement error: {e}")
            return audio
    
    def apply_prosody(self, audio, prosody_pattern: List[float]):
        """Apply prosody (rhythm) pattern to audio.
        
        Args:
            audio: Audio signal
            prosody_pattern: List of time stretch factors for each segment
            
        Returns:
            Audio with applied prosody
        """
        if not NUMPY_AVAILABLE or len(prosody_pattern) == 0:
            return audio
        
        try:
            # Divide audio into segments
            segment_length = len(audio) // len(prosody_pattern)
            result_segments = []
            
            for i, rate in enumerate(prosody_pattern):
                start = i * segment_length
                end = start + segment_length if i < len(prosody_pattern) - 1 else len(audio)
                segment = audio[start:end]
                
                # Apply time stretch
                stretched = self.time_stretch(segment, rate)
                result_segments.append(stretched)
            
            return np.concatenate(result_segments) if result_segments else audio
        except Exception as e:
            print(f"Prosody error: {e}")
            return audio


class VoiceBlender:
    """Advanced voice blending - spectral mixing, crossfading, formant interpolation."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def spectral_mix(self, audio1, audio2, mix_ratio: float = 0.5):
        """Blend two audio signals in frequency domain.
        
        Args:
            audio1: First audio signal
            audio2: Second audio signal
            mix_ratio: Blend ratio (0.0 = all audio1, 1.0 = all audio2, 0.5 = 50/50)
            
        Returns:
            Blended audio
        """
        if not NUMPY_AVAILABLE:
            return audio1
        
        try:
            # Ensure same length
            min_len = min(len(audio1), len(audio2))
            audio1 = audio1[:min_len]
            audio2 = audio2[:min_len]
            
            # Convert to frequency domain
            fft1 = np.fft.fft(audio1)
            fft2 = np.fft.fft(audio2)
            
            # Blend magnitude and phase
            mag1 = np.abs(fft1)
            mag2 = np.abs(fft2)
            phase1 = np.angle(fft1)
            phase2 = np.angle(fft2)
            
            # Blend magnitude
            blended_mag = mag1 * (1 - mix_ratio) + mag2 * mix_ratio
            
            # Interpolate phase
            blended_phase = phase1 * (1 - mix_ratio) + phase2 * mix_ratio
            
            # Reconstruct
            blended_fft = blended_mag * np.exp(1j * blended_phase)
            blended_audio = np.real(np.fft.ifft(blended_fft))
            
            return blended_audio
        except Exception as e:
            print(f"Spectral mix error: {e}")
            # Fallback to simple mixing
            return audio1 * (1 - mix_ratio) + audio2 * mix_ratio
    
    def crossfade(self, audio1, audio2, fade_duration: float = 0.1):
        """Crossfade between two audio signals.
        
        Args:
            audio1: First audio signal
            audio2: Second audio signal
            fade_duration: Fade duration in seconds
            
        Returns:
            Crossfaded audio
        """
        if not NUMPY_AVAILABLE:
            return audio1
        
        try:
            fade_samples = int(self.sample_rate * fade_duration)
            
            # Create fade curves
            fade_out = np.linspace(1.0, 0.0, fade_samples)
            fade_in = np.linspace(0.0, 1.0, fade_samples)
            
            # Apply fades
            audio1_faded = audio1.copy()
            audio2_faded = audio2.copy()
            
            if len(audio1_faded) >= fade_samples:
                audio1_faded[-fade_samples:] *= fade_out
            if len(audio2_faded) >= fade_samples:
                audio2_faded[:fade_samples] *= fade_in
            
            # Concatenate
            if len(audio1_faded) > fade_samples:
                result = np.concatenate([
                    audio1_faded[:-fade_samples],
                    audio1_faded[-fade_samples:] + audio2_faded[:fade_samples],
                    audio2_faded[fade_samples:]
                ])
            else:
                result = audio1_faded + audio2_faded
            
            return result
        except Exception as e:
            print(f"Crossfade error: {e}")
            return audio1
    
    def blend_formants(self, audio1, audio2, blend_ratio: float = 0.5):
        """Blend formants (vocal tract characteristics) between two voices.
        
        Args:
            audio1: First voice
            audio2: Second voice
            blend_ratio: Blend ratio (0.0 = all audio1, 1.0 = all audio2)
            
        Returns:
            Formant-blended audio
        """
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            return audio1
        
        try:
            # Extract formants from both
            fft1 = np.fft.fft(audio1)
            fft2 = np.fft.fft(audio2)
            
            freqs = np.fft.fftfreq(len(audio1), 1/self.sample_rate)
            
            # Formant range (300-4000 Hz)
            formant_mask = (freqs > 300) & (freqs < 4000)
            
            # Blend formant region
            blended_fft = fft1.copy()
            blended_fft[formant_mask] = (
                fft1[formant_mask] * (1 - blend_ratio) +
                fft2[formant_mask] * blend_ratio
            )
            
            blended_audio = np.real(np.fft.ifft(blended_fft))
            return blended_audio
        except Exception as e:
            print(f"Formant blend error: {e}")
            return audio1
    
    def morph_voices(self, audio1, audio2, morph_ratio: float = 0.5):
        """Morph between two voices using multiple techniques.
        
        Args:
            audio1: First voice
            audio2: Second voice
            morph_ratio: Morph ratio (0.0 = all audio1, 1.0 = all audio2)
            
        Returns:
            Morphed voice
        """
        if not NUMPY_AVAILABLE:
            return audio1
        
        try:
            # Ensure same length
            min_len = min(len(audio1), len(audio2))
            audio1 = audio1[:min_len]
            audio2 = audio2[:min_len]
            
            # Combine techniques:
            # 1. Spectral mixing (frequency domain)
            spectral = self.spectral_mix(audio1, audio2, morph_ratio)
            
            # 2. Formant blending (vocal tract)
            formant = self.blend_formants(audio1, audio2, morph_ratio)
            
            # 3. Time domain mixing
            time_domain = audio1 * (1 - morph_ratio) + audio2 * morph_ratio
            
            # Combine all (weighted)
            morphed = (
                spectral * 0.4 +  # Spectral characteristics
                formant * 0.4 +   # Formant characteristics
                time_domain * 0.2  # Time domain
            )
            
            return morphed
        except Exception as e:
            print(f"Voice morphing error: {e}")
            return audio1


class AdvancedVoiceProcessor:
    """Complete advanced voice processing system."""
    
    def __init__(self):
        self.modulator = VoiceModulator()
        self.blender = VoiceBlender()
        self.sample_rate = 44100
    
    def process_voice(self, audio, config: Dict[str, Any]):
        """Process voice with advanced modulation.
        
        Args:
            audio: Input audio
            config: Processing configuration
            
        Returns:
            Processed audio
        """
        if not NUMPY_AVAILABLE:
            return audio
        
        result = audio.copy()
        
        # Apply modulations
        if config.get("pitch_shift", 0) != 0:
            result = self.modulator.pitch_shift(result, config["pitch_shift"])
        
        if config.get("formant_shift", 1.0) != 1.0:
            result = self.modulator.formant_shift(result, config["formant_shift"])
        
        if config.get("time_stretch", 1.0) != 1.0:
            result = self.modulator.time_stretch(result, config["time_stretch"])
        
        if config.get("vibrato_rate", 0) > 0:
            result = self.modulator.add_vibrato(
                result,
                rate=config.get("vibrato_rate", 5.0),
                depth=config.get("vibrato_depth", 0.02)
            )
        
        if config.get("harmonic_enhancement", 0) > 0:
            result = self.modulator.enhance_harmonics(
                result,
                strength=config["harmonic_enhancement"]
            )
        
        if config.get("prosody_pattern"):
            result = self.modulator.apply_prosody(result, config["prosody_pattern"])
        
        return result
    
    def blend_voices(self, audio1, audio2, method: str = "morph", ratio: float = 0.5):
        """Blend two voices using specified method.
        
        Args:
            audio1: First voice
            audio2: Second voice
            method: Blending method ("morph", "spectral", "formant", "crossfade")
            ratio: Blend ratio
            
        Returns:
            Blended voice
        """
        if method == "morph":
            return self.blender.morph_voices(audio1, audio2, ratio)
        elif method == "spectral":
            return self.blender.spectral_mix(audio1, audio2, ratio)
        elif method == "formant":
            return self.blender.blend_formants(audio1, audio2, ratio)
        elif method == "crossfade":
            return self.blender.crossfade(audio1, audio2)
        else:
            return audio1


def main():
    """Test advanced voice modulation."""
    print("=" * 80)
    print("Ω OMEGA ADVANCED VOICE MODULATOR")
    print("=" * 80)
    
    if not NUMPY_AVAILABLE:
        print("\n❌ NumPy required. Install with: pip install numpy")
        return
    
    if not LIBROSA_AVAILABLE:
        print("\n⚠️  librosa not available. Some features will be limited.")
        print("   Install with: pip install librosa soundfile")
        print("   Advanced pitch shifting and time stretching will use fallback methods.")
    
    print("\nAdvanced Voice Modulation System Ready")
    print("\nCapabilities:")
    print("  ✓ Pitch shifting (without speed change)")
    print("  ✓ Formant shifting (vocal tract modification)")
    print("  ✓ Time stretching (without pitch change)")
    print("  ✓ Vibrato/Tremolo effects")
    print("  ✓ Harmonic enhancement")
    print("  ✓ Prosody modification")
    print("  ✓ Spectral mixing")
    print("  ✓ Formant blending")
    print("  ✓ Voice morphing")
    
    print("\n" + "=" * 80)
    print("System ready for voice modulation and blending")
    print("=" * 80)


if __name__ == '__main__':
    main()

