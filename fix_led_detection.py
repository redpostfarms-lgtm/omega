"""
LED Detection Fix - Multiple detection methods
Tries different approaches to detect and enable LEDs
"""

import subprocess
import time
from pathlib import Path

print("\n" + "="*70)
print("  🔧 LED DETECTION & FIX UTILITY")
print("="*70)

# Check OpenRGB
print("\n[1] Checking OpenRGB Connection...")
try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor, DeviceType

    client = OpenRGBClient()
    print(f"✓ Connected to OpenRGB server")

    devices = client.devices
    print(f"  Devices found: {len(devices)}")

    for i, device in enumerate(devices):
        print(f"\n  Device {i+1}: {device.name}")
        print(f"    Type: {device.type}")
        print(f"    LEDs: {len(device.leds)}")
        print(f"    Zones: {len(device.zones)}")
        print(f"    Modes: {len(device.modes)}")

        if len(device.leds) == 0 and len(device.zones) > 0:
            print(f"    ⚠️ Device has zones but no LEDs detected")
            print(f"       Zones might need manual configuration")

            for zone in device.zones:
                print(f"       Zone: {zone.name} ({zone.type})")

        # Try to get more info
        try:
            print(f"    Vendor: {device.vendor}")
            print(f"    Location: {device.location}")
        except:
            pass

    if len(devices) == 0:
        print("  ⚠️ No devices detected")
        print("\n  Troubleshooting:")
        print("    1. Click 'Rescan Devices' in OpenRGB GUI")
        print("    2. Check if LEDs are physically connected")
        print("    3. Enable RGB in BIOS (ASUS Aura settings)")
        print("    4. Try running OpenRGB as Administrator")

except Exception as e:
    print(f"✗ OpenRGB connection failed: {e}")
    print("  Make sure OpenRGB server is running")

# Check for ASUS Aura software
print("\n[2] Checking ASUS Aura Software...")
aura_paths = [
    Path("C:/Program Files (x86)/ASUS/AuraSync"),
    Path("C:/Program Files/ASUS/AuraSync"),
    Path("C:/Program Files (x86)/LightingService"),
]

aura_found = False
for path in aura_paths:
    if path.exists():
        print(f"✓ Found: {path}")
        aura_found = True

if not aura_found:
    print("⚠️ ASUS Aura software not found")
    print("  This might prevent LED detection")
    print("  OpenRGB usually works without it, but check:")
    print("    - BIOS RGB settings")
    print("    - Physical RGB connections")

# Check for RGB devices via WMI
print("\n[3] Checking System Devices...")
try:
    result = subprocess.run(
        ["powershell", "-Command", "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*RGB*' -or $_.FriendlyName -like '*LED*' -or $_.FriendlyName -like '*AURA*'} | Select-Object FriendlyName, Status"],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.stdout.strip():
        print("RGB-related devices:")
        print(result.stdout)
    else:
        print("⚠️ No RGB devices found in Device Manager")

except Exception as e:
    print(f"  Could not query devices: {e}")

# Manual LED test
print("\n[4] Manual LED Test...")
try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor

    client = OpenRGBClient()

    if len(client.devices) > 0:
        print("Testing each device with RED color...")

        for i, device in enumerate(client.devices):
            print(f"\n  Testing device {i+1}: {device.name}")

            try:
                # Try direct mode
                if len(device.modes) > 0:
                    print(f"    Setting to Direct mode...")
                    device.set_mode('direct')

                # Try setting color
                if len(device.leds) > 0:
                    print(f"    Setting {len(device.leds)} LEDs to RED...")
                    device.set_color(RGBColor(255, 0, 0))
                    print(f"    ✓ Command sent")
                    time.sleep(2)
                else:
                    print(f"    ⚠️ No LEDs to control")

                    # Try zones
                    if len(device.zones) > 0:
                        print(f"    Trying zones...")
                        for zone in device.zones:
                            try:
                                zone.set_color(RGBColor(255, 0, 0))
                                print(f"      ✓ Set zone: {zone.name}")
                            except Exception as ze:
                                print(f"      ✗ Zone {zone.name} failed: {ze}")

            except Exception as de:
                print(f"    ✗ Error: {de}")

except Exception as e:
    print(f"✗ Test failed: {e}")

# Summary
print("\n" + "="*70)
print("  LED DETECTION SUMMARY")
print("="*70)
print()
print("If LEDs still don't work:")
print()
print("1. BIOS Settings:")
print("   - Restart and enter BIOS (DEL or F2 key)")
print("   - Look for 'Onboard LED' or 'AURA Lighting'")
print("   - Enable RGB/LED control")
print()
print("2. Physical Connection:")
print("   - Check RGB headers on motherboard")
print("   - Ensure LED strips/devices are plugged in")
print("   - 3-pin or 4-pin RGB headers (not regular fan headers)")
print()
print("3. OpenRGB Settings:")
print("   - Tools → Settings → Enable SDK Server")
print("   - Tools → Rescan Devices")
print("   - Try 'Direct' mode for each device")
print()
print("4. Alternative:")
print("   - Install SignalRGB: https://signalrgb.com/")
print("   - Or ASUS Armoury Crate")
print()
