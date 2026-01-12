# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Simulator - Run Simulations on Voice & Create New Voice from Quantum Scrub Samples

"""
Ω Omega Voice Simulator

Runs simulations on Omega's voice using samples from quantum deep worldwide scrub.
Creates a completely new voice signature based on collected samples.
"""

import sys
import io
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Set UTF-8 encoding
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


def load_current_voice() -> Dict[str, Any]:
    """Load current voice signature."""
    signature_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
    if signature_file.exists():
        try:
            with open(signature_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_collected_samples() -> List[Dict[str, Any]]:
    """Load all collected voice samples from quantum scrub."""
    samples = []
    
    # Check multi_voice_library.json
    lib_file = OMEGA_VOICE_DIR / 'multi_voice_library.json'
    if lib_file.exists():
        try:
            with open(lib_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    voices = data.get('voices', {})
                    for voice_id, voice_data in voices.items():
                        if isinstance(voice_data, dict):
                            analysis = voice_data.get('analysis', {})
                            if analysis:
                                samples.append({
                                    'voice_id': voice_id,
                                    'source': voice_data.get('source', 'unknown'),
                                    'analysis': analysis,
                                    'type': 'multi_voice_library'
                                })
        except Exception as e:
            print(f"Error loading multi_voice_library: {e}")
    
    # Check waveform_library.json
    waveform_file = OMEGA_VOICE_DIR / 'waveform_library.json'
    if waveform_file.exists():
        try:
            with open(waveform_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    waveforms = data.get('waveforms', [])
                    for waveform in waveforms:
                        if isinstance(waveform, dict) and waveform.get('analysis'):
                            samples.append({
                                'voice_id': waveform.get('id', f"waveform_{len(samples)}"),
                                'source': waveform.get('source', 'waveform_library'),
                                'analysis': waveform.get('analysis', {}),
                                'type': 'waveform_library'
                            })
        except Exception as e:
            print(f"Error loading waveform_library: {e}")
    
    # Check voice_sources directory for audio files
    if VOICE_SOURCES_DIR.exists():
        for audio_file in VOICE_SOURCES_DIR.glob('*.wav'):
            try:
                if LIBROSA_AVAILABLE and NUMPY_AVAILABLE:
                    audio, sr = librosa.load(str(audio_file), sr=16000)
                    if len(audio) > 0:
                        # Basic analysis
                        f0_values = []
                        if LIBROSA_AVAILABLE:
                            f0, voiced_flag, voiced_probs = librosa.pyin(
                                audio, fmin=80, fmax=300, sr=sr
                            )
                            f0_values = f0[voiced_flag]
                        
                        if len(f0_values) > 0:
                            f0_mean = float(np.mean(f0_values))
                            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
                            
                            samples.append({
                                'voice_id': audio_file.stem,
                                'source': f'file:{audio_file.name}',
                                'analysis': {
                                    'fundamental_frequency': f0_mean,
                                    'spectral_centroid': spectral_centroid
                                },
                                'type': 'audio_file',
                                'file_path': str(audio_file)
                            })
            except Exception as e:
                print(f"Error analyzing {audio_file.name}: {e}")
    
    return samples


def simulate_voice_variations(base_signature: Dict[str, Any], samples: List[Dict[str, Any]], num_simulations: int = 10) -> List[Dict[str, Any]]:
    """Run simulations creating voice variations from collected samples."""
    simulations = []
    
    if not samples:
        print("⚠️  No samples found - using base signature variations")
        for i in range(num_simulations):
            sim = base_signature.copy()
            sim['simulation_id'] = f"sim_{i+1}"
            sim['base_frequency'] = base_signature.get('base_frequency', 135.0) + random.uniform(-5, 5)
            simulations.append(sim)
        return simulations
    
    print(f"\nRunning {num_simulations} voice simulations using {len(samples)} collected samples...")
    
    for i in range(num_simulations):
        # Randomly select samples to blend
        num_samples_to_blend = min(random.randint(2, 5), len(samples))
        selected_samples = random.sample(samples, num_samples_to_blend)
        
        # Extract voice characteristics
        f0_values = []
        spectral_centroids = []
        formants_list = []
        
        for sample in selected_samples:
            analysis = sample.get('analysis', {})
            f0 = analysis.get('fundamental_frequency', 0)
            if f0 > 0:
                f0_values.append(f0)
            
            sc = analysis.get('spectral_centroid', 0)
            if sc > 0:
                spectral_centroids.append(sc)
            
            formants = analysis.get('formants', [])
            if formants:
                formants_list.extend(formants)
        
        # Calculate weighted averages
        if f0_values:
            new_f0 = sum(f0_values) / len(f0_values)
        else:
            new_f0 = base_signature.get('base_frequency', 135.0)
        
        if spectral_centroids:
            new_spectral = sum(spectral_centroids) / len(spectral_centroids)
        else:
            new_spectral = base_signature.get('resonance_peak', 2300.0)
        
        # Create simulation signature
        sim_signature = {
            'simulation_id': f"sim_{i+1}",
            'base_frequency': max(100.0, min(180.0, new_f0)),
            'resonance_peak': max(1800.0, min(2800.0, new_spectral)),
            'modulation_depth': random.uniform(0.10, 0.18),
            'modulation_rate': random.uniform(2.2, 3.0),
            'harmonic_ratio': random.uniform(0.25, 0.40),
            'prosody_variation': random.uniform(0.12, 0.18),
            'attack_time': random.uniform(0.015, 0.035),
            'decay_time': random.uniform(0.08, 0.15),
            'sustain_level': random.uniform(0.65, 0.85),
            'release_time': random.uniform(0.10, 0.18),
            'samples_used': [s['voice_id'] for s in selected_samples],
            'num_samples': len(selected_samples),
            'created_at': datetime.now().isoformat()
        }
        
        simulations.append(sim_signature)
    
    return simulations


def create_new_voice_from_samples(samples: List[Dict[str, Any]], base_signature: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a completely new voice signature from collected samples."""
    print("\n" + "=" * 80)
    print("CREATING NEW VOICE FROM QUANTUM SCRUB SAMPLES")
    print("=" * 80)
    
    if not samples:
        print("⚠️  No samples found - creating default new voice")
        return {
            'base_frequency': 140.0,
            'modulation_depth': 0.145,
            'modulation_rate': 2.6,
            'harmonic_ratio': 0.32,
            'resonance_peak': 2350.0,
            'prosody_variation': 0.14,
            'attack_time': 0.025,
            'decay_time': 0.12,
            'sustain_level': 0.75,
            'release_time': 0.14,
            'created_at': datetime.now().isoformat(),
            'source': 'default_new'
        }
    
    print(f"\nAnalyzing {len(samples)} collected samples...")
    
    # Aggregate all voice characteristics
    all_f0 = []
    all_spectral = []
    all_formants = []
    
    for sample in samples:
        analysis = sample.get('analysis', {})
        f0 = analysis.get('fundamental_frequency', 0)
        if f0 > 0 and 80 <= f0 <= 300:  # Valid voice range
            all_f0.append(f0)
        
        sc = analysis.get('spectral_centroid', 0)
        if sc > 0:
            all_spectral.append(sc)
        
        formants = analysis.get('formants', [])
        if formants:
            all_formants.extend([f for f in formants if 200 <= f <= 4000])
    
    # Calculate new voice parameters
    if all_f0:
        new_f0 = sum(all_f0) / len(all_f0)
        print(f"  Average F0: {new_f0:.2f} Hz (from {len(all_f0)} samples)")
    else:
        new_f0 = 140.0
        print(f"  Using default F0: {new_f0:.2f} Hz")
    
    if all_spectral:
        new_spectral = sum(all_spectral) / len(all_spectral)
        print(f"  Average Spectral Centroid: {new_spectral:.1f} Hz (from {len(all_spectral)} samples)")
    else:
        new_spectral = 2350.0
        print(f"  Using default Spectral Centroid: {new_spectral:.1f} Hz")
    
    # Create new voice signature (completely new, not based on old)
    new_voice = {
        'base_frequency': max(120.0, min(160.0, new_f0)),
        'modulation_depth': 0.145,  # Natural modulation
        'modulation_rate': 2.6,  # Natural rhythm
        'harmonic_ratio': 0.32,  # Rich harmonics
        'resonance_peak': max(2100.0, min(2500.0, new_spectral)),
        'prosody_variation': 0.14,  # Natural prosody
        'attack_time': 0.025,  # Smooth attack
        'decay_time': 0.12,  # Natural decay
        'sustain_level': 0.75,  # Good sustain
        'release_time': 0.14,  # Smooth release
        'created_at': datetime.now().isoformat(),
        'source': 'quantum_scrub_samples',
        'num_samples_used': len(samples),
        'sample_ids': [s['voice_id'] for s in samples[:10]],  # First 10 IDs
        'version': '2.0',  # New version
        'previous_voice_replaced': True
    }
    
    print(f"\n✓ New voice created from {len(samples)} samples")
    print(f"  Base Frequency: {new_voice['base_frequency']:.2f} Hz")
    print(f"  Resonance Peak: {new_voice['resonance_peak']:.1f} Hz")
    print(f"  Harmonic Ratio: {new_voice['harmonic_ratio']:.3f}")
    
    return new_voice


def save_new_voice(new_voice: Dict[str, Any], filename: str = 'omega_new_voice.json'):
    """Save new voice signature."""
    output_file = OMEGA_VOICE_DIR / filename
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_voice, f, indent=2)
        print(f"\n✓ New voice saved to: {output_file.name}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving voice: {e}")
        return False


def main():
    """Main workflow: Run simulations and create new voice."""
    print("=" * 80)
    print("OMEGA VOICE SIMULATOR")
    print("=" * 80)
    print("\nThis will:")
    print("1. Load collected samples from quantum scrub")
    print("2. Run voice simulations")
    print("3. Create completely new voice from samples")
    print("4. Save new voice signature")
    
    # Load current voice (for reference, but we're replacing it)
    current_voice = load_current_voice()
    if current_voice:
        print(f"\n⚠️  Current voice found (will be replaced)")
        print(f"  Current F0: {current_voice.get('base_frequency', 135.0):.2f} Hz")
    
    # Load collected samples
    print("\n" + "=" * 80)
    print("LOADING QUANTUM SCRUB SAMPLES")
    print("=" * 80)
    samples = load_collected_samples()
    print(f"\n✓ Found {len(samples)} collected voice samples")
    
    if samples:
        print("\nSample sources:")
        for i, sample in enumerate(samples[:10], 1):  # Show first 10
            print(f"  {i}. {sample['voice_id']} ({sample['source']})")
        if len(samples) > 10:
            print(f"  ... and {len(samples) - 10} more")
    
    # Run simulations
    print("\n" + "=" * 80)
    print("RUNNING VOICE SIMULATIONS")
    print("=" * 80)
    simulations = simulate_voice_variations(current_voice, samples, num_simulations=10)
    print(f"\n✓ Generated {len(simulations)} voice simulations")
    
    # Create new voice from samples
    print("\n" + "=" * 80)
    print("CREATING NEW VOICE")
    print("=" * 80)
    new_voice = create_new_voice_from_samples(samples, current_voice)
    
    # Save new voice
    print("\n" + "=" * 80)
    print("SAVING NEW VOICE")
    print("=" * 80)
    
    # Save as new voice
    save_new_voice(new_voice, 'omega_new_voice.json')
    
    # Also replace the improved waveform (since current is unacceptable)
    save_new_voice(new_voice, 'omega_improved_waveform.json')
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\n✓ New voice created from quantum scrub samples")
    print("✓ Voice signature saved")
    print("✓ Previous voice replaced")
    print("\nOmega will use this new voice on next initialization.")


if __name__ == '__main__':
    main()

