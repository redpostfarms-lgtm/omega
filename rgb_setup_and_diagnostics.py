#!/usr/bin/env python3
"""
RGB Setup and Diagnostics Suite
=================================
Complete RGB lighting setup, diagnostics, and troubleshooting for Omega Control Panel.

Features:
- Installs OpenRGB (primary RGB solution)
- Detects ASUS AURA, Corsair iCUE, Razer Synapse, NZXT CAM
- Provides manufacturer-specific setup guides
- Tests RGB hardware detection
- Diagnoses RGB issues
- Creates recovery solutions
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import urllib.request
import zipfile
import shutil
import time

class RGBSetupManager:
    """Comprehensive RGB setup and diagnostics"""
    
    def __init__(self):
        self.system = platform.system()
        self.base_dir = Path(__file__).parent.absolute()
        self.setup_log = self.base_dir / "RGB_SETUP_LOG.json"
        self.results = {
            "timestamp": time.time(),
            "system": self.system,
            "steps_completed": [],
            "errors": [],
            "solutions_applied": []
        }
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'=' * 80}")
        print(f"{title.center(80)}")
        print(f"{'=' * 80}\n")
    
    def print_step(self, step: str, description: str = ""):
        """Print setup step"""
        print(f"\n[{step}]")
        if description:
            print(f"  {description}")
    
    def run_command(self, cmd: str, description: str = "", shell: bool = False) -> Tuple[bool, str]:
        """Run command and capture output"""
        try:
            if shell:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if description:
                print(f"  {description}: {'✓' if success else '✗'}")
            
            return success, output
        except Exception as e:
            print(f"  Command failed: {e}")
            return False, str(e)
    
    def detect_installed_applications(self) -> Dict[str, bool]:
        """Detect RGB software applications installed on system"""
        print("\n[DETECTING INSTALLED RGB APPLICATIONS]")
        
        applications = {
            "OpenRGB": self._check_openrgb(),
            "ASUS AURA": self._check_asus_aura(),
            "Corsair iCUE": self._check_corsair_icue(),
            "Razer Synapse": self._check_razer_synapse(),
            "NZXT CAM": self._check_nzxt_cam(),
            "MSI Dragon Center": self._check_msi_dragon()
        }
        
        print("\nDetected Applications:")
        for app, installed in applications.items():
            status = "✓ Installed" if installed else "✗ Not found"
            print(f"  {app}: {status}")
        
        return applications
    
    def _check_openrgb(self) -> bool:
        """Check if OpenRGB is installed"""
        if self.system == "Windows":
            # Check Program Files
            paths = [
                "C:\\Program Files\\OpenRGB\\openrgb.exe",
                "C:\\Program Files (x86)\\OpenRGB\\openrgb.exe",
                "C:\\Users\\*\\AppData\\Local\\OpenRGB\\openrgb.exe"
            ]
            
            for path in paths:
                if os.path.exists(path) or os.path.exists(path.replace("*", "*")):
                    return True
            
            # Check PATH
            success, _ = self.run_command("openrgb --list-devices", "", False)
            return success
        else:
            # Linux/Mac
            success, _ = self.run_command("which openrgb", "", True)
            return success
    
    def _check_asus_aura(self) -> bool:
        """Check if ASUS AURA is installed"""
        if self.system != "Windows":
            return False
        
        paths = [
            "C:\\Program Files\\ASUS\\AURA Service",
            "C:\\Program Files (x86)\\ASUS\\AURA Service",
            "C:\\Program Files\\ASUS\\ROG AURA"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _check_corsair_icue(self) -> bool:
        """Check if Corsair iCUE is installed"""
        if self.system != "Windows":
            return False
        
        paths = [
            "C:\\Program Files\\Corsair\\Corsair iCUE 4 Software",
            "C:\\Program Files (x86)\\Corsair\\Corsair iCUE 4 Software"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _check_razer_synapse(self) -> bool:
        """Check if Razer Synapse is installed"""
        if self.system != "Windows":
            return False
        
        paths = [
            "C:\\Program Files\\Razer\\Synapse3",
            "C:\\Program Files (x86)\\Razer\\Synapse3"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _check_nzxt_cam(self) -> bool:
        """Check if NZXT CAM is installed"""
        if self.system != "Windows":
            return False
        
        paths = [
            "C:\\Program Files\\NZXT\\CAM",
            "C:\\Program Files (x86)\\NZXT\\CAM"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def _check_msi_dragon(self) -> bool:
        """Check if MSI Dragon Center is installed"""
        if self.system != "Windows":
            return False
        
        paths = [
            "C:\\Program Files\\MSI\\Dragon Center",
            "C:\\Program Files (x86)\\MSI\\Dragon Center"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def install_openrgb(self) -> bool:
        """Install OpenRGB - Primary RGB solution"""
        self.print_step("INSTALL_OPENRGB", "Installing OpenRGB for universal RGB control...")
        
        if self.system == "Windows":
            print("\nOpenRGB Installation Options:")
            print("  1. Via Python Package (Recommended)")
            print("  2. Via Direct Download")
            print("  3. Via Portable ZIP\n")
            
            # Try pip install first
            print("Attempting to install via pip...")
            success, output = self.run_command(
                f"{sys.executable} -m pip install openrgb",
                "Python package installation",
                True
            )
            
            if success:
                print("  ✓ OpenRGB Python package installed successfully")
                self.results["steps_completed"].append("openrgb_pip_install")
                return True
            
            # Download from GitHub
            print("\nDownloading OpenRGB from GitHub...")
            try:
                # Latest release URL
                release_url = "https://github.com/CalcProgrammer1/OpenRGB/releases/download/release_0.9/OpenRGB_0.9_Windows_64_Portable.zip"
                target_path = self.base_dir / "openrgb_latest.zip"
                
                print(f"  Downloading from: {release_url}")
                urllib.request.urlretrieve(release_url, target_path)
                print(f"  ✓ Downloaded to {target_path}")
                
                # Extract
                extract_dir = self.base_dir / "openrgb"
                with zipfile.ZipFile(target_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                print(f"  ✓ Extracted to {extract_dir}")
                
                self.results["steps_completed"].append("openrgb_download")
                return True
            
            except Exception as e:
                error_msg = f"Download failed: {e}"
                print(f"  ✗ {error_msg}")
                self.results["errors"].append(error_msg)
                return False
        
        elif self.system == "Linux":
            # Linux installation via package manager
            print("\nOpenRGB Installation for Linux:")
            print("  Option 1: Ubuntu/Debian - sudo apt install openrgb")
            print("  Option 2: Arch - sudo pacman -S openrgb")
            print("  Option 3: Fedora - sudo dnf install openrgb\n")
            
            # Try apt (Ubuntu/Debian)
            success, _ = self.run_command("sudo apt install -y openrgb", "apt install", True)
            if success:
                print("  ✓ OpenRGB installed via apt")
                self.results["steps_completed"].append("openrgb_apt_install")
                return True
            
            print("  Note: Please install OpenRGB manually using your package manager")
            return False
        
        return False
    
    def install_python_package(self) -> bool:
        """Install python-openrgb package"""
        self.print_step("INSTALL_PYTHON_PACKAGE", "Installing Python OpenRGB package...")
        
        success, output = self.run_command(
            f"{sys.executable} -m pip install --upgrade openrgb",
            "Python OpenRGB package",
            True
        )
        
        if success:
            print("  ✓ Python OpenRGB package installed")
            self.results["steps_completed"].append("python_openrgb_install")
            return True
        else:
            print(f"  ✗ Installation failed: {output}")
            self.results["errors"].append(f"Python package install failed: {output}")
            return False
    
    def setup_usb_drivers(self) -> bool:
        """Setup USB drivers for RGB devices"""
        self.print_step("SETUP_USB_DRIVERS", "Configuring USB drivers for RGB devices...")
        
        if self.system != "Windows":
            print("  Note: USB driver setup is primarily for Windows")
            return True
        
        print("\nUSB Driver Setup:")
        print("  1. Install FTDI drivers (for many RGB devices)")
        print("  2. Install Silicon Labs CP210x drivers (for NZXT devices)")
        print("  3. Update device drivers in Device Manager\n")
        
        print("  FTDI Driver Download:")
        print("    https://ftdichip.com/drivers/d2xx/")
        print("\n  Silicon Labs Driver Download:")
        print("    https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers")
        
        print("\n  Installation Steps:")
        print("  1. Download the appropriate driver")
        print("  2. Run the installer")
        print("  3. Restart system")
        print("  4. OpenRGB will auto-detect devices")
        
        self.results["steps_completed"].append("usb_driver_setup_guide")
        return True
    
    def test_rgb_detection(self) -> Dict[str, Any]:
        """Test RGB device detection"""
        self.print_step("TEST_RGB_DETECTION", "Testing RGB device detection...")
        
        results = {
            "devices_found": 0,
            "devices": [],
            "success": False
        }
        
        try:
            from omega_rgb_advanced_controller import get_advanced_rgb_controller
            rgb = get_advanced_rgb_controller()
            
            status = rgb.get_status()
            results["available_methods"] = status["available_methods"]
            results["current_method"] = status["current_method"]
            results["success"] = True
            
            print(f"\n  RGB Controller Status:")
            print(f"    Active Method: {status['current_method']}")
            print(f"    Available Methods: {', '.join(status['available_methods'])}")
            print(f"    RGB Enabled: {status['enabled']}")
            print(f"    Current Color: {status['current_color_hex']}")
            
            self.results["steps_completed"].append("rgb_detection_test")
        
        except Exception as e:
            error_msg = f"RGB detection failed: {e}"
            print(f"  ✗ {error_msg}")
            self.results["errors"].append(error_msg)
            results["success"] = False
        
        return results
    
    def test_color_change(self) -> bool:
        """Test actual RGB color change"""
        self.print_step("TEST_COLOR_CHANGE", "Testing RGB color change...")
        
        try:
            from omega_rgb_advanced_controller import get_advanced_rgb_controller
            rgb = get_advanced_rgb_controller()
            
            # Test colors
            test_colors = [
                ("Red", (255, 0, 0)),
                ("Green", (0, 255, 0)),
                ("Blue", (0, 0, 255)),
            ]
            
            print("\n  Testing color changes:")
            for name, color in test_colors:
                success = rgb.set_color(*color)
                status = "✓" if success else "✗"
                print(f"    {name}: {status}")
                time.sleep(0.5)
            
            self.results["steps_completed"].append("color_change_test")
            return True
        
        except Exception as e:
            error_msg = f"Color change test failed: {e}"
            print(f"  ✗ {error_msg}")
            self.results["errors"].append(error_msg)
            return False
    
    def create_troubleshooting_guide(self) -> str:
        """Create RGB troubleshooting guide"""
        self.print_step("CREATE_TROUBLESHOOTING_GUIDE", "Creating troubleshooting guide...")
        
        guide_path = self.base_dir / "RGB_TROUBLESHOOTING_GUIDE.md"
        
        guide_content = """# RGB Lighting Troubleshooting Guide

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
print(f"Available RGB methods: {status['available_methods']}")
print(f"Current method: {status['current_method']}")
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
- **Resource**: https://www.asus.com/support
- **Download**: ASUS AURA Suite
- **Alternative**: OpenRGB (works with all ASUS RGB)

### Corsair RGB Devices
- **Resource**: https://corsair.com/ca/en/support
- **Download**: Corsair iCUE
- **Alternative**: OpenRGB (supports Corsair devices)

### Razer RGB Devices
- **Resource**: https://www2.razer.com/support
- **Download**: Razer Synapse
- **Alternative**: OpenRGB (supports Razer devices)

### NZXT RGB Devices  
- **Resource**: https://www.nzxt.com/support
- **Download**: NZXT CAM
- **Alternative**: OpenRGB (supports NZXT devices)

## Omega RGB System Info

### How Omega RGB Works
1. **Initialization**: Omega checks for available RGB control software
2. **Method Selection**: Uses best available method (OpenRGB preferred)
3. **Fallback Chain**: If one method fails, tries next in chain
4. **Simulation Mode**: If no hardware found, simulates RGB (for testing)

### Configuration File
```json
{
  "rgb_enabled": true,
  "preferred_method": "openrgb",
  "auto_color_temperature": true,
  "fallback_to_simulation": true
}
```

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
   - OpenRGB GitHub: https://github.com/CalcProgrammer1/OpenRGB
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
print(f"RGB Method: {status['current_method']}")
print(f"Available: {status['available_methods']}")

# Enable monitoring thread
rgb.start_monitoring(interval=5.0)
```

---
**Generated**: {timestamp}
**System**: {system}
"""
        
        guide_content = guide_content.format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            system=self.system
        )
        
        with open(guide_path, 'w') as f:
            f.write(guide_content)
        
        print(f"  ✓ Guide created: {guide_path}")
        self.results["solutions_applied"].append("troubleshooting_guide_created")
        return str(guide_path)
    
    def run_complete_setup(self):
        """Run complete RGB setup sequence"""
        self.print_header("OMEGA RGB SETUP AND DIAGNOSTICS")
        
        print(f"System: {self.system}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Base Directory: {self.base_dir}\n")
        
        # Step 1: Detect installed applications
        installed = self.detect_installed_applications()
        
        # Step 2: Install OpenRGB (primary method)
        if not installed.get("OpenRGB"):
            print("\n" + "=" * 80)
            print("OpenRGB is not installed - installing now (recommended)")
            print("=" * 80)
            
            openrgb_success = self.install_openrgb()
            if not openrgb_success:
                print("\nNote: OpenRGB installation had issues.")
                print("Will try Python package approach...")
                self.install_python_package()
        else:
            print("\n✓ OpenRGB already installed")
        
        # Step 3: Setup USB drivers
        self.setup_usb_drivers()
        
        # Step 4: Test RGB detection
        detection_results = self.test_rgb_detection()
        
        # Step 5: Test color change
        self.test_color_change()
        
        # Step 6: Create troubleshooting guide
        guide_path = self.create_troubleshooting_guide()
        
        # Save results
        self._save_results(guide_path)
        
        # Print summary
        self._print_summary()
    
    def _save_results(self, guide_path: str):
        """Save setup results to log"""
        self.results["guide_path"] = guide_path
        
        with open(self.setup_log, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n✓ Setup log saved: {self.setup_log}")
    
    def _print_summary(self):
        """Print setup summary"""
        self.print_header("SETUP SUMMARY")
        
        print(f"Steps Completed: {len(self.results['steps_completed'])}")
        for step in self.results['steps_completed']:
            print(f"  ✓ {step}")
        
        if self.results['errors']:
            print(f"\nErrors Encountered: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"  ✗ {error}")
        else:
            print("\n✓ No errors encountered!")
        
        print(f"\nSolutions Applied: {len(self.results['solutions_applied'])}")
        for solution in self.results['solutions_applied']:
            print(f"  ✓ {solution}")
        
        print(f"\nGuide Location: {self.results.get('guide_path', 'N/A')}")
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("""
1. If OpenRGB was installed:
   - Start OpenRGB
   - Click "Detect Devices"
   - Verify your RGB fans appear
   - Test color change in OpenRGB UI

2. Start Omega Control Panel:
   - python omega_control_panel_web.py --port 5000
   - Use RGB color picker to test

3. If still not working:
   - Review: RGB_TROUBLESHOOTING_GUIDE.md
   - Check: RGB_SETUP_LOG.json
   - Test: openrgb --list-devices (command line)

4. For specific RGB software:
   - ASUS: Install ASUS AURA Suite
   - Corsair: Install Corsair iCUE
   - Razer: Install Razer Synapse
   - NZXT: Install NZXT CAM
""")

if __name__ == "__main__":
    manager = RGBSetupManager()
    
    try:
        manager.run_complete_setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
