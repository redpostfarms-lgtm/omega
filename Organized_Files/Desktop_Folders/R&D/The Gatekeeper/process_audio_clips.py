# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Audio clip processing script

from pydub import AudioSegment
import os
from pathlib import Path

# Load the audio file
audio_file = "long_recording.wav"
if not os.path.exists(audio_file):
    # Try in current directory or common locations
    possible_paths = [
        Path(audio_file),
        Path("D:/RPF_BRAIN/The Gatekeeper") / audio_file,
        Path.cwd() / audio_file,
    ]
    audio_path = None
    for path in possible_paths:
        if path.exists():
            audio_path = path
            break
    if not audio_path:
        print(f"Error: Could not find {audio_file}")
        print("Please ensure the file exists in the current directory or update the path.")
        exit(1)
    audio_file = str(audio_path)

print(f"Loading audio file: {audio_file}")
audio = AudioSegment.from_wav(audio_file)

# Split into 15-second clips (15000 milliseconds)
clip_duration_ms = 15000
clips = [audio[i:i+clip_duration_ms] for i in range(0, len(audio), clip_duration_ms)]

print(f"Created {len(clips)} clips from {len(audio)/1000:.2f} seconds of audio")

# Process each clip
for i, clip in enumerate(clips):
    clip_duration = len(clip) / 1000.0
    print(f"Clip {i+1}: {clip_duration:.2f} seconds")
    
    # Save each clip (optional - uncomment to save)
    # output_filename = f"clip_{i+1:03d}.wav"
    # clip.export(output_filename, format="wav")
    # print(f"  Saved as: {output_filename}")
    
    # Add your processing code here
    # For example: analyze, modify, etc.

print("\nProcessing complete!")
