"""
Create short voice samples from the separated KITT voices
"""
import soundfile as sf
from pathlib import Path

print("\n" + "="*70)
print("🎤 Creating Voice Samples")
print("="*70 + "\n")

# Load both voices
voice1_path = Path("kitt_voice_1.wav")
voice2_path = Path("kitt_voice_2.wav")

for voice_file in [voice1_path, voice2_path]:
    if voice_file.exists():
        data, samplerate = sf.read(str(voice_file))
        
        # Get first 3 seconds as sample
        sample_duration = 3.0
        sample_length = int(sample_duration * samplerate)
        
        if len(data) > sample_length:
            sample = data[:sample_length]
        else:
            sample = data
        
        # Save sample
        sample_name = voice_file.stem + "_sample.wav"
        sf.write(sample_name, sample, samplerate)
        
        duration = len(sample) / samplerate
        print(f"✅ Created {sample_name} ({duration:.1f}s)")

print("\n" + "="*70)
print("🔊 Playing samples back-to-back for comparison...")
print("="*70 + "\n")

import subprocess

# Play Voice 1 sample
print("🎤 Voice 1 Sample (3 seconds)...")
subprocess.run([
    "powershell", "-c",
    '$player = New-Object System.Media.SoundPlayer("kitt_voice_1_sample.wav"); $player.PlaySync()'
])

print("✅ Voice 1 complete\n")

# Pause
import time
time.sleep(0.5)

# Play Voice 2 sample
print("🎤 Voice 2 Sample (3 seconds)...")
subprocess.run([
    "powershell", "-c",
    '$player = New-Object System.Media.SoundPlayer("kitt_voice_2_sample.wav"); $player.PlaySync()'
])

print("✅ Voice 2 complete\n")

print("="*70)
print("Which voice should be Gate's?")
print("  - Voice 1 (lower pitch)")
print("  - Voice 2 (higher pitch)")
print("="*70 + "\n")
