# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
VOICE HUMANIZATION - SIMPLE VERSION
Make Omega sound like a real human
"""

import sys
import json
import time
from pathlib import Path

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

try:
    from omega_voice import OmegaVoice, OmegaWaveform
    OMEGA_VOICE_AVAILABLE = True
except ImportError:
    OMEGA_VOICE_AVAILABLE = False

# Human voice parameters (optimized for natural human speech)
HUMAN_VOICE_PARAMS = {
    'base_frequency': 135.0,  # Hz (average male voice: 120-150 Hz)
    'modulation_depth': 0.12,  # Natural variation (not robotic)
    'modulation_rate': 2.8,  # Hz (natural speech rhythm)
    'harmonic_ratio': 0.35,  # Rich harmonics (human voice has many)
    'resonance_peak': 2400.0,  # Hz (natural formant)
    'prosody_variation': 0.18,  # More variation = more human
    'attack_time': 0.03,  # Slightly slower attack
    'decay_time': 0.15,  # Natural decay
    'sustain_level': 0.72,  # Slightly lower sustain
    'release_time': 0.18,  # Longer release (breath)
}

def apply_humanization():
    """Apply human voice parameters to Omega."""
    if not OMEGA_VOICE_AVAILABLE:
        print("[ERROR] Omega Voice not available")
        return False
    
    try:
        voice = OmegaVoice()
        
        print("[Updating] Voice signature with human parameters...")
        voice.waveform.signature.update(HUMAN_VOICE_PARAMS)
        voice.waveform._save_signature()
        
        print("[✓] Voice signature updated")
        print("\n[Human Parameters Applied]:")
        for key, value in HUMAN_VOICE_PARAMS.items():
            print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False

def test_voice():
    """Test the humanized voice."""
    if not OMEGA_VOICE_AVAILABLE:
        print("[ERROR] Omega Voice not available")
        return False
    
    try:
        voice = OmegaVoice()
        
        test_phrases = [
            "Hello. I'm Omega, and I sound more human now.",
            "How are you? I can have natural pauses and variations.",
            "Yeah... I think this is working better.",
            "No. That's not quite right, but it's getting there.",
            "Ruth... it's three in the morning...",
            "and the worms are singing again.",
            "You awake?",
        ]
        
        print("\n[Testing] Humanized voice...")
        for phrase in test_phrases:
            print(f"\n[Speaking] {phrase}")
            voice.speak(phrase, natural=True)
            time.sleep(0.8)
        
        print("\n[✓] Voice test complete!")
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 80)
    print("VOICE HUMANIZATION")
    print("Making Omega sound like a real human")
    print("=" * 80)
    
    # Apply humanization
    if apply_humanization():
        print("\n" + "=" * 80)
        print("Testing humanized voice...")
        print("=" * 80)
        test_voice()
    
    print("\n" + "=" * 80)
    print("HUMANIZATION COMPLETE")
    print("=" * 80)
    print("\nOmega's voice should now sound more human:")
    print("  ✓ Natural pauses and variations")
    print("  ✓ Human-like prosody")
    print("  ✓ Natural speech rhythm")
    print("  ✓ Not robotic, not smooth - alive and real")

if __name__ == '__main__':
    main()

