#!/usr/bin/env python3
"""
OMEGA Original Voice Player
Plays only the original voice samples provided
"""

import os
import subprocess
import time

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path, voice_name, description):
    """Play audio file"""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}♪ {voice_name}{RESET}")
    print(f"{CYAN}{description}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"  File: {file_path}")
    print(f"  Size: {size_mb:.2f} MB\n")
    
    try:
        abs_path = os.path.abspath(file_path)
        print(f"{GREEN}♪ Playing original voice...{RESET}\n")
        
        subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True,
            check=True
        )
        
        print(f"{GREEN}✓ Complete{RESET}\n")
        return True
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}\n")
        return False

print(f"\n{RED}{BOLD}{'='*70}{RESET}")
print(f"{RED}{BOLD}{'🔴 OMEGA ORIGINAL VOICE SAMPLES 🔴':^70}{RESET}")
print(f"{RED}{BOLD}{'='*70}{RESET}\n")

# Original voice samples only
voices = [
    {
        'file': 'clip_0001.wav',
        'name': 'OMEGA WARM VOICE',
        'description': 'Original Sample - Deep, Commanding Tone'
    },
    {
        'file': 'omega_downloaded.wav',
        'name': 'OMEGA BRIGHT VOICE',
        'description': 'Original Sample - Clear, Articulate Tone'
    }
]

# Check files
print(f"{CYAN}[CHECK] Verifying original voice samples...{RESET}\n")
available = []

for voice in voices:
    if os.path.exists(voice['file']):
        size_mb = os.path.getsize(voice['file']) / (1024 * 1024)
        print(f"{GREEN}  ✓ {voice['name']}: {voice['file']} ({size_mb:.2f} MB){RESET}")
        available.append(voice)
    else:
        print(f"{RED}  ✗ {voice['name']}: {voice['file']} NOT FOUND{RESET}")

if not available:
    print(f"\n{RED}[ERROR] No voice samples found!{RESET}\n")
    exit(1)

print(f"\n{YELLOW}{'='*70}{RESET}")
print(f"{YELLOW}{BOLD}Playing {len(available)} original voice samples...{RESET}")
print(f"{YELLOW}Press Ctrl+C to stop{RESET}")
print(f"{YELLOW}{'='*70}{RESET}\n")

time.sleep(2)

# Play original voices
for i, voice in enumerate(available, 1):
    try:
        print(f"\n{BOLD}[Sample {i}/{len(available)}]{RESET}")
        play_audio(voice['file'], voice['name'], voice['description'])
        
        if i < len(available):
            print(f"{YELLOW}Next voice in 2 seconds...{RESET}\n")
            time.sleep(2)
    
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[STOPPED] Playback interrupted{RESET}\n")
        break

print(f"\n{GREEN}{BOLD}{'='*70}{RESET}")
print(f"{GREEN}{BOLD}{'✓ ORIGINAL VOICE PLAYBACK COMPLETE':^70}{RESET}")
print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")

print(f"{CYAN}Omega Original Voice Samples:{RESET}")
print(f"  • WARM: Deep, commanding voice (27 seconds)")
print(f"  • BRIGHT: Clear, articulate voice (100 seconds)\n")
