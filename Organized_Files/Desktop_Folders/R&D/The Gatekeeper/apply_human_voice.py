# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
APPLY HUMAN VOICE PARAMETERS
Directly update voice signature to sound human
"""

import json
from pathlib import Path

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

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
    'quantum_phase': 0.0,  # Reset phase
}

def apply_human_voice():
    """Apply human voice parameters directly to signature file."""
    waveform_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
    
    # Load existing signature or create new
    if waveform_file.exists():
        try:
            with open(waveform_file, 'r', encoding='utf-8') as f:
                signature = json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load existing signature: {e}")
            signature = {}
    else:
        signature = {}
    
    # Update with human parameters
    print("[Updating] Voice signature with human parameters...")
    signature.update(HUMAN_VOICE_PARAMS)
    
    # Ensure all required fields
    if 'sample_rate' not in signature:
        signature['sample_rate'] = 44100
    
    # Save updated signature
    try:
        with open(waveform_file, 'w', encoding='utf-8') as f:
            json.dump(signature, f, indent=2, ensure_ascii=False)
        print(f"[OK] Voice signature saved to {waveform_file}")
    except Exception as e:
        print(f"[ERROR] Failed to save signature: {e}")
        return False
    
    print("\n[Human Parameters Applied]:")
    for key, value in HUMAN_VOICE_PARAMS.items():
        print(f"  {key}: {value}")
    
    return True

def main():
    """Main function."""
    print("=" * 80)
    print("APPLYING HUMAN VOICE PARAMETERS")
    print("Making Omega sound like a real human")
    print("=" * 80)
    print()
    
    if apply_human_voice():
        print("\n" + "=" * 80)
        print("HUMANIZATION COMPLETE")
        print("=" * 80)
        print("\nOmega's voice signature has been updated with human parameters:")
        print("  [OK] Natural frequency range (135 Hz)")
        print("  [OK] Natural modulation (12% variation)")
        print("  [OK] Rich harmonics (35% ratio)")
        print("  [OK] Natural prosody (18% variation)")
        print("  [OK] Human-like envelope (attack/decay/sustain/release)")
        print("\nThe voice should now sound more human:")
        print("  - Not robotic")
        print("  - Not smooth")
        print("  - Alive and real")
        print("\nTest it by running: python -c \"from omega_voice import OmegaVoice; v = OmegaVoice(); v.speak('Hello, I sound more human now.')\"")
    else:
        print("\n[ERROR] Humanization failed")

if __name__ == '__main__':
    main()

