# Omega System - Voice AI Assistant

## 🌅 **START HERE EVERY MORNING**

### Morning Initialization (NEW!)
Before starting work each day, run:
```batch
MORNING_INIT.bat
```

This will:
- ✅ Authenticate all services (Git, GitHub, Docker, Hugging Face)
- ✅ Initialize system components (Resource Manager, Voice Security)
- ✅ Check GPU and system health
- ✅ Generate status report

**See [START_HERE_EVERY_MORNING.md](START_HERE_EVERY_MORNING.md) for details.**

---

## Quick Start (First Time Setup)

### 1. Install Python 3.11
Download from: https://www.python.org/downloads/release/python-31111/
- Check "Add Python 3.11 to PATH" during installation

### 2. Install Dependencies
Double-click: `INSTALL_DEPS.bat`
Or run: `py -3.11 -m pip install -r requirements.txt`

### 3. Run Omega
Double-click: `START_HERE.bat`
Or run: `py -3.11 omega_full_brain.py`

---

## System Features

- **Voice Recognition** - Google Speech API with rate limiting
- **Text-to-Speech** - XTTS v2 with voice cloning
- **Emotion Detection** - SpeechBrain emotion recognition
- **Memory System** - Persistent conversation memory
- **Rate Limiting** - Exponential backoff for API calls
- **Async Operations** - Non-blocking I/O for performance

---

## Available Variants

- `omega_full_brain.py` - Full featured (Voice + Emotion) ⭐ Recommended
- `omega_combined_final.py` - Complete (Voice + Emotion + Memory)
- `omega_simple_final.py` - Simple (Voice + Memory)
- `omega_final_no_emotion.py` - Basic (Voice only)

---

## Troubleshooting

**Check Status:** Double-click `CHECK_STATUS.bat`

**Python 3.11 Issues:** See `FIX_PYTHON_VERSION.md`

**Installation Issues:** See `INSTALL_NOW.txt`

---

## Documentation

- `QUICK_START.md` - Step-by-step getting started guide
- `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `MASTER_SWEEP_REPORT.md` - Complete system audit report

---

**Status:** ✅ Ready for deployment
**Last Updated:** 2026-01-03
