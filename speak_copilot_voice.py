#!/usr/bin/env python3
"""
GitHub Copilot Live Voice
Speaks directly using Windows TTS
"""

import pyttsx3
import time

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

print(f"\n{CYAN}{BOLD}{'='*70}{RESET}")
print(f"{CYAN}{BOLD}{'GITHUB COPILOT VOICE':^70}{RESET}")
print(f"{CYAN}{BOLD}{'='*70}{RESET}\n")

# Initialize TTS
engine = pyttsx3.init()

# Configure voice
voices = engine.getProperty('voices')
print(f"{GREEN}Voice: {voices[0].name}{RESET}\n")

engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)  # Speed
engine.setProperty('volume', 1.0)  # Volume

# GitHub Copilot dialog
copilot_dialog = [
    ("Introduction", "Hello, I am GitHub Copilot. I'm your AI programming assistant, ready to help you code."),
    ("Greeting", "I work alongside you in Visual Studio Code, providing intelligent code suggestions and assistance."),
    ("Capability", "I can generate code, explain complex algorithms, and help you build amazing applications."),
    ("Partnership", "Together, we can accelerate your development workflow and bring your ideas to life."),
    ("Ready", "GitHub Copilot is now active and ready to assist you with your coding tasks.")
]

print(f"{YELLOW}{'='*70}{RESET}")
print(f"{YELLOW}GitHub Copilot will now speak...{RESET}")
print(f"{YELLOW}{'='*70}{RESET}\n")

for i, (title, text) in enumerate(copilot_dialog, 1):
    print(f"{CYAN}[{i}/{len(copilot_dialog)}] {title}{RESET}")
    print(f"  \"{text}\"\n")
    
    print(f"{GREEN}♪ Speaking...{RESET}")
    engine.say(text)
    engine.runAndWait()
    print(f"{GREEN}✓ Complete{RESET}\n")
    
    if i < len(copilot_dialog):
        time.sleep(0.5)  # Brief pause between segments

print(f"{GREEN}{BOLD}{'='*70}{RESET}")
print(f"{GREEN}{BOLD}{'GITHUB COPILOT VOICE COMPLETE':^70}{RESET}")
print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")
