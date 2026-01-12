# Audio Troubleshooting Guide

## Issue: Not Hearing Audio from TTS

### ✅ Verified Working:
- ✅ TTS generates audio files successfully
- ✅ Audio files are valid WAV format (RIFF header confirmed)
- ✅ Audio files are ~250-350 KB (correct size)
- ✅ Windows Audio Service is running
- ✅ Audio files open in media player

### 🔍 Troubleshooting Steps:

#### 1. **Check Windows Volume**
   - Click the speaker icon in system tray (bottom right)
   - Make sure volume is NOT muted
   - Increase volume slider
   - Click speaker icon to unmute if muted

#### 2. **Check Default Audio Device**
   - Right-click speaker icon → "Open Sound settings"
   - Under "Output", check "Choose your output device"
   - Make sure correct device is selected (headphones/speakers)
   - Test by clicking "Test" button

#### 3. **Test with Your Voice Sample**
   ```batch
   start clip_0001.wav
   ```
   - If you hear your voice: Audio output works, TTS should work
   - If you don't hear it: Audio output issue (not TTS)

#### 4. **Check Media Player**
   - When audio plays, check taskbar for media player window
   - Make sure player isn't minimized or behind other windows
   - Try manually opening: `start test_simple.wav`

#### 5. **Manual Playback Test**
   - Navigate to: `D:\RPF_BRAIN\The Gatekeeper\`
   - Double-click `test_simple.wav`
   - Should open in default media player

#### 6. **Check Audio Drivers**
   - Device Manager → Sound, video and game controllers
   - Make sure audio device shows no errors
   - Update drivers if needed

#### 7. **Test with PowerShell MediaPlayer**
   ```powershell
   Add-Type -AssemblyName presentationCore
   $mp = New-Object system.windows.media.mediaplayer
   $mp.open([uri]::new('D:\RPF_BRAIN\The Gatekeeper\test_simple.wav'))
   $mp.Play()
   Start-Sleep -Seconds 8
   ```

### 📝 Quick Test Script:
Run: `PLAY_AUDIO_DIRECT.bat`

This will:
- Open audio with default player
- Try Windows Media Player
- Show troubleshooting tips

### 🎯 Most Common Issues:
1. **Volume is muted** - Check speaker icon
2. **Wrong audio device** - Check sound settings
3. **Media player muted** - Check player's volume
4. **Audio device disconnected** - Check physical connections

### ✅ If Audio Works for clip_0001.wav:
TTS audio should work too. The files are identical format.
Try manually opening `test_simple.wav` in File Explorer.
