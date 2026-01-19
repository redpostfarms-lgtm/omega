#!/usr/bin/env python3
"""
Omega Voice Audio Enhancer
Cleans up existing voice output for smoother, clearer sound
"""

import numpy as np
import sys
import os

print("\n🔴 OMEGA VOICE ENHANCER")
print("="*60)

# Check if audio file exists
input_file = "omega_voice_output.wav"
if not os.path.exists(input_file):
    print(f"\n❌ Voice file not found: {input_file}")
    print("   Run speak_omega_voice.py first to generate voice")
    sys.exit(1)

try:
    import soundfile as sf
    from scipy import signal
    
    print(f"\n✓ Loading audio: {input_file}")
    audio_data, sample_rate = sf.read(input_file)
    
    duration = len(audio_data) / sample_rate
    print(f"  • Sample rate: {sample_rate} Hz")
    print(f"  • Duration: {duration:.1f}s")
    print(f"  • Channels: {'Stereo' if len(audio_data.shape) > 1 else 'Mono'}")
    
    print(f"\n🎧 APPLYING AUDIO ENHANCEMENTS...")
    
    # 1. Normalize audio (prevent clipping, balance volume)
    print("  1️⃣  Normalizing volume...")
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val * 0.92  # 92% to leave headroom
    
    # 2. High-pass filter (remove low-frequency rumble/noise)
    print("  2️⃣  Removing low-frequency rumble...")
    sos = signal.butter(4, 80, 'hp', fs=sample_rate, output='sos')
    audio_data = signal.sosfilt(sos, audio_data)
    
    # 3. Low-pass filter (reduce high-frequency harshness)
    print("  3️⃣  Smoothing high frequencies...")
    sos = signal.butter(4, 7500, 'lp', fs=sample_rate, output='sos')
    audio_data = signal.sosfilt(sos, audio_data)
    
    # 4. De-essing (reduce harsh 's' sounds)
    print("  4️⃣  De-essing (reducing sibilance)...")
    # Target sibilance frequency range (5-8kHz)
    sos = signal.butter(2, [4500, 8000], 'bp', fs=sample_rate, output='sos')
    sibilance = signal.sosfilt(sos, audio_data)
    sibilance_env = np.abs(sibilance)
    
    # Dynamic de-essing - only reduce peaks
    threshold = np.percentile(sibilance_env, 90)
    mask = sibilance_env > threshold
    reduction = np.where(mask, 0.6, 1.0)  # 40% reduction on harsh s-sounds
    
    # Smooth the reduction mask to avoid artifacts
    from scipy.ndimage import uniform_filter1d
    reduction = uniform_filter1d(reduction, size=int(sample_rate * 0.01))  # 10ms smoothing
    
    audio_data = audio_data * reduction
    
    # 5. Gentle compression (even out volume)
    print("  5️⃣  Applying gentle compression...")
    # Simple soft-knee compression
    threshold_db = -20
    ratio = 3.0
    threshold_linear = 10 ** (threshold_db / 20)
    
    audio_abs = np.abs(audio_data)
    mask = audio_abs > threshold_linear
    
    # Compress only signals above threshold
    compressed = np.copy(audio_data)
    compressed[mask] = np.sign(audio_data[mask]) * (
        threshold_linear + (audio_abs[mask] - threshold_linear) / ratio
    )
    audio_data = compressed
    
    # 6. Final normalization
    print("  6️⃣  Final normalization...")
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val * 0.88  # Conservative final level
    
    # Save enhanced audio
    output_file = "omega_voice_enhanced.wav"
    sf.write(output_file, audio_data, sample_rate)
    
    print(f"\n✅ ENHANCEMENT COMPLETE")
    print(f"="*60)
    print(f"  📁 Enhanced file: {output_file}")
    print(f"  🎚️  Processing applied:")
    print(f"     • Volume normalized")
    print(f"     • Low-frequency rumble removed")
    print(f"     • High-frequency smoothed")
    print(f"     • Sibilance reduced (de-essed)")
    print(f"     • Dynamic compression applied")
    print(f"\n  🔊 Voice is now cleaner and smoother!")
    print(f"="*60)
    
    # Play enhanced audio
    print(f"\n▶️  Playing enhanced audio...")
    import subprocess
    abs_path = os.path.abspath(output_file)
    subprocess.run(
        ['powershell', '-c', 
         f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
        timeout=120
    )
    print(f"✓ Playback complete\n")
    
except ImportError as e:
    print(f"\n❌ Missing libraries: {e}")
    print("   Install with: pip install soundfile scipy")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
