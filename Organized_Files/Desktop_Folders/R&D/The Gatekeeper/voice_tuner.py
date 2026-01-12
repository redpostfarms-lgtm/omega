# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# D:\RPF_BRAIN\The Gatekeeper\voice_tuner.py
# Voice modulation — free, local, no install
# Run once. Speak once. Then tweak the Gatekeeper's voice like a dial.

import pyttsx3
import numpy as np
import pickle
import sys
import time
import subprocess
from pathlib import Path

# Add Piper TTS support (deep voice, offline)
try:
    import onnxruntime
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False

PIPER_MODEL_PATH = Path(r'D:\RPF_BRAIN\The Gatekeeper\models\piper\ryan.onnx')

VOICE_DIR = Path(r'D:\RPF_BRAIN\Archived\voiceprint\tuned')
VOICE_DIR.mkdir(parents=True, exist_ok=True)

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Use deep, old, male voice as base
# Index may vary — test with 0 or 1
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
else:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 110)
engine.setProperty('volume', 0.7)

def say_with_piper(text: str):
    """Use Piper TTS for deep, natural voice (offline)."""
    if not PIPER_AVAILABLE or not PIPER_MODEL_PATH.exists():
        return False
    
    try:
        import onnxruntime as ort
        import numpy as np
        import wave
        import io
        
        # Load Piper model
        session = ort.InferenceSession(str(PIPER_MODEL_PATH))
        
        # Simple text-to-speech with Piper
        # Note: Full Piper integration would require phonemizer and audio processing
        # For now, fallback to pyttsx3 if Piper unavailable
        return False  # Simplified - use pyttsx3 fallback
    except Exception as e:
        return False

def tune_voice(text, pitch=50, echo=0.1):
    """
    Tune voice with pitch and echo.
    Pitch: 0-100 → 50 = neutral (old man), lower = deeper, higher = younger
    Echo: 0.0-1.0 → adds slight delay/reverb effect
    """
    # Try Piper first (deep voice, offline)
    if say_with_piper(text):
        return  # Piper handled it
    
    # Fallback to pyttsx3
    # Pitch: 0-100 → adjust pitch
    # 50 = neutral, lower = deeper, higher = younger
    pitch_adj = -0.002 * (pitch - 50)  # 50 = neutral
    
    # pyttsx3 pitch adjustment (limited support, but we try)
    try:
        engine.setProperty('pitch', pitch_adj)
    except:
        # Fallback: adjust rate slightly for pitch effect
        base_rate = 110
        rate_adj = base_rate + (pitch - 50) * 0.5
        engine.setProperty('rate', int(rate_adj))
    
    # Echo: fake reverb with silence buffer
    # Offline TTS can't do real echo, so we add a tiny delay
    if echo > 0:
        engine.say(text)
        engine.runAndWait()
        time.sleep(echo * 0.1)  # tiny delay for echo effect
    else:
        engine.say(text)
        engine.runAndWait()

def save_tune(pitch, echo):
    """Save tuning parameters."""
    tuned = {'pitch': pitch, 'echo': echo}
    with open(VOICE_DIR / 'tune.pkl', 'wb') as f:
        pickle.dump(tuned, f)

def load_tune():
    """Load saved tuning parameters."""
    try:
        with open(VOICE_DIR / 'tune.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return {'pitch': 50, 'echo': 0.1}  # default: old man, slight echo

def apply_tune(tune_settings=None):
    """Apply tuning settings to engine."""
    if tune_settings is None:
        tune_settings = load_tune()
    
    pitch = tune_settings.get('pitch', 50)
    echo = tune_settings.get('echo', 0.1)
    
    pitch_adj = -0.002 * (pitch - 50)
    try:
        engine.setProperty('pitch', pitch_adj)
    except:
        base_rate = 110
        rate_adj = base_rate + (pitch - 50) * 0.5
        engine.setProperty('rate', int(rate_adj))
    
    return pitch, echo

if __name__ == '__main__':
    if '--load' in sys.argv:
        # Load mode: apply saved settings
        print("Loading saved voice tuning...")
        t = load_tune()
        pitch, echo = apply_tune(t)
        print(f"Applied: pitch={pitch}, echo={echo}")
        print("Testing voice...")
        tune_voice("The doors of knowledge opens.", pitch, echo)
    else:
        # Interactive mode: set your style
        print("=" * 60)
        print("Gatekeeper Voice Tuner")
        print("=" * 60)
        print("Tweak the Gatekeeper's voice.")
        print("Pitch 0-100 (50 = old man, lower = deeper, higher = younger)")
        print("Echo 0.0-1.0 (0.0 = none, higher = more reverb effect)\n")
        
        try:
            pitch_input = input("Pitch [default: 55]: ").strip()
            pitch = int(pitch_input) if pitch_input else 55
            
            echo_input = input("Echo [default: 0.12]: ").strip()
            echo = float(echo_input) if echo_input else 0.12
            
            print(f"\nTesting with pitch={pitch}, echo={echo}...")
            tune_voice("The doors of knowledge opens.", pitch, echo)
            
            save_tune(pitch, echo)
            print(f"\nTuned: pitch={pitch}, echo={echo}")
            print(f"Settings saved to: {VOICE_DIR / 'tune.pkl'}")
            print("\nTo apply at startup, use: python voice_tuner.py --load")
            
        except ValueError:
            print("Invalid input. Using defaults.")
            pitch, echo = 55, 0.12
            tune_voice("The doors of knowledge opens.", pitch, echo)
            save_tune(pitch, echo)
        except KeyboardInterrupt:
            print("\nCancelled.")
        except Exception as e:
            print(f"Error: {e}")

