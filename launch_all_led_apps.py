"""
DIRECT LED APP LAUNCHER - Force launch each app and report
"""
import subprocess
import time

apps = [
    ("1. Aura Creator", "B9ECED6F.AURAC"),
    ("2. LED's App!", "WellKnownSoftware"),
    ("3. Magic Light BLE", "48425Shipwreck"),
    ("4. Smart LED WiFi", "Rython.SmartLE"),
    ("5. RGB bulb", "622PKar.RGBbul"),
    ("6. DarkLights", "51518DarkProje"),
]

print("\n" + "="*70)
print("DIRECT LED APP LAUNCHER")
print("="*70 + "\n")

for name, app_id in apps:
    print(f"Launching: {name}...")
    print(f"AppID: {app_id}")

    try:
        # Direct PowerShell launch
        cmd = f"Start-Process 'shell:AppsFolder\\{app_id}'"
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"✓ Launched successfully!")
        else:
            print(f"✗ Launch failed")
            if result.stderr:
                print(f"  Error: {result.stderr[:100]}")

        print(f"Waiting 5 seconds...")
        time.sleep(5)
        print()

    except Exception as e:
        print(f"✗ Exception: {e}\n")

print("="*70)
print("All apps launched. Check your screen for app windows.")
print("Try each app to control your LED.")
print("="*70)
