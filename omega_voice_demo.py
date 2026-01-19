"""
OMEGA Voice System - Interactive Demo
Quick voice synthesis and testing with real-time feedback
"""

import os
import sys
import time
from pathlib import Path

os.environ['TTS_ACCEPT_TO_S'] = '1'

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header():
    print(f"\n{RED}{BOLD}{'='*70}{RESET}")
    print(f"{RED}{BOLD}{'OMEGA VOICE SYSTEM - INTERACTIVE DEMO':^70}{RESET}")
    print(f"{RED}{BOLD}{'='*70}{RESET}\n")

def print_status(message, status="INFO"):
    colors = {
        "INFO": CYAN,
        "OK": GREEN,
        "ERROR": RED,
        "WARN": YELLOW,
        "LOAD": MAGENTA
    }
    color = colors.get(status, RESET)
    print(f"{color}[{status}]{RESET} {message}")

def check_voice_files():
    """Check if voice files exist and display info"""
    print_status("Checking voice files...", "LOAD")
    
    voice_files = {
        'clip_0001.wav': 'Original Omega Voice (WARM)',
        'omega_downloaded.wav': 'Enhanced Omega Voice (BRIGHT)'
    }
    
    available = {}
    for file, desc in voice_files.items():
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print_status(f"✓ {file}: {size_mb:.2f} MB - {desc}", "OK")
            available[file] = desc
        else:
            print_status(f"✗ {file}: NOT FOUND", "ERROR")
    
    return available

def load_tts_model():
    """Load TTS model with progress"""
    print_status("Loading TTS model (this may take 30-60 seconds)...", "LOAD")
    
    try:
        from TTS.api import TTS
        import torch
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print_status(f"Device: {device.upper()}", "INFO")
        
        tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
        print_status("TTS model loaded successfully!", "OK")
        return tts, device
    
    except Exception as e:
        print_status(f"Failed to load TTS: {e}", "ERROR")
        return None, None

def synthesize_voice(tts, text, speaker_file, output_file):
    """Synthesize speech with timing"""
    print_status(f"Synthesizing: '{text[:50]}...'", "LOAD")
    print_status(f"Voice: {speaker_file}", "INFO")
    
    start_time = time.time()
    
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_file,
            language='en',
            file_path=output_file
        )
        
        elapsed = time.time() - start_time
        
        if os.path.exists(output_file):
            size_kb = os.path.getsize(output_file) / 1024
            print_status(f"Generated: {output_file} ({size_kb:.1f} KB) in {elapsed:.2f}s", "OK")
            return True
        else:
            print_status("Output file not created", "ERROR")
            return False
    
    except Exception as e:
        print_status(f"Synthesis failed: {e}", "ERROR")
        return False

def play_audio(file_path):
    """Play audio file using Windows default player"""
    if not os.path.exists(file_path):
        print_status(f"File not found: {file_path}", "ERROR")
        return False
    
    try:
        import subprocess
        print_status(f"Playing: {file_path}", "INFO")
        subprocess.Popen(['powershell', '-c', f'(New-Object Media.SoundPlayer "{file_path}").PlaySync()'])
        return True
    except Exception as e:
        print_status(f"Playback error: {e}", "WARN")
        return False

def interactive_demo(tts, available_voices):
    """Interactive voice synthesis demo"""
    print(f"\n{YELLOW}{BOLD}{'='*70}{RESET}")
    print(f"{YELLOW}{BOLD}{'INTERACTIVE MODE':^70}{RESET}")
    print(f"{YELLOW}{BOLD}{'='*70}{RESET}\n")
    
    demo_phrases = [
        "I am Omega. My voice synthesis system is now fully operational.",
        "All systems are online and ready for deployment.",
        "Voice cloning has achieved optimal parameters for natural speech.",
        "I can now communicate with perfect clarity and expressiveness."
    ]
    
    print_status("Demo Phrases Available:", "INFO")
    for i, phrase in enumerate(demo_phrases, 1):
        print(f"  {i}. {phrase}")
    print(f"  {CYAN}C.{RESET} Custom text")
    print(f"  {RED}Q.{RESET} Quit\n")
    
    voices = list(available_voices.keys())
    
    while True:
        choice = input(f"\n{GREEN}Select option (1-{len(demo_phrases)}/C/Q):{RESET} ").strip().upper()
        
        if choice == 'Q':
            print_status("Exiting demo mode", "INFO")
            break
        
        if choice == 'C':
            text = input(f"{GREEN}Enter custom text:{RESET} ").strip()
            if not text:
                print_status("No text entered", "WARN")
                continue
        elif choice.isdigit() and 1 <= int(choice) <= len(demo_phrases):
            text = demo_phrases[int(choice) - 1]
        else:
            print_status("Invalid choice", "WARN")
            continue
        
        print_status("Available voices:", "INFO")
        for i, (file, desc) in enumerate(available_voices.items(), 1):
            print(f"  {i}. {desc} ({file})")
        
        voice_choice = input(f"{GREEN}Select voice (1-{len(voices)}):{RESET} ").strip()
        
        if not voice_choice.isdigit() or not (1 <= int(voice_choice) <= len(voices)):
            print_status("Invalid voice selection", "WARN")
            continue
        
        speaker_file = voices[int(voice_choice) - 1]
        output_file = f"omega_output_{int(time.time())}.wav"
        
        if synthesize_voice(tts, text, speaker_file, output_file):
            play_choice = input(f"{GREEN}Play audio? (Y/n):{RESET} ").strip().upper()
            if play_choice != 'N':
                play_audio(output_file)

def quick_demo(tts, available_voices):
    """Quick demo without interaction"""
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{'QUICK DEMO MODE':^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")
    
    text = "I am Omega. My voice synthesis system is now fully operational and ready for deployment."
    
    for speaker_file in available_voices.keys():
        output_file = f"omega_demo_{Path(speaker_file).stem}.wav"
        synthesize_voice(tts, text, speaker_file, output_file)
        print()
    
    print_status("Quick demo complete!", "OK")

def main():
    print_header()
    
    available_voices = check_voice_files()
    
    if not available_voices:
        print_status("No voice files found. Please ensure voice files are present.", "ERROR")
        return
    
    print()
    
    tts, device = load_tts_model()
    
    if not tts:
        print_status("Cannot proceed without TTS model", "ERROR")
        return
    
    print()
    
    print(f"{CYAN}Demo Modes:{RESET}")
    print(f"  {CYAN}1.{RESET} Interactive Mode (custom text & voice selection)")
    print(f"  {CYAN}2.{RESET} Quick Demo (generate samples with all voices)")
    print(f"  {CYAN}Q.{RESET} Quit\n")
    
    mode = input(f"{GREEN}Select mode (1/2/Q):{RESET} ").strip().upper()
    
    if mode == '1':
        interactive_demo(tts, available_voices)
    elif mode == '2':
        quick_demo(tts, available_voices)
    else:
        print_status("Exiting", "INFO")
    
    print(f"\n{GREEN}{BOLD}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}{'OMEGA VOICE DEMO COMPLETE':^70}{RESET}")
    print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[INTERRUPTED] Demo stopped by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[ERROR] {e}{RESET}\n")
        import traceback
        traceback.print_exc()
