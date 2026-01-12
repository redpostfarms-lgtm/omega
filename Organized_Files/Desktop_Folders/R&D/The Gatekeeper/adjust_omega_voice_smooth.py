# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Smooth Refinement
# Applies additional adjustments for smoother, more natural voice

"""
Ω Omega Voice Smooth Refinement

Refines Omega's voice for smoother, more natural speech.
Applies additional adjustments to make the voice flow better.
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
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

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)


def load_current_signature():
    """Load current voice signature."""
    # Priority: improved > blended > original
    improved_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
    blended_file = OMEGA_VOICE_DIR / 'blended_voice.json'
    waveform_file = OMEGA_VOICE_DIR / 'omega_waveform.json'
    
    signature = {}
    
    if improved_file.exists():
        try:
            with open(improved_file, 'r', encoding='utf-8') as f:
                signature = json.load(f)
            print("✓ Loaded improved waveform signature")
        except Exception:
            pass
    
    if not signature and blended_file.exists():
        try:
            with open(blended_file, 'r', encoding='utf-8') as f:
                signature = json.load(f)
            print("✓ Loaded blended voice signature")
        except Exception:
            pass
    
    if not signature and waveform_file.exists():
        try:
            with open(waveform_file, 'r', encoding='utf-8') as f:
                signature = json.load(f)
            print("✓ Loaded original waveform signature")
        except Exception:
            pass
    
    # Default signature if nothing loaded
    if not signature:
        signature = {
            "base_frequency": 140.0,
            "modulation_depth": 0.08,
            "modulation_rate": 2.2,
            "harmonic_ratio": 0.25,
            "attack_time": 0.05,
            "decay_time": 0.2,
            "sustain_level": 0.75,
            "release_time": 0.15,
            "resonance_peak": 2200.0,
            "quantum_phase": 0.0,
            "prosody_variation": 0.12,
            "breath_pauses": True,
            "emphasis_variation": 0.15
        }
        print("✓ Using default signature")
    
    return signature


def apply_smooth_refinements(signature):
    """Apply smooth refinements to voice signature."""
    print("\n" + "=" * 80)
    print("APPLYING SMOOTH REFINEMENTS")
    print("=" * 80)
    
    # Store original values for comparison
    original = signature.copy()
    
    # Refinements for smoother voice:
    # 1. Slightly lower base frequency for deeper, smoother tone
    if "base_frequency" in signature:
        current_f0 = signature["base_frequency"]
        # Smooth adjustment: slightly deeper (1-2 Hz lower)
        signature["base_frequency"] = max(135.0, current_f0 - 1.5)
        print(f"  Base frequency: {current_f0:.2f} Hz → {signature['base_frequency']:.2f} Hz (smoother)")
    
    # 2. Reduce modulation depth for smoother flow
    if "modulation_depth" in signature:
        current_depth = signature["modulation_depth"]
        signature["modulation_depth"] = max(0.06, current_depth * 0.9)
        print(f"  Modulation depth: {current_depth:.3f} → {signature['modulation_depth']:.3f} (smoother)")
    
    # 3. Adjust modulation rate for natural rhythm
    if "modulation_rate" in signature:
        current_rate = signature["modulation_rate"]
        signature["modulation_rate"] = max(2.0, min(2.5, current_rate * 0.95))
        print(f"  Modulation rate: {current_rate:.2f} Hz → {signature['modulation_rate']:.2f} Hz (natural)")
    
    # 4. Enhance harmonics for richer, smoother tone
    if "harmonic_ratio" in signature:
        current_harmonics = signature["harmonic_ratio"]
        signature["harmonic_ratio"] = min(0.30, current_harmonics * 1.08)
        print(f"  Harmonic ratio: {current_harmonics:.3f} → {signature['harmonic_ratio']:.3f} (richer)")
    
    # 5. Smooth attack for natural onset
    if "attack_time" in signature:
        current_attack = signature["attack_time"]
        signature["attack_time"] = min(0.06, current_attack * 1.1)
        print(f"  Attack time: {current_attack:.3f}s → {signature['attack_time']:.3f}s (smoother onset)")
    
    # 6. Longer decay for smoother transitions
    if "decay_time" in signature:
        current_decay = signature["decay_time"]
        signature["decay_time"] = min(0.25, current_decay * 1.1)
        print(f"  Decay time: {current_decay:.3f}s → {signature['decay_time']:.3f}s (smoother transitions)")
    
    # 7. Adjust sustain for consistent smoothness
    if "sustain_level" in signature:
        current_sustain = signature["sustain_level"]
        signature["sustain_level"] = max(0.70, min(0.78, current_sustain * 0.98))
        print(f"  Sustain level: {current_sustain:.3f} → {signature['sustain_level']:.3f} (consistent)")
    
    # 8. Longer release for smooth endings
    if "release_time" in signature:
        current_release = signature["release_time"]
        signature["release_time"] = min(0.18, current_release * 1.1)
        print(f"  Release time: {current_release:.3f}s → {signature['release_time']:.3f}s (smooth endings)")
    
    # 9. Adjust resonance peak for smoother formants
    if "resonance_peak" in signature:
        current_resonance = signature["resonance_peak"]
        signature["resonance_peak"] = max(2100.0, min(2300.0, current_resonance * 0.98))
        print(f"  Resonance peak: {current_resonance:.1f} Hz → {signature['resonance_peak']:.1f} Hz (smoother formants)")
    
    # 10. Adjust prosody for natural flow
    if "prosody_variation" in signature:
        current_prosody = signature["prosody_variation"]
        signature["prosody_variation"] = max(0.10, min(0.15, current_prosody * 1.05))
        print(f"  Prosody variation: {current_prosody:.3f} → {signature['prosody_variation']:.3f} (natural flow)")
    
    # 11. Smooth emphasis variation
    if "emphasis_variation" in signature:
        current_emphasis = signature["emphasis_variation"]
        signature["emphasis_variation"] = max(0.12, min(0.18, current_emphasis * 0.95))
        print(f"  Emphasis variation: {current_emphasis:.3f} → {signature['emphasis_variation']:.3f} (smooth)")
    
    # 12. Ensure breath pauses are enabled for natural flow
    signature["breath_pauses"] = True
    print(f"  Breath pauses: Enabled (natural flow)")
    
    # Add refinement metadata
    signature["refined_at"] = datetime.now().isoformat()
    signature["refinement_type"] = "smooth_enhancement"
    signature["original_base_frequency"] = original.get("base_frequency", 140.0)
    
    print("\n✓ Smooth refinements applied!")
    
    return signature


def save_refined_signature(signature):
    """Save refined voice signature."""
    output_file = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(signature, f, indent=2)
        
        print(f"\n✓ Refined signature saved: {output_file.name}")
        print(f"  File size: {output_file.stat().st_size / 1024:.2f} KB")
        return True
    except Exception as e:
        print(f"\n⚠️  Error saving signature: {e}")
        return False


def main():
    """Main workflow: refine voice for smoothness."""
    print("=" * 80)
    print("Ω OMEGA VOICE SMOOTH REFINEMENT")
    print("=" * 80)
    print("\nThis will refine Omega's voice for smoother, more natural speech.")
    print("Adjustments will be subtle but effective for better voice quality.")
    print()
    
    # Load current signature
    signature = load_current_signature()
    
    # Apply smooth refinements
    refined_signature = apply_smooth_refinements(signature)
    
    # Save refined signature
    success = save_refined_signature(refined_signature)
    
    if success:
        print(f"\n{'='*80}")
        print("✓ OMEGA VOICE REFINED SUCCESSFULLY")
        print(f"{'='*80}")
        print("\nOmega's voice has been refined for smoother, more natural speech.")
        print("The refined voice signature will be used automatically on next initialization.")
        print("\nKey improvements:")
        print("  • Deeper, smoother base frequency")
        print("  • Reduced modulation for smoother flow")
        print("  • Enhanced harmonics for richer tone")
        print("  • Smoother attack/decay/release for natural transitions")
        print("  • Optimized prosody for natural rhythm")
        print("  • Better resonance for clear formants")
    else:
        print("\n⚠️  Refinement completed but save failed. Check permissions.")
    
    print(f"\n{'='*80}")


if __name__ == '__main__':
    main()

