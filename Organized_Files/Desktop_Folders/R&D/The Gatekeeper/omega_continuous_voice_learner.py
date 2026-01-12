# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Continuous Voice Learner
# Records user voice during interactions and incrementally adjusts Omega's voice

"""
Ω Omega Continuous Voice Learner

Records user's waveform during interactions and uses each new waveform
as a reference to adjust and modulate the system. Each improvement
overlaps and builds on the previous ones for cumulative enhancement.
"""

import sys
import io
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

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

SIGNATURE_FILE = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
LEARNING_HISTORY_FILE = OMEGA_VOICE_DIR / 'omega_voice_learning_history.json'

# Audio processing libraries
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
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
    SOUNDFILE_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    SOUNDFILE_AVAILABLE = False


class ContinuousVoiceLearner:
    """Continuously learns from user voice and incrementally adjusts Omega's voice."""
    
    def __init__(self):
        self.signature_file = SIGNATURE_FILE
        self.history_file = LEARNING_HISTORY_FILE
        self.current_signature = self._load_current_signature()
        self.learning_history = self._load_learning_history()
        
    def _load_current_signature(self) -> Dict[str, Any]:
        """Load current voice signature."""
        if self.signature_file.exists():
            try:
                with open(self.signature_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default signature
        return {
            "base_frequency": 135.0,
            "modulation_depth": 0.135,
            "modulation_rate": 2.5,
            "harmonic_ratio": 0.30,
            "attack_time": 0.022,
            "decay_time": 0.165,
            "sustain_level": 0.78,
            "release_time": 0.110,
            "resonance_peak": 2300.0,
            "prosody_variation": 0.126,
            "emphasis_variation": 0.142,
            "breath_pauses": True,
            "created_at": datetime.now().isoformat()
        }
    
    def _load_learning_history(self) -> list:
        """Load learning history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def _save_signature(self):
        """Save current signature."""
        try:
            with open(self.signature_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_signature, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving signature: {e}")
            return False
    
    def _save_history(self):
        """Save learning history."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_history, f, indent=2)
            return True
        except Exception:
            return False
    
    def record_voice(self, duration: float = 5.0) -> Optional[Dict[str, Any]]:
        """Record user's voice."""
        if not PYAUDIO_AVAILABLE or not NUMPY_AVAILABLE:
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
            
            return {
                "audio": audio_array,
                "sample_rate": sample_rate
            }
        except Exception as e:
            print(f"Recording error: {e}")
            return None
    
    def analyze_voice(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze voice characteristics."""
        if not NUMPY_AVAILABLE or not LIBROSA_AVAILABLE:
            return {}
        
        try:
            from omega_voice_collector import VoiceAnalyzer
            analyzer = VoiceAnalyzer(sample_rate=sample_rate)
            analysis = analyzer.analyze_voice(audio)
            return analysis
        except Exception:
            # Fallback analysis
            if not NUMPY_AVAILABLE:
                return {}
            try:
                # Basic frequency analysis
                fft = np.fft.rfft(audio)
                freqs = np.fft.rfftfreq(len(audio), 1/sample_rate)
                magnitude = np.abs(fft)
                
                # Voice range (80-300 Hz)
                voice_range = (freqs >= 80) & (freqs <= 300)
                if np.any(voice_range):
                    voice_magnitude = magnitude[voice_range]
                    voice_freqs = freqs[voice_range]
                    dominant_idx = np.argmax(voice_magnitude)
                    f0 = float(voice_freqs[dominant_idx])
                else:
                    f0 = 140.0
                
                spectral_centroid = 2000.0
                if LIBROSA_AVAILABLE:
                    try:
                        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate)))
                    except Exception:
                        pass
                
                return {
                    "fundamental_frequency": f0,
                    "spectral_centroid": spectral_centroid
                }
            except Exception:
                return {}
    
    def merge_signature(self, user_analysis: Dict[str, Any], merge_weight: float = 0.15) -> Dict[str, Any]:
        """Merge user voice characteristics with current signature (overlapping/building on old).
        
        Args:
            user_analysis: Analysis of user's voice
            merge_weight: Weight for user voice (0.0 = all Omega, 1.0 = all user, 0.15 = 15% user, 85% Omega)
        
        Returns:
            Updated signature that overlaps/builds on previous
        """
        updated_signature = self.current_signature.copy()
        
        user_f0 = user_analysis.get("fundamental_frequency", 0)
        user_formants = user_analysis.get("formants", [])
        user_spectral_centroid = user_analysis.get("spectral_centroid", 0)
        
        # Current values
        current_f0 = updated_signature.get("base_frequency", 135.0)
        current_resonance = updated_signature.get("resonance_peak", 2300.0)
        
        # Merge base frequency (weighted average - overlaps old)
        if user_f0 > 0:
            # Weighted blend: 85% current, 15% user (incremental)
            merged_f0 = current_f0 * (1 - merge_weight) + user_f0 * merge_weight
            updated_signature["base_frequency"] = max(130.0, min(160.0, merged_f0))
        
        # Merge resonance peak (formants)
        if user_spectral_centroid > 0:
            merged_resonance = current_resonance * (1 - merge_weight) + user_spectral_centroid * merge_weight
            updated_signature["resonance_peak"] = max(2000.0, min(2500.0, merged_resonance))
        
        # Merge formants if available
        if user_formants and len(user_formants) > 0:
            user_f1 = user_formants[0] if len(user_formants) > 0 else current_resonance
            current_f1 = current_resonance
            merged_f1 = current_f1 * (1 - merge_weight) + user_f1 * merge_weight
            updated_signature["resonance_peak"] = max(2000.0, min(2500.0, merged_f1))
        
        # Adjust modulation slightly based on user voice
        # User voices often have less modulation - blend it in
        current_mod_depth = updated_signature.get("modulation_depth", 0.135)
        # Slightly reduce modulation depth if user voice is more stable
        user_energy_var = user_analysis.get("energy_variance", 0)
        if user_energy_var > 0:
            # Adjust modulation depth slightly (subtle adjustment)
            updated_signature["modulation_depth"] = max(0.06, min(0.15, current_mod_depth * (1 - merge_weight * 0.3)))
        
        # Adjust prosody variation (user speech patterns)
        current_prosody = updated_signature.get("prosody_variation", 0.126)
        user_prosody = user_analysis.get("prosody", {})
        if isinstance(user_prosody, dict) and user_prosody.get("variation"):
            merged_prosody = current_prosody * (1 - merge_weight) + user_prosody["variation"] * merge_weight
            updated_signature["prosody_variation"] = max(0.10, min(0.18, merged_prosody))
        
        # Add learning metadata
        updated_signature["last_updated"] = datetime.now().isoformat()
        updated_signature["learning_iteration"] = updated_signature.get("learning_iteration", 0) + 1
        updated_signature["merge_weight"] = merge_weight
        
        return updated_signature
    
    def learn_from_recording(self, audio: np.ndarray, sample_rate: int, save_audio: bool = True) -> bool:
        """Learn from a voice recording and update signature incrementally."""
        print("\n" + "=" * 80)
        print("LEARNING FROM USER VOICE")
        print("=" * 80)
        
        # Analyze user voice
        print("\nAnalyzing user voice...")
        user_analysis = self.analyze_voice(audio, sample_rate)
        
        if not user_analysis or user_analysis.get("error"):
            print("⚠️  Could not analyze voice")
            return False
        
        user_f0 = user_analysis.get("fundamental_frequency", 0)
        print(f"  User F0: {user_f0:.2f} Hz")
        
        # Show current signature
        current_f0 = self.current_signature.get("base_frequency", 135.0)
        print(f"  Current Omega F0: {current_f0:.2f} Hz")
        
        # Merge signatures (overlapping - building on old)
        print(f"\nMerging with current signature (15% user, 85% Omega)...")
        updated_signature = self.merge_signature(user_analysis, merge_weight=0.15)
        
        # Show changes
        new_f0 = updated_signature.get("base_frequency", current_f0)
        print(f"  New Omega F0: {new_f0:.2f} Hz (incremental change: {new_f0 - current_f0:+.2f} Hz)")
        
        # Save audio if requested
        if save_audio and SOUNDFILE_AVAILABLE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = OMEGA_VOICE_DIR / f"user_voice_learning_{timestamp}.wav"
            try:
                sf.write(str(audio_file), audio, sample_rate)
                print(f"  Audio saved: {audio_file.name}")
            except Exception:
                pass
        
        # Update signature
        self.current_signature = updated_signature
        
        # Add to learning history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "iteration": updated_signature.get("learning_iteration", 0),
            "user_f0": float(user_f0),
            "omega_f0_before": float(current_f0),
            "omega_f0_after": float(new_f0),
            "merge_weight": 0.15,
            "changes": {
                "base_frequency": float(new_f0 - current_f0),
                "resonance_peak": float(updated_signature.get("resonance_peak", 2300.0) - self.current_signature.get("resonance_peak", 2300.0))
            }
        }
        self.learning_history.append(history_entry)
        
        # Keep last 100 entries
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]
        
        # Save updated signature and history
        if self._save_signature() and self._save_history():
            print(f"\n✓ Voice signature updated! (Iteration {updated_signature.get('learning_iteration', 0)})")
            print(f"  Each improvement overlaps and builds on previous ones.")
            return True
        else:
            print("\n⚠️  Signature update failed")
            return False
    
    def record_and_learn(self, duration: float = 5.0) -> bool:
        """Record user voice and learn from it."""
        if not PYAUDIO_AVAILABLE:
            print("\n⚠️  PyAudio not available. Cannot record.")
            print("Install with: pip install pyaudio")
            return False
        
        print(f"\n🎤 Recording your voice for {duration:.1f} seconds...")
        recording = self.record_voice(duration)
        
        if not recording:
            print("\n⚠️  Recording failed")
            return False
        
        audio = recording["audio"]
        sample_rate = recording["sample_rate"]
        
        # Check if audio has content
        if len(audio) == 0 or np.max(np.abs(audio)) < 0.001:
            print("\n⚠️  No audio detected")
            return False
        
        # Learn from recording
        return self.learn_from_recording(audio, sample_rate)
    
    def learn_from_file(self, audio_file: Path) -> bool:
        """Learn from an audio file."""
        if not SOUNDFILE_AVAILABLE or not LIBROSA_AVAILABLE:
            print("\n⚠️  Audio libraries not available")
            return False
        
        if not audio_file.exists():
            print(f"\n⚠️  Audio file not found: {audio_file}")
            return False
        
        try:
            audio, sample_rate = librosa.load(str(audio_file), sr=44100)
            return self.learn_from_recording(audio, sample_rate, save_audio=False)
        except Exception as e:
            print(f"\n⚠️  Error loading audio file: {e}")
            return False


def learn_from_interaction(duration: float = 5.0) -> bool:
    """Record user voice during interaction and learn from it.
    
    This should be called each time there's user interaction.
    Each call builds on previous learning (overlapping improvements).
    """
    learner = ContinuousVoiceLearner()
    return learner.record_and_learn(duration)


def learn_from_audio_file(audio_file: Path) -> bool:
    """Learn from an audio file (for batch processing)."""
    learner = ContinuousVoiceLearner()
    return learner.learn_from_file(audio_file)


def main():
    """Main entry point for continuous learning."""
    print("=" * 80)
    print("Ω OMEGA CONTINUOUS VOICE LEARNER")
    print("=" * 80)
    print("\nThis system learns from your voice during each interaction.")
    print("Each new waveform is used as a reference to adjust Omega's voice.")
    print("Improvements overlap and build on previous ones (cumulative learning).")
    print()
    
    learner = ContinuousVoiceLearner()
    
    # Show current state
    print("Current Voice Signature:")
    print(f"  Base Frequency: {learner.current_signature.get('base_frequency', 135.0):.2f} Hz")
    print(f"  Learning Iterations: {learner.current_signature.get('learning_iteration', 0)}")
    print(f"  Last Updated: {learner.current_signature.get('last_updated', 'Never')}")
    print(f"\nLearning History: {len(learner.learning_history)} entries")
    
    # Record and learn
    print("\n" + "=" * 80)
    print("READY TO LEARN")
    print("=" * 80)
    print("\nRecording your voice...")
    
    success = learner.record_and_learn(duration=5.0)
    
    if success:
        print("\n" + "=" * 80)
        print("✓ LEARNING COMPLETE")
        print("=" * 80)
        print("\nOmega's voice has been updated based on your voice.")
        print("This improvement overlaps and builds on all previous learning.")
        print("\nNext interaction will continue building on this updated voice.")
    else:
        print("\n⚠️  Learning failed. Check microphone and dependencies.")


if __name__ == '__main__':
    main()

