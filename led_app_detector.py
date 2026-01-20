"""
🔍 LED Application Detector & Controller
Detects installed LED/RGB control apps and creates unified interface
"""

import json
import subprocess
from pathlib import Path

def determine_app_type(name: str) -> str:
    """Determine the type of LED control app"""
    name_lower = name.lower()
    if "aura" in name_lower:
        return "aura"
    elif "magic" in name_lower or "ble" in name_lower:
        return "bluetooth"
    elif "wifi" in name_lower or "smart" in name_lower:
        return "wifi"
    elif "rgb bulb" in name_lower:
        return "bulb"
    elif "dark" in name_lower:
        return "ambient"
    else:
        return "universal"

print("\n" + "=" * 70)
print("  🔍 LED APPLICATION DETECTOR")
print("=" * 70 + "\n")

# Detect installed LED apps
print("[1] Scanning for LED/RGB control applications...")

try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-StartApps | Where-Object { $_.Name -match 'LED|RGB|Light|Color|Aura|Signal' } | ConvertTo-Json",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode == 0 and result.stdout.strip():
        apps_data = json.loads(result.stdout)

        # Handle single app or multiple apps
        if isinstance(apps_data, dict):
            apps_data = [apps_data]

        print(f"✓ Found {len(apps_data)} LED control applications:\n")

        detected_apps = []
        for app in apps_data:
            name = app.get("Name", "Unknown")
            app_id = app.get("AppID", "Unknown")
            print(f"  • {name}")
            print(f"    AppID: {app_id}")

            detected_apps.append({
                "name": name,
                "app_id": app_id,
                "type": determine_app_type(name)
            })

        print(f"\n✓ Total apps detected: {len(detected_apps)}")

        # Save detection results
        config_path = Path(__file__).parent / "led_apps_config.json"
        with open(config_path, "w") as f:
            json.dump({"apps": detected_apps}, f, indent=2)

        print(f"✓ Configuration saved to: {config_path}")

    else:
        print("✗ No LED applications detected")
        detected_apps = []

except Exception as e:
    print(f"✗ Error detecting applications: {e}")
    detected_apps = []

print("\n[2] Hardware Detection")
print("-" * 70)

# Check for AURA LED Controller
try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-PnpDevice | Where-Object { $_.FriendlyName -match 'LED|RGB|Light' -or $_.FriendlyName -match 'AURA' -or $_.InstanceId -match 'VID_0B05' } | Select-Object FriendlyName, Status, InstanceId | ConvertTo-Json",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode == 0 and result.stdout.strip():
        devices = json.loads(result.stdout)
        if isinstance(devices, dict):
            devices = [devices]

        print(f"✓ Found {len(devices)} LED hardware device(s):\n")
        for device in devices:
            print(f"  • {device['FriendlyName']}")
            print(f"    Status: {device['Status']}")
            print(f"    ID: {device['InstanceId'][:50]}...")
    else:
        print("  ℹ️ No USB LED devices detected")

except Exception as e:
    print(f"  ⚠️ Could not check hardware: {e}")

print("\n" + "=" * 70)
print("  📊 DETECTION COMPLETE")
print("=" * 70 + "\n")

if detected_apps:
    print("✅ LED control apps are available!")
    print("\nRecommended apps for your AURA LED Controller:")

    priority_apps = []
    for app in detected_apps:
        if app["type"] in ["aura", "universal", "bluetooth"]:
            priority_apps.append(app)

    if priority_apps:
        print("\n🎯 Best matches:")
        for app in priority_apps:
            print(f"  • {app['name']} ({app['type']})")

    print("\nNext: Creating unified LED controller...")
else:
    print("⚠️ No LED control apps detected")
    print("  Consider using OpenRGB (already installed)")

print("\n" + "=" * 70)

if __name__ == "__main__":
    print("\n💡 Run: python led_unified_controller.py")
    print("   to control your LED with any detected app\n")
