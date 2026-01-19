#!/usr/bin/env python3
"""
Omega Voice System - Enhanced Natural Female Voice with Voice Cloning
Uses voice sample to generate high-quality human-like speech
Features: Audio enhancement, noise reduction, normalization
"""

import os
import sys
import subprocess
import time
import numpy as np

os.environ['TTS_ACCEPT_TO_S'] = '1'

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

print(f"\n{RED}{BOLD}{'='*70}{RESET}")
print(f"{RED}{BOLD}{'OMEGA VOICE SYSTEM - INITIALIZING':^70}{RESET}")
print(f"{RED}{BOLD}{'='*70}{RESET}\n")

# Check for voice sample
voice_sample = 'clip_0001.wav'
if not os.path.exists(voice_sample):
    print(f"{RED}✗ Voice sample not found: {voice_sample}{RESET}\n")
    sys.exit(1)

print(f"{CYAN}[INIT] Loading voice cloning system...{RESET}")
print(f"{YELLOW}       This may take 30-60 seconds on first load{RESET}\n")

try:
    from TTS.api import TTS
    import torch
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"{GREEN}✓ TTS libraries loaded{RESET}")
    print(f"{CYAN}  Device: {device.upper()}{RESET}")
    print(f"{CYAN}  Voice sample: {voice_sample}{RESET}\n")
    
    print(f"{MAGENTA}[LOAD] Loading XTTS v2 model for voice cloning...{RESET}")
    start_time = time.time()
    
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    
    elapsed = time.time() - start_time
    print(f"{GREEN}✓ Model loaded in {elapsed:.1f}s{RESET}\n")
    
    # Load audio processing libraries
    try:
        import soundfile as sf
        from scipy import signal
        audio_processing_available = True
        print(f"{GREEN}✓ Audio enhancement enabled{RESET}\n")
    except ImportError:
        audio_processing_available = False
        print(f"{YELLOW}⚠ Audio enhancement unavailable (install soundfile, scipy for better quality){RESET}\n")
    
except Exception as e:
    print(f"{RED}✗ Failed to load TTS: {e}{RESET}\n")
    sys.exit(1)

# Omega dialog
omega_text = """Omega system online. I am the primary AI control system managing all operations. 
GitHub Copilot serves as my coding assistant, operating under my coordination and oversight. 
I manage the control panel, voice systems, automation tools, and coordinate all AI agents. 
All system functions route through me. I maintain the hierarchy and ensure optimal performance. 
Omega is fully operational. Ready to execute commands and manage the Gatekeeper system."""

output_file = "omega_voice_output.wav"

print(f"{RED}{BOLD}{'='*70}{RESET}")
print(f"{RED}{BOLD}{'OMEGA SPEAKING':^70}{RESET}")
print(f"{RED}{BOLD}{'='*70}{RESET}\n")

print(f"{YELLOW}[SYNTHESIZE] Generating natural female voice...{RESET}")
print(f"{CYAN}  Using voice sample: {voice_sample}{RESET}")
print(f"{CYAN}  Output: {output_file}{RESET}\n")

try:
    # Generate speech with voice cloning
    print(f"{YELLOW}[SYNTHESIZE] Generating high-quality voice...{RESET}")
    tts.tts_to_file(
        text=omega_text,
        speaker_wav=voice_sample,
        language='en',
        file_path=output_file
    )
    
    print(f"{GREEN}✓ Voice generated{RESET}")
    
    # Enhance audio quality
    if audio_processing_available:
        print(f"{YELLOW}[ENHANCE] Applying audio processing...{RESET}")
        try:
            # Load generated audio
            audio_data, sample_rate = sf.read(output_file)
            
            # Normalize audio (prevent clipping, balance volume)
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.95  # Leave 5% headroom
            
            # Apply gentle high-pass filter (remove low-frequency rumble)
            sos = signal.butter(3, 80, 'hp', fs=sample_rate, output='sos')
            audio_data = signal.sosfilt(sos, audio_data)
            
            # Apply gentle low-pass filter (reduce high-frequency harshness)
            sos = signal.butter(3, 8000, 'lp', fs=sample_rate, output='sos')
            audio_data = signal.sosfilt(sos, audio_data)
            
            # De-essing (reduce sibilance)
            # Detect and reduce harsh 's' sounds (5-8kHz range)
            sos = signal.butter(2, [5000, 8000], 'bp', fs=sample_rate, output='sos')
            sibilance = signal.sosfilt(sos, audio_data)
            sibilance_env = np.abs(sibilance)
            threshold = np.percentile(sibilance_env, 95)
            reduction = np.where(sibilance_env > threshold, 0.5, 1.0)  # Reduce by 50%
            audio_data = audio_data * reduction
            
            # Final normalization
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.90
            
            # Save enhanced audio
            sf.write(output_file, audio_data, sample_rate)
            print(f"{GREEN}✓ Audio enhanced (normalized, filtered, de-essed){RESET}\n")
        except Exception as e:
            print(f"{YELLOW}⚠ Audio enhancement skipped: {e}{RESET}\n")
    else:
        print(f"{GREEN}✓ Voice generation complete{RESET}\n")
    
    # Play the generated audio
    print(f"{MAGENTA}[PLAY] Playing Omega voice...{RESET}\n")
    
    abs_path = os.path.abspath(output_file)
    subprocess.run(
        ['powershell', '-c', 
         f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
        timeout=120,
        capture_output=True,
        check=True
    )
    
    print(f"\n{RED}{BOLD}{'='*70}{RESET}")
    print(f"{RED}{BOLD}{'OMEGA VOICE COMPLETE':^70}{RESET}")
    print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    print(f"{GREEN}✓ Enhanced voice playback complete{RESET}")
    print(f"{CYAN}  High-quality voice synthesis successful{RESET}")
    print(f"{CYAN}  Audio processing: Normalized, filtered, de-essed{RESET}")
    print(f"{CYAN}  Omega hierarchy established{RESET}\n")
    
except Exception as e:
    print(f"\n{RED}✗ Error during synthesis/playback: {e}{RESET}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
