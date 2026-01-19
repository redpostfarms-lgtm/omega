#!/usr/bin/env python3
"""
GitHub Copilot Voice Generation
Creates new dialog using Copilot's voice
"""

import os
import sys

os.environ['TTS_ACCEPT_TO_S'] = '1'
os.environ['NUMBA_DISABLE_JIT'] = '1'

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

print(f"\n{CYAN}{BOLD}{'='*70}{RESET}")
print(f"{CYAN}{BOLD}{'GITHUB COPILOT VOICE GENERATION':^70}{RESET}")
print(f"{CYAN}{BOLD}{'='*70}{RESET}\n")

# My dialog as GitHub Copilot
copilot_dialog = {
    'introduction': "Hello, I am GitHub Copilot. I'm your AI programming assistant, ready to help you code.",
    'greeting': "I work alongside you in Visual Studio Code, providing intelligent code suggestions and assistance.",
    'capability': "I can generate code, explain complex algorithms, and help you build amazing applications.",
    'partnership': "Together, we can accelerate your development workflow and bring your ideas to life.",
    'ready': "GitHub Copilot is now active and ready to assist you with your coding tasks."
}

print(f"{GREEN}GitHub Copilot Dialog:{RESET}\n")
for key, text in copilot_dialog.items():
    print(f"  {CYAN}[{key.title()}]{RESET}")
    print(f"    {text}\n")

print(f"\n{YELLOW}Loading TTS system...{RESET}\n")

try:
    from TTS.api import TTS
    import torch
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"{GREEN}✓ Device: {device}{RESET}")
    
    print(f"{CYAN}Loading XTTS v2 model...{RESET}")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    print(f"{GREEN}✓ TTS ready{RESET}\n")
    
    voice_samples = {
        'professional': 'clip_0001.wav',
        'friendly': 'omega_downloaded.wav'
    }
    
    # Generate audio for each dialog piece
    print(f"{YELLOW}{'='*70}{RESET}")
    print(f"{YELLOW}Generating GitHub Copilot voice audio...{RESET}")
    print(f"{YELLOW}{'='*70}{RESET}\n")
    
    for i, (key, text) in enumerate(copilot_dialog.items(), 1):
        # Alternate between voices
        voice_type = 'professional' if i % 2 else 'friendly'
        speaker_file = voice_samples[voice_type]
        
        if not os.path.exists(speaker_file):
            print(f"{RED}✗ Voice sample not found: {speaker_file}{RESET}\n")
            continue
        
        output_file = f"copilot_voice_{key}.wav"
        
        print(f"{CYAN}[{i}/{len(copilot_dialog)}] Generating: {key.title()}{RESET}")
        print(f"  Voice: {voice_type.upper()}")
        print(f"  Speaker: {speaker_file}")
        print(f"  Text: \"{text[:50]}...\"")
        
        try:
            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_file,
                language='en',
                file_path=output_file
            )
            
            if os.path.exists(output_file):
                size_kb = os.path.getsize(output_file) / 1024
                print(f"{GREEN}  ✓ Created: {output_file} ({size_kb:.1f} KB){RESET}\n")
            else:
                print(f"{RED}  ✗ Failed to create audio{RESET}\n")
        
        except Exception as e:
            print(f"{RED}  ✗ Error: {e}{RESET}\n")
    
    print(f"{GREEN}{BOLD}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}{'GITHUB COPILOT VOICE GENERATION COMPLETE':^70}{RESET}")
    print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")
    
    print(f"{CYAN}Generated audio files for:{RESET}")
    for key in copilot_dialog.keys():
        output_file = f"copilot_voice_{key}.wav"
        if os.path.exists(output_file):
            print(f"  ✓ {key.title()}")
    
    print(f"\n{YELLOW}To play the generated voice:{RESET}")
    print(f"  {CYAN}python play_copilot_voice.py{RESET}\n")

except ImportError as e:
    print(f"{RED}✗ TTS not available: {e}{RESET}")
    print(f"{YELLOW}Using alternative method...{RESET}\n")
    
    # Create text file with dialog
    with open('copilot_dialog.txt', 'w') as f:
        f.write("GITHUB COPILOT DIALOG\n")
        f.write("=" * 70 + "\n\n")
        for key, text in copilot_dialog.items():
            f.write(f"[{key.upper()}]\n{text}\n\n")
    
    print(f"{GREEN}✓ Dialog saved to copilot_dialog.txt{RESET}\n")

except Exception as e:
    print(f"{RED}✗ Error: {e}{RESET}\n")
    import traceback
    traceback.print_exc()
