#!/usr/bin/env python3
"""
Omega Voice Analysis System - Skip TTS Model
Focus on voice file analysis only
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

print("[*] Omega Voice Analysis System")
print("=" * 70)

voice_files = {
    'clip_0001.wav': 'Original Omega Voice',
    'omega_downloaded.wav': 'Enhanced Voice'
}

voice_profiles = {}

# Phase 1: Analyze voice files
print("\n[PHASE 1] Voice File Analysis")
print("-" * 70)

try:
    import librosa
    import numpy as np
    
    for voice_file, description in voice_files.items():
        if not os.path.exists(voice_file):
            print(f"  [SKIP] {voice_file} not found")
            continue
        
        print(f"\n  [LOAD] {description}: {voice_file}")
        
        # Load audio
        y, sr = librosa.load(voice_file, sr=None, mono=True)
        duration = len(y) / sr
        print(f"    • Sample rate: {sr:,} Hz")
        print(f"    • Duration: {duration:.2f}s")
        
        # Spectral analysis
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        
        voice_profiles[voice_file] = {
            'sr': int(sr),
            'duration': round(float(duration), 2),
            'centroid_hz': round(float(np.mean(centroid)), 0),
            'rolloff_hz': round(float(np.mean(rolloff)), 0),
            'rms_energy': round(float(np.mean(rms)), 4),
            'zcr_quality': round(float(np.mean(zcr)), 4),
            'loudness': "loud" if np.mean(rms) > 0.01 else "moderate",
            'brightness': "bright" if np.mean(centroid) > 2000 else "warm"
        }
        
        print(f"    • Brightness: {voice_profiles[voice_file]['centroid_hz']} Hz ({voice_profiles[voice_file]['brightness']})")
        print(f"    • Loudness: {voice_profiles[voice_file]['rms_energy']} ({voice_profiles[voice_file]['loudness']})")
        print(f"    • Voice Quality: {voice_profiles[voice_file]['zcr_quality']}")
        print(f"    ✓ Analysis complete")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Phase 2: Compare voices
print("\n\n[PHASE 2] Voice Comparison")
print("-" * 70)

if len(voice_profiles) == 2:
    files = list(voice_profiles.keys())
    p0, p1 = voice_profiles[files[0]], voice_profiles[files[1]]
    
    print(f"\n  File 1: {files[0]}")
    print(f"    Brightness: {p0['centroid_hz']} Hz | Energy: {p0['rms_energy']} | Quality: {p0['zcr_quality']}")
    
    print(f"\n  File 2: {files[1]}")
    print(f"    Brightness: {p1['centroid_hz']} Hz | Energy: {p1['rms_energy']} | Quality: {p1['zcr_quality']}")
    
    brightness_diff = abs(p0['centroid_hz'] - p1['centroid_hz'])
    energy_diff = abs(p0['rms_energy'] - p1['rms_energy'])
    
    print(f"\n  Differences:")
    print(f"    • Brightness: {brightness_diff} Hz")
    print(f"    • Energy: {energy_diff}")
    
    brighter = files[0] if p0['centroid_hz'] > p1['centroid_hz'] else files[1]
    louder = files[0] if p0['rms_energy'] > p1['rms_energy'] else files[1]
    
    print(f"\n  Recommendations:")
    print(f"    • Use {brighter} for brightness/presence")
    print(f"    • Use {louder} for power/loudness")
    print(f"    • Blend both for optimal voice quality")

# Phase 3: Generate Report
print("\n\n[PHASE 3] Generating Report")
print("-" * 70)

report = {
    'timestamp': datetime.now().isoformat(),
    'analysis_type': 'Voice Profile Analysis Only',
    'status': 'COMPLETE',
    'voice_profiles': voice_profiles,
    'total_files_analyzed': len(voice_profiles),
    'next_step': 'Run TTS generation when ready',
    'tts_command': 'python omega_dual_voice_blend.py'
}

report_file = 'voice_profiles_analysis.json'
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n  ✓ Report saved: {report_file}")

# Display summary
print("\n\n[SUMMARY]")
print("=" * 70)
print(f"Voice files analyzed: {len(voice_profiles)}")
print(f"Analysis complete: {datetime.now().isoformat()}")
print(f"\nOutput file: {report_file}")
print("\nSTATUS: ✅ VOICE ANALYSIS COMPLETE")
print("=" * 70)
