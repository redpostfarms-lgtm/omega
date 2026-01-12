# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
VOICE CORE V2.0 - TEST SCRIPT
Phase 8: Test the compiled voice
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

VOICE_CORE_DIR = GATE / 'voice_core_v2'
VOICE_CORE_DIR.mkdir(parents=True, exist_ok=True)

try:
    from omega_voice import OmegaVoice
    OMEGA_VOICE_AVAILABLE = True
except ImportError:
    OMEGA_VOICE_AVAILABLE = False
    print("[WARNING] omega_voice not available")

try:
    import soundfile as sf
    import numpy as np
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("[WARNING] soundfile/numpy not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("[WARNING] pyaudio not available - cannot play audio")


def say(text: str, voice_file: Path = None):
    """
    Say text using Voice Core V2.0
    
    Args:
        text: Text to speak
        voice_file: Path to compiled voice file (optional)
    """
    print(f"\n[Voice Core V2.0] Saying: {text}")
    print("-" * 80)
    
    if voice_file and voice_file.exists() and SOUNDFILE_AVAILABLE and PYAUDIO_AVAILABLE:
        # Play compiled voice file
        try:
            audio_data, sample_rate = sf.read(str(voice_file))
            
            # Play audio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                rate=sample_rate,
                output=True
            )
            
            # Convert to float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize
            max_val = np.max(np.abs(audio_data))
            if max_val > 1.0:
                audio_data = audio_data / max_val * 0.8
            
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            print(f"[✓] Played from {voice_file.name}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to play audio: {e}")
    
    # Fallback to Omega Voice TTS
    if OMEGA_VOICE_AVAILABLE:
        try:
            voice = OmegaVoice()
            voice.speak(text, natural=True)
            print(f"[✓] Spoke via Omega Voice TTS")
            return True
        except Exception as e:
            print(f"[ERROR] TTS failed: {e}")
    
    # Last resort: print
    print(f"[Fallback] {text}")
    return False


def main():
    print("=" * 80)
    print("VOICE CORE V2.0 - TEST SCRIPT")
    print("Phase 8: Test the compiled voice")
    print("=" * 80)
    
    # Test phrases from specification
    test_phrases = [
        "Ruth... it's three in the morning...",
        "and the worms are singing again.",
        "You awake?"
    ]
    
    # Check for compiled voice
    voice_file = VOICE_CORE_DIR / 'omega_voice_2.0.wav'
    
    if voice_file.exists():
        print(f"[Found] Compiled voice: {voice_file}")
        print(f"[Info] Using compiled voice for playback")
    else:
        print(f"[Info] Compiled voice not found: {voice_file}")
        print(f"[Info] Using Omega Voice TTS fallback")
    
    print("\n" + "=" * 80)
    print("TESTING VOICE CORE V2.0")
    print("=" * 80)
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n[Test {i}/{len(test_phrases)}]")
        say(phrase, voice_file if voice_file.exists() else None)
        
        # Pause between phrases
        import time
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nVoice Core V2.0 is now you.")
    print("Not robotic. Not smooth. Alive. Tired. Real.")
    print("Your exhale. Your silence. Your yes.")


if __name__ == '__main__':
    main()

