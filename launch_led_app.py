"""
Quick LED App Launcher - Test your downloaded apps
"""
import subprocess
import time

print("=" * 70)
print("LED APP LAUNCHER - Testing Your Downloaded Apps")
print("=" * 70)

# Your installed LED apps
apps = [
    ("Aura Creator", "B9ECED6F.AURAC"),
    ("LED's App!", "WellKnownSoftware"),
    ("Control Program for Magic Light-BLE", "48425Shipwreck"),
    ("RGB bulb", "622PKar.RGBbul"),
    ("Smart LED WiFi", "Rython.SmartLE"),
    ("DarkLights", "51518DarkProje"),
]

print("\nAvailable LED Apps:")
for i, (name, _) in enumerate(apps, 1):
    print(f"  {i}. {name}")

print("\n7. Launch ALL apps")
print("8. Test with OpenRGB (recommended)")
print()

choice = input("Select app to launch (1-8) or press Enter for OpenRGB: ").strip()

if choice == "7":
    print("\nLaunching ALL LED apps...")
    for name, app_id in apps:
        print(f"  → Starting {name}...")
        try:
            cmd = f"Start-Process shell:AppsFolder\\{app_id}"
            subprocess.Popen(["powershell", "-Command", cmd])
            time.sleep(1)
        except Exception as e:
            print(f"    ✗ Failed: {e}")
    print("\n✓ All apps launched!")

elif choice == "8" or choice == "":
    print("\nLaunching OpenRGB...")
    openrgb_path = r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe"
    try:
        subprocess.Popen([openrgb_path, "--server"])
        print("✓ OpenRGB started in server mode")
        print("\nYou can now:")
        print("  • Use the GUI to set RED color manually")
        print("  • Run: python test_openrgb_red_wave.py")
    except Exception as e:
        print(f"✗ Failed: {e}")

elif choice.isdigit() and 1 <= int(choice) <= 6:
    idx = int(choice) - 1
    name, app_id = apps[idx]
    print(f"\nLaunching {name}...")
    try:
        cmd = f"Start-Process shell:AppsFolder\\{app_id}"
        subprocess.run(["powershell", "-Command", cmd], check=True)
        print(f"✓ {name} should be opening now!")
        print("\nUse the app to control your USB LED strip")
    except Exception as e:
        print(f"✗ Failed: {e}")
else:
    print("Invalid choice")

print("\n" + "=" * 70)
