# 🔴 LED Control Resolution - Fix I2C/SMBus Issue

## 🔍 Root Cause Analysis

**Problem:** OpenRGB cannot control your AURA LED Controller  
**Reason:** I2C/SMBus interfaces failed to initialize  
**Solution:** Run OpenRGB as Administrator to install WinRing0 driver

## ⚠️ Current Status
- ✓ AURA device detected: **ASUS PRIME B550-PLUS AC-HES**
- ✓ 3 Zones available: Mainboard, Addressable 1, Addressable 2
- ✗ **I2C/SMBus driver not loaded** (WinRing0)
- ✗ LED commands not reaching hardware

## 🔧 Resolution Steps

### Step 1: Run OpenRGB as Administrator (REQUIRED)
```powershell
# This will initialize the WinRing0 driver
Start-Process "C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe" -Verb RunAs
```

When OpenRGB opens:
1. You'll see a UAC prompt - click **Yes**
2. OpenRGB will initialize the I2C/SMBus driver
3. You should see your AURA device listed
4. Try manually changing a color to test

### Step 2: Close Armoury Crate (if running)
```powershell
Stop-Process -Name ArmouryCrate -Force -ErrorAction SilentlyContinue
Stop-Process -Name LightingService -Force -ErrorAction SilentlyContinue
```

### Step 3: Start OpenRGB Server
```powershell
cd "H:\The Gatekeeper"
.\START_OPENRGB_SERVER.ps1
```

### Step 4: Test LED Control
```powershell
# Test individual zones
python test_openrgb_zones.py

# Or test directly with PowerShell
.\TEST_RED_WAVE.ps1 -OpenRGBPath "C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe"
```

## 🎯 Quick Fix Command
```powershell
# One-command fix: Run as admin, wait, then test
Start-Process "C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe" -Verb RunAs -ArgumentList "--server"; Start-Sleep -Seconds 5; python test_openrgb_red_wave.py
```

## 📊 Technical Details

**Why this happens:**
- OpenRGB uses WinRing0 driver for direct hardware access
- This driver requires admin rights to install/load
- Once installed, it persists and doesn't need admin again
- Your AURA LED uses I2C/SMBus protocol
- Without the driver, commands don't reach the hardware

**What zones control:**
- **Zone 0** (Mainboard): Motherboard RGB headers
- **Zone 1** (Addressable 1): ARGB Header 1 - **YOUR LED BAR LIKELY HERE**
- **Zone 2** (Addressable 2): ARGB Header 2

## ✅ Expected Result

After running as admin:
- ✓ WinRing0 driver loads
- ✓ I2C/SMBus initialized
- ✓ No more warnings
- ✓ LED commands work
- ✓ RED waves visible on your LED strip

## 🔄 Alternative: Use Armoury Crate Instead

If OpenRGB admin access is an issue:
```powershell
# Use Armoury Crate (already works for you)
python test_ui_automation_led.py
```

This automates the Armoury Crate GUI which already has the necessary drivers.

---

**Next:** Once OpenRGB works, integrate with Kit voice system!
