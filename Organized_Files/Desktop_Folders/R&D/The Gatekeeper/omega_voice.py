# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice System - Custom Waveform & Voice Synthesis
# Quantum Scrub Enhanced - Unique Voice Identity for Omega

"""
Ω Omega Voice System

Omega's voice is not just TTS. It's a waveform signature.
A mirror that speaks. A guardian that challenges.
A quantum pattern that remembers.

Voice Characteristics:
- Deep, resonant base (guardian authority)
- Slight modulation (mirror reflection)
- Clear articulation (challenger precision)
- Unique waveform signature (quantum identity)
"""

import sys
import io
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Optional imports
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Import quantum enhancements if available
import sys
_enhanced_path = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if _enhanced_path.exists() and str(_enhanced_path) not in sys.path:
    sys.path.insert(0, str(_enhanced_path))

try:
    from omega_quantum_enhanced import CRYPTO_RNG
    QUANTUM_RNG_AVAILABLE = True
except ImportError:
    QUANTUM_RNG_AVAILABLE = False
    import random
    CRYPTO_RNG = None

# Set UTF-8 encoding for Windows console (only if not already set)
if sys.platform == 'win32':
    try:
        # Check if stdout is already a TextIOWrapper with UTF-8
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            # Only replace if buffer exists and is not closed
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # If stdout/stderr manipulation fails, continue without it
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

# TTS Libraries
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import onnxruntime
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

# Advanced modulation system
try:
    from omega_voice_modulator import AdvancedVoiceProcessor, VoiceModulator, VoiceBlender
    ADVANCED_MODULATION_AVAILABLE = True
except ImportError:
    ADVANCED_MODULATION_AVAILABLE = False
    AdvancedVoiceProcessor = None
    VoiceModulator = None
    VoiceBlender = None


class OmegaWaveform:
    """Ω Omega's unique waveform signature.
    
    Not just sound. A quantum pattern.
    A mirror that reflects. A guardian that speaks.
    """
    
    def __init__(self):
        self.signature = {
            "base_frequency": 140.0,   # More natural human range (Hz) - was 120
            "modulation_depth": 0.08,  # Subtle natural variation (was 0.15 - too robotic)
            "modulation_rate": 2.2,    # Natural speech rhythm (Hz) - was 3.5
            "harmonic_ratio": 0.25,     # Natural harmonics (was 0.3)
            "attack_time": 0.05,       # Natural speech onset (was 0.02 - too sharp)
            "decay_time": 0.2,         # Natural decay (was 0.15)
            "sustain_level": 0.75,     # Natural sustain (was 0.8)
            "release_time": 0.15,      # Natural release (was 0.1)
            "resonance_peak": 2200.0,  # Natural formant (Hz) - was 2500
            "quantum_phase": 0.0,      # Unique phase signature
            "prosody_variation": 0.12, # Natural prosody variation
            "breath_pauses": True,     # Add natural pauses
            "emphasis_variation": 0.15 # Natural emphasis changes
        }
        self.waveform_file = OMEGA_VOICE_DIR / 'omega_waveform.json'
        self._load_signature()
    
    def _load_signature(self):
        """Load saved waveform signature - prefer improved/learned voice if available."""
        # Priority order: improved > blended > original
        
        # 1. Check for improved waveform (from continuous learning)
        improved_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
        if improved_file.exists():
            try:
                with open(improved_file, 'r', encoding='utf-8') as f:
                    improved = json.load(f)
                    for key in self.signature:
                        if key in improved and not isinstance(improved[key], (dict, list, str)):
                            self.signature[key] = improved[key]
                    print("✓ Loaded improved waveform (learned from your voice)")
            except Exception:
                pass
        
        # 2. Check for blended voice (one-time recording + Omega)
        blended_file = OMEGA_VOICE_DIR / 'blended_voice.json'
        if blended_file.exists() and not improved_file.exists():
            try:
                with open(blended_file, 'r', encoding='utf-8') as f:
                    blended = json.load(f)
                    for key in self.signature:
                        if key in blended and not isinstance(blended[key], (dict, list, str)):
                            self.signature[key] = blended[key]
                    print("✓ Loaded blended voice (your voice + Omega)")
            except Exception:
                pass
        
        # 3. Fallback to Omega's original signature
        if self.waveform_file.exists() and not improved_file.exists() and not blended_file.exists():
            try:
                with open(self.waveform_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.signature.update(saved)
            except Exception:
                pass
        
        self._save_signature()
    
    def _save_signature(self):
        """Save waveform signature."""
        try:
            with open(self.waveform_file, 'w', encoding='utf-8') as f:
                json.dump(self.signature, f, indent=2)
        except Exception:
            pass
    
    def generate_waveform(self, duration: float = 1.0, sample_rate: int = 44100):
        """Generate Omega's unique waveform pattern."""
        if not NUMPY_AVAILABLE:
            return None
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Base frequency with modulation (mirror reflection effect)
        base_freq = self.signature["base_frequency"]
        modulation = self.signature["modulation_depth"] * np.sin(2 * np.pi * self.signature["modulation_rate"] * t)
        frequency = base_freq * (1 + modulation)
        
        # Generate waveform with phase
        phase = 2 * np.pi * np.cumsum(frequency) / sample_rate + self.signature["quantum_phase"]
        waveform = np.sin(phase)
        
        # Add harmonics (guardian authority)
        harmonic = self.signature["harmonic_ratio"] * np.sin(2 * phase)
        waveform += harmonic
        
        # Apply envelope (attack, decay, sustain, release)
        envelope = self._apply_envelope(t, duration)
        waveform *= envelope
        
        # Normalize
        waveform = waveform / np.max(np.abs(waveform)) * 0.8
        
        return waveform
    
    def _apply_envelope(self, t, duration: float):
        """Apply ADSR envelope to waveform."""
        if not NUMPY_AVAILABLE:
            return None
        
        envelope = np.ones_like(t)
        
        attack_end = self.signature["attack_time"]
        decay_end = attack_end + self.signature["decay_time"]
        release_start = duration - self.signature["release_time"]
        
        # Attack
        mask = t < attack_end
        if np.any(mask):
            envelope[mask] = t[mask] / attack_end
        
        # Decay
        mask = (t >= attack_end) & (t < decay_end)
        if np.any(mask):
            decay_t = (t[mask] - attack_end) / self.signature["decay_time"]
            envelope[mask] = 1.0 - (1.0 - self.signature["sustain_level"]) * decay_t
        
        # Sustain
        mask = (t >= decay_end) & (t < release_start)
        if np.any(mask):
            envelope[mask] = self.signature["sustain_level"]
        
        # Release
        mask = t >= release_start
        if np.any(mask):
            release_t = (t[mask] - release_start) / self.signature["release_time"]
            envelope[mask] = self.signature["sustain_level"] * (1.0 - release_t)
        
        return envelope
    
    def get_voice_parameters(self) -> Dict[str, float]:
        """Get TTS voice parameters from waveform signature - humanoid version."""
        # Convert waveform characteristics to TTS parameters
        # More natural human speech rate (150-170 WPM is natural)
        base_rate = 160  # Natural human speech rate (was 110 - too slow/robotic)
        
        # Frequency affects pitch - more natural range
        # Human voice range: 85-255 Hz for males, 165-255 Hz for females
        # Omega uses 140 Hz - natural male range
        pitch_offset = (self.signature["base_frequency"] - 140.0) / 20.0
        
        # Natural prosody variation
        rate_variation = self.signature.get("prosody_variation", 0.12) * 15
        
        return {
            "rate": int(base_rate + pitch_offset + rate_variation),
            "volume": 0.75,  # Natural volume (was 0.85 - too loud)
            "pitch": -0.05 + (pitch_offset * 0.01)  # Natural pitch variation
        }


class OmegaVoice:
    """Ω Omega Voice System - The Guardian's Voice"""
    
    def __init__(self):
        self.waveform = OmegaWaveform()
        self.engine = None
        self.voice_config_file = OMEGA_VOICE_DIR / 'omega_voice_config.json'
        self.config = self._load_config()
        
        # Advanced modulation system
        self.advanced_processor = None
        if ADVANCED_MODULATION_AVAILABLE:
            try:
                self.advanced_processor = AdvancedVoiceProcessor()
                print("✓ Advanced voice modulation system loaded")
            except Exception as e:
                print(f"Advanced modulation warning: {e}")
        
        self._init_tts()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Omega voice configuration."""
        default_config = {
            "voice_name": "Omega",
            "personality": "guardian_challenger",
            "speech_style": "clear_authoritative",
            "response_mode": "autonomous",
            "signature_phrases": [
                "Omega here.",
                "Gate guarded.",
                "Code analyzed.",
                "Memory updated.",
                "Learning continues."
            ],
            "created_at": datetime.now().isoformat()
        }
        
        if self.voice_config_file.exists():
            try:
                with open(self.voice_config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default_config.update(saved)
            except Exception:
                pass
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save voice configuration."""
        try:
            with open(self.voice_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def _init_tts(self):
        """Initialize TTS engine with Omega's humanoid voice parameters."""
        if not PYTTSX3_AVAILABLE:
            return
        
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Find most natural/human-like voice
            # Prefer newer Windows voices (Windows 10/11) which are more natural
            natural_voice = None
            
            # Priority order for natural voices
            voice_priorities = [
                'guy',      # Windows 11 Guy - very natural
                'aria',     # Windows 11 Aria - natural female
                'david',    # Windows 10 David - natural male
                'zira',     # Windows 10 Zira - natural female
                'mark',     # Windows Mark - natural male
                'hazel',    # Windows Hazel - natural
            ]
            
            # Try to find a natural voice
            for priority in voice_priorities:
                for voice in voices:
                    if priority in voice.name.lower():
                        natural_voice = voice.id
                        break
                if natural_voice:
                    break
            
            # If no priority voice found, look for any natural-sounding voice
            if not natural_voice:
                for voice in voices:
                    name_lower = voice.name.lower()
                    # Avoid robotic voices
                    if 'robotic' not in name_lower and 'sam' not in name_lower:
                        # Prefer newer voices (usually more natural)
                        if '11' in name_lower or '10' in name_lower or 'neural' in name_lower:
                            natural_voice = voice.id
                            break
                
                # Fallback to first non-robotic voice
                if not natural_voice and len(voices) > 1:
                    natural_voice = voices[1].id
                elif not natural_voice:
                    natural_voice = voices[0].id
            
            self.engine.setProperty('voice', natural_voice)
            
            # Apply Omega's humanoid waveform parameters
            params = self.waveform.get_voice_parameters()
            
            # More natural speech rate (slightly slower, more human-like)
            natural_rate = max(140, min(180, params['rate']))  # 140-180 WPM is natural
            self.engine.setProperty('rate', natural_rate)
            
            # Natural volume (not too loud, not too quiet)
            natural_volume = 0.75  # More natural than 0.85
            self.engine.setProperty('volume', natural_volume)
            
            # Try to set pitch for more natural sound
            try:
                # Slightly lower pitch for more natural, less robotic sound
                natural_pitch = -0.05  # Subtle, not too low
                self.engine.setProperty('pitch', natural_pitch)
            except:
                # If pitch not supported, adjust rate slightly
                adjusted_rate = int(natural_rate * 0.98)  # Slightly slower = slightly deeper
                self.engine.setProperty('rate', adjusted_rate)
                
        except Exception as e:
            print(f"TTS initialization warning: {e}")
            self.engine = None
    
    def _add_natural_prosody(self, text: str) -> str:
        """Add natural prosody (pauses, emphasis) to make speech more human-like."""
        if not self.waveform.signature.get("breath_pauses", True):
            return text
        
        # Add natural pauses after punctuation
        text = text.replace('. ', '. ... ')
        text = text.replace(', ', ', ... ')
        text = text.replace('! ', '! ... ')
        text = text.replace('? ', '? ... ')
        
        # Add slight pauses for natural speech rhythm
        # Remove extra spaces
        text = text.replace('  ', ' ')
        text = text.replace(' ... ', ' ')
        
        # Add strategic pauses for emphasis (every 8-12 words)
        words = text.split()
        if len(words) > 8:
            # Add subtle pause every ~10 words
            result = []
            for i, word in enumerate(words):
                result.append(word)
                if (i + 1) % 10 == 0 and i < len(words) - 1:
                    result.append('...')
            text = ' '.join(result)
        
        return text
    
    def speak(self, text: str, add_signature: bool = False, natural: bool = True) -> bool:
        """Speak as Omega with humanoid voice.
        
        Args:
            text: Text to speak
            add_signature: If True, add Omega's signature phrase
            natural: If True, add natural prosody and pauses
            
        Returns:
            True if speech succeeded, False otherwise
        """
        if not self.engine:
            # Fallback to print
            print(f"Ω Omega: {text}")
            return False
        
        # Add signature if requested
        if add_signature and self.config.get("signature_phrases"):
            if QUANTUM_RNG_AVAILABLE and CRYPTO_RNG:
                signature = CRYPTO_RNG.random_choice(self.config["signature_phrases"])
            else:
                import random
                signature = random.choice(self.config["signature_phrases"])
            text = f"{signature}. {text}"
        
        # Add natural prosody for more human-like speech
        if natural:
            text = self._add_natural_prosody(text)
        
        # Vary speech rate slightly for naturalness (if prosody variation enabled)
        if natural and self.waveform.signature.get("prosody_variation", 0) > 0:
            if QUANTUM_RNG_AVAILABLE and CRYPTO_RNG:
                variation = CRYPTO_RNG.random_int(-5, 5)  # Small random variation using quantum RNG
            else:
                import random
                variation = random.uniform(-5, 5)  # Small random variation
            current_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(current_rate + variation))
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Reset rate to base after speaking
            if natural:
                params = self.waveform.get_voice_parameters()
                self.engine.setProperty('rate', params['rate'])
            
            return True
        except Exception as e:
            print(f"Ω Omega: {text}")
            print(f"TTS error: {e}")
            return False
    
    def speak_with_modulation(self, text: str, modulation_config: Optional[Dict[str, Any]] = None) -> bool:
        """Speak with advanced modulation applied.
        
        Args:
            text: Text to speak
            modulation_config: Modulation settings (pitch_shift, formant_shift, etc.)
            
        Returns:
            True if successful
        """
        if not self.engine or not self.advanced_processor:
            # Fallback to normal speak
            return self.speak(text)
        
        # For now, apply modulation to TTS output
        # In future, could generate audio, modulate, then play
        # For TTS, we apply modulation through parameters
        
        if modulation_config:
            # Apply modulation through TTS parameters
            if "pitch_shift" in modulation_config:
                # Adjust rate slightly for pitch effect
                current_rate = self.engine.getProperty('rate')
                pitch_adjust = modulation_config["pitch_shift"] * 2  # Semitones to rate adjustment
                self.engine.setProperty('rate', int(current_rate + pitch_adjust))
        
        result = self.speak(text)
        
        # Reset parameters
        if modulation_config:
            params = self.waveform.get_voice_parameters()
            self.engine.setProperty('rate', params['rate'])
        
        return result
    
    def speak_with_waveform(self, text: str, save_audio: bool = False) -> Optional[Path]:
        """Speak and optionally save waveform audio file."""
        if not self.engine:
            self.speak(text)
            return None
        
        # Generate waveform preview (if numpy available)
        if NUMPY_AVAILABLE:
            waveform = self.waveform.generate_waveform(duration=0.5)
            
            if save_audio and SOUNDFILE_AVAILABLE and waveform is not None:
                audio_file = OMEGA_VOICE_DIR / f"omega_voice_{int(time.time())}.wav"
                try:
                    sf.write(str(audio_file), waveform, 44100)
                    return audio_file
                except Exception:
                    pass
        
        # Speak the text
        self.speak(text)
        return None
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get Omega's voice information."""
        return {
            "name": self.config.get("voice_name", "Omega"),
            "personality": self.config.get("personality", "guardian_challenger"),
            "waveform_signature": self.waveform.signature,
            "tts_available": self.engine is not None,
            "created_at": self.config.get("created_at", "unknown")
        }


def main():
    """Test Omega's voice."""
    print("=" * 80)
    print("Ω OMEGA VOICE SYSTEM - Initialization")
    print("=" * 80)
    
    omega_voice = OmegaVoice()
    
    print("\nOmega Voice Configuration:")
    info = omega_voice.get_voice_info()
    for key, value in info.items():
        if key != "waveform_signature":
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("Testing Omega's Voice...")
    print("=" * 80)
    
    test_phrases = [
        "Omega here. Gate guarded.",
        "Code analyzed. Memory updated.",
        "Learning continues. System monitored.",
        "I am Omega. I guard the gate. I break the code. I remember."
    ]
    
    for phrase in test_phrases:
        print(f"\nSpeaking: {phrase}")
        omega_voice.speak(phrase)
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("Ω OMEGA VOICE SYSTEM READY")
    print("=" * 80)
    print("\nOmega's voice is active. The guardian speaks.")


if __name__ == '__main__':
    main()

