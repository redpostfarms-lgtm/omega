"""
KITT Voice Trimmer - Simple End Removal
Remove unwanted sound from the end of KITT voice
"""
import numpy as np
import soundfile as sf
from pathlib import Path

kitt_voice = Path("H:/The Gatekeeper/static/audio/kitt_voice.wav")

print("\n" + "="*70)
print("✂️  KITT Voice Trimmer")
print("="*70 + "\n")

# Load audio
print(f"📂 Loading: {kitt_voice.name}")
data, samplerate = sf.read(str(kitt_voice))

total_duration = len(data) / samplerate
print(f"✅ Total duration: {total_duration:.2f} seconds\n")

# Show 10-second intervals
print("⏱️  Audio timeline (10-second intervals):\n")
for i in range(0, int(total_duration) + 1, 10):
    if i == 0:
        print(f"  0:00 - Start")
    else:
        mins = i // 60
        secs = i % 60
        print(f"  {mins}:{secs:02d}")

print(f"\n  END at {int(total_duration//60)}:{int(total_duration%60):02d}\n")

print("="*70)
print("📋 TO TRIM THE END:")
print("="*70)
print("\nEnter the time WHERE YOU WANT IT TO END (remove everything after)")
print("Format: MM:SS (e.g., '1:30' for 1 minute 30 seconds)")
print("Or just seconds (e.g., '90' for 1 minute 30 seconds)\n")

trim_input = input("Cut audio at time: ").strip()

# Parse input
try:
    if ':' in trim_input:
        parts = trim_input.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        trim_seconds = minutes * 60 + seconds
    else:
        trim_seconds = float(trim_input)
    
    if trim_seconds <= 0 or trim_seconds >= total_duration:
        print("\n❌ Invalid time! Must be between 0 and total duration.\n")
        exit(1)
    
    # Trim audio
    trim_sample = int(trim_seconds * samplerate)
    trimmed_data = data[:trim_sample]
    
    # Save trimmed version
    output_file = "kitt_voice_trimmed.wav"
    sf.write(output_file, trimmed_data, samplerate)
    
    new_duration = len(trimmed_data) / samplerate
    removed_duration = total_duration - new_duration
    
    print(f"\n✅ Trimmed audio saved!")
    print(f"   File: {output_file}")
    print(f"   New duration: {new_duration:.2f}s")
    print(f"   Removed: {removed_duration:.2f}s from the end\n")
    
    # Play preview
    print("🔊 Playing trimmed version...")
    import subprocess
    subprocess.run([
        "powershell", "-c",
        f'$player = New-Object System.Media.SoundPlayer("{output_file}"); $player.PlaySync()'
    ])
    
    print("\n✅ Preview complete!")
    print("\nIf this sounds good, I'll update Gate to use kitt_voice_trimmed.wav\n")
    
except ValueError:
    print("\n❌ Invalid input format!\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
