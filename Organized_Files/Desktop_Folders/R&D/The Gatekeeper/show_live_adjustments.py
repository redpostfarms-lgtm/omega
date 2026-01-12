# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Omega Live Voice Adjustments Demonstration

import sys
import io
import json
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
OMEGA_VOICE_DIR = GATE / 'omega_voice'
SIGNATURE_FILE = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'

# Load signature
if SIGNATURE_FILE.exists():
    with open(SIGNATURE_FILE, 'r', encoding='utf-8') as f:
        sig = json.load(f)
else:
    sig = {
        'base_frequency': 135.0,
        'modulation_depth': 0.135,
        'modulation_rate': 2.5,
        'harmonic_ratio': 0.30,
        'resonance_peak': 2300.0,
        'prosody_variation': 0.126
    }

print("=" * 80)
print("OMEGA LIVE VOICE ADJUSTMENTS")
print("=" * 80)

# Show current
print("\nCURRENT SIGNATURE:")
print(f"  Base Frequency: {sig.get('base_frequency', 135.0):.2f} Hz")
print(f"  Harmonic Ratio: {sig.get('harmonic_ratio', 0.30):.3f}")
print(f"  Resonance Peak: {sig.get('resonance_peak', 2300.0):.1f} Hz")

# Adjustment 1
orig1 = sig.copy()
sig['base_frequency'] = sig.get('base_frequency', 135.0) - 3.0
sig['harmonic_ratio'] = min(0.35, sig.get('harmonic_ratio', 0.30) * 1.15)
sig['resonance_peak'] = sig.get('resonance_peak', 2300.0) - 100.0

print("\n" + "=" * 80)
print("LIVE ADJUSTMENT 1: DEEPER & RICHER VOICE")
print("=" * 80)
print(f"\nBase Frequency: {orig1.get('base_frequency', 135.0):.2f} Hz → {sig['base_frequency']:.2f} Hz ({sig['base_frequency'] - orig1.get('base_frequency', 135.0):+.2f} Hz)")
print(f"Harmonic Ratio: {orig1.get('harmonic_ratio', 0.30):.3f} → {sig['harmonic_ratio']:.3f} (+{sig['harmonic_ratio'] - orig1.get('harmonic_ratio', 0.30):+.3f})")
print(f"Resonance Peak: {orig1.get('resonance_peak', 2300.0):.1f} Hz → {sig['resonance_peak']:.1f} Hz ({sig['resonance_peak'] - orig1.get('resonance_peak', 2300.0):+.1f} Hz)")

with open(SIGNATURE_FILE, 'w', encoding='utf-8') as f:
    json.dump(sig, f, indent=2)
print("\n✓ Adjustment 1 saved!")

# Adjustment 2
orig2 = sig.copy()
sig['modulation_rate'] = max(2.3, min(2.7, sig.get('modulation_rate', 2.5) * 1.04))
sig['prosody_variation'] = max(0.12, min(0.16, sig.get('prosody_variation', 0.126) * 1.08))
sig['resonance_peak'] = min(2350.0, sig.get('resonance_peak', 2300.0) + 50.0)

print("\n" + "=" * 80)
print("LIVE ADJUSTMENT 2: CLEARER & MORE NATURAL VOICE")
print("=" * 80)
print(f"\nModulation Rate: {orig2.get('modulation_rate', 2.5):.2f} Hz → {sig['modulation_rate']:.2f} Hz ({sig['modulation_rate'] - orig2.get('modulation_rate', 2.5):+.2f} Hz)")
print(f"Prosody Variation: {orig2.get('prosody_variation', 0.126):.3f} → {sig['prosody_variation']:.3f} (+{sig['prosody_variation'] - orig2.get('prosody_variation', 0.126):+.3f})")
print(f"Resonance Peak: {orig2.get('resonance_peak', 2300.0):.1f} Hz → {sig['resonance_peak']:.1f} Hz ({sig['resonance_peak'] - orig2.get('resonance_peak', 2300.0):+.1f} Hz)")

with open(SIGNATURE_FILE, 'w', encoding='utf-8') as f:
    json.dump(sig, f, indent=2)
print("\n✓ Adjustment 2 saved!")

# Final
print("\n" + "=" * 80)
print("FINAL SIGNATURE")
print("=" * 80)
print(f"\nBase Frequency: {sig['base_frequency']:.2f} Hz")
print(f"Modulation Depth: {sig.get('modulation_depth', 0.135):.3f}")
print(f"Modulation Rate: {sig['modulation_rate']:.2f} Hz")
print(f"Harmonic Ratio: {sig['harmonic_ratio']:.3f}")
print(f"Resonance Peak: {sig['resonance_peak']:.1f} Hz")
print(f"Prosody Variation: {sig['prosody_variation']:.3f}")
print("\n✓ Omega will use this updated voice on next initialization!")
print("=" * 80)

