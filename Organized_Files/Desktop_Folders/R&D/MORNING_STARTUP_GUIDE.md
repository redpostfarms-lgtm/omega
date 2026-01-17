# Morning Startup Guide

## ✅ **Auto-Diagnostic on Boot**

**Status:** Configured to run full scan and diagnosis every morning, then continue normal operations.

---

## Setup (One-Time)

### Windows Startup
```bash
setup_morning_startup.bat
```text

This will:
1. Create a shortcut in Windows Startup folder
2. Configure morning startup to run on boot
3. Create optional feature flags

---

## What Happens on Boot

### 1. Full Scan and Diagnosis
- Runs `diagnostic_engine.py` automatically
- Scans hardware (CPU, GPU, RAM, disk, battery)
- Scans software (Python version, OS, processes)
- Hashes all files, compares to baseline
- Auto-fixes code issues
- Quantum deep scrub for improvements
- Saves log to `logs/diag-v{timestamp}.json`
- Whisper: "System optimized. Ready."

### 2. Continue Normal Operations
- Checks for optional auto-start features
- Starts agent swarm (if `swarm_auto_start.flag` exists)
- Prepares game framework (if `games_auto_start.flag` exists)
- Loads startup tasks (if `startup_tasks.json` exists)
- System ready for commands

---

## Optional Features

### Auto-Start Agent Swarm
Create flag file:
```bash
echo. > swarm_auto_start.flag
```text

This will automatically start the 4-agent swarm (Chess, Checkers, Mahjong, Go) after diagnostic.

### Auto-Start Games
Create flag file:
```bash
echo. > games_auto_start.flag
```text

This prepares the game framework for immediate use.

### Custom Startup Tasks
Create `startup_tasks.json`:
```json
{
  "tasks": [
    {
      "name": "Task Name",
      "enabled": true,
      "command": "python script.py"
    }
  ]
}
```text

---

## Manual Execution

### Run Morning Startup Now
```bash
python morning_startup.py
```text

Or:
```bash
morning_startup.bat
```text

---

## Files

- `morning_startup.py` - Main startup script
- `morning_startup.bat` - Windows batch wrapper
- `setup_morning_startup.bat` - One-time setup script
- `swarm_auto_start.flag` - Optional swarm auto-start
- `games_auto_start.flag` - Optional games auto-start
- `startup_tasks.json` - Optional custom tasks

---

## Disable Auto-Start

### Remove from Startup
1. Press `Win + R`
2. Type: `shell:startup`
3. Delete "Morning Startup.lnk"

Or run:
```powershell
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Morning Startup.lnk"
```text

---

## Logs

Diagnostic logs saved to:
- `logs/diag-v{timestamp}.json`
- `logs/diag-execution-{timestamp}.txt`

Check logs to see what was scanned and optimized each morning.

---

## Status

✅ **Configured and Ready**

Tomorrow morning, when the system boots:
1. Full scan and diagnosis runs automatically
2. System optimized and ready
3. Normal operations continue
4. System reports: "System optimized. Ready."

**Everything runs smoother by breakfast.**

---

**Run `setup_morning_startup.bat` once to enable.**

