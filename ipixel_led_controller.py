"""
Ipixel LED Matrix Controller - LED_32*16_58FO_L
Password: 139069
Currently displaying: Clock function
"""
import socket
import time
import struct

DEVICE_NAME = "LED_32*16_58FO_L"
PASSWORD = "139069"

def scan_network_fast():
    """Quick network scan for LED matrix"""
    print("🔍 Scanning network for LED matrix...\n")
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    network_base = '.'.join(local_ip.split('.')[:3])
    
    print(f"📡 Your PC: {local_ip}")
    print(f"   Network: {network_base}.x\n")
    
    # Ipixel standard port
    port = 8899
    
    found_devices = []
    
    print("Scanning common device IPs...")
    # Common router assigned IPs
    common_ranges = list(range(2, 20)) + list(range(100, 120)) + list(range(150, 170))
    
    for i in common_ranges:
        ip = f"{network_base}.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                print(f"\n✅ Found device at {ip}:{port}")
                found_devices.append((ip, port))
            
            sock.close()
        except:
            pass
        
        if i % 10 == 0:
            print(f".", end="", flush=True)
    
    print()
    return found_devices

def connect_ipixel(ip, port=8899):
    """Connect and verify Ipixel device"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        # Query device status
        sock.send(b'\x81\x8a\x8b\x96')
        time.sleep(0.1)
        
        try:
            response = sock.recv(1024)
            print(f"   Device response: {response.hex()}")
        except:
            pass
        
        sock.close()
        return True
    except Exception as e:
        return False

def set_color(ip, port, r, g, b):
    """Set solid color on LED matrix"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        # Ipixel color command
        checksum = (0x31 + r + g + b) & 0xFF
        command = bytes([0x31, r, g, b, 0x00, 0x00, 0x00, 0x00, 0x0f, checksum])
        sock.send(command)
        
        sock.close()
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def show_text(ip, port, text):
    """Display text on LED matrix"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        # Text display command (protocol varies by firmware)
        # This is a basic attempt
        text_bytes = text.encode('utf-8')
        command = b'\x50' + bytes([len(text_bytes)]) + text_bytes
        sock.send(command)
        
        sock.close()
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def display_clock_override(ip, port):
    """Try to override clock with custom display"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        # Try to switch from clock mode to color mode
        # First, send mode change command
        sock.send(b'\x61\x01\x0f')  # Exit clock mode
        time.sleep(0.2)
        
        # Then set a color
        command = bytes([0x31, 128, 0, 128, 0x00, 0x00, 0x00, 0x00, 0x0f])
        sock.send(command)
        
        sock.close()
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_matrix(ip, port):
    """Test LED matrix with colors"""
    print(f"\n🎨 Testing LED matrix at {ip}:{port}...\n")
    
    colors = [
        ("Red", 255, 0, 0),
        ("Green", 0, 255, 0),
        ("Blue", 0, 0, 255),
        ("Purple", 128, 0, 128),
        ("White", 255, 255, 255),
    ]
    
    print("   Trying to override clock display...")
    display_clock_override(ip, port)
    time.sleep(0.5)
    
    for name, r, g, b in colors:
        print(f"   Setting {name}...")
        if set_color(ip, port, r, g, b):
            print(f"   ✅ {name} sent")
        time.sleep(1)
    
    # Return to purple
    set_color(ip, port, 128, 0, 128)

if __name__ == "__main__":
    print("═" * 70)
    print(f"  IPIXEL LED MATRIX CONTROLLER")
    print(f"  Device: {DEVICE_NAME}")
    print(f"  Password: {PASSWORD}")
    print(f"  Current mode: Clock")
    print("═" * 70)
    print()
    
    # Try manual IP first
    test_ips = [
        "192.168.1.100",
        "192.168.1.150",
        "192.168.0.100",
        "192.168.0.150",
    ]
    
    print("🔍 Quick test of common IPs...")
    for ip in test_ips:
        if connect_ipixel(ip, 8899):
            print(f"\n✅ Found device at {ip}:8899")
            test_matrix(ip, 8899)
            exit(0)
    
    # Full network scan
    devices = scan_network_fast()
    
    if devices:
        ip, port = devices[0]
        print(f"\n✅ Using device at {ip}:{port}")
        test_matrix(ip, port)
    else:
        print("\n❌ No Ipixel devices found on network")
        print("\nPLEASE PROVIDE:")
        print("1. Open Ipixel Color app")
        print("2. Go to: Settings → Device Info")
        print("3. Find the IP address (192.168.x.x)")
        print("4. Tell me the IP address")
