"""
Omega Voice Analysis Without TTS Generation
Tests voice file loading and analysis without requiring FFmpeg
"""

import os
import sys
import json
from pathlib import Path

print("[*] Omega Voice Analysis System (FFmpeg-Free)")
print("=" * 70)

voice_files = {
    'clip_0001.wav': 'Original Omega Voice',
    'omega_downloaded.wav': 'Enhanced Voice'
}

voice_profiles = {}

print("\n[PHASE 1] Voice File Analysis")
print("-" * 70)

try:
    import librosa
    import numpy as np
    print("✓ Audio analysis libraries loaded")
    
    for voice_file, description in voice_files.items():
        if not os.path.exists(voice_file):
            print(f"✗ {voice_file} not found")
            continue
        
        print(f"\n  Analyzing: {description} ({voice_file})")
        
        y, sr = librosa.load(voice_file, sr=None)
        duration = len(y) / sr
        print(f"    • Sample rate: {sr:,} Hz")
        print(f"    • Duration: {duration:.2f} seconds")
        
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        rms = librosa.feature.rms(y=y)[0]
        
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        voice_profiles[voice_file] = {
            'sr': sr,
            'duration': float(duration),
            'centroid_mean': float(np.mean(centroid)),
            'centroid_std': float(np.std(centroid)),
            'rolloff_mean': float(np.mean(rolloff)),
            'rms_mean': float(np.mean(rms)),
            'rms_std': float(np.std(rms)),
            'zcr_mean': float(np.mean(zcr)),
            'zcr_std': float(np.std(zcr)),
            'mfcc_mean': float(np.mean(mfcc)),
            'onset_strength_mean': float(np.mean(onset_env)),
        }
        
        print(f"    • Brightness (Spectral Centroid): {voice_profiles[voice_file]['centroid_mean']:.0f} Hz")
        print(f"    • Energy (RMS): {voice_profiles[voice_file]['rms_mean']:.4f}")
        print(f"    • Voice Quality (ZCR): {voice_profiles[voice_file]['zcr_mean']:.4f}")
        print(f"    • Spectral Shape (Rolloff): {voice_profiles[voice_file]['rolloff_mean']:.0f} Hz")
        print(f"    • Dynamics (Onset): {voice_profiles[voice_file]['onset_strength_mean']:.4f}")
        
except Exception as e:
    print(f"\n✗ Error during voice analysis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n\n[PHASE 2] Voice Profile Comparison")
print("-" * 70)

if len(voice_profiles) == 2:
    files = list(voice_profiles.keys())
    profile_0 = voice_profiles[files[0]]
    profile_1 = voice_profiles[files[1]]
    
    print(f"\nComparing: {files[0]} vs {files[1]}")
    print(f"  • Brightness difference: {abs(profile_0['centroid_mean'] - profile_1['centroid_mean']):.0f} Hz")
    print(f"  • Energy difference: {abs(profile_0['rms_mean'] - profile_1['rms_mean']):.4f}")
    print(f"  • Voice quality difference: {abs(profile_0['zcr_mean'] - profile_1['zcr_mean']):.4f}")
    
    if profile_0['centroid_mean'] > profile_1['centroid_mean']:
        brighter = files[0]
    else:
        brighter = files[1]
    
    if profile_0['rms_mean'] > profile_1['rms_mean']:
        louder = files[0]
    else:
        louder = files[1]
    
    print(f"\nRecommendations:")
    print(f"  • Brighter voice: {brighter}")
    print(f"  • Louder voice: {louder}")
    print(f"  • Blending strategy: Use both voices for complementary characteristics")
    
    voice_profiles['comparison'] = {
        'brighter_voice': brighter,
        'louder_voice': louder,
        'brightness_diff': float(abs(profile_0['centroid_mean'] - profile_1['centroid_mean'])),
        'energy_diff': float(abs(profile_0['rms_mean'] - profile_1['rms_mean']))
    }

print("\n\n[PHASE 3] Analysis Summary")
print("-" * 70)

report = {
    'timestamp': __import__('datetime').datetime.now().isoformat(),
    'status': 'VOICE ANALYSIS COMPLETE',
    'files_analyzed': len(voice_profiles) - (1 if 'comparison' in voice_profiles else 0),
    'voice_profiles': voice_profiles,
    'ready_for_tts': True,
    'next_step': 'Install FFmpeg and run TTS voice generation'
}

report_file = 'voice_analysis_report.json'
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n✓ Voice analysis complete")
print(f"✓ Results saved to: {report_file}")
print(f"\nNext Steps:")
print(f"  1. Install FFmpeg: winget install FFmpeg")
print(f"  2. Add to system PATH")
print(f"  3. Run: python omega_dual_voice_blend.py")

print("\n[SUCCESS] Voice analysis phase complete")
print("=" * 70)
