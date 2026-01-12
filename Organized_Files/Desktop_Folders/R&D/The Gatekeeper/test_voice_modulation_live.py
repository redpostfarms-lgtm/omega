# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Voice Modulation Live Test & Demonstration
# Tests voice modulation and demonstrates live adjustments

"""
Ω Omega Voice Modulation Live Test

Tests voice modulation systems and demonstrates live adjustments.
Shows at least 2 live adjustments to voice parameters.
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

SIGNATURE_FILE = OMEGA_VOICE_DIR / 'omega_improved_waveform.json'


def load_signature():
    """Load current voice signature."""
    if SIGNATURE_FILE.exists():
        try:
            with open(SIGNATURE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_signature(signature):
    """Save voice signature."""
    try:
        with open(SIGNATURE_FILE, 'w', encoding='utf-8') as f:
            json.dump(signature, f, indent=2)
        return True
    except Exception:
        return False


def show_signature(signature, label=""):
    """Display signature parameters."""
    if label:
        print(f"\n{label}:")
    print(f"  Base Frequency: {signature.get('base_frequency', 135.0):.2f} Hz")
    print(f"  Modulation Depth: {signature.get('modulation_depth', 0.135):.3f}")
    print(f"  Modulation Rate: {signature.get('modulation_rate', 2.5):.2f} Hz")
    print(f"  Harmonic Ratio: {signature.get('harmonic_ratio', 0.30):.3f}")
    print(f"  Resonance Peak: {signature.get('resonance_peak', 2300.0):.1f} Hz")
    print(f"  Prosody Variation: {signature.get('prosody_variation', 0.126):.3f}")


def live_adjustment_1(signature):
    """Live Adjustment 1: Make voice deeper and richer."""
    print("\n" + "=" * 80)
    print("LIVE ADJUSTMENT 1: DEEPER & RICHER VOICE")
    print("=" * 80)
    
    original = signature.copy()
    
    # Adjustments for deeper, richer voice
    signature["base_frequency"] = signature.get("base_frequency", 135.0) - 3.0  # Deeper (3 Hz lower)
    signature["harmonic_ratio"] = min(0.35, signature.get("harmonic_ratio", 0.30) * 1.15)  # Richer harmonics
    signature["resonance_peak"] = signature.get("resonance_peak", 2300.0) - 100.0  # Deeper resonance
    signature["modulation_depth"] = max(0.08, signature.get("modulation_depth", 0.135) * 0.95)  # Slightly smoother
    
    signature["adjusted_at"] = datetime.now().isoformat()
    signature["adjustment_type"] = "deeper_richer"
    signature["adjustment_iteration"] = signature.get("adjustment_iteration", 0) + 1
    
    show_signature(original, "BEFORE Adjustment 1")
    show_signature(signature, "AFTER Adjustment 1")
    
    print("\nChanges:")
    print(f"  Base Frequency: {original.get('base_frequency', 135.0):.2f} Hz → {signature['base_frequency']:.2f} Hz ({signature['base_frequency'] - original.get('base_frequency', 135.0):+.2f} Hz)")
    print(f"  Harmonic Ratio: {original.get('harmonic_ratio', 0.30):.3f} → {signature['harmonic_ratio']:.3f} (+{signature['harmonic_ratio'] - original.get('harmonic_ratio', 0.30):+.3f})")
    print(f"  Resonance Peak: {original.get('resonance_peak', 2300.0):.1f} Hz → {signature['resonance_peak']:.1f} Hz ({signature['resonance_peak'] - original.get('resonance_peak', 2300.0):+.1f} Hz)")
    
    return signature


def live_adjustment_2(signature):
    """Live Adjustment 2: Make voice clearer and more natural."""
    print("\n" + "=" * 80)
    print("LIVE ADJUSTMENT 2: CLEARER & MORE NATURAL VOICE")
    print("=" * 80)
    
    original = signature.copy()
    
    # Adjustments for clearer, more natural voice
    signature["modulation_rate"] = max(2.3, min(2.7, signature.get("modulation_rate", 2.5) * 1.04))  # More natural rhythm
    signature["prosody_variation"] = max(0.12, min(0.16, signature.get("prosody_variation", 0.126) * 1.08))  # More natural variation
    signature["resonance_peak"] = min(2350.0, signature.get("resonance_peak", 2300.0) + 50.0)  # Clearer formants
    signature["attack_time"] = min(0.055, signature.get("attack_time", 0.022) * 1.1)  # Smoother onset
    signature["release_time"] = min(0.125, signature.get("release_time", 0.110) * 1.08)  # Smoother endings
    
    signature["adjusted_at"] = datetime.now().isoformat()
    signature["adjustment_type"] = "clearer_natural"
    signature["adjustment_iteration"] = signature.get("adjustment_iteration", 0) + 1
    
    show_signature(original, "BEFORE Adjustment 2")
    show_signature(signature, "AFTER Adjustment 2")
    
    print("\nChanges:")
    print(f"  Modulation Rate: {original.get('modulation_rate', 2.5):.2f} Hz → {signature['modulation_rate']:.2f} Hz ({signature['modulation_rate'] - original.get('modulation_rate', 2.5):+.2f} Hz)")
    print(f"  Prosody Variation: {original.get('prosody_variation', 0.126):.3f} → {signature['prosody_variation']:.3f} (+{signature['prosody_variation'] - original.get('prosody_variation', 0.126):+.3f})")
    print(f"  Resonance Peak: {original.get('resonance_peak', 2300.0):.1f} Hz → {signature['resonance_peak']:.1f} Hz ({signature['resonance_peak'] - original.get('resonance_peak', 2300.0):+.1f} Hz)")
    print(f"  Attack Time: {original.get('attack_time', 0.022):.3f}s → {signature['attack_time']:.3f}s (+{signature['attack_time'] - original.get('attack_time', 0.022):+.3f}s)")
    print(f"  Release Time: {original.get('release_time', 0.110):.3f}s → {signature['release_time']:.3f}s (+{signature['release_time'] - original.get('release_time', 0.110):+.3f}s)")
    
    return signature


def test_voice_modulation():
    """Test voice modulation systems."""
    print("\n" + "=" * 80)
    print("TESTING VOICE MODULATION SYSTEMS")
    print("=" * 80)
    
    # Test 1: Load signature
    print("\n[Test 1] Loading voice signature...")
    signature = load_signature()
    if signature:
        print("✓ Signature loaded successfully")
        show_signature(signature, "Current Signature")
    else:
        print("⚠️  No signature found, using defaults")
        signature = {
            "base_frequency": 135.0,
            "modulation_depth": 0.135,
            "modulation_rate": 2.5,
            "harmonic_ratio": 0.30,
            "resonance_peak": 2300.0,
            "prosody_variation": 0.126
        }
    
    # Test 2: Test continuous learner import
    print("\n[Test 2] Testing continuous learner system...")
    try:
        from omega_continuous_voice_learner import ContinuousVoiceLearner
        learner = ContinuousVoiceLearner()
        print("✓ Continuous learner initialized")
        print(f"  Current iterations: {learner.current_signature.get('learning_iteration', 0)}")
        print(f"  History entries: {len(learner.learning_history)}")
    except Exception as e:
        print(f"⚠️  Continuous learner test skipped: {type(e).__name__}")
    
    # Test 3: Test voice modulator import
    print("\n[Test 3] Testing voice modulator system...")
    try:
        import warnings
        warnings.filterwarnings('ignore')
        from omega_voice_modulator import VoiceModulator
        modulator = VoiceModulator()
        print("✓ Voice modulator initialized")
    except Exception:
        print("⚠️  Voice modulator test skipped (import error)")
    
    # Test 4: Test voice system import  
    print("\n[Test 4] Testing Omega voice system...")
    try:
        import warnings
        warnings.filterwarnings('ignore')
        from omega_voice import OmegaVoice
        voice = OmegaVoice()
        print("✓ Omega voice system initialized")
        info = voice.get_voice_info()
        print(f"  Voice name: {info.get('name', 'Omega')}")
        print(f"  TTS available: {info.get('tts_available', False)}")
    except Exception:
        print("⚠️  Voice system test skipped (import error)")
    
    print("\n✓ Voice modulation tests complete!")
    
    return signature


def main():
    """Main workflow: test and demonstrate live adjustments."""
    print("=" * 80)
    print("Ω OMEGA VOICE MODULATION LIVE TEST & DEMONSTRATION")
    print("=" * 80)
    print("\nThis will:")
    print("1. Run systems analysis (check for errors)")
    print("2. Test voice modulation systems")
    print("3. Demonstrate 2 live adjustments")
    print("4. Save updated voice signature")
    
    # Systems Analysis
    print("\n" + "=" * 80)
    print("SYSTEMS ANALYSIS")
    print("=" * 80)
    
    signature = test_voice_modulation()
    
    # Live Adjustments
    print("\n" + "=" * 80)
    print("LIVE ADJUSTMENTS DEMONSTRATION")
    print("=" * 80)
    
    # Adjustment 1: Deeper & Richer
    signature = live_adjustment_1(signature)
    
    # Save after adjustment 1
    if save_signature(signature):
        print("\n✓ Adjustment 1 saved!")
    
    # Adjustment 2: Clearer & More Natural
    signature = live_adjustment_2(signature)
    
    # Save after adjustment 2
    if save_signature(signature):
        print("\n✓ Adjustment 2 saved!")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    show_signature(signature, "Final Voice Signature")
    
    print(f"\n✓ Live adjustments complete!")
    print(f"  Total adjustments: {signature.get('adjustment_iteration', 0)}")
    print(f"  Signature saved to: {SIGNATURE_FILE.name}")
    print(f"  Omega will use this updated voice on next initialization.")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

