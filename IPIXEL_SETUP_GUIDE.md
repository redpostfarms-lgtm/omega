# IPIXEL LED MATRIX SETUP GUIDE

## Device Information
- **Model**: LED_32*16_58FO_L
- **Size**: 16x32 pixels (173x70mm)
- **Power**: 5V @ 2A
- **App**: Ipixel Color v3.4.6
- **Password**: 139069

## WiFi Connection
**Router**: HOUSEOFCHAOS  
**Password**: FiX562722!

## Setup Steps

### 1. Connect Matrix to WiFi (via Ipixel App)
1. Open **Ipixel Color** app on your phone
2. Tap **Settings** (⚙️)
3. Tap **WiFi Settings** or **Device Setup**
4. Select **HOUSEOFCHAOS** from WiFi list
5. Enter password: **FiX562722!**
6. Wait for connection (LED should show WiFi icon or steady pattern)

### 2. Find Matrix IP Address
**Option A - Via App:**
1. Open Ipixel Color app
2. Go to **Settings → Device Info**
3. Look for IP address (format: 10.0.0.x or 192.168.x.x)

**Option B - Via Python:**
```bash
python unified_led_controller.py
# Choose option 3 to scan for IP
```

### 3. Control the Matrix
Once connected to WiFi:
```bash
python unified_led_controller.py
# Choose option 1 for Red Wave (both LEDs)
# Choose option 2 for Purple (both LEDs)
```

## Troubleshooting

**Matrix not connecting to WiFi:**
- Make sure matrix is powered (5V 2A adapter)
- Clock should be visible on display
- Try resetting WiFi in app Settings
- Check router allows 2.4GHz connections (most LED matrices don't support 5GHz)

**Python can't find matrix:**
- Confirm PC and matrix on same network (HOUSEOFCHAOS)
- Check firewall isn't blocking port 8899
- Get IP from app and test: `ping [matrix-ip]`

**Commands not working:**
- Port 8899 is standard for Ipixel
- Try ports 5577 or 8080 if 8899 fails
- Some versions use different command format

## Manual Control (if needed)
```python
import socket

def send_color(ip, r, g, b):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 8899))
    cmd = bytes([0x31, r, g, b, 0x00, 0xf0, 0x0f])
    sock.send(cmd)
    sock.close()

# Red
send_color("10.0.0.x", 255, 0, 0)

# Purple  
send_color("10.0.0.x", 128, 0, 128)
```

## Current Status
- ✅ Motherboard LEDs: 20 addressable (ASUS AURA)
- ⏳ LED Matrix: Awaiting WiFi connection
- 🎯 Goal: Unified control of both LED systems
