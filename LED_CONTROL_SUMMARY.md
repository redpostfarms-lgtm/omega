# 🔴 LED Control Summary - What We Found

## ✅ Hardware Status
- **AURA LED Controller** detected (USB VID_0B05&PID_1939)
- **Manual control works** through Armoury Crate GUI
- **LED bar responds** to Armoury Crate color changes

## 🔍 Software Discovery

### Running Services
- `ArmouryCrate.exe` - Main application
- `ArmourySocketServer.exe` - Socket API (ports 9012, 9013)
- `LightingService.exe` - LED control service

### Configuration Files
- `C:\ProgramData\ASUS\RogAura30\AuraSync.ini` - Color settings (ColorR, ColorG, ColorB)
- `C:\ProgramData\ASUS\AuraProcess.ini` - Process config

### SDK Files
- `C:\Program Files (x86)\ASUS\ArmouryDevice\dll\ArmourySDK.dll`

## ⚠️ Challenge
**Armoury Crate maintains exclusive control** of the LED hardware. Any programmatic changes are immediately overridden.

## 🎯 Working Solutions

### Option 1: UI Automation (Reliable)
Automate Armoury Crate interface using pyautogui:
```bash
pip install pyautogui
python test_ui_automation_led.py
```

### Option 2: Stop Armoury Crate & Use SDK
1. Close Armoury Crate
2. Stop LightingService
3. Use ArmourySDK.dll directly
4. May require reverse engineering the DLL

### Option 3: OpenRGB (Recommended for programmatic control)
Install OpenRGB to bypass Armoury Crate:
```powershell
# Download from: https://openrgb.org/
# OpenRGB provides a proper API for LED control
```

## 🚀 Best Path Forward

**For your Kit voice + LED integration:**

1. **Install OpenRGB** (if you want full programmatic control)
   - Bypasses Armoury Crate
   - Has Python API: `pip install openrgb-python`
   - Direct hardware access

2. **OR Use UI Automation** (if keeping Armoury Crate)
   - Keep Armoury Crate running
   - Script sends UI clicks to change colors
   - Works but requires GUI

3. **OR Create Armoury Crate Plugin** (advanced)
   - Use Armoury SDK properly
   - May require C++ development

## 📝 Next Steps for Kit Voice Integration

Once LED control is working:
```python
# Example integration:
def speak_kit_voice():
    play_audio("clip_0001.wav")
    set_led_color(255, 0, 0)  # RED during speech
    # Wave LED in sync with voice intensity
```

Would you like me to:
- A) Install and configure OpenRGB for full control
- B) Set up UI automation with existing Armoury Crate
- C) Research the Armoury SDK further

?
