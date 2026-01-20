"""
Ipixel LED Matrix Controller - LED_32*16_58FO_L
Direct control for specific device
"""
import socket
import time

def find_device_by_name():
    """Search for LED_32*16_58FO_L device"""
    print("🔍 Searching for: LED_32*16_58FO_L\n")

    # Get local network
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    network_base = '.'.join(local_ip.split('.')[:3])

    print(f"📡 Scanning network: {network_base}.1-254")
    print("   Looking for device on common LED ports...\n")

    # Ipixel common ports
    test_ports = [8080, 8899, 5577, 48899]

    found = []
    for i in range(1, 255):
        ip = f"{network_base}.{i}"
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, port))

                if result == 0:
                    print(f"✅ Found device at {ip}:{port}")
                    found.append((ip, port))

                sock.close()
            except:
                pass

        if i % 50 == 0:
            print(f"   Scanned {i}/254...")

    return found

def connect_ipixel(ip, port=8899):
    """Connect to Ipixel LED matrix"""
    print(f"\n🔌 Connecting to {ip}:{port}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))

        # Send status query
        sock.send(b'\x81\x8a\x8b')
        response = sock.recv(1024)

        print(f"✅ Connected! Response: {response.hex()}")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def set_matrix_color(ip, port, r, g, b):
    """Set LED matrix to solid color"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))

        # Ipixel color command format
        command = bytes([0x31, r, g, b, 0x00, 0x00, 0x00, 0xf0, 0x0f])
        sock.send(command)

        print(f"✅ Set color RGB({r}, {g}, {b})")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("═" * 60)
    print("  IPIXEL LED MATRIX: LED_32*16_58FO_L")
    print("═" * 60)
    print()

    # Check if user knows IP
    manual_ip = input("Do you know the IP address? (press Enter to scan): ")

    if manual_ip.strip():
        ip = manual_ip.strip()
        port = 8899

        if connect_ipixel(ip, port):
            print("\n🎨 Testing colors...")
            set_matrix_color(ip, port, 255, 0, 0)    # Red
            time.sleep(1)
            set_matrix_color(ip, port, 0, 255, 0)    # Green
            time.sleep(1)
            set_matrix_color(ip, port, 0, 0, 255)    # Blue
            time.sleep(1)
            set_matrix_color(ip, port, 128, 0, 128)  # Purple
    else:
        devices = find_device_by_name()

        if devices:
            print(f"\n✅ Found {len(devices)} device(s)")
            for ip, port in devices:
                print(f"\nTesting {ip}:{port}...")
                if connect_ipixel(ip, port):
                    set_matrix_color(ip, port, 128, 0, 128)  # Purple
        else:
            print("\n❌ No devices found")
            print("\nMANUAL STEPS:")
            print("1. Open Ipixel app on phone")
            print("2. Go to Settings → Device Info")
            print("3. Note the IP address (192.168.x.x)")
            print("4. Run: python ipixel_direct_control.py")
            print("5. Enter the IP address when prompted")
