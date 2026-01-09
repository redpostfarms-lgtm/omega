# Omega System Deployment Guide

## Quick Start

### Automatic Deployment
```bash
python deploy.py
```

This will:
- Check Python version (3.8+ required)
- Install all dependencies
- Verify critical files
- Run system tests
- Create startup scripts

### Manual Deployment

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Setup**
   - Ensure `clip_0001.wav` exists (voice sample)
   - Check microphone is connected
   - Verify internet connection (for Google Speech API)

3. **Start System**
   ```bash
   # Windows
   start_omega.bat
   
   # Unix/Mac
   ./start_omega.sh
   
   # Or directly
   python omega_full_brain.py
   ```

## System Variants

Choose the Omega variant that fits your needs:

- **omega_full_brain.py** - Full featured (Voice + Emotion Detection)
- **omega_combined_final.py** - Complete (Voice + Emotion + Memory)
- **omega_simple_final.py** - Simple (Voice + Memory)
- **omega_final_no_emotion.py** - Basic (Voice only)

## Requirements

### System Requirements
- Python 3.8 or higher
- Windows 10+ / Linux / macOS
- Microphone
- Internet connection (for Google Speech API)

### Python Dependencies
All listed in `requirements.txt`:
- TTS (Text-to-Speech)
- torch (PyTorch)
- sounddevice (Audio I/O)
- speech_recognition (Speech-to-Text)
- speechbrain (Emotion detection)
- And more...

## Configuration

### Rate Limiting
The system includes automatic rate limiting for API calls:
- Google Speech API: 50 requests/minute
- Exponential backoff on failures
- Automatic retry with backoff

### Audio Settings
- Sample rate: 16000 Hz
- Recording duration: 5 seconds
- Format: WAV, 16-bit PCM

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "No microphone found"
- Check microphone is connected
- Verify system audio settings
- On Linux, may need: `sudo apt-get install portaudio19-dev`

### "API error" messages
- Check internet connection
- Google Speech API may be rate-limited
- System will automatically retry with backoff

### Audio playback issues
- Check system audio settings
- Verify audio drivers are installed
- On Linux, may need: `sudo apt-get install alsa-utils`

## Performance

The system is optimized for:
- **Non-blocking operations** - All I/O uses async/await
- **Rate limiting** - Prevents API throttling
- **Error recovery** - Automatic retries with exponential backoff
- **Memory management** - Proper cleanup of temporary files

## Security

- Input sanitization (via omega_security_enhanced.py)
- Sandbox isolation for code execution
- Security audit logging
- Entropy killswitch for emergency shutdown

## Support

For issues or questions:
1. Check `MASTER_SWEEP_REPORT.md` for detailed information
2. Review error messages in console output
3. Check system logs if available

## Next Steps

After deployment:
1. Test with: `python test_system.py`
2. Record voice sample: `clip_0001.wav` (if not present)
3. Start system: `python omega_full_brain.py`
4. Speak to test recognition

---

**Status:** Production Ready ✅
**Last Updated:** 2026-01-03
