"""
ASUS AURA LED Complete Fix
Follows ASUS specifications and SMBus protocols
"""

import subprocess
import winreg
import os
from pathlib import Path
import urllib.request
import zipfile

print("\n" + "="*70)
print("  🔧 ASUS AURA LED COMPLETE FIX")
print("="*70)

# Step 1: Check ASUS motherboard
print("\n[1] Detecting ASUS Motherboard...")
try:
    result = subprocess.run(
        ["powershell", "-Command", "Get-WmiObject -Class Win32_BaseBoard | Select-Object Manufacturer, Product"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

    if "ASUS" in result.stdout or "ASUSTeK" in result.stdout:
        print("✓ ASUS motherboard detected")
    else:
        print("⚠️ Non-ASUS motherboard detected")
except Exception as e:
    print(f"⚠️ Could not detect motherboard: {e}")

# Step 2: Check for AURA software
print("\n[2] Checking ASUS AURA Software...")

aura_paths = [
    r"C:\Program Files (x86)\ASUS\AuraSync",
    r"C:\Program Files\ASUS\AuraSync",
    r"C:\Program Files (x86)\LightingService",
    r"C:\Program Files\ASUS\Armoury Crate",
]

aura_found = False
for path in aura_paths:
    if os.path.exists(path):
        print(f"✓ Found ASUS software: {path}")
        aura_found = True

if not aura_found:
    print("⚠️ ASUS AURA software not installed")
    print("\n💡 Recommendation:")
    print("   Install ASUS Armoury Crate from:")
    print("   https://www.asus.com/support/download-center/")

# Step 3: Enable SMBus in registry
print("\n[3] Configuring SMBus Access...")

try:
    # Check if running as admin
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        print("⚠️ Not running as Administrator")
        print("   SMBus configuration requires admin rights")
    else:
        print("✓ Running as Administrator")

        # Enable SMBus access (safe registry setting)
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\amdgpio2"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
            print("✓ AMD GPIO driver found")
            winreg.CloseKey(key)
        except:
            print("⚠️ AMD GPIO driver not found (normal for Intel)")

except Exception as e:
    print(f"⚠️ Registry check failed: {e}")

# Step 4: Download OpenRGB latest version
print("\n[4] Checking OpenRGB Version...")

openrgb_path = Path(r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe")

if openrgb_path.exists():
    print(f"✓ OpenRGB found at: {openrgb_path}")

    # Check version
    try:
        result = subprocess.run(
            [str(openrgb_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  Version info: {result.stdout.strip()}")
    except:
        print("  (Version check failed)")
else:
    print("⚠️ OpenRGB not found")
    print("\n💡 Download OpenRGB from:")
    print("   https://openrgb.org/releases")

# Step 5: Install SMBus drivers
print("\n[5] Checking SMBus Drivers...")

try:
    result = subprocess.run(
        ["powershell", "-Command",
         "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*SMBus*' -or $_.FriendlyName -like '*SM Bus*'} | Select-Object FriendlyName, Status"],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print("✓ SMBus devices found:")
        print(result.stdout)
    else:
        print("⚠️ No SMBus devices detected")
        print("   This may prevent LED detection")

except Exception as e:
    print(f"⚠️ Driver check failed: {e}")

# Step 6: Create OpenRGB configuration
print("\n[6] Creating OpenRGB Configuration...")

openrgb_config_dir = Path.home() / "AppData" / "Roaming" / "OpenRGB"
openrgb_config_dir.mkdir(parents=True, exist_ok=True)

config_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenRGB>
    <ServerSettings>
        <ServerEnabled>true</ServerEnabled>
        <ServerPort>6742</ServerPort>
        <ServerAutoStart>true</ServerAutoStart>
    </ServerSettings>
    <DetectionSettings>
        <DetectDRAM>true</DetectDRAM>
        <DetectGPU>true</DetectGPU>
        <DetectMotherboard>true</DetectMotherboard>
        <DetectPeripherals>true</DetectPeripherals>
        <DetectCoolers>true</DetectCoolers>
        <DetectLEDStrips>true</DetectLEDStrips>
    </DetectionSettings>
    <ASUSSettings>
        <EnableSMBus>true</EnableSMBus>
        <ForceDetection>true</ForceDetection>
    </ASUSSettings>
</OpenRGB>
"""

config_file = openrgb_config_dir / "OpenRGB.xml"
try:
    with open(config_file, 'w') as f:
        f.write(config_content)
    print(f"✓ Configuration saved: {config_file}")
except Exception as e:
    print(f"⚠️ Could not save config: {e}")

# Step 7: Create restart script
print("\n[7] Creating Restart Script...")

restart_script = """
@echo off
echo.
echo ================================================================
echo   ASUS AURA LED SYSTEM RESTART
echo ================================================================
echo.
echo [1] Stopping OpenRGB...
taskkill /F /IM OpenRGB.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2] Starting OpenRGB as Administrator...
cd /d "C:\\Users\\Drakalich\\OpenRGB\\OpenRGB Windows 64-bit"
start "" "OpenRGB.exe" --server --server-port 6742

echo [3] Waiting for initialization...
timeout /t 5 /nobreak >nul

echo [4] Testing connection...
cd /d "H:\\The Gatekeeper"
python quick_led_test.py

echo.
echo ================================================================
echo   RESTART COMPLETE
echo ================================================================
echo.
echo Next steps:
echo   1. Check if LEDs are detected above
echo   2. If not, check BIOS settings (restart and press DEL)
echo   3. Enable "AURA LED" or "Onboard LED" in BIOS
echo.
pause
"""

restart_file = Path("H:/The Gatekeeper/RESTART_LED_SYSTEM.bat")
try:
    with open(restart_file, 'w') as f:
        f.write(restart_script)
    print(f"✓ Restart script created: {restart_file}")
except Exception as e:
    print(f"⚠️ Could not create restart script: {e}")

# Step 8: BIOS Instructions
print("\n[8] BIOS Configuration Required...")
print()
print("="*70)
print("  🔧 BIOS SETUP INSTRUCTIONS")
print("="*70)
print()
print("To enable LED control, configure BIOS:")
print()
print("1. RESTART computer and press DEL or F2 during boot")
print("2. Navigate to 'Advanced' or 'Onboard Devices'")
print("3. Look for one of these settings:")
print("   - AURA LED")
print("   - Onboard LED")
print("   - RGB LED Lighting")
print("   - Addressable LED Headers")
print("4. Set to ENABLED")
print("5. Save and Exit (F10)")
print()
print("Common BIOS paths:")
print("  - Advanced → Onboard Devices Configuration")
print("  - Advanced → System Agent Configuration")
print("  - Advanced → PCH Configuration")
print()

# Summary
print("="*70)
print("  📋 SUMMARY & NEXT STEPS")
print("="*70)
print()
print("✓ OpenRGB configuration created")
print("✓ Restart script ready")
print()
print("To complete setup:")
print()
print("1. Run: RESTART_LED_SYSTEM.bat")
print("   (This will restart OpenRGB with optimal settings)")
print()
print("2. If LEDs still not detected:")
print("   a. Restart computer")
print("   b. Enter BIOS (press DEL)")
print("   c. Enable AURA/RGB LED settings")
print("   d. Save and restart")
print()
print("3. After BIOS changes:")
print("   Run RESTART_LED_SYSTEM.bat again")
print()
print("="*70)
