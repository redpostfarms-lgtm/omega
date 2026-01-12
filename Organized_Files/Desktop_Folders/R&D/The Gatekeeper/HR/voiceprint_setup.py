#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# VOICEPRINT SETUP - Record your voiceprint for Harriet

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r'D:\RPF_BRAIN\HR')
VOICEPRINT = ROOT / 'harriet_waveform.wav'

try:
    import speech_recognition as sr
    import pyaudio
    import wave
except ImportError:
    print("[ERROR] Required packages not installed:")
    print("  pip install SpeechRecognition pyaudio")
    sys.exit(1)

def record_voiceprint():
    """Record voiceprint for Harriet."""
    print("=" * 60)
    print("HARRIET VOICEPRINT SETUP")
    print("=" * 60)
    print()
    print("Speak the phrase: 'Harriet, this is my voiceprint'")
    print("Recording in 3 seconds...")
    print()
    
    import time
    time.sleep(3)
    
    # Record audio
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 5
    
    p = pyaudio.PyAudio()
    
    print("Recording...")
    
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []
    
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("Recording complete.")
    
    # Save to file
    ROOT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(VOICEPRINT), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
    
    print(f"Voiceprint saved to: {VOICEPRINT}")
    print("Harriet is now voiceprint-locked to your voice.")

if __name__ == '__main__':
    record_voiceprint()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

