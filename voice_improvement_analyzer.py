#!/usr/bin/env python3
# Voice Improvement Analyzer - Analyzes voices to improve TTS quality
import librosa
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
from scipy import signal

def analyze_voice_sample(audio_path):
    """Comprehensive voice analysis."""
    print(f"\n[Analyzing] {Path(audio_path).name}")
    
    audio, sr = librosa.load(str(audio_path), sr=16000)
    
    # Fundamental frequency (pitch)
    pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
    pitch_values = pitches[pitches > 0]
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
    zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
    
    # MFCCs (voice characteristics)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    
    # Chroma features (harmonic content)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    
    # Tempo/rhythm
    tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
    
    # Harmonic and percussive separation
    harmonic, percussive = librosa.effects.hpss(audio)
    
    analysis = {
        'file': str(audio_path),
        'duration': len(audio) / sr,
        'sample_rate': sr,
        'pitch': {
            'mean': float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0,
            'std': float(np.std(pitch_values)) if len(pitch_values) > 0 else 0,
            'min': float(np.min(pitch_values)) if len(pitch_values) > 0 else 0,
            'max': float(np.max(pitch_values)) if len(pitch_values) > 0 else 0,
        },
        'spectral': {
            'centroid_mean': float(np.mean(spectral_centroids)),
            'centroid_std': float(np.std(spectral_centroids)),
            'rolloff_mean': float(np.mean(spectral_rolloff)),
            'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
        },
        'mfccs_mean': [float(x) for x in np.mean(mfccs, axis=1)],
        'chroma_mean': [float(x) for x in np.mean(chroma, axis=1)],
        'tempo': float(tempo),
        'energy': {
            'total': float(np.sum(audio**2)),
            'rms_mean': float(np.mean(librosa.feature.rms(y=audio)[0])),
        },
        'harmonic_ratio': float(np.sum(harmonic**2) / (np.sum(audio**2) + 1e-10)),
    }
    
    return analysis, audio, sr

def compare_multiple_voices(voice_paths):
    """Compare multiple voice samples to find optimal characteristics."""
    print("\n" + "=" * 60)
    print("  VOICE COMPARISON ANALYSIS")
    print("=" * 60)
    
    all_analyses = []
    for path in voice_paths:
        if Path(path).exists():
            analysis, _, _ = analyze_voice_sample(path)
            all_analyses.append(analysis)
            print(f"\n{Path(path).name}:")
            print(f"  Pitch: {analysis['pitch']['mean']:.2f} Hz (±{analysis['pitch']['std']:.2f})")
            print(f"  Spectral Centroid: {analysis['spectral']['centroid_mean']:.2f}")
            print(f"  Tempo: {analysis['tempo']:.2f} BPM")
            print(f"  Harmonic Ratio: {analysis['harmonic_ratio']:.4f}")
    
    if len(all_analyses) > 1:
        # Calculate averages for optimal voice characteristics
        avg_pitch = np.mean([a['pitch']['mean'] for a in all_analyses])
        avg_centroid = np.mean([a['spectral']['centroid_mean'] for a in all_analyses])
        avg_mfccs = np.mean([np.array(a['mfccs_mean']) for a in all_analyses], axis=0)
        
        print("\n" + "=" * 60)
        print("  OPTIMAL VOICE CHARACTERISTICS")
        print("=" * 60)
        print(f"  Average Pitch: {avg_pitch:.2f} Hz")
        print(f"  Average Spectral Centroid: {avg_centroid:.2f}")
        print(f"  Average MFCCs: {avg_mfccs.tolist()}")
        
        return {
            'optimal_pitch': float(avg_pitch),
            'optimal_spectral_centroid': float(avg_centroid),
            'optimal_mfccs': avg_mfccs.tolist(),
            'voice_count': len(all_analyses)
        }
    
    return None

def find_audio_resources():
    """Search for and list free audio resources."""
    resources = {
        'sound_effects': [
            'Freesound.org - https://freesound.org (CC0/CC-BY licensed)',
            'Zapsplat - https://www.zapsplat.com (Free with attribution)',
            'BBC Sound Effects Library - https://sound-effects.bbcrewind.co.uk',
            'OpenGameArt - https://opengameart.org/content/sound-effects',
            'Incompetech - https://incompetech.com/music/royalty-free',
        ],
        'voice_samples': [
            'Common Voice (Mozilla) - https://commonvoice.mozilla.org',
            'LibriSpeech - https://www.openslr.org/12/',
            'VoxCeleb - https://www.robots.ox.ac.uk/~vgg/data/voxceleb/',
            'TED-LIUM - http://www.openslr.org/7/',
            'LJSpeech - https://keithito.com/LJ-Speech-Dataset/',
        ],
        'music_background': [
            'Free Music Archive - https://freemusicarchive.org',
            'Incompetech - https://incompetech.com',
            'Purple Planet - https://www.purple-planet.com',
            'YouTube Audio Library - https://www.youtube.com/audiolibrary',
        ]
    }
    
    return resources

if __name__ == "__main__":
    print("=" * 60)
    print("  VOICE IMPROVEMENT ANALYZER")
    print("=" * 60)
    
    # Find free audio resources
    print("\n[FREE AUDIO RESOURCES]")
    resources = find_audio_resources()
    for category, items in resources.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")
    
    # Analyze existing voice samples
    print("\n" + "=" * 60)
    print("  ANALYZING YOUR VOICE SAMPLES")
    print("=" * 60)
    
    voice_samples = [
        Path('clip_0001.wav'),
        Path('conversations') / 'conversation_*.wav',
    ]
    
    # Find all conversation files
    conversation_files = list(Path('conversations').glob('*.wav')) if Path('conversations').exists() else []
    all_voices = [Path('clip_0001.wav')] + conversation_files if Path('clip_0001.wav').exists() else conversation_files
    
    if all_voices:
        compare_multiple_voices(all_voices)
    else:
        print("\n[INFO] No voice samples found yet.")
        print("Run conversation_recorder.py to record samples first.")
