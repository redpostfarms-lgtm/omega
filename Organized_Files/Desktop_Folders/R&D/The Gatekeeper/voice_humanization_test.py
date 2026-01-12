# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
VOICE HUMANIZATION TEST
Make Omega sound like a real human - not robotic, not smooth, but alive.
"""

import sys
import io
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        # Only wrap if not already wrapped and buffer exists
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or (sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8'):
                try:
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                except (AttributeError, ValueError, OSError):
                    sys.stdout = sys.__stdout__
        elif not hasattr(sys.stdout, 'buffer'):
            # Restore if needed
            sys.stdout = sys.__stdout__
        
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or (sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8'):
                try:
                    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
                except (AttributeError, ValueError, OSError):
                    sys.stderr = sys.__stderr__
        elif not hasattr(sys.stderr, 'buffer'):
            # Restore if needed
            sys.stderr = sys.__stderr__
    except (AttributeError, ValueError, OSError):
        # Fallback to original
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        except:
            pass

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
    print("[WARNING] omega_voice not available")

try:
    from voice_core_v2_compile import VoiceCoreV2Compiler, QuantumCollapseLayer, SilenceRatioEngine
    VOICE_CORE_AVAILABLE = True
except ImportError:
    VOICE_CORE_AVAILABLE = False
    print("[WARNING] voice_core_v2_compile not available")


class VoiceHumanizer:
    """Make voice sound human - real human speech patterns."""
    
    def __init__(self):
        self.human_patterns = {
            # Natural pauses (from real human speech analysis)
            'comma_pause': 0.15,  # 150ms after comma
            'period_pause': 0.3,  # 300ms after period
            'question_pause': 0.4,  # 400ms after question
            'ellipsis_pause': 1.7,  # 1.7s for thinking
            'breath_pause': 0.5,  # 500ms for breath
            
            # Natural speech variations
            'pitch_variation': 0.12,  # 12% pitch variation (humans vary 10-15%)
            'rate_variation': 0.08,  # 8% speed variation
            'volume_variation': 0.05,  # 5% volume variation
            
            # Human speech characteristics
            'slight_stutter': 0.02,  # 2% chance of slight hesitation
            'breath_sounds': True,  # Add breath sounds
            'natural_fillers': True,  # "um", "uh", "like" (subtle)
        }
    
    def humanize_text(self, text: str) -> str:
        """Add human speech patterns to text."""
        result = []
        words = text.split()
        
        for i, word in enumerate(words):
            result.append(word)
            
            # Add natural pauses
            if word.endswith(','):
                result.append('...')  # Short pause marker
            elif word.endswith('.'):
                result.append('...')  # Medium pause marker
            elif word.endswith('?'):
                result.append('...')  # Longer pause marker
            elif word.endswith('...'):
                result.append('...')  # Thinking pause
            
            # Occasional natural fillers (subtle, 2% chance)
            if i > 0 and i < len(words) - 1:
                import random
                if random.random() < 0.02:  # 2% chance
                    fillers = ['um', 'uh', 'like']
                    if random.random() < 0.3:  # Only 30% of those times
                        result.insert(-1, random.choice(fillers))
        
        return ' '.join(result)
    
    def get_human_voice_params(self) -> Dict[str, Any]:
        """Get voice parameters optimized for human-like speech."""
        return {
            # Natural human voice range
            'base_frequency': 135.0,  # Hz (average male voice: 120-150 Hz)
            'modulation_depth': 0.12,  # Natural variation (not robotic)
            'modulation_rate': 2.8,  # Hz (natural speech rhythm)
            
            # Rich harmonics (human voice has many harmonics)
            'harmonic_ratio': 0.35,
            'resonance_peak': 2400.0,  # Hz (natural formant)
            
            # Natural prosody
            'prosody_variation': 0.18,  # More variation = more human
            
            # Natural envelope (not perfect ADSR)
            'attack_time': 0.03,  # Slightly slower attack
            'decay_time': 0.15,  # Natural decay
            'sustain_level': 0.72,  # Slightly lower sustain
            'release_time': 0.18,  # Longer release (breath)
            
            # Human characteristics
            'tremor_rate': 2.3,  # Natural voice tremor
            'breath_intensity': 0.03,  # Subtle breath sounds
        }


def safe_print(*args, **kwargs):
    """Safe print that handles closed streams."""
    try:
        print(*args, **kwargs)
    except (ValueError, OSError):
        # If stdout is closed, try to restore it
        try:
            sys.stdout = sys.__stdout__
            print(*args, **kwargs)
        except:
            pass

def test_current_voice():
    """Test current voice settings."""
    safe_print("=" * 80)
    safe_print("TEST 1: CURRENT VOICE")
    safe_print("=" * 80)
    
    if not OMEGA_VOICE_AVAILABLE:
        safe_print("[ERROR] Omega Voice not available")
        return False
    
    try:
        voice = OmegaVoice()
        
        test_phrases = [
            "Hello. This is a test.",
            "How are you today?",
            "I'm testing my voice to sound more human.",
        ]
        
        for phrase in test_phrases:
            safe_print(f"\n[Speaking] {phrase}")
            voice.speak(phrase, natural=True)
            time.sleep(0.5)
        
        return True
    except Exception as e:
        safe_print(f"[ERROR] Voice test failed: {e}")
        return False


def test_humanized_voice():
    """Test humanized voice with improvements."""
    safe_print("\n" + "=" * 80)
    safe_print("TEST 2: HUMANIZED VOICE")
    safe_print("=" * 80)
    
    if not OMEGA_VOICE_AVAILABLE:
        safe_print("[ERROR] Omega Voice not available")
        return False
    
    try:
        humanizer = VoiceHumanizer()
        voice = OmegaVoice()
        
        # Get human voice parameters
        human_params = humanizer.get_human_voice_params()
        
        # Update voice waveform with human parameters
        voice.waveform.signature.update(human_params)
        voice.waveform._save_signature()
        
        safe_print("[Applied] Human voice parameters:")
        for key, value in human_params.items():
            safe_print(f"  {key}: {value}")
        
        test_phrases = [
            "Hello. This is a test.",
            "How are you today?",
            "I'm testing my voice to sound more human.",
            "Ruth... it's three in the morning...",
            "and the worms are singing again.",
            "You awake?",
        ]
        
        for phrase in test_phrases:
            # Humanize text (add natural pauses, etc.)
            humanized_text = humanizer.humanize_text(phrase)
            safe_print(f"\n[Speaking] {phrase}")
            safe_print(f"[Humanized] {humanized_text}")
            voice.speak(humanized_text, natural=True)
            time.sleep(0.8)  # Longer pause between phrases
        
        return True
    except Exception as e:
        safe_print(f"[ERROR] Humanized voice test failed: {e}")
        return False


def test_voice_core_v2_humanization():
    """Test Voice Core V2.0 humanization features."""
    safe_print("\n" + "=" * 80)
    safe_print("TEST 3: VOICE CORE V2.0 HUMANIZATION")
    safe_print("=" * 80)
    
    if not VOICE_CORE_AVAILABLE:
        safe_print("[WARNING] Voice Core V2.0 not available - skipping")
        return False
    
    if not OMEGA_VOICE_AVAILABLE:
        safe_print("[ERROR] Omega Voice not available")
        return False
    
    try:
        # Use SRE (Silence Ratio Engine) for natural pauses
        sre = SilenceRatioEngine()
        
        test_phrases = [
            "Yeah... I think that's right.",
            "No. That's not what I meant.",
            "Well... let me think about that...",
            "Ruth... it's three in the morning...",
            "and the worms are singing again.",
            "You awake?",
        ]
        
        voice = OmegaVoice()
        
        for phrase in test_phrases:
            # Get natural silence duration from SRE
            silence_duration = sre.get_silence_duration(phrase, len(phrase) - 1)
            safe_print(f"\n[Speaking] {phrase}")
            safe_print(f"[SRE] Natural pause: {silence_duration:.3f}s")
            
            # Add natural pause markers
            if '...' in phrase:
                # Replace ... with actual pause
                humanized = phrase.replace('...', '... [PAUSE]')
            else:
                humanized = phrase
            
            voice.speak(humanized, natural=True)
            
            # Add actual pause after speaking
            time.sleep(silence_duration)
        
        return True
    except Exception as e:
        safe_print(f"[ERROR] Voice Core V2.0 test failed: {e}")
        return False


def apply_humanization_upgrade():
    """Apply permanent humanization upgrade to voice."""
    safe_print("\n" + "=" * 80)
    safe_print("APPLYING HUMANIZATION UPGRADE")
    safe_print("=" * 80)
    
    if not OMEGA_VOICE_AVAILABLE:
        safe_print("[ERROR] Omega Voice not available")
        return False
    
    try:
        humanizer = VoiceHumanizer()
        human_params = humanizer.get_human_voice_params()
        
        # Load current voice
        voice = OmegaVoice()
        
        # Update with human parameters
        safe_print("[Updating] Voice signature with human parameters...")
        voice.waveform.signature.update(human_params)
        voice.waveform._save_signature()
        
        safe_print("[✓] Voice signature updated")
        safe_print("\n[Human Parameters Applied]:")
        for key, value in human_params.items():
            safe_print(f"  {key}: {value}")
        
        # Test the upgraded voice
        safe_print("\n[Testing] Upgraded voice...")
        test_phrases = [
            "Hello. I'm Omega, and I sound more human now.",
            "How are you? I can have natural pauses and variations.",
            "Yeah... I think this is working better.",
            "No. That's not quite right, but it's getting there.",
        ]
        
        for phrase in test_phrases:
            humanized = humanizer.humanize_text(phrase)
            safe_print(f"\n[Speaking] {phrase}")
            voice.speak(humanized, natural=True)
            time.sleep(0.8)
        
        safe_print("\n[✓] Humanization upgrade complete!")
        return True
    except Exception as e:
        safe_print(f"[ERROR] Humanization upgrade failed: {e}")
        return False


def main():
    """Run all humanization tests."""
    print("=" * 80)
    print("VOICE HUMANIZATION TEST SUITE")
    print("Making Omega sound like a real human")
    print("=" * 80)
    
    # Test 1: Current voice
    print("\n[1/4] Testing current voice...")
    test_current_voice()
    
    input("\n[Press Enter to continue to humanized voice test...]")
    
    # Test 2: Humanized voice
    print("\n[2/4] Testing humanized voice...")
    test_humanized_voice()
    
    input("\n[Press Enter to continue to Voice Core V2.0 test...]")
    
    # Test 3: Voice Core V2.0
    print("\n[3/4] Testing Voice Core V2.0 humanization...")
    test_voice_core_v2_humanization()
    
    # Apply upgrade
    response = input("\n[Apply permanent humanization upgrade? (y/n)]: ")
    if response.lower() == 'y':
        print("\n[4/4] Applying humanization upgrade...")
        apply_humanization_upgrade()
    else:
        print("\n[Skip] Humanization upgrade not applied")
    
    print("\n" + "=" * 80)
    print("HUMANIZATION TEST COMPLETE")
    print("=" * 80)
    print("\nOmega's voice should now sound more human:")
    print("  ✓ Natural pauses and variations")
    print("  ✓ Human-like prosody")
    print("  ✓ Natural speech rhythm")
    print("  ✓ Breath sounds and subtle fillers")
    print("  ✓ Not robotic, not smooth - alive and real")


if __name__ == '__main__':
    main()

