"""
UNIFIED LED CONTROLLER
Controls both ASUS motherboard LEDs (OpenRGB) and Ipixel LED Matrix
Router: HOUSEOFCHAOS | Password: FiX562722!
Device: LED_32*16_58FO_L | App: Ipixel Color v3.4.6
"""
import socket
import time

from openrgb import OpenRGBClient  # type: ignore
from openrgb.utils import RGBColor  # type: ignore

# Ipixel LED Matrix Configuration
MATRIX_PASSWORD = "139069"
MATRIX_NAME = "LED_32*16_58FO_L"
MATRIX_IP = None  # Will be auto-detected
MATRIX_PORT = 8899


def find_ipixel_matrix() -> str | None:
    """Auto-detect Ipixel LED matrix on network"""
    print("🔍 Scanning for Ipixel LED matrix...\n")

    # Get local network
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    network_base = '.'.join(local_ip.split('.')[:3])
    print(f"   Network: {network_base}.x")

    # Quick scan common IPs
    for i in [10, 20, 50, 100, 150, 200, 250]:
        ip = f"{network_base}.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            if sock.connect_ex((ip, MATRIX_PORT)) == 0:
                print(f"   ✅ Found at {ip}:{MATRIX_PORT}")
                sock.close()
                return ip
            sock.close()
        except Exception:
            pass

    print("   ❌ Matrix not found")
    return None

def set_matrix_color(ip: str, r: int, g: int, b: int) -> bool:
    """Send color command to Ipixel matrix"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, MATRIX_PORT))

        # Ipixel color command
        cmd = bytes([0x31, r, g, b, 0x00, 0xf0, 0x0f])
        sock.send(cmd)
        sock.close()
        return True
    except Exception:
        return False

def unified_red_wave():
    """Red wave on BOTH motherboard LEDs and LED matrix"""
    print("═" * 70)
    print("  UNIFIED LED CONTROLLER - RED WAVE")
    print("  Motherboard: ASUS PRIME B550-PLUS (20 LEDs)")
    print(f"  LED Matrix: {MATRIX_NAME} (16x32 pixels)")
    print("═" * 70)
    print()

    # Connect to OpenRGB for motherboard LEDs
    print("🔌 Connecting to OpenRGB...")
    try:
        openrgb_client = OpenRGBClient()
        mb_devices = [d for d in openrgb_client.devices if len(d.leds) > 0]

        if mb_devices:
            for dev in mb_devices:
                dev.set_mode('direct')
            print(f"   ✅ Motherboard LEDs: {sum(len(d.leds) for d in mb_devices)} total")
        else:
            print("   ⚠️ No motherboard LEDs detected")
            mb_devices = []
    except Exception as e:
        print(f"   ❌ OpenRGB failed: {e}")
        mb_devices = []

    # Find Ipixel LED matrix
    matrix_ip = find_ipixel_matrix()

    if not matrix_ip and not mb_devices:
        print("\n❌ No LED devices available")
        return

    print("\n🌊 RED WAVE ACTIVE - Press Ctrl+C to stop\n")

    try:
        wave_position = 0
        while True:
            # Update motherboard LEDs
            for device in mb_devices:
                for i, led in enumerate(device.leds):
                    wave_offset = (i + wave_position) % 20
                    brightness = int(255 * (0.5 + 0.5 * (wave_offset / 20)))
                    device.leds[i].set_color(RGBColor(brightness, 0, 0))

            # Update LED matrix
            if matrix_ip:
                wave_brightness = int(255 * abs(((wave_position % 40) - 20) / 20))
                set_matrix_color(matrix_ip, wave_brightness, 0, 0)

            wave_position = (wave_position + 1) % 40
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping red wave...")

        # Turn off motherboard LEDs
        for device in mb_devices:
            for led in device.leds:
                led.set_color(RGBColor(0, 0, 0))

        # Turn off LED matrix
        if matrix_ip:
            set_matrix_color(matrix_ip, 0, 0, 0)

        print("✅ All LEDs off. Goodbye!")

def set_all_purple():
    """Set both motherboard and matrix to purple"""
    print("💜 Setting all LEDs to purple...\n")

    # Motherboard
    try:
        client = OpenRGBClient()
        for device in client.devices:
            device.set_mode('direct')
            for led in device.leds:
                led.set_color(RGBColor(128, 0, 128))
        print("   ✅ Motherboard: Purple")
    except Exception:
        print("   ⚠️ Motherboard: Not available")

    # Matrix
    matrix_ip = find_ipixel_matrix()
    if matrix_ip:
        if set_matrix_color(matrix_ip, 128, 0, 128):
            print(f"   ✅ LED Matrix ({matrix_ip}): Purple")
    else:
        print("   ⚠️ LED Matrix: Not connected")

if __name__ == "__main__":
    print("\n🎮 CHOOSE MODE:")
    print("   1. Red Wave (animated)")
    print("   2. All Purple (static)")
    print("   3. Find Matrix IP only")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        unified_red_wave()
    elif choice == "2":
        set_all_purple()
    elif choice == "3":
        ip = find_ipixel_matrix()
        if ip:
            print(f"\n✅ Matrix IP: {ip}:{MATRIX_PORT}")
    else:
        print("Invalid choice")
