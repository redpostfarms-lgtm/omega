"""
🎮 Unified LED Controller - Multi-App Support
Controls your USB LED using any detected application
"""

import math
import subprocess
import time
from pathlib import Path

print("\n" + "=" * 70)
print("  🎮 UNIFIED LED CONTROLLER")
print("=" * 70 + "\n")

# Detected LED Apps (from your system)
LED_APPS = {
    "aura_creator": {
        "name": "Aura Creator",
        "app_id": "B9ECED6F.AURAC",
        "type": "aura",
        "supports_usb": True,
        "priority": 1
    },
    "magic_light": {
        "name": "Control Program for Magic Light-BLE",
        "app_id": "48425Shipwreck",
        "type": "bluetooth",
        "supports_usb": False,
        "priority": 3
    },
    "dark_lights": {
        "name": "DarkLights",
        "app_id": "51518DarkProje",
        "type": "ambient",
        "supports_usb": False,
        "priority": 4
    },
    "leds_app": {
        "name": "LED's App!",
        "app_id": "WellKnownSoftw",
        "type": "universal",
        "supports_usb": True,
        "priority": 2
    },
    "rgb_bulb": {
        "name": "RGB bulb",
        "app_id": "622PKar.RGBbul",
        "type": "bulb",
        "supports_usb": False,
        "priority": 5
    },
    "smart_led": {
        "name": "Smart LED WiFi",
        "app_id": "Rython.SmartLE",
        "type": "wifi",
        "supports_usb": False,
        "priority": 6
    },
    "openrgb": {
        "name": "OpenRGB",
        "path": r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe",
        "type": "universal",
        "supports_usb": True,
        "priority": 7
    }
}


class UnifiedLEDController:
    """Unified interface for controlling LED via multiple apps"""

    def __init__(self):
        self.active_app = None
        self.openrgb_path = Path(r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe")

    def detect_best_app(self):
        """Find the best available app for USB LED control"""
        print("[1] Detecting best LED control method...")

        # Check OpenRGB first (most reliable for USB control)
        if self.openrgb_path.exists():
            print(f"  ✓ OpenRGB available: {self.openrgb_path}")
            self.active_app = "openrgb"
            return True

        # Check for USB-compatible apps
        usb_apps = [app for app, data in LED_APPS.items()
                   if data.get("supports_usb", False)]

        if usb_apps:
            # Sort by priority
            usb_apps.sort(key=lambda x: LED_APPS[x]["priority"])
            self.active_app = usb_apps[0]
            print(f"  ✓ Using: {LED_APPS[self.active_app]['name']}")
            return True

        print("  ✗ No USB-compatible LED apps found")
        return False

    def launch_app(self, app_key: str) -> bool:
        """Launch the specified LED control app"""
        app_data = LED_APPS.get(app_key)

        if not app_data:
            return False

        try:
            if "path" in app_data:
                # Launch via executable path
                subprocess.Popen([app_data["path"]])
                print(f"  ✓ Launched: {app_data['name']}")
            elif "app_id" in app_data:
                # Launch via AppID
                cmd = f"Start-Process shell:AppsFolder\\{app_data['app_id']}"
                subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    timeout=5
                )
                print(f"  ✓ Launched: {app_data['name']}")

            time.sleep(2)  # Give app time to start
            return True

        except Exception as e:
            print(f"  ✗ Failed to launch {app_data['name']}: {e}")
            return False

    def set_color_via_openrgb(self, red: int, green: int, blue: int) -> bool:
        """Set LED color using OpenRGB"""
        if not self.openrgb_path.exists():
            return False

        try:
            hex_color = f"{red:02X}{green:02X}{blue:02X}"
            subprocess.run(
                [str(self.openrgb_path), "--color", hex_color],
                capture_output=True,
                timeout=2
            )
            return True
        except Exception:
            return False

    def red_wave_pattern(self, duration: int = 10) -> None:
        """Display RED wave pattern"""
        print(f"\n[2] Starting RED WAVE pattern for {duration} seconds...")
        print("    Watch your USB LED strip!\n")

        if self.active_app == "openrgb":
            # Use OpenRGB for direct control
            iterations = int(duration * 2)

            for i in range(iterations):
                # Calculate wave intensity
                intensity = int(abs(math.sin(i * 0.3)) * 255)

                # Set RED color with varying intensity
                self.set_color_via_openrgb(intensity, 0, 0)

                print(f"    Wave {i+1}/{iterations}: RED intensity {intensity}/255", end="\r")
                time.sleep(0.5)

            print("\n\n  ✓ Wave pattern complete!")

        else:
            # Launch the app and let user control manually
            print(f"  → Opening {LED_APPS[self.active_app]['name']}...")
            print("  → Please set RED wave pattern manually in the app")
            self.launch_app(self.active_app)

    def test_all_apps(self):
        """Test launching all detected USB apps"""
        print("\n[TEST MODE] Launching all USB-compatible apps...")

        for app_key, app_data in LED_APPS.items():
            if app_data.get("supports_usb", False):
                print(f"\n  Testing: {app_data['name']}")
                self.launch_app(app_key)
                time.sleep(1)


def main():
    controller = UnifiedLEDController()

    if controller.detect_best_app():
        print("\n" + "-" * 70)

        # Show menu
        print("\n🎮 Control Options:")
        print("  1. RED Wave Pattern (10 seconds)")
        print("  2. Launch App for Manual Control")
        print("  3. Test All Apps")
        print()

        choice = input("Select option (1-3) or press Enter for RED wave: ").strip()

        if choice == "3":
            controller.test_all_apps()
        elif choice == "2":
            controller.launch_app(controller.active_app)
        else:
            # Default: RED wave
            controller.red_wave_pattern(duration=10)
    else:
        print("\n⚠️ No compatible LED control method found")
        print("\nAvailable apps (may not support USB):")
        for app_key, app_data in LED_APPS.items():
            if app_key != "openrgb":
                print(f"  • {app_data['name']} ({app_data['type']})")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
