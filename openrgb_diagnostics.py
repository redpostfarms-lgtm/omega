"""
OpenRGB Device Diagnostics & Auto-Detection
Helps identify LED hardware issues
"""
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import time

print("\n" + "="*70)
print("  🔍 OPENRGB DEVICE DIAGNOSTICS")
print("="*70 + "\n")

try:
    # Connect
    print("[1/5] Connecting to OpenRGB server...")
    client = OpenRGBClient()
    print("      ✅ Connected to OpenRGB\n")

    # Get device count
    print(f"[2/5] Total devices detected: {len(client.devices)}\n")

    # Detailed device information
    print("[3/5] Device Details:")
    for i, device in enumerate(client.devices):
        print(f"\n      Device #{i+1}: {device.name}")
        print(f"      Type: {device.type}")
        print(f"      Vendor: {device.vendor if hasattr(device, 'vendor') else 'N/A'}")
        print(f"      Location: {device.location if hasattr(device, 'location') else 'N/A'}")
        print(f"      Serial: {device.serial if hasattr(device, 'serial') else 'N/A'}")
        print(f"      Version: {device.version if hasattr(device, 'version') else 'N/A'}")
        print(f"      LEDs: {len(device.leds)}")
        print(f"      Zones: {len(device.zones)}")
        print(f"      Modes: {len(device.modes)}")

        # Show available modes
        if device.modes:
            print(f"      Available Modes:")
            for mode in device.modes:
                print(f"         - {mode.name}")

        # Zone information
        if device.zones:
            print(f"      Zone Information:")
            for zone in device.zones:
                print(f"         - {zone.name}: {len(zone.leds)} LEDs")

    # Check for I2C/SMBus devices
    print("\n[4/5] Hardware Detection Status:")
    smbus_devices = [d for d in client.devices if 'I2C' in d.location or 'SMBus' in d.location]
    usb_devices = [d for d in client.devices if 'USB' in d.location or 'HID' in d.location]

    print(f"      SMBus/I2C Devices: {len(smbus_devices)}")
    print(f"      USB Devices: {len(usb_devices)}")

    # Recommendations
    print("\n[5/5] Recommendations:")

    total_leds = sum(len(d.leds) for d in client.devices)
    if total_leds == 0:
        print("\n      ⚠️  NO LEDs DETECTED")
        print("\n      Possible Solutions:")
        print("      1. Enable ASUS Aura in BIOS:")
        print("         - Restart → BIOS → Advanced → Onboard Devices")
        print("         - Enable 'Aura LED' or 'RGB LED Lighting'")
        print("")
        print("      2. Connect physical LED strips:")
        print("         - Check 12V RGB or 5V ARGB headers on motherboard")
        print("         - Ensure strips are properly connected")
        print("")
        print("      3. Install SMBus drivers:")
        print("         - Download chipset drivers from ASUS website")
        print("         - Ensure SMBus controller is enabled in Device Manager")
        print("")
        print("      4. Run OpenRGB as Administrator:")
        print("         - Required for SMBus/I2C access")
        print("         - Right-click OpenRGB.exe → Run as administrator")
        print("")
        print("      5. Rescan devices in OpenRGB:")
        print("         - Tools → SMBus Tools → Scan for devices")
        print("         - Settings → Enable all SMBus/I2C adapters")
    else:
        print(f"      ✅ {total_leds} controllable LEDs found!")
        print("      Ready to test lighting effects.")

    print("\n" + "="*70)
    print("  DIAGNOSTIC COMPLETE")
    print("="*70 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure OpenRGB server is running")
    print("2. Check if OpenRGB.exe is running as Administrator")
    print("3. Verify port 6742 is not blocked by firewall")
