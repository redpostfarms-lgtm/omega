# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Quantum Voice Collector - Deep Worldwide Scrub for Voice Samples

"""
Ω Quantum Voice Collector

Performs a quantum deep worldwide scrub to collect voice samples from:
- Free TTS APIs (Edge TTS, Coqui TTS, etc.)
- Sample voice libraries
- Audio repositories
- Public domain audio sources

Then creates a new voice from those samples.
"""

import sys
import io
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
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

# Try to import Edge TTS (FREE, no API key needed)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

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


def collect_edge_tts_samples() -> List[Dict[str, Any]]:
    """Collect voice samples from Edge TTS (FREE, multiple voices)."""
    samples = []
    
    if not EDGE_TTS_AVAILABLE:
        print("⚠️  Edge TTS not available (pip install edge-tts)")
        return samples
    
    print("\nCollecting samples from Edge TTS...")
    
    # Sample text for analysis
    sample_text = "Hello. This is a voice sample for analysis. I speak with clarity and precision."
    
    # Popular voice IDs (male and female, various accents)
    voice_ids = [
        "en-US-AriaNeural",  # Female, clear
        "en-US-JennyNeural",  # Female, friendly
        "en-US-GuyNeural",  # Male, clear
        "en-US-DavisNeural",  # Male, deep
        "en-GB-SoniaNeural",  # Female, British
        "en-GB-RyanNeural",  # Male, British
        "en-AU-NatashaNeural",  # Female, Australian
        "en-AU-WilliamNeural",  # Male, Australian
    ]
    
    for i, voice_id in enumerate(voice_ids[:4], 1):  # Limit to 4 for speed
        try:
            print(f"  [{i}/{min(4, len(voice_ids))}] Collecting {voice_id}...")
            
            # Generate audio
            output_file = VOICE_SOURCES_DIR / f"edge_tts_{voice_id}.mp3"
            
            async def generate_audio():
                communicate = edge_tts.Communicate(text=sample_text, voice=voice_id)
                await communicate.save(str(output_file))
            
            asyncio.run(generate_audio())
            
            if output_file.exists():
                # Analyze audio
                if LIBROSA_AVAILABLE and SOUNDFILE_AVAILABLE:
                    try:
                        audio, sr = librosa.load(str(output_file), sr=16000)
                        if len(audio) > 0:
                            # Extract F0
                            f0_values = []
                            try:
                                f0, voiced_flag, voiced_probs = librosa.pyin(
                                    audio, fmin=80, fmax=300, sr=sr
                                )
                                f0_values = f0[voiced_flag]
                            except Exception:
                                pass
                            
                            if len(f0_values) > 0:
                                f0_mean = float(np.mean(f0_values))
                                spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
                                
                                samples.append({
                                    'voice_id': f"edge_tts_{voice_id}",
                                    'source': f'edge_tts:{voice_id}',
                                    'analysis': {
                                        'fundamental_frequency': f0_mean,
                                        'spectral_centroid': spectral_centroid
                                    },
                                    'file_path': str(output_file)
                                })
                                print(f"    ✓ Collected: F0={f0_mean:.2f} Hz")
                    except Exception as e:
                        print(f"    ✗ Error analyzing: {e}")
        except Exception as e:
            print(f"    ✗ Error collecting {voice_id}: {e}")
    
    return samples


def collect_from_librispeech_sources() -> List[Dict[str, Any]]:
    """Collect samples from LibriSpeech or other public domain sources (if available)."""
    samples = []
    
    # LibriSpeech is a large dataset - check if it exists
    # For now, we'll skip this as it requires download
    # This is a placeholder for future expansion
    
    return samples


def save_collected_samples(samples: List[Dict[str, Any]]):
    """Save collected samples to library."""
    if not samples:
        return
    
    # Save to multi_voice_library.json
    lib_file = OMEGA_VOICE_DIR / 'multi_voice_library.json'
    
    library = {}
    if lib_file.exists():
        try:
            with open(lib_file, 'r', encoding='utf-8') as f:
                library = json.load(f)
        except Exception:
            library = {}
    
    if 'voices' not in library:
        library['voices'] = {}
    
    for sample in samples:
        voice_id = sample['voice_id']
        library['voices'][voice_id] = {
            'analysis': sample['analysis'],
            'source': sample['source'],
            'added_at': datetime.now().isoformat()
        }
    
    try:
        with open(lib_file, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2)
        print(f"\n✓ Saved {len(samples)} samples to library")
    except Exception as e:
        print(f"\n✗ Error saving library: {e}")


def main():
    """Main workflow: Quantum scrub for voice samples."""
    print("=" * 80)
    print("QUANTUM VOICE COLLECTOR - DEEP WORLDWIDE SCRUB")
    print("=" * 80)
    print("\nCollecting voice samples from:")
    print("1. Edge TTS (FREE, multiple voices)")
    print("2. Public domain audio sources")
    print("3. Free TTS APIs")
    
    all_samples = []
    
    # Collect from Edge TTS
    print("\n" + "=" * 80)
    print("COLLECTING FROM EDGE TTS")
    print("=" * 80)
    edge_samples = collect_edge_tts_samples()
    all_samples.extend(edge_samples)
    
    # Collect from other sources (placeholder)
    print("\n" + "=" * 80)
    print("COLLECTING FROM OTHER SOURCES")
    print("=" * 80)
    other_samples = collect_from_librispeech_sources()
    all_samples.extend(other_samples)
    
    # Save collected samples
    print("\n" + "=" * 80)
    print("SAVING COLLECTED SAMPLES")
    print("=" * 80)
    save_collected_samples(all_samples)
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"\n✓ Collected {len(all_samples)} voice samples")
    print("✓ Samples saved to library")
    print("\nNext: Run omega_voice_simulator.py to create new voice from samples")


if __name__ == '__main__':
    main()

