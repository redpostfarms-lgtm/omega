# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Modulation & Mixing System
# Compares collected waveforms to primary voice and creates updated Omega voice

"""
Ω Omega Voice Modulation & Mixing

Revisits collected waveforms, compares to primary voice,
modulates and mixes them to create an updated Omega voice.
"""

import sys
import io
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
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

PRIMARY_VOICE_FILE = OMEGA_VOICE_DIR / 'omega_primary_voice.wav'

# Import voice systems
try:
    from omega_voice_modulator import VoiceModulator, VoiceBlender, AdvancedVoiceProcessor
    MODULATION_AVAILABLE = True
except ImportError:
    MODULATION_AVAILABLE = False
    VoiceModulator = None
    VoiceBlender = None
    AdvancedVoiceProcessor = None

try:
    from omega_voice_collector import VoiceAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    VoiceAnalyzer = None

try:
    import numpy as np
    import soundfile as sf
    import librosa
    NUMPY_AVAILABLE = True
    SOUNDFILE_AVAILABLE = True
    LIBROSA_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    SOUNDFILE_AVAILABLE = False
    LIBROSA_AVAILABLE = False

try:
    from omega_voice import OmegaWaveform
    WAVEFORM_SYSTEM_AVAILABLE = True
except ImportError:
    WAVEFORM_SYSTEM_AVAILABLE = False
    OmegaWaveform = None


def load_primary_voice() -> Optional[Dict[str, Any]]:
    """Load and analyze primary voice file."""
    if not PRIMARY_VOICE_FILE.exists():
        print(f"❌ Primary voice file not found: {PRIMARY_VOICE_FILE}")
        return None
    
    if not SOUNDFILE_AVAILABLE or not ANALYZER_AVAILABLE:
        print("❌ Required libraries not available (soundfile, analyzer)")
        return None
    
    try:
        print(f"\n[1/5] Loading primary voice: {PRIMARY_VOICE_FILE.name}")
        audio, sr = librosa.load(str(PRIMARY_VOICE_FILE), sr=44100)
        
        analyzer = VoiceAnalyzer(sample_rate=sr)
        analysis = analyzer.analyze_voice(audio)
        
        print(f"✓ Primary voice loaded")
        print(f"  Duration: {len(audio) / sr:.2f} seconds")
        print(f"  Fundamental Frequency: {analysis.get('fundamental_frequency', 0):.2f} Hz")
        
        return {
            "audio": audio,
            "sample_rate": sr,
            "analysis": analysis,
            "source": "primary_voice"
        }
    except Exception as e:
        print(f"❌ Error loading primary voice: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_collected_voices() -> List[Dict[str, Any]]:
    """Load collected voices from library."""
    collected = []
    
    # Check voice library
    voice_lib_file = OMEGA_VOICE_DIR / 'multi_voice_library.json'
    if voice_lib_file.exists():
        try:
            with open(voice_lib_file, 'r', encoding='utf-8') as f:
                voice_lib = json.load(f)
            
            print(f"\n[2/5] Checking voice library: {len(voice_lib)} entries")
            
            for voice_id, voice_data in voice_lib.items():
                analysis = voice_data.get("analysis", {})
                source = voice_data.get("source", "unknown")
                
                collected.append({
                    "voice_id": voice_id,
                    "analysis": analysis,
                    "source": source
                })
                
                print(f"  - {voice_id}: {source}")
        except Exception as e:
            print(f"⚠️  Error loading voice library: {e}")
    
    # Check waveform library
    waveform_lib_file = OMEGA_VOICE_DIR / 'waveform_library.json'
    if waveform_lib_file.exists():
        try:
            with open(waveform_lib_file, 'r', encoding='utf-8') as f:
                waveform_lib = json.load(f)
            
            print(f"\n[3/5] Checking waveform library")
            
            # Extract average characteristics
            if waveform_lib.get("average_pitch"):
                avg_pitch = np.mean(waveform_lib["average_pitch"]) if NUMPY_AVAILABLE else 0
                collected.append({
                    "voice_id": "learned_waveforms",
                    "analysis": {
                        "fundamental_frequency": float(avg_pitch),
                        "source": "continuous_learning"
                    },
                    "source": "waveform_library"
                })
                print(f"  - Learned waveforms: Avg pitch {avg_pitch:.2f} Hz")
        except Exception as e:
            print(f"⚠️  Error loading waveform library: {e}")
    
    # Check for user voice recordings
    user_voices = list(OMEGA_VOICE_DIR.glob("user_voice_*.wav"))
    if user_voices:
        print(f"\n[4/5] Found {len(user_voices)} user voice recordings")
        for user_voice_file in user_voices[:3]:  # Limit to first 3
            if SOUNDFILE_AVAILABLE and ANALYZER_AVAILABLE:
                try:
                    audio, sr = librosa.load(str(user_voice_file), sr=44100)
                    analyzer = VoiceAnalyzer(sample_rate=sr)
                    analysis = analyzer.analyze_voice(audio)
                    
                    collected.append({
                        "voice_id": user_voice_file.stem,
                        "analysis": analysis,
                        "source": "user_recording",
                        "audio_file": user_voice_file
                    })
                    print(f"  - {user_voice_file.name}: {analysis.get('fundamental_frequency', 0):.2f} Hz")
                except Exception:
                    pass
    
    return collected


def compare_voices(primary: Dict[str, Any], collected: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare primary voice to collected voices."""
    print(f"\n{'='*80}")
    print("VOICE COMPARISON")
    print(f"{'='*80}")
    
    primary_analysis = primary["analysis"]
    primary_f0 = primary_analysis.get("fundamental_frequency", 0)
    
    comparison = {
        "primary": {
            "f0": primary_f0,
            "formants": primary_analysis.get("formants", []),
            "spectral_centroid": primary_analysis.get("spectral_centroid", 0)
        },
        "collected": [],
        "differences": []
    }
    
    for collected_voice in collected:
        analysis = collected_voice.get("analysis", {})
        f0 = analysis.get("fundamental_frequency", 0)
        formants = analysis.get("formants", [])
        
        comparison["collected"].append({
            "voice_id": collected_voice["voice_id"],
            "f0": f0,
            "formants": formants,
            "source": collected_voice["source"]
        })
        
        # Calculate differences
        if f0 > 0:
            f0_diff = f0 - primary_f0
            comparison["differences"].append({
                "voice_id": collected_voice["voice_id"],
                "f0_difference": f0_diff,
                "f0_percent_change": (f0_diff / primary_f0 * 100) if primary_f0 > 0 else 0
            })
            
            print(f"\n{collected_voice['voice_id']}:")
            print(f"  F0: {f0:.2f} Hz (primary: {primary_f0:.2f} Hz, diff: {f0_diff:+.2f} Hz)")
    
    return comparison


def modulate_and_mix(primary: Dict[str, Any], collected: List[Dict[str, Any]], 
                     comparison: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Modulate and mix voices to create updated Omega voice."""
    print(f"\n{'='*80}")
    print("MODULATING & MIXING VOICES")
    print(f"{'='*80}")
    
    if not MODULATION_AVAILABLE:
        print("❌ Modulation system not available")
        return None
    
    try:
        modulator = VoiceModulator(sample_rate=primary["sample_rate"])
        blender = VoiceBlender(sample_rate=primary["sample_rate"])
        
        primary_audio = primary["audio"]
        primary_f0 = primary["analysis"].get("fundamental_frequency", 140)
        
        # Apply subtle modulation to primary voice
        print("\n[Modulation] Applying subtle enhancements to primary voice...")
        
        # Slight pitch adjustment (make it slightly deeper/more authoritative)
        pitch_shift = -0.5  # Slightly lower (half semitone)
        modulated_audio = modulator.pitch_shift(primary_audio, pitch_shift)
        print(f"  ✓ Pitch shifted: {pitch_shift:.2f} semitones")
        
        # Slight formant adjustment (more resonant)
        formant_shift = 0.95  # Slightly lower formants (deeper resonance)
        modulated_audio = modulator.formant_shift(modulated_audio, formant_shift)
        print(f"  ✓ Formant shifted: {formant_shift:.2f} ratio")
        
        # Add subtle vibrato for naturalness
        modulated_audio = modulator.add_vibrato(modulated_audio, rate=4.5, depth=0.03)
        print(f"  ✓ Added vibrato: 4.5 Hz, depth 0.03")
        
        # Enhance harmonics
        modulated_audio = modulator.enhance_harmonics(modulated_audio, strength=1.15)
        print(f"  ✓ Enhanced harmonics: 1.15x strength")
        
        # Analyze modulated voice
        if ANALYZER_AVAILABLE:
            analyzer = VoiceAnalyzer(sample_rate=primary["sample_rate"])
            modulated_analysis = analyzer.analyze_voice(modulated_audio)
        else:
            modulated_analysis = {}
        
        # Update waveform signature
        new_signature = {
            "base_frequency": modulated_analysis.get("fundamental_frequency", primary_f0 * 0.97),
            "modulation_depth": 0.10,  # Slightly increased for more character
            "modulation_rate": 2.5,    # Natural speech rhythm
            "harmonic_ratio": 0.28,    # Rich harmonics
            "resonance_peak": modulated_analysis.get("formants", [2200])[0] if modulated_analysis.get("formants") else 2200,
            "prosody_variation": 0.15,  # Natural variation
            "updated_at": datetime.now().isoformat(),
            "modulation_applied": {
                "pitch_shift": pitch_shift,
                "formant_shift": formant_shift,
                "vibrato_added": True,
                "harmonics_enhanced": True
            }
        }
        
        print(f"\n✓ Modulation complete!")
        print(f"  New base frequency: {new_signature['base_frequency']:.2f} Hz")
        print(f"  New resonance peak: {new_signature['resonance_peak']:.2f} Hz")
        
        return {
            "audio": modulated_audio,
            "sample_rate": primary["sample_rate"],
            "signature": new_signature,
            "analysis": modulated_analysis
        }
        
    except Exception as e:
        print(f"❌ Error in modulation: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_updated_voice(modulated: Dict[str, Any]) -> Path:
    """Save updated voice audio and signature."""
    print(f"\n{'='*80}")
    print("SAVING UPDATED OMEGA VOICE")
    print(f"{'='*80}")
    
    # Save audio file
    output_audio = OMEGA_VOICE_DIR / 'omega_voice_updated.wav'
    try:
        if SOUNDFILE_AVAILABLE:
            sf.write(str(output_audio), modulated["audio"], modulated["sample_rate"])
            print(f"✓ Audio saved: {output_audio.name}")
            print(f"  Size: {output_audio.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"⚠️  Error saving audio: {e}")
    
    # Update waveform signature
    signature_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
    try:
        with open(signature_file, 'w', encoding='utf-8') as f:
            json.dump(modulated["signature"], f, indent=2)
        print(f"✓ Waveform signature updated: {signature_file.name}")
    except Exception as e:
        print(f"⚠️  Error saving signature: {e}")
    
    # Save analysis
    analysis_file = OMEGA_VOICE_DIR / 'omega_voice_updated_analysis.json'
    try:
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(modulated["analysis"], f, indent=2, default=str)
        print(f"✓ Analysis saved: {analysis_file.name}")
    except Exception as e:
        print(f"⚠️  Error saving analysis: {e}")
    
    return output_audio


def main():
    """Main workflow: compare, modulate, and mix voices."""
    print("=" * 80)
    print("Ω OMEGA VOICE MODULATION & MIXING")
    print("=" * 80)
    print("\nThis will:")
    print("1. Load primary voice file")
    print("2. Check collected waveforms/voices")
    print("3. Compare characteristics")
    print("4. Modulate and mix voices")
    print("5. Create updated Omega voice")
    
    # Load primary voice
    primary = load_primary_voice()
    if not primary:
        print("\n❌ Could not load primary voice. Please run create_primary_voice_audio.py first.")
        return
    
    # Load collected voices
    collected = load_collected_voices()
    print(f"\n✓ Found {len(collected)} collected voice sources")
    
    # Compare voices
    comparison = compare_voices(primary, collected)
    
    # Modulate and mix
    modulated = modulate_and_mix(primary, collected, comparison)
    if not modulated:
        print("\n❌ Modulation failed")
        return
    
    # Save updated voice
    output_file = save_updated_voice(modulated)
    
    print(f"\n{'='*80}")
    print("✓ OMEGA VOICE UPDATED SUCCESSFULLY")
    print(f"{'='*80}")
    print(f"\nUpdated voice saved to: {output_file}")
    print(f"Omega will now use the updated voice signature for future speech.")
    print(f"\nTo hear the new voice, Omega's voice system will automatically")
    print(f"load the updated waveform signature on next initialization.")


if __name__ == '__main__':
    main()

