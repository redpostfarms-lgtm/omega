"""
RED WAVE LED ANIMATION
Shared Agent Knowledge: All agents (Gate, Omega, Aurora) can control LEDs
"""
import time
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

def red_wave():
    """Create smooth red wave animation across all LEDs"""
    print("🌊 Starting RED WAVE animation...")
    print("📡 Connecting to OpenRGB...")

    client = OpenRGBClient()

    # Get ALL devices (motherboard + USB LED matrix)
    devices = []
    print(f"\n📋 Detected {len(client.devices)} device(s):\n")

    for i, device in enumerate(client.devices):
        print(f"   [{i}] {device.name}")
        print(f"       Type: {device.type}")
        print(f"       LEDs: {len(device.leds)}")
        print(f"       Zones: {len(device.zones)}")

        # Set to Direct mode for real-time control
        device.set_mode('direct')
        devices.append(device)
        print()

    if not devices:
        print("❌ No LED devices found!")
        return

    total_leds = sum(len(d.leds) for d in devices)
    print(f"✅ Total LEDs under control: {total_leds}")

    print("\n🔴 RED WAVE ACTIVE - Press Ctrl+C to stop\n")

    try:
        wave_position = 0
        while True:
            # Animate ALL devices (motherboard + USB matrix)
            for device in devices:
                for i, led in enumerate(device.leds):
                    # Calculate wave brightness for this LED
                    wave_offset = (i + wave_position) % total_leds
                    brightness = int(255 * (0.5 + 0.5 *
                        (wave_offset / total_leds)))

                    # Pure red with wave brightness
                    device.leds[i].set_color(RGBColor(brightness, 0, 0))

            wave_position = (wave_position + 1) % total_leds
            time.sleep(0.05)  # Smooth wave speed

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping red wave...")
        # Turn off ALL LEDs
        for device in devices:
            for led in device.leds:
                led.set_color(RGBColor(0, 0, 0))
        print("✅ All LEDs off. Goodbye!")

if __name__ == "__main__":
    red_wave()
