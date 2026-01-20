"""
Gate Voice Direct Playback - No TTS Processing
Use Voice 1 directly with different speeds and effects
"""
import soundfile as sf
import sounddevice as sd
import numpy as np
from scipy import signal
from pathlib import Path

print("\n" + "="*70)
print("🎤 GATE - Voice 1 Direct Playback Test")
print("="*70 + "\n")

voice1_path = Path("kitt_voice_1.wav")

if not voice1_path.exists():
    print(f"❌ Voice not found: {voice1_path}\n")
    exit(1)

# Load Voice 1
data, samplerate = sf.read(str(voice1_path))
print(f"✅ Loaded: {voice1_path.name}")
print(f"   Duration: {len(data)/samplerate:.2f}s\n")

print("="*70)
print("🗣️  Gate Voice Variations")
print("="*70 + "\n")

# Test 1: Original Voice 1
print("1️⃣  Original Voice 1 (as separated)")
print("   🔊 Playing...")
sd.play(data, samplerate)
sd.wait()
print("   ✅ Complete\n")

import time
time.sleep(0.5)

# Test 2: Slightly slower (more dramatic)
print("2️⃣  Slower speed (0.9x - more dramatic)")
print("   🔊 Playing...")
slower_data = signal.resample(data, int(len(data) * 1.1))
sd.play(slower_data, samplerate)
sd.wait()
print("   ✅ Complete\n")

time.sleep(0.5)

# Test 3: Slightly faster (more alert)
print("3️⃣  Faster speed (1.1x - more alert)")
print("   🔊 Playing...")
faster_data = signal.resample(data, int(len(data) * 0.9))
sd.play(faster_data, samplerate)
sd.wait()
print("   ✅ Complete\n")

time.sleep(0.5)

# Test 4: With reverb effect
print("4️⃣  With reverb (more robotic)")
print("   🔊 Playing...")
# Simple reverb by mixing with delayed copy
delay_samples = int(samplerate * 0.05)  # 50ms delay
reverb_data = data.copy()
if len(data.shape) == 1:
    reverb_data[delay_samples:] += data[:-delay_samples] * 0.3
else:
    reverb_data[delay_samples:] += data[:-delay_samples] * 0.3
sd.play(reverb_data, samplerate)
sd.wait()
print("   ✅ Complete\n")

print("="*70)
print("📋 Which version sounds best for Gate?")
print("   1. Original")
print("   2. Slower (dramatic)")
print("   3. Faster (alert)")
print("   4. With reverb (robotic)")
print("="*70 + "\n")
