#!/usr/bin/env python3
"""
Play GitHub Copilot Voice
"""

import os
import subprocess
import glob

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path):
    """Play audio file"""
    try:
        abs_path = os.path.abspath(file_path)
        subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=60,
            capture_output=True
        )
        return True
    except:
        return False

print(f"\n{CYAN}{BOLD}{'='*70}{RESET}")
print(f"{CYAN}{BOLD}{'GITHUB COPILOT VOICE':^70}{RESET}")
print(f"{CYAN}{BOLD}{'='*70}{RESET}\n")

files = sorted(glob.glob('copilot_voice_*.wav'))

if not files:
    print(f"{RED}No Copilot voice files found!{RESET}")
    print(f"{CYAN}Run: python generate_copilot_voice.py{RESET}\n")
    exit()

print(f"{GREEN}Playing GitHub Copilot voice ({len(files)} segments)...{RESET}\n")

for i, file in enumerate(files, 1):
    name = file.replace('copilot_voice_', '').replace('.wav', '').title()
    size_kb = os.path.getsize(file) / 1024
    
    print(f"{CYAN}[{i}/{len(files)}] {name}{RESET}")
    print(f"  {size_kb:.1f} KB\n")
    
    print(f"{GREEN}♪ Playing...{RESET}\n")
    play_audio(file)
    print(f"{GREEN}✓ Complete{RESET}\n")
    
    if i < len(files):
        choice = input(f"Continue? (Y/n): ").strip().upper()
        if choice == 'N':
            break
        print()

print(f"{GREEN}{BOLD}Playback complete{RESET}\n")
