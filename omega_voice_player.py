"""
OMEGA Voice Player - Plays existing voice samples with alternation
Works without TTS - uses pre-recorded samples
"""

import os
import sys
import time
import subprocess
from pathlib import Path

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class OmegaVoicePlayer:
    """Play Omega voice samples with alternation"""
    
    def __init__(self):
        self.current_voice = 'warm'
        self.voices = {
            'warm': {
                'file': 'clip_0001.wav',
                'name': 'WARM',
                'description': 'Deep, Commanding Voice',
                'color': RED
            },
            'bright': {
                'file': 'omega_downloaded.wav',
                'name': 'BRIGHT',
                'description': 'Clear, Articulate Voice',
                'color': CYAN
            }
        }
        self.play_count = 0
    
    def print_header(self):
        print(f"\n{RED}{BOLD}{'='*70}{RESET}")
        print(f"{RED}{BOLD}{'🔴 OMEGA VOICE PLAYER 🔴':^70}{RESET}")
        print(f"{RED}{BOLD}{'Alternating Voice Demonstration':^70}{RESET}")
        print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    def check_files(self):
        """Check voice files"""
        print(f"{CYAN}[CHECK] Verifying voice files...{RESET}\n")
        all_ok = True
        
        for key, voice in self.voices.items():
            if os.path.exists(voice['file']):
                size_mb = os.path.getsize(voice['file']) / (1024 * 1024)
                print(f"{GREEN}  ✓ {voice['name']}: {voice['file']}{RESET}")
                print(f"    Size: {size_mb:.2f} MB - {voice['description']}\n")
            else:
                print(f"{RED}  ✗ {voice['name']}: {voice['file']} NOT FOUND{RESET}\n")
                all_ok = False
        
        return all_ok
    
    def switch_voice(self):
        """Switch between voices"""
        self.current_voice = 'bright' if self.current_voice == 'warm' else 'warm'
        voice = self.voices[self.current_voice]
        print(f"\n{voice['color']}{'='*70}{RESET}")
        print(f"{voice['color']}{BOLD}[SWITCHING] Now using {voice['name']} voice{RESET}")
        print(f"{voice['color']}{voice['description']:^70}{RESET}")
        print(f"{voice['color']}{'='*70}{RESET}\n")
    
    def play_audio(self, file_path, description=""):
        """Play audio file"""
        voice = self.voices[self.current_voice]
        
        print(f"{voice['color']}[{voice['name']}] PLAYING:{RESET}")
        if description:
            print(f"  {description}")
        print(f"  File: {file_path}")
        print(f"  Duration: ~{self.get_duration_estimate(file_path)}\n")
        
        try:
            abs_path = os.path.abspath(file_path)
            result = subprocess.run(
                ['powershell', '-c', 
                 f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
                timeout=120,
                capture_output=True
            )
            
            if result.returncode == 0:
                print(f"{GREEN}  ✓ Playback complete{RESET}\n")
                return True
            else:
                print(f"{RED}  ✗ Playback failed{RESET}\n")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}  ⚠ Playback timeout{RESET}\n")
            return False
        except Exception as e:
            print(f"{RED}  ✗ Error: {e}{RESET}\n")
            return False
    
    def get_duration_estimate(self, file_path):
        """Estimate duration from file size"""
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            seconds = size_mb * 10
            if seconds < 60:
                return f"{seconds:.0f}s"
            else:
                mins = int(seconds // 60)
                secs = int(seconds % 60)
                return f"{mins}m {secs}s"
        except:
            return "unknown"
    
    def demo_alternating(self):
        """Play both voices alternating"""
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}{'ALTERNATING VOICE DEMO':^70}{RESET}")
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
        
        print(f"{GREEN}This demo will play both Omega voices in alternation.{RESET}")
        print(f"{GREEN}You'll hear the WARM voice, then the BRIGHT voice.{RESET}")
        print(f"{YELLOW}Press Ctrl+C at any time to stop.{RESET}\n")
        
        input(f"{CYAN}Press Enter to begin... {RESET}")
        print()
        
        rounds = 2  # Play each voice 2 times
        
        for round_num in range(1, rounds + 1):
            try:
                print(f"{BOLD}{'='*70}{RESET}")
                print(f"{BOLD}ROUND {round_num}/{rounds}{RESET}")
                print(f"{BOLD}{'='*70}{RESET}\n")
                
                voice_info = self.voices['warm']
                self.current_voice = 'warm'
                print(f"{voice_info['color']}[Voice Sample {round_num*2-1}]{RESET}")
                self.play_audio(voice_info['file'], voice_info['description'])
                
                if round_num < rounds:
                    time.sleep(2)
                    
                    self.switch_voice()
                    
                    voice_info = self.voices['bright']
                    print(f"{voice_info['color']}[Voice Sample {round_num*2}]{RESET}")
                    self.play_audio(voice_info['file'], voice_info['description'])
                    
                    if round_num < rounds:
                        time.sleep(2)
            
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}[STOP] Demo interrupted{RESET}\n")
                break
        
        print(f"\n{GREEN}{BOLD}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}{'DEMO COMPLETE':^70}{RESET}")
        print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")
    
    def continuous_mode(self):
        """Continuously alternate between voices"""
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}{'CONTINUOUS ALTERNATING MODE':^70}{RESET}")
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
        
        print(f"{GREEN}Voices will continuously alternate.{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop.{RESET}\n")
        
        input(f"{CYAN}Press Enter to begin... {RESET}")
        print()
        
        count = 0
        while True:
            try:
                count += 1
                voice_info = self.voices[self.current_voice]
                
                print(f"{BOLD}[Playback #{count}]{RESET}")
                self.play_audio(voice_info['file'], voice_info['description'])
                
                self.switch_voice()
                time.sleep(1)
            
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}[STOP] Continuous mode stopped{RESET}\n")
                print(f"{CYAN}Played {count} samples{RESET}\n")
                break
    
    def manual_mode(self):
        """Manual voice selection"""
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}{'MANUAL CONTROL MODE':^70}{RESET}")
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
        
        while True:
            try:
                voice_info = self.voices[self.current_voice]
                
                print(f"{CYAN}Commands:{RESET}")
                print(f"  {RED}1{RESET} - Play WARM voice")
                print(f"  {CYAN}2{RESET} - Play BRIGHT voice")
                print(f"  {YELLOW}S{RESET} - Switch voice")
                print(f"  {GREEN}P{RESET} - Play current voice")
                print(f"  {RED}Q{RESET} - Quit\n")
                
                print(f"{voice_info['color']}Current: {voice_info['name']} voice{RESET}")
                choice = input(f"\n{GREEN}Choose: {RESET}").strip().upper()
                print()
                
                if choice == 'Q':
                    break
                elif choice == '1':
                    self.current_voice = 'warm'
                    self.play_audio(self.voices['warm']['file'])
                elif choice == '2':
                    self.current_voice = 'bright'
                    self.play_audio(self.voices['bright']['file'])
                elif choice == 'S':
                    self.switch_voice()
                elif choice == 'P':
                    self.play_audio(voice_info['file'])
                else:
                    print(f"{RED}Invalid choice{RESET}\n")
            
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}[EXIT]{RESET}\n")
                break
    
    def run(self):
        """Main entry point"""
        self.print_header()
        
        if not self.check_files():
            print(f"{RED}[ERROR] Cannot continue - voice files missing{RESET}\n")
            return
        
        print(f"{CYAN}Select Mode:{RESET}\n")
        print(f"  {YELLOW}1{RESET}. Alternating Demo (plays both voices back-to-back)")
        print(f"  {YELLOW}2{RESET}. Continuous Mode (endless alternation)")
        print(f"  {YELLOW}3{RESET}. Manual Control (choose when to play)")
        print(f"  {RED}Q{RESET}. Quit\n")
        
        choice = input(f"{GREEN}Choose mode: {RESET}").strip().upper()
        print()
        
        if choice == '1':
            self.demo_alternating()
        elif choice == '2':
            self.continuous_mode()
        elif choice == '3':
            self.manual_mode()
        else:
            print(f"{CYAN}Exiting...{RESET}\n")
        
        print(f"{GREEN}{BOLD}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}{'OMEGA VOICE PLAYER - SESSION END':^70}{RESET}")
        print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")


def main():
    try:
        player = OmegaVoicePlayer()
        player.run()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[INTERRUPTED]{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[ERROR] {e}{RESET}\n")


if __name__ == "__main__":
    main()
