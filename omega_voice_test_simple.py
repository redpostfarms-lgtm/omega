#!/usr/bin/env python3
"""
OMEGA Voice Quick Test - No TTS Loading
Just tests voice file availability and plays samples
"""

import os
import subprocess
import time

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header():
    print(f"\n{RED}{BOLD}{'='*70}{RESET}")
    print(f"{RED}{BOLD}{'OMEGA VOICE QUICK TEST':^70}{RESET}")
    print(f"{RED}{BOLD}{'='*70}{RESET}\n")

def check_voice_files():
    """Check and display voice files"""
    voice_files = {
        'clip_0001.wav': 'WARM Voice (Deep, Commanding)',
        'omega_downloaded.wav': 'BRIGHT Voice (Clear, Articulate)'
    }
    
    print(f"{CYAN}[INFO] Checking voice files...{RESET}\n")
    
    available = {}
    for file, desc in voice_files.items():
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            duration = get_audio_duration(file)
            print(f"{GREEN}✓ {file}{RESET}")
            print(f"  Description: {desc}")
            print(f"  Size: {size_mb:.2f} MB")
            if duration:
                print(f"  Duration: ~{duration:.1f} seconds")
            print()
            available[file] = desc
        else:
            print(f"{RED}✗ {file} - NOT FOUND{RESET}\n")
    
    return available

def get_audio_duration(file_path):
    """Get audio duration using ffprobe if available"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 
             'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
             file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return None

def play_audio(file_path):
    """Play audio file"""
    if not os.path.exists(file_path):
        print(f"{RED}[ERROR] File not found: {file_path}{RESET}")
        return False
    
    print(f"\n{CYAN}[PLAYING] {file_path}{RESET}")
    print("Press Ctrl+C to stop...\n")
    
    try:
        # Use Windows Media Player
        subprocess.run(
            ['powershell', '-c', 
             f'(New-Object Media.SoundPlayer "{os.path.abspath(file_path)}").PlaySync()'],
            timeout=120
        )
        print(f"{GREEN}[DONE] Playback completed{RESET}\n")
        return True
    except KeyboardInterrupt:
        print(f"\n{CYAN}[STOPPED] Playback interrupted{RESET}\n")
        return False
    except Exception as e:
        print(f"{RED}[ERROR] Playback failed: {e}{RESET}\n")
        return False

def main():
    print_header()
    
    # Check files
    available = check_voice_files()
    
    if not available:
        print(f"{RED}[ERROR] No voice files found!{RESET}\n")
        return
    
    # Menu
    print(f"{BOLD}Available Options:{RESET}")
    files = list(available.keys())
    for i, (file, desc) in enumerate(available.items(), 1):
        print(f"  {i}. Play {desc} ({file})")
    print(f"  Q. Quit\n")
    
    # Interactive loop
    while True:
        try:
            choice = input(f"{GREEN}Select option (1-{len(files)}/Q):{RESET} ").strip().upper()
            
            if choice == 'Q':
                print(f"\n{CYAN}[EXIT] Goodbye!{RESET}\n")
                break
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    file = files[idx]
                    play_audio(file)
                else:
                    print(f"{RED}[ERROR] Invalid choice{RESET}\n")
            else:
                print(f"{RED}[ERROR] Invalid input{RESET}\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{CYAN}[EXIT] Interrupted by user{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}[ERROR] {e}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{RED}[FATAL] {e}{RESET}\n")
