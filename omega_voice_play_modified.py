#!/usr/bin/env python3
"""
OMEGA Modified Voice Player
Plays all modified voice variations
"""

import os
import sys
import time
import subprocess
import glob

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path, voice_name):
    """Play audio file"""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}♪ NOW PLAYING: {voice_name}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"  File: {file_path}")
    print(f"  Size: {size_mb:.2f} MB\n")
    
    try:
        abs_path = os.path.abspath(file_path)
        print(f"{GREEN}♪ Audio playing...{RESET}\n")
        
        subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True
        )
        
        print(f"{GREEN}✓ Complete{RESET}\n")
        return True
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}\n")
        return False

def main():
    print(f"\n{RED}{BOLD}{'='*70}{RESET}")
    print(f"{RED}{BOLD}{'🔴 OMEGA MODIFIED VOICE PLAYER 🔴':^70}{RESET}")
    print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    # Find modified voice files
    voice_files = glob.glob('omega_voice_*_*.wav')
    
    if not voice_files:
        print(f"{RED}No modified voice files found!{RESET}")
        print(f"{YELLOW}Run omega_voice_modifier.py first to create variations.{RESET}\n")
        return
    
    # Organize by variation
    variations = {}
    for file in sorted(voice_files):
        parts = file.replace('.wav', '').split('_')
        if len(parts) >= 4:
            source = parts[2]  # warm or bright
            variation = '_'.join(parts[3:])  # variation name
            
            if variation not in variations:
                variations[variation] = []
            variations[variation].append((source, file))
    
    print(f"{GREEN}Found {len(voice_files)} modified voices:{RESET}\n")
    
    # Display menu
    var_list = list(variations.keys())
    for i, var in enumerate(var_list, 1):
        files = variations[var]
        print(f"  {CYAN}{i}. {var.replace('_', ' ').title()}{RESET}")
        print(f"     {len(files)} variations: {', '.join([f[0].upper() for f in files])}")
    
    print(f"\n  {YELLOW}A. Play All (sequential){RESET}")
    print(f"  {RED}Q. Quit{RESET}\n")
    
    choice = input(f"{GREEN}Select option: {RESET}").strip().upper()
    print()
    
    if choice == 'Q':
        print(f"{CYAN}Goodbye!{RESET}\n")
        return
    
    if choice == 'A':
        # Play all variations
        print(f"{YELLOW}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}Playing all voice variations...{RESET}")
        print(f"{YELLOW}Press Ctrl+C to skip{RESET}")
        print(f"{YELLOW}{'='*70}{RESET}\n")
        
        time.sleep(2)
        
        count = 0
        for variation, files in variations.items():
            try:
                print(f"\n{MAGENTA}{BOLD}[{variation.replace('_', ' ').title()}]{RESET}\n")
                
                for source, file in files:
                    count += 1
                    voice_name = f"{source.upper()} - {variation.replace('_', ' ').title()}"
                    print(f"{BOLD}[{count}/{len(voice_files)}]{RESET}")
                    play_audio(file, voice_name)
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Skipping to next...{RESET}\n")
                time.sleep(0.5)
    
    elif choice.isdigit() and 1 <= int(choice) <= len(var_list):
        # Play specific variation
        var_idx = int(choice) - 1
        variation = var_list[var_idx]
        files = variations[variation]
        
        print(f"{MAGENTA}{'='*70}{RESET}")
        print(f"{MAGENTA}{BOLD}{variation.replace('_', ' ').title()}{RESET}")
        print(f"{MAGENTA}{'='*70}{RESET}\n")
        
        for source, file in files:
            voice_name = f"{source.upper()} - {variation.replace('_', ' ').title()}"
            play_audio(file, voice_name)
            time.sleep(1)
    
    else:
        print(f"{RED}Invalid choice{RESET}\n")
    
    print(f"{GREEN}{BOLD}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}{'Playback complete!':^70}{RESET}")
    print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[STOPPED]{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[ERROR] {e}{RESET}\n")
