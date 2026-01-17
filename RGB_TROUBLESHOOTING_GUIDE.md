# RGB Lighting Troubleshooting Guide

## Issue: RGB Fans Not Showing Color / Not Changing

### Root Causes

1. **No RGB Control Software Installed** - Omega needs software to communicate with RGB hardware
2. **USB Drivers Missing** - RGB devices may not be recognized by the system
3. **RGB Disabled in BIOS** - Some BIOS versions disable RGB by default
4. **Device Not Connected Properly** - RGB header may be loose or disconnected
5. **Firmware Outdated** - Fan firmware may need updating

### Solution Overview

Omega uses a multi-layer approach:

```
OpenRGB (Primary) -> ASUS AURA -> Corsair iCUE -> Razer Chroma -> NZXT CAM -> WinRing0 -> Simulated
```

## Step-by-Step Solutions

### Solution 1: Install OpenRGB (Recommended)

**Why**: Universal RGB control, works with 100+ device types

```bash
# Option A: Python Package (Easiest)
pip install openrgb

# Option B: Windows Portable
# Download from: https://github.com/CalcProgrammer1/OpenRGB/releases
# Extract and run OpenRGB.exe

# Option C: Linux Package
sudo apt install openrgb  # Ubuntu/Debian
sudo pacman -S openrgb    # Arch
sudo dnf install openrgb  # Fedora
```

#### After Installation

1. Start OpenRGB
2. Click "Detect Devices"
3. You should see your RGB fans listed
4. Test color change from OpenRGB UI
5. Omega will auto-use OpenRGB when available

### Solution 2: Install ASUS AURA (If You Have ASUS Motherboard)

**Why**: Native ASUS RGB support

```
1. Visit: https://rog.asus.com/ca/
2. Search for your motherboard model
3. Download "ASUS AURA" from driver page
4. Install and restart
5. Omega will detect automatically
```

### Solution 3: Install USB Drivers

**Why**: RGB devices need drivers to be recognized

#### For FTDI Devices (Most common)

```
1. Download: https://ftdichip.com/drivers/d2xx/
2. Run installer
3. Restart PC
4. Devices should appear in OpenRGB
```

#### For Silicon Labs CP210x (NZXT, some others)

```
1. Download: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
2. Run installer
3. Restart PC
```

### Solution 4: Check BIOS Settings

**Why**: BIOS may disable RGB for performance reasons

```
Steps:
1. Restart and press DEL or F2 (depends on motherboard)
2. Look for sections like:
   - "RGB Lighting"
   - "RGB Management"
   - "OnBoard LED"
   - "Aura Lighting"
3. Enable RGB settings
4. Save and exit (usually F10)
5. Restart Omega Control Panel
```

### Solution 5: Check Physical Connections

**Why**: Most common cause of non-functional RGB

```
Steps:
1. Power off and unplug system
2. Open case
3. Check RGB header connection on motherboard:
   - RGB_HEADER (usually white connector)
   - Should be firmly inserted
4. Check fan RGB connector to RGB header
5. Ensure connectors not backwards
6. Power on and test
```

### Solution 6: Update Fan Firmware

**Why**: Older firmware may have RGB issues

```
Steps:
1. Identify your fan brand/model
2. Visit manufacturer's website
3. Download latest firmware
4. Follow firmware update instructions
5. Restart Omega
```

## Diagnostics

### Check If Devices Are Detected

```python
from omega_rgb_advanced_controller import get_advanced_rgb_controller
rgb = get_advanced_rgb_controller()
status = rgb.get_status()
print("Available RGB methods:", status['available_methods'])
print("Current method:", status['current_method'])
```

### Test OpenRGB Command Line

```bash
# List all detected devices
openrgb --list-devices

# Test color change (red)
openrgb -c FF0000

# Test specific device
openrgb -d 0 -c 00FF00  # Device 0, green
```

### Check Device Manager (Windows)

1. Right-click Start Menu
2. Select "Device Manager"
3. Look for:
   - Unknown devices (drivers missing)
   - "Other devices"
   - Devices with yellow warning (!)
4. Right-click and "Update driver"

## Manufacturer Support

### ASUS ROG Motherboards

- **Resource**: <https://www.asus.com/support>
- **Download**: ASUS AURA Suite
- **Alternative**: OpenRGB (works with all ASUS RGB)

### Corsair RGB Devices

- **Resource**: <https://corsair.com/ca/en/support>
- **Download**: Corsair iCUE
- **Alternative**: OpenRGB (supports Corsair devices)

### Razer RGB Devices

- **Resource**: <https://www2.razer.com/support>
- **Download**: Razer Synapse
- **Alternative**: OpenRGB (supports Razer devices)

### NZXT RGB Devices  

- **Resource**: <https://www.nzxt.com/support>
- **Download**: NZXT CAM
- **Alternative**: OpenRGB (supports NZXT devices)

## Omega RGB System Info

### How Omega RGB Works

1. **Initialization**: Omega checks for available RGB control software
2. **Method Selection**: Uses best available method (OpenRGB preferred)
3. **Fallback Chain**: If one method fails, tries next in chain
4. **Simulation Mode**: If no hardware found, simulates RGB (for testing)

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Now RGB operations will show detailed debug info
```

## Quick Checklist

- [ ] OpenRGB installed and running
- [ ] RGB devices show in OpenRGB "Detect Devices"
- [ ] Color change works in OpenRGB UI
- [ ] USB drivers installed (FTDI/CP210x)
- [ ] BIOS RGB settings enabled
- [ ] Physical connections verified (RGB headers)
- [ ] Fan firmware up to date
- [ ] Omega Control Panel restarted

## Still Not Working?

1. **Collect Diagnostics**:

   ```python
   from omega_rgb_advanced_controller import get_advanced_rgb_controller
   rgb = get_advanced_rgb_controller()
   import json
   print(json.dumps(rgb.get_status(), indent=2, default=str))
   ```

2. **Check Logs**:
   - `RGB_SETUP_LOG.json` - Setup history
   - Windows Event Viewer - USB device errors
   - OpenRGB console output

3. **Get Help**:
   - OpenRGB GitHub: <https://github.com/CalcProgrammer1/OpenRGB>
   - Motherboard manufacturer support
   - Fan manufacturer support

## Advanced: Custom RGB Configuration

```python
# Use a specific RGB method
from omega_rgb_advanced_controller import AdvancedRGBController

rgb = AdvancedRGBController()

# Set color
rgb.set_color(255, 0, 0)  # Red
rgb.set_color_hex("#00FF00")  # Green
rgb.set_color_hex("#0000FF")  # Blue

# Monitor status
status = rgb.get_status()
print("RGB Method:", status['current_method'])
print("Available:", status['available_methods'])

# Enable monitoring thread
rgb.start_monitoring(interval=5.0)
```

---
**Generated**: 2024 Omega RGB System
**For Issues**: Check RGB_SETUP_LOG.json for diagnostic details
