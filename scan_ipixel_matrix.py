"""
Ipixel LED Matrix Network Scanner
Device: LED_32*16_58FO_L
App Password: 139069
"""
import socket


def scan_network_fast() -> list[tuple[str, int]]:
    """Fast network scan for LED matrix"""
    print("🔍 Scanning for LED_32*16_58FO_L...\n")

    # Get local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    network_base = '.'.join(local_ip.split('.')[:3])
    print(f"📡 Your PC: {local_ip}")
    print(f"   Scanning: {network_base}.1-254 on Ipixel ports\n")

    # Ipixel ports
    ports = [8899, 5577, 8080]
    found: list[tuple[str, int]] = []

    for i in range(1, 255):
        ip = f"{network_base}.{i}"

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.05)
                result = sock.connect_ex((ip, port))
                sock.close()

                if result == 0:
                    print(f"✅ Device found: {ip}:{port}")
                    found.append((ip, port))
                    break
            except Exception:
                pass

    return found

def test_ipixel_connection(ip: str, port: int = 8899) -> bool:
    """Test connection and send color command"""
    print(f"\n🔌 Testing {ip}:{port}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, port))

        # Purple color command for Ipixel
        cmd = bytes([0x31, 128, 0, 128, 0x00, 0xf0, 0x0f])
        sock.send(cmd)

        print("✅ Connected! Sent purple command")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("═" * 60)
    print("  IPIXEL MATRIX SCANNER")
    print("  Device: LED_32*16_58FO_L | Clock mode active")
    print("═" * 60)
    print()

    devices = scan_network_fast()

    if devices:
        print(f"\n✅ Found {len(devices)} potential device(s)\n")

        for ip, port in devices:
            if test_ipixel_connection(ip, port):
                print(f"\n🎯 LED Matrix IP: {ip}:{port}")
                print("   Ready for control!")
                break
    else:
        print("\n❌ No devices found on network")
        print("\nCheck:")
        print("  1. LED matrix is powered (5V 2A)")
        print("  2. Clock is visible on display")
        print("  3. WiFi is connected")
        print("  4. Both on same network")
