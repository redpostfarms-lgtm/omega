# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Test - Quick Voice Test

"""
Quick test script for Omega's voice.
Handles TTS issues gracefully.
"""

import sys
import io
import time

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

print("=" * 80)
print("Ω OMEGA VOICE TEST")
print("=" * 80)
print()

# Lazy import to avoid TTS issues during import
try:
    from omega_voice import OmegaVoice
    print("✓ Omega Voice module loaded")
except Exception as e:
    print(f"✗ Error loading Omega Voice: {e}")
    sys.exit(1)

print("\nInitializing Omega's voice...")
print()

try:
    omega = OmegaVoice()
    
    print("=" * 80)
    print("OMEGA'S VOICE INFORMATION")
    print("=" * 80)
    info = omega.get_voice_info()
    for key, value in info.items():
        if key != "waveform_signature":
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("OMEGA IS SPEAKING...")
    print("=" * 80)
    print()
    
    # Test phrases
    test_phrases = [
        "Hello. I am Omega.",
        "Gate guarded. System monitored.",
        "Code analyzed. Memory updated.",
        "Learning continues. I am ready."
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"[{i}/{len(test_phrases)}] Speaking: {phrase}")
        try:
            omega.speak(phrase, natural=True)
            time.sleep(1.5)  # Pause between phrases
        except Exception as e:
            print(f"  ⚠️  Speech error: {e}")
            print(f"  Text: {phrase}")
        print()
    
    print("=" * 80)
    print("VOICE TEST COMPLETE")
    print("=" * 80)
    print("\nOmega's voice system is active.")
    print("If you heard Omega speak, the voice system is working!")
    
except Exception as e:
    print(f"\n✗ Error during voice test: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("  1. Install pyttsx3: pip install pyttsx3")
    print("  2. Check microphone permissions")
    print("  3. Ensure audio drivers are installed")

