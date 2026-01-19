"""
Omega AURA LED Hardware Controller
Controls ASUS AURA LED hardware via USB
"""

import time
import subprocess
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("PySerial not installed. Install with: pip install pyserial")


class OmegaAuraLEDController:
    """Control ASUS AURA LED hardware"""
    
    def __init__(self):
        self.led_count = 30
        self.aura_found = False
        self.device_path = None
        
        # Try to find AURA device
        self.detect_aura()
    
    def detect_aura(self):
        """Detect ASUS AURA LED Controller"""
        if not SERIAL_AVAILABLE:
            print("⚠️ PySerial not available")
            return False
        
        # Check for AURA device
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'AURA' in port.description or '0B05' in port.hwid:  # ASUS VID
                self.device_path = port.device
                self.aura_found = True
                print(f"✅ AURA LED Controller found: {port.device}")
                print(f"   Description: {port.description}")
                return True
        
        print("⚠️ AURA LED Controller not found on COM ports")
        return False
    
    def wave_pattern(self, duration=10.0):
        """Send wave pattern to AURA LEDs"""
        print(f"\n🌊 Sending wave pattern to AURA LED Controller...")
        print(f"   Duration: {duration} seconds")
        print(f"   LEDs: {self.led_count}")
        
        if not self.aura_found:
            print("❌ AURA device not connected")
            return False
        
        try:
            # Open serial connection
            with serial.Serial(self.device_path, 115200, timeout=1) as ser:
                start_time = time.time()
                offset = 0
                
                while time.time() - start_time < duration:
                    # Generate wave pattern
                    led_data = []
                    for i in range(self.led_count):
                        import math
                        intensity = int((1 + math.sin((i + offset) * 0.3)) * 127)
                        # RGB values (cyan wave)
                        r = 0
                        g = intensity
                        b = intensity
                        led_data.extend([r, g, b])
                    
                    # Send to AURA (protocol may vary)
                    command = bytes([0xFF, 0x00, self.led_count]) + bytes(led_data)
                    ser.write(command)
                    
                    offset += 1
                    time.sleep(0.05)
                
                print("✅ Wave pattern complete")
                return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def use_aura_sync(self):
        """Try to use ASUS Aura Sync software"""
        print("\n💡 Attempting to use ASUS Aura Sync software...")
        
        # Check for Aura Sync installation
        aura_paths = [
            Path("C:/Program Files (x86)/ASUS/AURA"),
            Path("C:/Program Files/ASUS/AURA"),
            Path("C:/Program Files (x86)/LightingService"),
        ]
        
        for path in aura_paths:
            if path.exists():
                print(f"✅ Found ASUS software: {path}")
                
                # Look for executable
                exe_files = list(path.glob("**/*.exe"))
                if exe_files:
                    print(f"   Found {len(exe_files)} executables")
                    for exe in exe_files[:3]:
                        print(f"   - {exe.name}")
                return True
        
        print("⚠️ ASUS Aura Sync software not found")
        print("   Install from: https://www.asus.com/support/download-center/")
        return False


def main():
    """Test AURA LED control"""
    controller = OmegaAuraLEDController()
    
    print("\n" + "="*60)
    print("  OMEGA AURA LED HARDWARE CONTROLLER")
    print("="*60 + "\n")
    
    if controller.aura_found:
        controller.wave_pattern(10.0)
    else:
        print("\n💡 Alternative methods:")
        controller.use_aura_sync()
        
        print("\n📦 To install PySerial:")
        print("   pip install pyserial")
        
        print("\n🔧 To use ASUS Aura SDK:")
        print("   1. Install ASUS Aura Sync software")
        print("   2. Enable SDK in Aura settings")
        print("   3. Use OpenRGB as alternative:")
        print("      https://openrgb.org/")


if __name__ == "__main__":
    main()
