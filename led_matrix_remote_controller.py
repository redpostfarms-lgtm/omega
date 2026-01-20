"""
LED Matrix Remote Controller
16x32 LED matrix with onboard controller and remote control
Specs: 173x70mm, 5V @ 2A, USB connection
"""
import serial
import serial.tools.list_ports
import time

def find_led_matrix_serial():
    """Find LED matrix serial/COM port"""
    print("🔍 Scanning for LED matrix controller...\n")

    ports = serial.tools.list_ports.comports()

    if not ports:
        print("❌ No COM ports found")
        return None

    print("📋 Available COM ports:\n")
    for port in ports:
        print(f"   Port: {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")

        # Check for common LED matrix identifiers
        if any(keyword in port.description.lower() for keyword in
               ['ch340', 'cp210', 'ftdi', 'usb serial', 'uart', 'led']):
            print(f"   ✅ POTENTIAL LED MATRIX CONTROLLER")
        print()

    return ports

def send_led_command(port, command):
    """Send command to LED matrix"""
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(0.5)  # Wait for connection

        ser.write(command.encode())
        time.sleep(0.1)

        response = ser.read(100)
        ser.close()

        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_led_matrix_protocols():
    """Test common LED matrix control protocols"""
    print("🧪 Testing LED matrix protocols...\n")

    ports = find_led_matrix_serial()
    if not ports:
        return

    # Common LED matrix commands
    test_commands = {
        "Clear Screen": b'\x00\x00\x00\x00',
        "All Red": b'\xFF\x00\x00\xFF',
        "All Green": b'\x00\xFF\x00\xFF',
        "All Blue": b'\x00\x00\xFF\xFF',
        "Protocol Test": b'AT\r\n',  # AT command
        "Status": b'?\r\n',
    }

    for port in ports:
        print(f"Testing {port.device}...")
        for name, cmd in test_commands.items():
            print(f"  Trying: {name}")
            response = send_led_command(port.device, cmd.decode('latin-1'))
            if response:
                print(f"    Response: {response}")

if __name__ == "__main__":
    print("═" * 60)
    print("  LED MATRIX REMOTE CONTROLLER")
    print("  16x32 pixels | 173x70mm | 5V @ 2A")
    print("═" * 60)
    print()

    find_led_matrix_serial()

    print("\n" + "─" * 60)
    print("NEXT STEPS:")
    print("1. Check which COM port is your LED matrix")
    print("2. The matrix likely uses one of these protocols:")
    print("   - Serial RGB commands (most common)")
    print("   - DMX512 protocol")
    print("   - Proprietary protocol with IR remote")
    print("3. What software came with the remote control?")
    print("─" * 60)
