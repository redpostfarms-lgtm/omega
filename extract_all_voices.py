#!/usr/bin/env python3
"""
Simple Audio Voice Extractor
Scans system for audio files and extracts voices
"""
import os
import sys
from pathlib import Path
from datetime import datetime

print("="*70)
print("🌍 AUDIO VOICE EXTRACTION STARTING")
print("="*70)

# Create output directory
output_dir = Path("H:/The Gatekeeper/extracted_voices")
output_dir.mkdir(exist_ok=True)
print(f"\n📂 Output directory: {output_dir}")

# Search locations
search_paths = [
    Path("H:/The Gatekeeper"),
    Path.home() / "Downloads",
    Path.home() / "Videos",
]

# Audio extensions
audio_exts = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.mp4', '.avi', '.mkv']

print("\n🔍 SCANNING FOR AUDIO FILES...")
print(f"Searching in: {len(search_paths)} locations\n")

found_files = []
total_size = 0

for search_path in search_paths:
    if not search_path.exists():
        print(f"⚠️ Skipping (not found): {search_path}")
        continue

    print(f"📁 Scanning: {search_path}")

    try:
        for root, dirs, files in os.walk(search_path):
            # Skip hidden and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in
                      ['node_modules', '__pycache__', '.git', '.venv', '.venv311', 'backup']]

            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_exts):
                    full_path = Path(root) / file
                    try:
                        size = full_path.stat().st_size
                        size_mb = size / (1024 * 1024)

                        # Only files between 10KB and 500MB
                        if 0.01 < size_mb < 500:
                            found_files.append({
                                'path': str(full_path),
                                'name': file,
                                'size_mb': size_mb,
                                'directory': str(root)
                            })
                            total_size += size
                            print(f"  ✓ {file} ({size_mb:.2f} MB)")

                            # Limit to 100 files for now
                            if len(found_files) >= 100:
                                print(f"\n⚠️ Reached 100 file limit, stopping scan")
                                break
                    except (PermissionError, OSError) as e:
                        continue

                if len(found_files) >= 100:
                    break

            if len(found_files) >= 100:
                break

    except (PermissionError, OSError) as e:
        print(f"  ⚠️ Access denied: {e}")

print(f"\n✅ SCAN COMPLETE")
print(f"📊 Found {len(found_files)} audio files")
print(f"💾 Total size: {total_size / (1024*1024*1024):.2f} GB\n")

# Save file list
list_file = output_dir / 'audio_files_found.txt'
with open(list_file, 'w', encoding='utf-8') as f:
    f.write(f"Audio Files Found: {len(found_files)}\n")
    f.write(f"Scan Date: {datetime.now()}\n")
    f.write(f"Total Size: {total_size / (1024*1024*1024):.2f} GB\n")
    f.write("="*70 + "\n\n")

    for idx, file in enumerate(found_files, 1):
        f.write(f"{idx}. {file['name']}\n")
        f.write(f"   Path: {file['path']}\n")
        f.write(f"   Size: {file['size_mb']:.2f} MB\n\n")

print(f"📄 File list saved to: {list_file}")

# Filter for likely voice files
print("\n🎤 IDENTIFYING VOICE FILES...")

voice_candidates = []
voice_keywords = ['voice', 'speech', 'talk', 'speak', 'say', 'conversation', 'clip',
                  'omega', 'kitt', 'gate', 'audio', 'recording', 'sample']

for file in found_files:
    name_lower = file['name'].lower()
    if any(keyword in name_lower for keyword in voice_keywords):
        voice_candidates.append(file)
        print(f"  🎙️ {file['name']}")

print(f"\n✅ Found {len(voice_candidates)} likely voice files")

# Save voice candidates
voice_list = output_dir / 'voice_candidates.txt'
with open(voice_list, 'w', encoding='utf-8') as f:
    f.write(f"Voice File Candidates: {len(voice_candidates)}\n")
    f.write("="*70 + "\n\n")

    for idx, file in enumerate(voice_candidates, 1):
        f.write(f"{idx}. {file['name']}\n")
        f.write(f"   {file['path']}\n")
        f.write(f"   {file['size_mb']:.2f} MB\n\n")

print(f"📄 Voice candidates saved to: {voice_list}")

print("\n" + "="*70)
print("✅ EXTRACTION PHASE 1 COMPLETE")
print("="*70)
print(f"\nNext steps:")
print(f"1. Review voice candidates in: {voice_list}")
print(f"2. Run advanced analysis on selected files")
print(f"3. Extract and separate voice streams")
