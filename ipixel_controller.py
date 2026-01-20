"""
Ipixel LED Matrix Controller
WiFi/Bluetooth LED matrix - 16x32 pixels
App: Ipixel Color v3.4.6
Features: Gallery, Remote, DIY Animation, Clock, Text, Rhythm
"""
import socket
import struct
import time

def scan_ipixel_devices():
    """Scan network for Ipixel LED matrix devices"""
    print("🔍 Scanning for Ipixel LED matrix on network...\n")

    # Ipixel devices typically broadcast on UDP or respond to discovery
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3)

    # Common Ipixel discovery ports
    discovery_ports = [8080, 8899, 5577, 9999, 48899]

    print("📡 Broadcasting discovery packets...\n")

    for port in discovery_ports:
        try:
            # Send discovery broadcast
            discovery_msg = b'\x81\x8a\x8b\x96'  # Common LED discovery packet
            sock.sendto(discovery_msg, ('255.255.255.255', port))

            print(f"   Sent to port {port}...")

            # Try to receive response
            try:
                data, addr = sock.recvfrom(1024)
                print(f"\n✅ FOUND LED MATRIX!")
                print(f"   IP Address: {addr[0]}")
                print(f"   Port: {addr[1]}")
                print(f"   Response: {data.hex()}")
                return addr[0], addr[1]
            except socket.timeout:
                pass

        except Exception as e:
            print(f"   Error on port {port}: {e}")

    print("\n❌ No Ipixel device found via broadcast")
    print("\nTrying network scan...")
    return None

def get_local_network():
    """Get local network IP range"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"   Your PC IP: {local_ip}")

    # Get network range (e.g., 192.168.1.x)
    ip_parts = local_ip.split('.')
    network_base = '.'.join(ip_parts[:3])

    return network_base, local_ip

def quick_network_scan():
    """Quick scan of local network for LED matrix"""
    network_base, local_ip = get_local_network()
    print(f"   Network range: {network_base}.1-254\n")

    print("🔎 Scanning common IP addresses...")

    # Common device IPs
    common_ips = [
        f"{network_base}.10",
        f"{network_base}.100",
        f"{network_base}.150",
        f"{network_base}.200",
        f"{network_base}.250",
    ]

    for ip in common_ips:
        for port in [8080, 8899, 5577]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                sock.close()

                if result == 0:
                    print(f"\n✅ Device responding at {ip}:{port}")
                    return ip, port
            except:
                pass

    print("\n❌ No devices found in quick scan")
    return None

def send_ipixel_command(ip, port, command):
    """Send command to Ipixel LED matrix"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))

        sock.send(command)
        time.sleep(0.1)

        response = sock.recv(1024)
        sock.close()

        return response
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return None

def test_ipixel_display(ip, port):
    """Test Ipixel display with color commands"""
    print(f"\n🧪 Testing Ipixel commands on {ip}:{port}...\n")

    # Common Ipixel/LED WiFi controller commands
    commands = {
        "Power On": b'\x71\x23\x0f\xa3',
        "Power Off": b'\x71\x24\x0f\xa4',
        "Red": b'\x31\xff\x00\x00\x00\x00\x00\xf0\x0f',
        "Green": b'\x31\x00\xff\x00\x00\x00\x00\xf0\x0f',
        "Blue": b'\x31\x00\x00\xff\x00\x00\x00\xf0\x0f',
        "Purple": b'\x31\x80\x00\x80\x00\x00\x00\xf0\x0f',
    }

    for name, cmd in commands.items():
        print(f"   Sending: {name}")
        response = send_ipixel_command(ip, port, cmd)
        if response:
            print(f"   ✅ Response: {response.hex()}")
        time.sleep(1)

if __name__ == "__main__":
    print("═" * 70)
    print("  IPIXEL LED MATRIX CONTROLLER")
    print("  App: Ipixel Color v3.4.6 | 16x32 pixels | WiFi/Bluetooth")
    print("═" * 70)
    print()

    # Try broadcast discovery first
    device = scan_ipixel_devices()

    if not device:
        # Try network scan
        device = quick_network_scan()

    if device:
        ip, port = device
        print(f"\n✅ Ready to control LED matrix at {ip}:{port}")

        # Test display
        response = input("\nTest the display? (y/n): ")
        if response.lower() == 'y':
            test_ipixel_display(ip, port)
    else:
        print("\n" + "─" * 70)
        print("TROUBLESHOOTING:")
        print("1. Make sure LED matrix is powered on (5V 2A)")
        print("2. Connect LED matrix to your WiFi network using Ipixel app")
        print("3. Check LED matrix IP in app Settings → Device Info")
        print("4. Ensure PC and LED matrix are on same network")
        print("─" * 70)
