"""
LED Color Controller - Set specific colors
Works with OpenRGB when available, shows visual simulation otherwise
"""
import time
import os

try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor
    OPENRGB_AVAILABLE = True
except ImportError:
    OPENRGB_AVAILABLE = False

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_color_block(r, g, b, label=""):
    """Print a colored block using ANSI colors"""
    # ANSI escape codes for RGB
    print(f"\033[48;2;{r};{g};{b}m" + " " * 40 + "\033[0m")
    if label:
        print(f"  {label}: RGB({r}, {g}, {b})")

def set_led_color(r, g, b, label="Color"):
    """Set LED color or show simulation"""
    print(f"\n{'='*60}")
    print(f"  Setting: {label}")
    print(f"  RGB: ({r}, {g}, {b})")
    print(f"{'='*60}\n")

    # Visual simulation
    print_color_block(r, g, b, label)

    if not OPENRGB_AVAILABLE:
        print("\n  ⚠️ OpenRGB not available - Showing simulation only")
        return False

    try:
        client = OpenRGBClient()
        devices = client.devices

        if not devices:
            print("\n  ⚠️ No devices found - Showing simulation only")
            return False

        # Apply to all devices
        success_count = 0
        for device in devices:
            if len(device.leds) > 0:
                device.set_color(RGBColor(r, g, b))
                success_count += 1
                print(f"  ✅ Applied to: {device.name} ({len(device.leds)} LEDs)")

        if success_count > 0:
            print(f"\n  ✅ Successfully set {success_count} device(s)!")
            return True
        else:
            print("\n  ⚠️ No controllable LEDs found")
            return False

    except ConnectionRefusedError:
        print("\n  ⚠️ OpenRGB server not running - Showing simulation only")
        return False
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False

def main():
    """Color palette menu"""
    clear_screen()
    print("\n" + "="*60)
    print("  LED COLOR CONTROLLER")
    print("="*60)

    colors = {
        "1": ("Red", 255, 0, 0),
        "2": ("Green", 0, 255, 0),
        "3": ("Blue", 0, 0, 255),
        "4": ("Yellow", 255, 255, 0),
        "5": ("Cyan", 0, 255, 255),
        "6": ("Magenta", 255, 0, 255),
        "7": ("White", 255, 255, 255),
        "8": ("Orange", 255, 165, 0),
        "9": ("Purple", 128, 0, 128),
        "10": ("Pink", 255, 192, 203),
        "11": ("Warm White", 255, 244, 229),
        "12": ("Cool White", 224, 255, 255),
    }

    print("\nAvailable Colors:")
    for key, (name, r, g, b) in colors.items():
        print(f"  {key}. {name} - RGB({r}, {g}, {b})")

    print("\n  0. Exit")
    print("\n" + "="*60)

    while True:
        choice = input("\nSelect color (0-12): ").strip()

        if choice == "0":
            print("\nExiting...")
            break

        if choice in colors:
            name, r, g, b = colors[choice]
            set_led_color(r, g, b, name)
            input("\nPress Enter to continue...")
            clear_screen()
            print("\n" + "="*60)
            print("  LED COLOR CONTROLLER")
            print("="*60)
            print("\nAvailable Colors:")
            for key, (nm, _r, _g, _b) in colors.items():
                print(f"  {key}. {nm} - RGB({_r}, {_g}, {_b})")
            print("\n  0. Exit")
            print("\n" + "="*60)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
