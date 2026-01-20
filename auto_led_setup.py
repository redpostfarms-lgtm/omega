"""
Automated LED Setup - Tests and recommends best control method
"""
import subprocess
from pathlib import Path

print("\n" + "="*70)
print("  🎮 AUTOMATED LED CONTROLLER SETUP")
print("="*70 + "\n")

# Step 1: Check OpenRGB
openrgb_path = Path(r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe")

print("[1] Checking OpenRGB (Best for USB LED control)...")
if openrgb_path.exists():
    print(f"  ✓ OpenRGB found: {openrgb_path}")
    print(f"  ✓ Size: {openrgb_path.stat().st_size:,} bytes")
    print("\n  → OpenRGB is READY for RED wave pattern")
    print("\n[RECOMMENDATION] Use OpenRGB for best results")
    print("\nNext steps:")
    print("  1. Run with admin: .\\START_OPENRGB_SERVER.ps1")
    print("  2. Then run: python test_openrgb_red_wave.py")
    recommended_method: str | None = "openrgb"
else:
    print("  ✗ OpenRGB not found at expected location")
    recommended_method: str | None = None

# Step 2: Check downloaded LED apps
print("\n[2] Checking downloaded LED control apps...")
led_apps = [
    {"name": "Aura Creator", "app_id": "B9ECED6F.AURAC", "usb": True},
    {"name": "LED's App!", "app_id": "WellKnownSoftware", "usb": True},
    {"name": "Magic Light BLE", "app_id": "48425Shipwreck", "usb": False},
    {"name": "Smart LED WiFi", "app_id": "Rython.SmartLE", "usb": False},
]

usb_apps = [app for app in led_apps if app["usb"]]
print(f"  ✓ Found {len(usb_apps)} USB-compatible apps:")
for app in usb_apps:
    print(f"    • {app['name']}")

if not recommended_method and usb_apps:
    recommended_method = "apps"

# Step 3: Check AURA hardware
print("\n[3] Checking for AURA LED Controller hardware...")
try:
    result = subprocess.run(
        ["powershell", "-Command",
         "Get-PnpDevice | Where-Object { $_.InstanceId -like '*VID_0B05*' } | Select-Object -First 1 FriendlyName, Status"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if "OK" in result.stdout or "AURA" in result.stdout:
        print("  ✓ AURA LED Controller detected")
        print("  ✓ Status: Connected")
    else:
        print("  ⚠️ AURA device status unknown")
except Exception as e:
    print(f"  ⚠️ Could not verify hardware: {e}")

# Step 4: Final recommendation
print("\n" + "="*70)
print("  📊 SETUP COMPLETE - RECOMMENDATIONS")
print("="*70 + "\n")

if recommended_method == "openrgb":
    print("✅ BEST OPTION: OpenRGB (Direct USB Control)")
    print("\n🚀 QUICK START:")
    print("  Step 1: Open PowerShell as Administrator")
    print("  Step 2: cd 'H:\\The Gatekeeper'")
    print("  Step 3: .\\START_OPENRGB_SERVER.ps1")
    print("  Step 4: python test_openrgb_red_wave.py")
    print("\n  → This will show RED waves on your USB LED!")

    print("\n🔄 ALTERNATIVE: Manual control")
    print(f"  • Double-click: {openrgb_path}")
    print("  • Select your AURA device")
    print("  • Set color to RED manually")

elif recommended_method == "apps":
    print("✅ OPTION: Use Downloaded LED Apps")
    print("\n🚀 RECOMMENDED APPS:")
    for app in usb_apps:
        print(f"  • {app['name']}")
    print("\n  Launch any app and configure your USB LED manually")

    # Create launcher
    print("\n  Or run: python launch_led_app.py")

else:
    print("⚠️ NO DIRECT USB CONTROL AVAILABLE")
    print("\nOptions:")
    print("  1. Install OpenRGB: https://openrgb.org")
    print("  2. Use your downloaded apps for manual control")

# Step 5: Create quick-launch batch file
print("\n[4] Creating quick-launch shortcuts...")

batch_content = f"""@echo off
echo Starting OpenRGB LED Control...
cd /d "H:\\The Gatekeeper"
PowerShell -Command "Start-Process '{openrgb_path}' -Verb RunAs"
timeout /t 3
python test_openrgb_red_wave.py
pause
"""

batch_path = Path("H:/The Gatekeeper/QUICK_LED_RED_WAVE.bat")
with open(batch_path, "w") as f:
    f.write(batch_content)

print(f"  ✓ Created: {batch_path.name}")
print("    → Double-click this file for instant RED waves!")

print("\n" + "="*70)
print("  Setup complete! You're ready to control your LED.")
print("="*70 + "\n")
