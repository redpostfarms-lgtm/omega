#!/usr/bin/env python3
"""
Alternative CPU Temperature Reader
Uses OpenHardwareMonitor or HWiNFO data if running
"""

def get_cpu_temp_from_hwinfo():
    """Try to read CPU temperature from HWiNFO shared memory or registry"""
    import winreg
    import struct
    
    # Try HWiNFO registry keys
    try:
        reg_paths = [
            r"SOFTWARE\HWiNFO64\VSB",
            r"SOFTWARE\HWiNFO32\VSB",
        ]
        
        for reg_path in reg_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if 'CPU' in name and 'Temp' in name:
                            return float(value)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except FileNotFoundError:
                continue
    except Exception:
        pass
    
    return None


if __name__ == "__main__":
    temp = get_cpu_temp_from_hwinfo()
    if temp:
        print(f"CPU Temperature from HWiNFO: {temp}°C")
    else:
        print("CPU temperature not available from HWiNFO")
        print("\nTo enable CPU temperature monitoring:")
        print("1. Install OpenHardwareMonitor or LibreHardwareMonitor")
        print("2. Run it in the background")
        print("3. Or install HWiNFO64 with 'Shared Memory Support' enabled")
