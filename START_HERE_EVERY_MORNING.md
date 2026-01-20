# 🌅 MORNING STARTUP INSTRUCTIONS

## **START HERE EVERY MORNING** ☕

### Step 1: Run Morning Initialization
Open PowerShell or Command Prompt:

```batch
cd "H:\The Gatekeeper"
MORNING_INIT.bat
```

**OR** just double-click: `MORNING_INIT.bat`

---

### Step 2: Review Status Report
The initialization will:
- ✅ Authenticate all services (Git, GitHub, Docker, Hugging Face, Telegram)
- ✅ Initialize system components (Resource Manager, Relationship System, Voice Security)
- ✅ Check GPU availability
- ✅ Validate disk space, RAM, CPU
- ✅ Generate `morning_init_status.json`

---

### Step 3: Check Results

#### **If you see:**
```
✅ SYSTEM READY FOR OPERATIONS
```
**→ You're good to go! Start working.**

#### **If you see:**
```
⚠️ SYSTEM READY WITH WARNINGS
```
**→ Check the console output or `morning_init_status.json` for details.**  
Most warnings are non-critical (e.g., Docker not running).

---

## 🔧 Troubleshooting

### Common Issues:

**❌ "Git not found"**
- Install Git: https://git-scm.com/download/win
- Or add Git to PATH

**❌ "GitHub authentication failed"**
```batch
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

**❌ "Hugging Face token missing"**
```python
from huggingface_hub import login
login()  # Follow prompts
```

**❌ "Docker not available"**
- Start Docker Desktop
- Or ignore if not needed today

**❌ "GPU not detected"**
- Check CUDA installation
- Update NVIDIA drivers
- System will work in CPU mode

---

## 📋 What Gets Initialized

### Services:
- ✅ Git (local repository)
- ✅ GitHub (authentication)
- ✅ Docker (daemon)
- ✅ Hugging Face (token)
- ✅ Telegram Bot (if configured)

### Components:
- ✅ Resource Manager (CPU/GPU optimization)
- ✅ Relationship System (tracks interaction level)
- ✅ Voice Security (authentication)
- ✅ GPU (CUDA device validation)

### Health:
- ✅ Disk Space (C: drive)
- ✅ RAM Usage
- ✅ CPU Usage
- ✅ Python Environment

---

## 🚀 Optional: Auto-Start at Windows Login

1. Press `Win + R`
2. Type: `shell:startup` and press Enter
3. Right-click → New → Shortcut
4. Browse to: `H:\The Gatekeeper\MORNING_INIT.bat`
5. Name it: "Morning Initialization"
6. Click Finish

**Now it runs automatically every time you log in!**

---

## 📊 Status Report Location

After each run, check:
```
H:\The Gatekeeper\morning_init_status.json
```

Contains:
- Timestamp
- All service statuses
- Errors and warnings
- Overall readiness

---

## 💡 Tips

- ✅ Run this **BEFORE** starting any work
- ✅ Takes ~30 seconds to complete
- ✅ Saves time by catching issues early
- ✅ Provides confidence that all systems are ready

---

**The Gatekeeper wakes up properly now. No more forgotten authentications!** ✨
