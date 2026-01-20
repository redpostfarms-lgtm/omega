"""
Omega Voice Analyzer & Blender
Analyzes all voice files and creates optimal blend
"""

import os
from pathlib import Path
import soundfile as sf
import numpy as np

print("\n" + "="*70)
print("  🎤 OMEGA VOICE ANALYZER & BLENDER")
print("="*70)

# Main voice candidates
main_voices = {
    'clip_0001.wav': 'Original Recording',
    'omega_downloaded.wav': 'Enhanced Download',
    'omega_intro.wav': 'Intro Voice',
    'omega_test.wav': 'Recent Test',
    'omega_voice_bright_brighter.wav': 'Bright & Brighter',
    'omega_voice_bright_deeper.wav': 'Bright & Deeper',
    'omega_voice_warm_brighter.wav': 'Warm & Brighter',
    'omega_voice_warm_deeper.wav': 'Warm & Deeper'
}

print("\n📊 Analyzing Voice Files...")
print("="*70)

voice_data = {}

for filename, description in main_voices.items():
    filepath = Path(filename)

    if not filepath.exists():
        print(f"⚠️ {filename} - NOT FOUND")
        continue

    try:
        # Load audio
        audio, samplerate = sf.read(str(filepath))

        # Calculate characteristics
        duration = len(audio) / samplerate
        filesize = filepath.stat().st_size / (1024 * 1024)  # MB

        # Audio characteristics
        rms = np.sqrt(np.mean(audio**2))  # Volume
        peak = np.max(np.abs(audio))  # Peak level

        voice_data[filename] = {
            'description': description,
            'duration': duration,
            'filesize': filesize,
            'samplerate': samplerate,
            'rms': rms,
            'peak': peak,
            'quality_score': duration * rms * (samplerate / 22050)
        }

        print(f"\n✓ {filename}")
        print(f"  {description}")
        print(f"  Duration: {duration:.1f}s | Size: {filesize:.1f}MB")
        print(f"  Sample Rate: {samplerate}Hz")
        print(f"  Volume (RMS): {rms:.3f} | Peak: {peak:.3f}")
        print(f"  Quality Score: {voice_data[filename]['quality_score']:.2f}")

    except Exception as e:
        print(f"✗ {filename} - ERROR: {e}")

# Rank voices
print("\n" + "="*70)
print("📈 VOICE RANKINGS (by Quality Score)")
print("="*70)

ranked = sorted(voice_data.items(), key=lambda x: x[1]['quality_score'], reverse=True)

for i, (filename, data) in enumerate(ranked, 1):
    print(f"\n{i}. {filename}")
    print(f"   {data['description']}")
    print(f"   Score: {data['quality_score']:.2f} | Duration: {data['duration']:.1f}s")

# Recommend best voice
print("\n" + "="*70)
print("🎯 RECOMMENDATION")
print("="*70)

if ranked:
    best = ranked[0]
    print(f"\n✨ Best Overall: {best[0]}")
    print(f"   {best[1]['description']}")
    print(f"   This voice has the highest quality score.")
    print()

    # Find good backups
    long_voices = [v for v in ranked if v[1]['duration'] > 3.0]
    high_quality = [v for v in ranked if v[1]['rms'] > 0.01]

    print("💡 Voice Strategy:")
    print()
    print(f"   PRIMARY: {best[0]}")

    if len(long_voices) > 1:
        backup = long_voices[1]
        print(f"   BACKUP:  {backup[0]} ({backup[1]['duration']:.1f}s long)")

    print()
    print("   Use PRIMARY for all TTS voice cloning.")
    print("   The system will automatically use it for Omega's voice.")

# Create symlink or copy best voice
print("\n" + "="*70)
print("🔧 SETUP")
print("="*70)

if ranked:
    best_file = ranked[0][0]
    target = Path('omega_voice_best.wav')

    try:
        # Copy best voice as the default
        audio, sr = sf.read(best_file)
        sf.write(str(target), audio, sr)
        print(f"\n✓ Created: omega_voice_best.wav")
        print(f"  Copied from: {best_file}")
        print()
        print("  This is now the default voice for Omega.")

    except Exception as e:
        print(f"\n✗ Could not create default voice: {e}")

print("\n" + "="*70)
print("🎤 NEXT STEPS")
print("="*70)
print()
print("1. Test the best voice:")
print("   python omega_voice_test_best.py")
print()
print("2. Listen to top 3 voices:")
print("   python omega_voice_compare.py")
print()
print("3. Record a NEW voice if unsatisfied:")
print("   python omega_record_new_voice.py")
print()
print("="*70)
