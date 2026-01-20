"""
Record a NEW voice sample for Omega
Records 10 seconds of speech to create better voice clone
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime

print("\n" + "="*70)
print("  🎤 OMEGA NEW VOICE RECORDING")
print("="*70)
print()
print("This will record a NEW voice sample for Omega.")
print()
print("Instructions:")
print("  1. Get ready to speak for 10 seconds")
print("  2. Speak clearly and naturally")
print("  3. Say varied sentences with different emotions")
print()
print("Example text to read:")
print("  'Hello, I am Omega, your AI partner.'")
print("  'I can help you with LED control, coding, and system tasks.'")
print("  'Let's work together to solve problems.'")
print()

input("Press Enter when ready to start recording...")

print("\n🔴 RECORDING IN 3...")
import time
time.sleep(1)
print("🔴 RECORDING IN 2...")
time.sleep(1)
print("🔴 RECORDING IN 1...")
time.sleep(1)
print("\n🔴 RECORDING NOW! Speak for 10 seconds...\n")

# Record
duration = 10  # seconds
sample_rate = 22050  # Good quality for TTS
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()

print("\n✓ Recording complete!")
print("Processing...")

# Save as new voice file
new_voice_file = f"omega_voice_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
sf.write(new_voice_file, audio, sample_rate)

print(f"\n✓ Saved as: {new_voice_file}")
print(f"  Size: {len(audio) / sample_rate:.1f} seconds")
print()

# Also save as the default
sf.write("omega_voice_current.wav", audio, sample_rate)
print("✓ Set as current voice: omega_voice_current.wav")

print("\n" + "="*70)
print("  VOICE RECORDING COMPLETE")
print("="*70)
print()
print("Next: Test the new voice")
print("  python omega_voice_test.py")
print()
