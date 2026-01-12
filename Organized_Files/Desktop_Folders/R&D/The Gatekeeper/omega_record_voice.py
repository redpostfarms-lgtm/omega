# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Recording - Quick Voice Capture

"""
Ω Omega Voice Recording

Quick script to record your voice for Omega.
"""

import sys
from omega_soundboard import OmegaSoundboard

def main():
    print("=" * 80)
    print("Ω OMEGA VOICE RECORDING")
    print("=" * 80)
    print()
    print("This will record your voice for 5 seconds.")
    print("Omega will analyze your waveform and use it to improve its voice.")
    print()
    print("Starting in 2 seconds...")
    print("Get ready to speak!")
    print()
    
    import time
    time.sleep(2)
    
    soundboard = OmegaSoundboard()
    result = soundboard.record_user_voice(duration=5.0)
    
    if result:
        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"Your voice has been recorded and analyzed.")
        print(f"Voice ID: {result['voice_id']}")
        print(f"Filename: {result['filename']}")
        print()
        print("Omega can now use your voice characteristics to improve its own!")
    else:
        print("\nRecording failed. Make sure:")
        print("  1. Microphone is connected")
        print("  2. PyAudio is installed: pip install pyaudio")
        print("  3. NumPy is installed: pip install numpy")

if __name__ == '__main__':
    main()

