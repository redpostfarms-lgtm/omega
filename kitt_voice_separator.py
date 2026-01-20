"""
KITT Voice Separator - Split Two Different Voices
Separate two distinct voices into separate files
"""
import numpy as np
import soundfile as sf
from pathlib import Path
from scipy import signal
from scipy.ndimage import gaussian_filter1d

kitt_voice = Path("H:/The Gatekeeper/static/audio/kitt_voice.wav")

print("\n" + "="*70)
print("🎙️  KITT Voice Separator - Two Voice Analysis")
print("="*70 + "\n")

# Load audio
print(f"📂 Loading: {kitt_voice.name}")
data, samplerate = sf.read(str(kitt_voice))
total_duration = len(data) / samplerate

print(f"✅ Duration: {total_duration:.2f} seconds")
print(f"   Sample Rate: {samplerate} Hz\n")

# Convert to mono
if len(data.shape) > 1:
    audio_mono = np.mean(data, axis=1)
else:
    audio_mono = data

# Analyze frequency characteristics in segments
print("🔍 Analyzing voice characteristics...\n")

segment_length = int(samplerate * 0.5)  # 500ms segments
segments_data = []

for i in range(0, len(audio_mono) - segment_length, segment_length):
    segment = audio_mono[i:i + segment_length]
    
    # Calculate spectral features
    frequencies, times, spectrogram = signal.spectrogram(segment, samplerate)
    
    # Get dominant frequency (pitch)
    freq_sum = np.sum(spectrogram, axis=1)
    dominant_freq_idx = np.argmax(freq_sum)
    dominant_freq = frequencies[dominant_freq_idx]
    
    # Energy
    energy = np.mean(segment ** 2)
    
    # Spectral centroid (brightness)
    spectral_centroid = np.sum(frequencies * freq_sum) / np.sum(freq_sum)
    
    if energy > 0.001:  # Only analyze non-silent segments
        segments_data.append({
            'start': i,
            'end': i + segment_length,
            'time': i / samplerate,
            'dominant_freq': dominant_freq,
            'energy': energy,
            'spectral_centroid': spectral_centroid
        })

if not segments_data:
    print("❌ No voice segments found!\n")
    exit(1)

# Cluster into two voices based on pitch/frequency
dominant_freqs = [s['dominant_freq'] for s in segments_data]
median_freq = np.median(dominant_freqs)

print(f"📊 Voice Analysis:")
print(f"   Total speech segments: {len(segments_data)}")
print(f"   Median frequency: {median_freq:.1f} Hz\n")

# Separate into two groups
voice1_segments = []  # Lower/different pitch
voice2_segments = []  # Higher/different pitch

for seg in segments_data:
    if seg['dominant_freq'] < median_freq:
        voice1_segments.append(seg)
    else:
        voice2_segments.append(seg)

print(f"🎤 Voice 1: {len(voice1_segments)} segments")
if voice1_segments:
    v1_avg_freq = np.mean([s['dominant_freq'] for s in voice1_segments])
    v1_duration = sum([(s['end'] - s['start']) / samplerate for s in voice1_segments])
    print(f"   Average pitch: {v1_avg_freq:.1f} Hz")
    print(f"   Total duration: {v1_duration:.2f}s\n")

print(f"🎤 Voice 2: {len(voice2_segments)} segments")
if voice2_segments:
    v2_avg_freq = np.mean([s['dominant_freq'] for s in voice2_segments])
    v2_duration = sum([(s['end'] - s['start']) / samplerate for s in voice2_segments])
    print(f"   Average pitch: {v2_avg_freq:.1f} Hz")
    print(f"   Total duration: {v2_duration:.2f}s\n")

# Create continuous audio for each voice
print("✂️  Extracting voices...\n")

def extract_voice(segments, audio, original_stereo_data, samplerate):
    """Extract and concatenate segments for one voice"""
    voice_samples = []
    
    for seg in segments:
        start = seg['start']
        end = seg['end']
        
        # Get segment (use stereo if available)
        if len(original_stereo_data.shape) > 1:
            segment = original_stereo_data[start:end]
        else:
            segment = audio[start:end]
        
        voice_samples.append(segment)
    
    if voice_samples:
        return np.concatenate(voice_samples)
    return np.array([])

voice1_audio = extract_voice(voice1_segments, audio_mono, data, samplerate)
voice2_audio = extract_voice(voice2_segments, audio_mono, data, samplerate)

# Apply noise reduction (simple high-pass filter)
def reduce_noise(audio, samplerate):
    """Apply simple noise reduction"""
    # High-pass filter to remove low-frequency rumble
    sos = signal.butter(4, 100, 'hp', fs=samplerate, output='sos')
    filtered = signal.sosfilt(sos, audio.T).T if len(audio.shape) > 1 else signal.sosfilt(sos, audio)
    return filtered

# Save voices
if len(voice1_audio) > 0:
    voice1_clean = reduce_noise(voice1_audio, samplerate)
    sf.write("kitt_voice_1.wav", voice1_clean, samplerate)
    duration = len(voice1_audio) / samplerate
    print(f"✅ Saved: kitt_voice_1.wav ({duration:.2f}s)")

if len(voice2_audio) > 0:
    voice2_clean = reduce_noise(voice2_audio, samplerate)
    sf.write("kitt_voice_2.wav", voice2_clean, samplerate)
    duration = len(voice2_audio) / samplerate
    print(f"✅ Saved: kitt_voice_2.wav ({duration:.2f}s)")

print("\n" + "="*70)
print("📋 NEXT STEPS:")
print("="*70)
print("\nListen to both files:")
print("  - kitt_voice_1.wav")
print("  - kitt_voice_2.wav")
print("\nThen tell me which one is Gate's voice!\n")
