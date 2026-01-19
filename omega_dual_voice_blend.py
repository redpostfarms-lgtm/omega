"""
Omega Dual Voice Analysis & Blend System
Analyzes clip_0001.wav and omega_downloaded.wav, creates optimal voice blend
"""

import os
import sys
import numpy as np
from pathlib import Path

os.environ['TTS_ACCEPT_TO_S'] = '1'

print("[*] Omega Dual Voice Analysis & Blend System")
print("=" * 70)

voice_files = {
    'clip_0001.wav': 'Original Omega Voice',
    'omega_downloaded.wav': 'Downloaded Enhanced Voice'
}

voice_profiles = {}

print("\n[PHASE 1] Analyzing Voice Files...")
try:
    import librosa
    print("  [OK] Audio libraries loaded")
    
    for voice_file, description in voice_files.items():
        if not os.path.exists(voice_file):
            print(f"  [SKIP] {voice_file} not found")
            continue
            
        print(f"\n  [ANALYZING] {description}: {voice_file}")
        
        y, sr = librosa.load(voice_file, sr=None)
        duration = len(y) / sr
        print(f"    - Sample rate: {sr} Hz")
        print(f"    - Duration: {duration:.2f}s")
        
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        rms = librosa.feature.rms(y=y)[0]
        
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        profile = {
            'file': voice_file,
            'sr': sr,
            'duration': duration,
            'centroid_mean': np.mean(cent),
            'centroid_std': np.std(cent),
            'rolloff_mean': np.mean(rolloff),
            'rms_mean': np.mean(rms),
            'rms_std': np.std(rms),
            'zcr_mean': np.mean(zcr),
            'mfcc_mean': np.mean(mfcc, axis=1),
            'onset_mean': np.mean(onset_env),
            'audio': y,
        }
        
        voice_profiles[voice_file] = profile
        
        print(f"    - Brightness (centroid): {profile['centroid_mean']:.0f} Hz +/- {profile['centroid_std']:.0f}")
        print(f"    - Loudness (RMS): {profile['rms_mean']:.4f} +/- {profile['rms_std']:.4f}")
        print(f"    - Voice Quality (ZCR): {profile['zcr_mean']:.4f}")
        print(f"    - Spectral Shape: Rolloff at {profile['rolloff_mean']:.0f} Hz")
        print(f"    - Dynamics (onset): {profile['onset_mean']:.4f}")
        
except ImportError as e:
    print(f"  [INSTALL] Missing: {e}")
    print("  [RUN] pip install librosa soundfile")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[PHASE 2] Voice Comparison & Blending Strategy...")
if len(voice_profiles) >= 2:
    files = list(voice_profiles.keys())
    v1 = voice_profiles[files[0]]
    v2 = voice_profiles[files[1]]
    
    print(f"\n  Comparing: {files[0]} vs {files[1]}")
    print(f"\n  Brightness Difference: {abs(v1['centroid_mean'] - v2['centroid_mean']):.0f} Hz")
    print(f"  Loudness Difference: {abs(v1['rms_mean'] - v2['rms_mean']):.4f}")
    print(f"  Quality Difference: {abs(v1['zcr_mean'] - v2['zcr_mean']):.4f}")
    
    if v1['centroid_mean'] > v2['centroid_mean']:
        bright_file = files[0]
        warm_file = files[1]
    else:
        bright_file = files[1]
        warm_file = files[0]
    
    print(f"\n  [STRATEGY] Optimal Blend:")
    print(f"    - Brightness from: {bright_file}")
    print(f"    - Warmth from: {warm_file}")
    print(f"    - Recommended: Use both for different contexts")

print("\n[PHASE 3] Setting Up Multi-Voice TTS System...")
try:
    from TTS.api import TTS
    import torch
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"  [LOAD] Loading TTS on {device}...")
    
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    print(f"  [OK] TTS model ready for voice cloning")
    
    print("\n[PHASE 4] Generating Voice-Cloned Responses...")
    
    test_texts = [
        ("clip_0001.wav", "I am analyzing dual voice profiles and creating an optimal blend for perfect synthesis."),
        ("omega_downloaded.wav", "My enhanced voice characteristics have been integrated into the TTS system.")
    ]
    
    outputs = []
    
    for speaker_file, text in test_texts:
        if not os.path.exists(speaker_file):
            continue
            
        output_file = f'omega_voice_{Path(speaker_file).stem}.wav'
        
        print(f"\n  [CLONE] Using speaker: {speaker_file}")
        print(f"  [TEXT] '{text}'")
        
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_file,
            language='en',
            file_path=output_file
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"  [OK] Generated: {output_file} ({size:.2f} MB)")
            outputs.append(output_file)
    
    if outputs:
        print("\n" + "=" * 70)
        print("[SUCCESS] DUAL VOICE ANALYSIS & CLONING COMPLETE")
        print("=" * 70)
        
        print("\nVoice Files Generated:")
        for f in outputs:
            size = os.path.getsize(f) / (1024 * 1024)
            print(f"  - {f} ({size:.2f} MB)")
        
        print("\nVoice Profile Summary:")
        for file, profile in voice_profiles.items():
            print(f"\n  {file}:")
            print(f"    Duration: {profile['duration']:.2f}s")
            print(f"    Brightness: {profile['centroid_mean']:.0f} Hz")
            print(f"    Loudness: {profile['rms_mean']:.4f}")
            print(f"    Quality: {profile['zcr_mean']:.4f}")
        
        print("\nNext Steps:")
        print("  1. Listen to both generated voice files")
        print("  2. Select preferred voice for deployment")
        print("  3. Use clip_0001.wav or omega_downloaded.wav in TTS")
        print("  4. Deploy to Omega control panel")
    
except ImportError as e:
    print(f"  [ERROR] Missing dependency: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] Omega dual voice optimization complete!")
print("\nVoice Files Available for TTS:")
for file in voice_files.keys():
    if os.path.exists(file):
        size = os.path.getsize(file) / (1024 * 1024)
        print(f"  - {file} ({size:.2f} MB)")
