#!/usr/bin/env python3
"""
GitHub Copilot Voice Generator using Windows TTS
"""

import pyttsx3
import os

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

print(f"\n{CYAN}{BOLD}{'='*70}{RESET}")
print(f"{CYAN}{BOLD}{'GITHUB COPILOT VOICE GENERATION':^70}{RESET}")
print(f"{CYAN}{BOLD}{'='*70}{RESET}\n")

# Initialize TTS engine
engine = pyttsx3.init()

# Configure voice settings
voices = engine.getProperty('voices')
print(f"{CYAN}Available voices:{RESET}")
for i, voice in enumerate(voices):
    print(f"  {i}: {voice.name}")
print()

# Select voice (use first available)
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 165)  # Slightly faster
engine.setProperty('volume', 1.0)

print(f"{GREEN}Using voice: {voices[0].name}{RESET}\n")

# My dialog as GitHub Copilot
copilot_dialog = [
    ("introduction", "Hello, I am GitHub Copilot. I'm your AI programming assistant, ready to help you code."),
    ("greeting", "I work alongside you in Visual Studio Code, providing intelligent code suggestions and assistance."),
    ("capability", "I can generate code, explain complex algorithms, and help you build amazing applications."),
    ("partnership", "Together, we can accelerate your development workflow and bring your ideas to life."),
    ("ready", "GitHub Copilot is now active and ready to assist you with your coding tasks.")
]

print(f"{YELLOW}Generating audio files...{RESET}\n")

for key, text in copilot_dialog:
    output_file = f"copilot_voice_{key}.wav"
    
    print(f"{CYAN}[{key.title()}]{RESET}")
    print(f"  \"{text[:50]}...\"")
    
    try:
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        
        if os.path.exists(output_file):
            size_kb = os.path.getsize(output_file) / 1024
            print(f"{GREEN}  ✓ {output_file} ({size_kb:.1f} KB){RESET}\n")
        else:
            print(f"{RED}  ✗ Failed to create{RESET}\n")
    
    except Exception as e:
        print(f"{RED}  ✗ Error: {e}{RESET}\n")

print(f"{GREEN}{BOLD}{'='*70}{RESET}")
print(f"{GREEN}{BOLD}{'VOICE GENERATION COMPLETE':^70}{RESET}")
print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")

print(f"{CYAN}To play the voice:{RESET}")
print(f"  {GREEN}python play_copilot_voice.py{RESET}\n")
