"""
KITT Voice Audio Separator
Analyze and split the KITT voice file into segments
"""
import numpy as np
import soundfile as sf
from pathlib import Path
import matplotlib.pyplot as plt

kitt_voice = Path("H:/The Gatekeeper/static/audio/kitt_voice.wav")

print("\n" + "="*70)
print("🎵 KITT Voice Audio Analyzer")
print("="*70 + "\n")

# Load the audio file
print(f"📂 Loading: {kitt_voice.name}")
data, samplerate = sf.read(str(kitt_voice))

print(f"✅ Audio loaded:")
print(f"   Duration: {len(data) / samplerate:.2f} seconds")
print(f"   Sample Rate: {samplerate} Hz")
print(f"   Samples: {len(data):,}")
print(f"   Channels: {'Stereo' if len(data.shape) > 1 else 'Mono'}\n")

# Convert stereo to mono if needed
if len(data.shape) > 1:
    audio_mono = np.mean(data, axis=1)
else:
    audio_mono = data

# Detect silence and segments
print("🔍 Analyzing audio segments...\n")

# Calculate RMS energy in windows
window_size = int(samplerate * 0.1)  # 100ms windows
rms_values = []
for i in range(0, len(audio_mono) - window_size, window_size):
    window = audio_mono[i:i + window_size]
    rms = np.sqrt(np.mean(window ** 2))
    rms_values.append(rms)

# Find segments based on energy threshold
threshold = np.max(rms_values) * 0.1  # 10% of max energy
segments = []
in_segment = False
segment_start = 0

for i, rms in enumerate(rms_values):
    time_seconds = (i * window_size) / samplerate
    
    if rms > threshold and not in_segment:
        segment_start = i * window_size
        in_segment = True
    elif rms <= threshold and in_segment:
        segment_end = i * window_size
        segments.append((segment_start, segment_end))
        in_segment = False

# Add final segment if still active
if in_segment:
    segments.append((segment_start, len(audio_mono)))

# Display segments
print(f"Found {len(segments)} audio segments:\n")
for idx, (start, end) in enumerate(segments, 1):
    start_time = start / samplerate
    end_time = end / samplerate
    duration = end_time - start_time
    print(f"Segment {idx}:")
    print(f"  Time: {start_time:.2f}s - {end_time:.2f}s")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Samples: {start:,} - {end:,}")
    print()

# Save individual segments
print("\n💾 Saving segments as separate files...\n")
for idx, (start, end) in enumerate(segments, 1):
    if len(data.shape) > 1:
        segment_data = data[start:end]
    else:
        segment_data = audio_mono[start:end]
    
    output_file = f"kitt_voice_segment_{idx}.wav"
    sf.write(output_file, segment_data, samplerate)
    duration = (end - start) / samplerate
    print(f"✅ Saved: {output_file} ({duration:.2f}s)")

print("\n" + "="*70)
print("📋 INSTRUCTIONS:")
print("="*70)
print("\nListen to each segment file:")
for idx in range(1, len(segments) + 1):
    print(f"  - kitt_voice_segment_{idx}.wav")

print("\nThen tell me which segments to KEEP for Gate's voice.")
print("Example: 'Keep segment 1' or 'Keep segments 1 and 2'\n")
