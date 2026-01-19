#!/usr/bin/env python3
"""
OMEGA Voice Player - Manual Approval Mode
Plays one voice at a time, waits for your approval before continuing
"""

import os
import subprocess

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path):
    """Play audio file once"""
    try:
        abs_path = os.path.abspath(file_path)
        subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")
        return False

print(f"\n{RED}{BOLD}{'='*70}{RESET}")
print(f"{RED}{BOLD}{'🔴 OMEGA VOICE - MANUAL APPROVAL MODE 🔴':^70}{RESET}")
print(f"{RED}{BOLD}{'='*70}{RESET}\n")

voices = [
    ('clip_0001.wav', 'OMEGA WARM VOICE', 'Deep, Commanding'),
    ('omega_downloaded.wav', 'OMEGA BRIGHT VOICE', 'Clear, Articulate')
]

print(f"{CYAN}Available Original Voices:{RESET}\n")
for i, (file, name, desc) in enumerate(voices, 1):
    if os.path.exists(file):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"  {i}. {name} - {desc} ({size_mb:.2f} MB)")
    else:
        print(f"  {i}. {name} - {RED}NOT FOUND{RESET}")

print(f"\n{YELLOW}{'='*70}{RESET}")
print(f"{YELLOW}Each voice plays ONCE, then waits for your approval{RESET}")
print(f"{YELLOW}{'='*70}{RESET}\n")

for i, (file, name, desc) in enumerate(voices, 1):
    if not os.path.exists(file):
        continue
    
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}[{i}/{len(voices)}] {name}{RESET}")
    print(f"{CYAN}{desc}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    
    print(f"{GREEN}♪ Playing now...{RESET}\n")
    play_audio(file)
    
    print(f"{GREEN}✓ Playback complete{RESET}\n")
    
    if i < len(voices):
        choice = input(f"{YELLOW}Play next voice? (Y/n): {RESET}").strip().upper()
        if choice == 'N':
            print(f"\n{CYAN}Stopped{RESET}\n")
            break
    else:
        print(f"\n{GREEN}{BOLD}All voices played{RESET}\n")
