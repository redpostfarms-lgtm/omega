"""
Omega Mouse-Reactive LED System
LED colors change based on mouse movement and position
With voice narration
"""

import time
import math
from pathlib import Path

print("\n" + "="*70)
print("  🖱️💡 OMEGA MOUSE-REACTIVE LED SYSTEM")
print("="*70)

# Initialize systems
tts_available = False
mouse_available = False
openrgb_available = False

# Check TTS
try:
    from TTS.api import TTS
    import torch
    import sounddevice as sd
    import soundfile as sf

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)

    voice_file = Path('clip_0001.wav')
    speaker_wav = str(voice_file) if voice_file.exists() else None

    tts_available = True
    print("✓ Voice system ready")
except:
    print("⚠ Voice system not available")

# Check mouse tracking
try:
    from pynput import mouse
    mouse_available = True
    print("✓ Mouse tracking ready")
except:
    print("⚠ Mouse tracking not available")

# Check OpenRGB
try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor

    client = OpenRGBClient()
    devices = client.devices

    if len(devices) > 0:
        openrgb_available = True
        print(f"✓ OpenRGB connected: {len(devices)} device(s)")
        for i, dev in enumerate(devices):
            print(f"  {i+1}. {dev.name} ({len(dev.leds)} LEDs)")
    else:
        print("⚠ OpenRGB connected but no LED devices")
except:
    print("⚠ OpenRGB not available")

def speak(text):
    """Omega speaks"""
    if not tts_available:
        print(f"[Omega] {text}")
        return

    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language='en',
            file_path='omega_speech.wav'
        )
        data, samplerate = sf.read('omega_speech.wav')
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"[Omega] {text}")
        print(f"  (Voice error: {e})")

def mouse_to_color(x, y, screen_width=1920, screen_height=1080):
    """Convert mouse position to RGB color"""
    # Normalize position
    hue = (x / screen_width) * 360  # X position determines hue
    brightness = (y / screen_height)  # Y position determines brightness

    # Convert HSV to RGB
    h = hue / 60
    c = brightness
    x_val = c * (1 - abs(h % 2 - 1))

    if h < 1:
        r, g, b = c, x_val, 0
    elif h < 2:
        r, g, b = x_val, c, 0
    elif h < 3:
        r, g, b = 0, c, x_val
    elif h < 4:
        r, g, b = 0, x_val, c
    elif h < 5:
        r, g, b = x_val, 0, c
    else:
        r, g, b = c, 0, x_val

    return (int(r * 255), int(g * 255), int(b * 255))

def on_move(x, y):
    """Handle mouse movement"""
    color = mouse_to_color(x, y)

    # Update LEDs
    if openrgb_available:
        try:
            for device in client.devices:
                if len(device.leds) > 0:
                    rgb_color = RGBColor(*color)
                    device.set_color(rgb_color)
        except:
            pass

    # Print color
    print(f"\rMouse: ({x:4}, {y:4}) → RGB({color[0]:3}, {color[1]:3}, {color[2]:3})", end='')

def main():
    print("\n" + "="*70)

    # Greeting
    speak("Hello! This is Omega. I'm starting the mouse-reactive LED system.")
    time.sleep(0.5)

    if not mouse_available:
        speak("Mouse tracking is not available. Please install pynput.")
        return

    if not openrgb_available:
        speak("OpenRGB is not detecting LED devices. The system will simulate colors, but LEDs won't light up.")
        print("\n💡 To enable LEDs:")
        print("  1. Open OpenRGB GUI")
        print("  2. Click 'Rescan Devices'")
        print("  3. Check BIOS LED settings if needed")
        print()
    else:
        speak("LED devices detected. As you move your mouse, the colors will change based on position.")

    speak("Move your mouse around the screen. Press Control plus C to stop.")

    print("\n" + "="*70)
    print("Mouse-Reactive LED Mode Active!")
    print("X position = Color hue, Y position = Brightness")
    print("Press Ctrl+C to exit")
    print("="*70 + "\n")

    # Start mouse listener
    with mouse.Listener(on_move=on_move) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        if tts_available:
            speak("Mouse-reactive LED system stopped. Thank you!")
        else:
            print("[Omega] Mouse-reactive LED system stopped. Thank you!")
        print("="*70)
