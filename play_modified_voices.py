#!/usr/bin/env python3
"""
Play Modified Omega Voices - Auto Mode
"""

import os
import subprocess
import time
import glob

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path):
    """Play audio file"""
    try:
        abs_path = os.path.abspath(file_path)
        subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True
        )
        return True
    except:
        return False

print(f"\n{RED}{BOLD}{'='*70}{RESET}")
print(f"{RED}{BOLD}{'🔴 OMEGA MODIFIED VOICES - AUTO PLAYER 🔴':^70}{RESET}")
print(f"{RED}{BOLD}{'='*70}{RESET}\n")

# Find files
files = sorted(glob.glob('omega_voice_*_*.wav'))

if not files:
    print(f"{RED}No modified voices found!{RESET}\n")
    exit()

print(f"{GREEN}Found {len(files)} modified voices{RESET}\n")

descriptions = {
    'warm_deeper': 'WARM Voice → DEEPER (Lower pitch + bass boost)',
    'warm_brighter': 'WARM Voice → BRIGHTER (Higher pitch + treble boost)',
    'bright_deeper': 'BRIGHT Voice → DEEPER (Lower pitch + bass boost)',
    'bright_brighter': 'BRIGHT Voice → BRIGHTER (Higher pitch + treble boost)',
}

print(f"{YELLOW}Starting playback in 3 seconds...{RESET}")
print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")
time.sleep(3)

for i, file in enumerate(files, 1):
    try:
        # Extract description
        name = file.replace('omega_voice_', '').replace('.wav', '')
        desc = descriptions.get(name, name.replace('_', ' ').title())
        
        size_kb = os.path.getsize(file) / 1024
        
        print(f"{CYAN}{'='*70}{RESET}")
        print(f"{CYAN}{BOLD}[{i}/{len(files)}] {desc}{RESET}")
        print(f"{CYAN}{'='*70}{RESET}")
        print(f"  File: {file}")
        print(f"  Size: {size_kb:.1f} KB\n")
        
        print(f"{GREEN}♪ Playing...{RESET}\n")
        play_audio(file)
        
        print(f"{GREEN}✓ Complete{RESET}\n")
        
        if i < len(files):
            print(f"{YELLOW}Next voice in 2 seconds...{RESET}\n")
            time.sleep(2)
    
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopped by user{RESET}\n")
        break

print(f"\n{GREEN}{BOLD}{'='*70}{RESET}")
print(f"{GREEN}{BOLD}{'✓ ALL MODIFIED VOICES PLAYED':^70}{RESET}")
print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")

print(f"{CYAN}Voice Transformations Applied:{RESET}")
print(f"  • Deeper: -3 semitones pitch + bass enhancement")
print(f"  • Brighter: +2 semitones pitch + treble enhancement\n")
