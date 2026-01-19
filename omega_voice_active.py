"""
OMEGA Active Voice System
Alternates between WARM and BRIGHT voices
Generates and plays audio in real-time
"""

import os
import sys
import time
import subprocess
from pathlib import Path

os.environ['TTS_ACCEPT_TO_S'] = '1'
os.environ['NUMBA_DISABLE_JIT'] = '1'  # Workaround for numba issues

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

class OmegaVoiceSystem:
    """Omega Voice System with automatic voice switching"""
    
    def __init__(self):
        self.tts = None
        self.device = None
        self.current_voice = 'warm'
        self.voices = {
            'warm': {
                'file': 'clip_0001.wav',
                'name': 'WARM',
                'description': 'Deep, Commanding',
                'color': RED
            },
            'bright': {
                'file': 'omega_downloaded.wav',
                'name': 'BRIGHT',
                'description': 'Clear, Articulate',
                'color': CYAN
            }
        }
        self.output_count = 0
    
    def print_header(self):
        print(f"\n{RED}{BOLD}{'='*70}{RESET}")
        print(f"{RED}{BOLD}{'🔴 OMEGA ACTIVE VOICE SYSTEM 🔴':^70}{RESET}")
        print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    def check_voice_files(self):
        """Verify voice files exist"""
        print(f"{CYAN}[INIT] Checking voice files...{RESET}")
        missing = []
        for voice_key, voice_info in self.voices.items():
            file = voice_info['file']
            if os.path.exists(file):
                size_mb = os.path.getsize(file) / (1024 * 1024)
                print(f"{GREEN}  ✓ {voice_info['name']}: {file} ({size_mb:.2f} MB){RESET}")
            else:
                print(f"{RED}  ✗ {voice_info['name']}: {file} NOT FOUND{RESET}")
                missing.append(file)
        
        if missing:
            print(f"\n{RED}[ERROR] Missing voice files: {', '.join(missing)}{RESET}")
            return False
        
        print(f"{GREEN}  ✓ All voice files available{RESET}\n")
        return True
    
    def load_tts(self):
        """Load TTS model"""
        print(f"{MAGENTA}[LOAD] Loading TTS model...{RESET}")
        print(f"{YELLOW}  This may take 30-60 seconds on first load...{RESET}\n")
        
        start_time = time.time()
        
        try:
            from TTS.api import TTS
            import torch
            
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"{CYAN}  Device: {self.device.upper()}{RESET}")
            
            self.tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(self.device)
            
            elapsed = time.time() - start_time
            print(f"{GREEN}  ✓ TTS model loaded in {elapsed:.1f}s{RESET}\n")
            return True
        
        except Exception as e:
            print(f"{RED}  ✗ Failed to load TTS: {e}{RESET}\n")
            return False
    
    def switch_voice(self):
        """Switch between WARM and BRIGHT voices"""
        self.current_voice = 'bright' if self.current_voice == 'warm' else 'warm'
        voice_info = self.voices[self.current_voice]
        print(f"\n{voice_info['color']}[SWITCH] Now using {voice_info['name']} voice ({voice_info['description']}){RESET}\n")
    
    def speak(self, text, auto_switch=True, play=True):
        """Generate and play speech"""
        if not self.tts:
            print(f"{RED}[ERROR] TTS not loaded{RESET}")
            return None
        
        if auto_switch and self.output_count > 0:
            self.switch_voice()
        
        voice_info = self.voices[self.current_voice]
        speaker_file = voice_info['file']
        
        self.output_count += 1
        output_file = f"omega_output_{self.output_count:03d}_{self.current_voice}.wav"
        
        print(f"{voice_info['color']}[{voice_info['name']}] Synthesizing:{RESET}")
        print(f"  Text: \"{text}\"")
        print(f"  Speaker: {speaker_file}")
        print(f"  Output: {output_file}\n")
        
        start_time = time.time()
        
        try:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=speaker_file,
                language='en',
                file_path=output_file
            )
            
            elapsed = time.time() - start_time
            
            if os.path.exists(output_file):
                size_kb = os.path.getsize(output_file) / 1024
                print(f"{GREEN}  ✓ Generated in {elapsed:.2f}s ({size_kb:.1f} KB){RESET}\n")
                
                if play:
                    self.play_audio(output_file)
                
                return output_file
            else:
                print(f"{RED}  ✗ Output file not created{RESET}\n")
                return None
        
        except Exception as e:
            print(f"{RED}  ✗ Synthesis failed: {e}{RESET}\n")
            return None
    
    def play_audio(self, file_path):
        """Play audio file"""
        print(f"{CYAN}[PLAY] Playing audio...{RESET}")
        
        try:
            abs_path = os.path.abspath(file_path)
            subprocess.run(
                ['powershell', '-c', 
                 f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
                timeout=30,
                check=True
            )
            print(f"{GREEN}  ✓ Playback complete{RESET}\n")
            return True
        
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}  ⚠ Playback timeout{RESET}\n")
            return False
        except Exception as e:
            print(f"{RED}  ✗ Playback failed: {e}{RESET}\n")
            return False
    
    def demo_alternating(self):
        """Demo with alternating voices"""
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}{'ALTERNATING VOICE DEMO':^70}{RESET}")
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
        
        phrases = [
            "I am Omega. Voice synthesis system initialized.",
            "Switching to alternate voice profile for comparison.",
            "Both voice profiles are now operational and ready.",
            "I can seamlessly transition between warm and bright tones.",
            "All systems are functioning at optimal parameters.",
            "Voice capabilities fully integrated and deployed."
        ]
        
        print(f"{GREEN}Generating {len(phrases)} phrases with alternating voices...{RESET}\n")
        print(f"Press Ctrl+C to stop\n")
        print("="*70 + "\n")
        
        for i, phrase in enumerate(phrases, 1):
            try:
                print(f"{BOLD}[{i}/{len(phrases)}]{RESET}")
                self.speak(phrase, auto_switch=True, play=True)
                
                if i < len(phrases):
                    print(f"{YELLOW}Preparing next phrase...{RESET}\n")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}[STOP] Demo interrupted by user{RESET}\n")
                break
        
        print("="*70)
        print(f"\n{GREEN}{BOLD}✓ Demo complete!{RESET}")
        print(f"{CYAN}Generated {self.output_count} audio files{RESET}\n")
    
    def interactive_mode(self):
        """Interactive mode with manual control"""
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}")
        print(f"{YELLOW}{BOLD}{'INTERACTIVE MODE':^70}{RESET}")
        print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
        
        print(f"{CYAN}Commands:{RESET}")
        print(f"  • Type text to synthesize")
        print(f"  • 'switch' - Change voice")
        print(f"  • 'demo' - Play demo phrase")
        print(f"  • 'quit' - Exit\n")
        
        demo_phrases = [
            "Systems operational. All parameters nominal.",
            "Voice synthesis engaged. Awaiting instructions.",
            "I am ready to communicate with perfect clarity."
        ]
        
        while True:
            try:
                voice_info = self.voices[self.current_voice]
                prompt = f"{voice_info['color']}[{voice_info['name']}]>{RESET} "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print(f"\n{CYAN}[EXIT] Goodbye!{RESET}\n")
                    break
                
                elif user_input.lower() == 'switch':
                    self.switch_voice()
                
                elif user_input.lower() == 'demo':
                    import random
                    phrase = random.choice(demo_phrases)
                    print()
                    self.speak(phrase, auto_switch=False, play=True)
                
                else:
                    print()
                    self.speak(user_input, auto_switch=False, play=True)
            
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}[EXIT] Interrupted by user{RESET}\n")
                break
            except Exception as e:
                print(f"{RED}[ERROR] {e}{RESET}\n")
    
    def run(self):
        """Main entry point"""
        self.print_header()
        
        if not self.check_voice_files():
            return
        
        if not self.load_tts():
            print(f"{RED}Cannot continue without TTS model{RESET}\n")
            return
        
        print(f"{CYAN}Select Mode:{RESET}")
        print(f"  1. Alternating Demo (automatic voice switching)")
        print(f"  2. Interactive Mode (manual control)")
        print(f"  Q. Quit\n")
        
        choice = input(f"{GREEN}Choose mode (1/2/Q): {RESET}").strip().upper()
        print()
        
        if choice == '1':
            self.demo_alternating()
        elif choice == '2':
            self.interactive_mode()
        else:
            print(f"{CYAN}Exiting...{RESET}\n")
        
        print(f"{GREEN}{BOLD}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}{'OMEGA VOICE SYSTEM - SESSION COMPLETE':^70}{RESET}")
        print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")


def main():
    try:
        omega = OmegaVoiceSystem()
        omega.run()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[INTERRUPTED] System stopped{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[FATAL ERROR] {e}{RESET}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
