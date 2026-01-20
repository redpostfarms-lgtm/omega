"""
Omega Complete Setup - Install ALL Dependencies
Includes: TTS, OpenRGB, Voice, Mouse Tracking, LED Control
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run command and show progress"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print('='*70)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout[:500])
        else:
            print(f"⚠ {description} - WARNING")
            if result.stderr:
                print(result.stderr[:500])
        return result.returncode == 0
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🌟 OMEGA COMPLETE SETUP - INSTALLING ALL DEPENDENCIES 🌟")
    print("="*70)
    print("\nThis will install everything Omega needs to:")
    print("  🎤 Speak to you (TTS)")
    print("  💡 Control RGB LEDs")
    print("  🖱️ Track mouse movement")
    print("  🎮 Create reactive lighting")
    print()

    input("Press Enter to begin installation...")

    # Core Python packages
    packages = [
        # TTS and Voice
        ("TTS", "Text-to-Speech system"),
        ("sounddevice", "Audio playback"),
        ("soundfile", "Audio file handling"),
        ("numpy", "Numerical operations"),
        ("scipy", "Scientific computing"),

        # Speech Recognition
        ("SpeechRecognition", "Voice recognition"),
        ("pyaudio", "Audio input"),

        # OpenRGB
        ("openrgb-python", "OpenRGB SDK"),

        # Mouse tracking
        ("pynput", "Mouse and keyboard tracking"),
        ("pyautogui", "Screen and mouse control"),

        # Serial/Hardware
        ("pyserial", "Serial communication"),

        # Utilities
        ("python-dotenv", "Environment variables"),
        ("requests", "HTTP requests"),
        ("psutil", "System utilities"),
    ]

    print("\n" + "="*70)
    print("  PHASE 1: Python Dependencies")
    print("="*70)

    for package, description in packages:
        run_command(
            f'python -m pip install {package} --upgrade',
            f"Installing {package} ({description})"
        )

    print("\n" + "="*70)
    print("  PHASE 2: TTS Models")
    print("="*70)

    # Download TTS model
    run_command(
        'python -c "from TTS.api import TTS; TTS(\'tts_models/multilingual/multi-dataset/xtts_v2\')"',
        "Downloading XTTS v2 voice model"
    )

    print("\n" + "="*70)
    print("  PHASE 3: OpenRGB Setup")
    print("="*70)

    openrgb_path = Path("C:/Users/Drakalich/OpenRGB/OpenRGB Windows 64-bit/OpenRGB.exe")
    if openrgb_path.exists():
        print(f"✓ OpenRGB found at: {openrgb_path}")
    else:
        print("⚠ OpenRGB not found. Download from: https://openrgb.org/")
        print("  Install to: C:/Users/Drakalich/OpenRGB/")

    print("\n" + "="*70)
    print("  PHASE 4: Testing Systems")
    print("="*70)

    # Test imports
    tests = [
        ("TTS.api", "TTS System"),
        ("openrgb", "OpenRGB SDK"),
        ("pynput.mouse", "Mouse Tracking"),
        ("sounddevice", "Audio System"),
    ]

    for module, name in tests:
        try:
            __import__(module)
            print(f"✓ {name} - READY")
        except ImportError as e:
            print(f"✗ {name} - NOT AVAILABLE: {e}")

    print("\n" + "="*70)
    print("  🎉 INSTALLATION COMPLETE 🎉")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python omega_voice_test.py")
    print("  2. Run: python omega_mouse_led_reactive.py")
    print("  3. Open OpenRGB GUI and rescan for devices")
    print()

if __name__ == "__main__":
    main()
