# 🔴 Quick LED Setup - RED Wave Test

## Current Status
- ✅ AURA LED Controller detected (USB VID_0B05)
- ✅ Kit voice system working
- ❌ OpenRGB not installed (needed for LED control)

## Install OpenRGB (1 minute)

### Option A: Automatic Installation
```powershell
cd "H:\The Gatekeeper"
.\INSTALL_OPENRGB.ps1
```

### Option B: Manual Installation
1. Download: <https://openrgb.org/releases/release_0.9/OpenRGB_0.9_Windows_64_b5f46e3.zip>
2. Extract to: `C:\Program Files\OpenRGB`
3. Done!

## Test RED Waves (After OpenRGB is installed)

```powershell
cd "H:\The Gatekeeper"
.\TEST_RED_WAVE.ps1
```

**You should see:** RED waves pulsing on your tower LED strip for 10 seconds

## Alternative: Check for ASUS Software

If you have ASUS Armoury Crate or Aura Sync already installed:

```powershell
# Check for Armoury Crate
Test-Path "C:\Program Files (x86)\ASUS\ArmouryDevice"

# Check for Aura Sync  
Test-Path "C:\Program Files (x86)\ASUS\AuraService"
```

## Next: Voice + LED Integration

Once LED control is working, we can integrate it with Kit voice:
- Kit speaks → RED waves pulse
- Different voice profiles → different LED colors
- Voice intensity → LED brightness

---

**Ready?** Run `.\INSTALL_OPENRGB.ps1` to get started! 🚀
