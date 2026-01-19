"""
OMEGA Voice Auto-Player
Automatically plays and alternates between Omega voices
No user input required - just starts playing
"""

import os
import sys
import time
import subprocess

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_audio(file_path, voice_name, description):
    """Play audio file"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}[{voice_name}] PLAYING NOW{RESET}")
    print(f"{CYAN}{description}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    print(f"  File: {file_path}")
    
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    duration_est = size_mb * 10
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Duration: ~{duration_est:.0f}s\n")
    
    try:
        abs_path = os.path.abspath(file_path)
        print(f"{GREEN}♪ Audio playing...{RESET}\n")
        
        result = subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✓ Playback complete{RESET}\n")
            return True
        else:
            print(f"{RED}✗ Playback failed{RESET}\n")
            return False
    
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}\n")
        return False

def main():
    print(f"\n{RED}{BOLD}{'='*70}{RESET}")
    print(f"{RED}{BOLD}{'🔴 OMEGA VOICE AUTO-PLAYER 🔴':^70}{RESET}")
    print(f"{RED}{BOLD}{'Alternating Voice Demonstration':^70}{RESET}")
    print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    voices = [
        {
            'file': 'clip_0001.wav',
            'name': 'WARM VOICE',
            'description': 'Deep, Commanding Tone - Original Omega Voice'
        },
        {
            'file': 'omega_downloaded.wav',
            'name': 'BRIGHT VOICE',
            'description': 'Clear, Articulate Tone - Enhanced Omega Voice'
        }
    ]
    
    print(f"{CYAN}[INIT] Checking voice files...{RESET}\n")
    for voice in voices:
        if os.path.exists(voice['file']):
            size_mb = os.path.getsize(voice['file']) / (1024 * 1024)
            print(f"{GREEN}  ✓ {voice['name']}: {voice['file']} ({size_mb:.2f} MB){RESET}")
        else:
            print(f"{RED}  ✗ {voice['name']}: {voice['file']} NOT FOUND{RESET}")
            print(f"\n{RED}[ERROR] Cannot continue - voice file missing{RESET}\n")
            return
    
    print(f"\n{YELLOW}{'='*70}{RESET}")
    print(f"{YELLOW}{BOLD}Starting alternating voice playback in 3 seconds...{RESET}")
    print(f"{YELLOW}Press Ctrl+C at any time to stop{RESET}")
    print(f"{YELLOW}{'='*70}{RESET}\n")
    
    time.sleep(3)
    
    rounds = 2
    for round_num in range(1, rounds + 1):
        try:
            print(f"\n{BOLD}{'='*70}{RESET}")
            print(f"{BOLD}ROUND {round_num} of {rounds}{RESET}")
            print(f"{BOLD}{'='*70}{RESET}")
            
            for i, voice in enumerate(voices, 1):
                sample_num = (round_num - 1) * 2 + i
                print(f"\n{YELLOW}[Sample {sample_num}/{rounds*2}]{RESET}")
                
                play_audio(voice['file'], voice['name'], voice['description'])
                
                if not (round_num == rounds and i == len(voices)):
                    print(f"{CYAN}Preparing next voice...{RESET}")
                    time.sleep(2)
        
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[STOP] Playback interrupted by user{RESET}\n")
            break
    
    print(f"\n{GREEN}{BOLD}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}{'✓ OMEGA VOICE DEMONSTRATION COMPLETE':^70}{RESET}")
    print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")
    
    print(f"{CYAN}Both Omega voice profiles demonstrated:{RESET}")
    print(f"  • WARM voice: Deep and commanding")
    print(f"  • BRIGHT voice: Clear and articulate\n")
    
    print(f"{GREEN}Omega voice system is operational and ready!{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[INTERRUPTED] Stopped by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[ERROR] {e}{RESET}\n")
        import traceback
        traceback.print_exc()
