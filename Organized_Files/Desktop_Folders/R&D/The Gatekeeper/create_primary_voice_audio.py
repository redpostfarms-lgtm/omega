# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Primary Voice Audio Generator
# Creates primary audio file for Omega's voice

"""
Ω Omega Primary Voice Audio Generator

Creates a primary audio file that can be used and tweaked as Omega's base voice.
Uses Edge TTS (preferred) or pyttsx3 to generate high-quality audio.
"""

import sys
import io
from pathlib import Path
from typing import Optional

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

PRIMARY_VOICE_FILE = OMEGA_VOICE_DIR / 'omega_primary_voice.wav'
PRIMARY_VOICE_TEXT = """Hello. I am Omega, your autonomous AI guardian and challenger. 
I analyze code, protect systems, and learn continuously. 
My voice represents my unique waveform signature - deep, resonant, and clear.
This is my primary voice sample that can be used and tweaked for various applications."""

# Try Edge TTS first (best quality, free, no API key)
EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    pass

# Fallback to pyttsx3
PYTTSX3_AVAILABLE = False
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pass

# Audio saving
try:
    import soundfile as sf
    import numpy as np
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


async def generate_with_edge_tts(text: str, output_file: Path) -> bool:
    """Generate audio using Edge TTS (Microsoft)."""
    try:
        # Use a natural male voice (David or similar)
        voices = await edge_tts.list_voices()
        
        # Find a natural male voice (prefer David, Guy, or similar)
        voice_name = None
        for voice in voices:
            if voice['Gender'] == 'Male' and 'en-US' in voice['Locale']:
                # Prefer natural-sounding voices
                if 'david' in voice['ShortName'].lower() or 'guy' in voice['ShortName'].lower():
                    voice_name = voice['ShortName']
                    break
        
        # Fallback to first male US voice
        if not voice_name:
            for voice in voices:
                if voice['Gender'] == 'Male' and 'en-US' in voice['Locale']:
                    voice_name = voice['ShortName']
                    break
        
        # Final fallback to any US voice
        if not voice_name:
            for voice in voices:
                if 'en-US' in voice['Locale']:
                    voice_name = voice['ShortName']
                    break
        
        if not voice_name:
            voice_name = 'en-US-DavisNeural'  # Default natural male voice
        
        print(f"Using Edge TTS voice: {voice_name}")
        
        # Generate audio
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(str(output_file))
        
        return True
    except Exception as e:
        print(f"Edge TTS error: {e}")
        return False


def generate_with_pyttsx3(text: str, output_file: Path) -> bool:
    """Generate audio using pyttsx3 (fallback)."""
    if not PYTTSX3_AVAILABLE:
        return False
    
    try:
        import tempfile
        import shutil
        
        engine = pyttsx3.init()
        
        # Find natural voice
        voices = engine.getProperty('voices')
        natural_voice = None
        
        # Priority order for natural voices
        voice_priorities = ['guy', 'david', 'mark', 'zira', 'aria']
        for priority in voice_priorities:
            for voice in voices:
                if priority in voice.name.lower():
                    natural_voice = voice.id
                    break
            if natural_voice:
                break
        
        if not natural_voice and len(voices) > 0:
            natural_voice = voices[0].id
        
        engine.setProperty('voice', natural_voice)
        engine.setProperty('rate', 160)  # Natural speech rate
        engine.setProperty('volume', 0.75)  # Natural volume
        
        print(f"Using pyttsx3 voice: {natural_voice}")
        
        # Create temporary file path
        tmp_path = output_file.parent / f"temp_{output_file.name}"
        
        # Save to file - must call runAndWait() after save_to_file()
        engine.save_to_file(text, str(tmp_path))
        engine.runAndWait()  # This is required for save_to_file to work
        
        # Move to final location
        if tmp_path.exists() and tmp_path.stat().st_size > 0:
            if output_file.exists():
                output_file.unlink()  # Remove old file if exists
            shutil.move(str(tmp_path), str(output_file))
            return True
        else:
            # Clean up empty temp file
            if tmp_path.exists():
                tmp_path.unlink()
            return False
        
    except Exception as e:
        print(f"pyttsx3 error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Generate primary voice audio file."""
    print("=" * 80)
    print("Ω OMEGA PRIMARY VOICE AUDIO GENERATOR")
    print("=" * 80)
    print(f"\nOutput file: {PRIMARY_VOICE_FILE}")
    print(f"Text length: {len(PRIMARY_VOICE_TEXT)} characters")
    
    # Try Edge TTS first (best quality)
    if EDGE_TTS_AVAILABLE:
        print("\n[1/2] Attempting to generate with Edge TTS (Microsoft)...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(generate_with_edge_tts(PRIMARY_VOICE_TEXT, PRIMARY_VOICE_FILE))
            loop.close()
            
            if success and PRIMARY_VOICE_FILE.exists():
                print(f"\n✓ Primary voice audio created: {PRIMARY_VOICE_FILE}")
                print(f"  File size: {PRIMARY_VOICE_FILE.stat().st_size / 1024:.2f} KB")
                return
        except Exception as e:
            print(f"Edge TTS generation failed: {e}")
    
    # Fallback to pyttsx3
    if PYTTSX3_AVAILABLE:
        print("\n[2/2] Attempting to generate with pyttsx3 (fallback)...")
        success = generate_with_pyttsx3(PRIMARY_VOICE_TEXT, PRIMARY_VOICE_FILE)
        if success and PRIMARY_VOICE_FILE.exists():
            print(f"\n✓ Primary voice audio created: {PRIMARY_VOICE_FILE}")
            print(f"  File size: {PRIMARY_VOICE_FILE.stat().st_size / 1024:.2f} KB")
            return
    
    # No TTS available
    print("\n❌ Error: No TTS engine available")
    print("  Install one of:")
    print("    pip install edge-tts  (recommended - free, high quality)")
    print("    pip install pyttsx3   (fallback)")
    sys.exit(1)


if __name__ == '__main__':
    main()

