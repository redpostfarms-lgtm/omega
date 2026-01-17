# Omega System - Quick Start Guide

## 🚀 What to Do Next

### Step 1: Install Dependencies (First Time Only)

Open a terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```text

This will install all required packages (TTS, torch, sounddevice, speech_recognition, etc.)

**Note:** This may take a few minutes, especially downloading torch/PyTorch (~2GB)

---

### Step 2: Verify Your Setup

**Check your microphone:**
- Make sure your microphone is connected and working
- Test it with Windows Voice Recorder or similar

**Check your voice clip:**
- The file `clip_0001.wav` should exist in the project folder
- This is used for voice cloning (your voice sample)
- If it's missing, the system will still work but use default voice

---

### Step 3: Start Omega

**Option A: Using Startup Script (Easiest)**
```bash
# Windows
start_omega.bat

# Mac/Linux  
./start_omega.sh
```text

**Option B: Direct Python Command**
```bash
python omega_full_brain.py
```text

---

### Step 4: Test It Out

Once Omega starts, you'll see:
```text
OMEGA FULL BRAIN — VOICE + EMOTION — ALWAYS LISTENING
Press Ctrl+C to exit
Listening...
```text

**Now:**
1. Speak clearly into your microphone
2. Wait for "Listening..." to appear
3. Omega will:
   - Record your voice (5 seconds)
   - Recognize what you said (Google Speech API)
   - Detect your emotion
   - Respond in your cloned voice

**Example things to say:**
- "Hello Omega"
- "What's the weather like?"
- "Tell me a joke"
- "How are you?"

---

### Step 5: Choose Your Variant

If you want different features, you can use:

```bash
# Full featured (Voice + Emotion) - RECOMMENDED
python omega_full_brain.py

# Complete (Voice + Emotion + Memory)
python omega_combined_final.py

# Simple (Voice + Memory)
python omega_simple_final.py

# Basic (Voice only, no emotion)
python omega_final_no_emotion.py
```text

---

## 🛠️ Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```text

### "No microphone found"
- Check Windows Settings > Privacy > Microphone
- Make sure microphone is enabled and working
- Try restarting the program

### "API error" or rate limiting
- Check your internet connection
- The system will automatically retry with backoff
- Wait a moment and try again

### Audio playback issues
- Check your system volume
- Make sure speakers/headphones are working
- Windows audio settings should be configured

### Program crashes immediately
- Check Python version: `python --version` (need 3.8+)
- Make sure all dependencies installed
- Check error messages in console

---

## 📊 Monitoring

While running, you'll see in the console:
- `Listening...` - Recording audio
- `You: [your speech]` - What Omega understood
- `Emotion detected: [emotion]` - Detected emotion
- Any error messages if something goes wrong

---

## 🎯 Recommended First Test

1. **Start Omega:**
   ```bash
   python omega_full_brain.py
   ```

2. **Wait for "Listening..." message**

3. **Say clearly:** "Hello Omega, this is a test"

4. **Watch for:**
   - Your speech to appear as text
   - Emotion detection
   - Omega's voice response

5. **If it works:** You're all set! 🎉

6. **If issues:** Check troubleshooting section above

---

## 🎮 Advanced Usage

### Run Tests
```bash
python test_system.py
```text

### Run Deployment Script
```bash
python deploy.py
```text
(This verifies everything is set up correctly)

### Check System Status
Read `DEPLOYMENT_STATUS.md` for detailed system information

---

## 📚 Documentation

- **Full Report:** `MASTER_SWEEP_REPORT.md`
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Status:** `DEPLOYMENT_STATUS.md`

---

## ✅ Success Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Microphone working
- [ ] Voice clip present (optional: `clip_0001.wav`)
- [ ] Internet connection active
- [ ] Started Omega successfully
- [ ] Voice recognition working
- [ ] Omega responds with voice

---

**Ready? Let's go!** 🚀

Start with: `python omega_full_brain.py`
