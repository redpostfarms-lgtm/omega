# Gatekeeper Quick Start Guide

## 5-Minute Setup

### Step 1: Run Complete Setup
```bash
"The Gatekeeper\setup_complete_system.bat"
```text
This will:
- Create all directories
- Prime the brain
- Load prompts
- Set up voiceprint (you'll speak your name)
- Tune voice
- Schedule all weekly tasks

### Step 2: Optional - Max Out Pipelines
```bash
python "The Gatekeeper\max_out_pipelines.py"
```text
Sets all education pipelines to 100%. One-time run.

### Step 3: Add to Startup (Optional)
Copy `brain_wakeup.bat` to Windows Startup folder:
- Press `Win + R`
- Type: `shell:startup`
- Copy `brain_wakeup.bat` there

## Daily Use

### Morning
- 6:00 AM: Automatic voice briefing
- "Morning. 18650 bank at 94%. Panel 7 trending low. Grant deadline in 11 days. Wind 14 mph west. Coffee's on."

### During Day
- Say: "Hey, Gatekeeper, [command]"
- Only your voice activates it
- Commands logged automatically

### Evening
- Check status: "Hey, Gatekeeper, status"
- Response: "The doors of knowledge opens. All green. You're good. Go eat steak. 2026 is handled."

## Weekly Schedule

- **Monday 3:00 AM**: Self-learning (with approval)
- **Wednesday 10:24 PM**: Growth loop (with approval)
- **Daily 6:00 AM**: Morning briefing

## Key Commands

### Voice Commands
- "Hey, Gatekeeper, status" - System status
- "Hey, Gatekeeper, charge level?" - Battery report
- "Hey, Gatekeeper, new REAP grant 15k" - Create grant
- "Hey, Gatekeeper, sun tomorrow?" - Solar forecast
- "Hey, Gatekeeper, open Word" - Launch app
- "Gatekeeper, scorched earth" (3x) - Emergency shutdown

### Emergency
- **Voice**: Say "scorched earth" three times fast
- **Hardware**: Press physical panic button (if installed)
- Requires voiceprint + USB key to restore

## File Locations

- **Brain**: `D:\RPF_BRAIN\The Gatekeeper\`
- **Archived**: `D:\RPF_BRAIN\Archived\`
- **Voiceprint**: `D:\RPF_BRAIN\Archived\voiceprint\`
- **Knowledge**: `D:\RPF_BRAIN\Archived\learning\gatekeeper_knowledge.json`

## Troubleshooting

### Voice not working?
1. Run `voiceprint_auth.py` again
2. Check microphone permissions
3. Verify `voice_tuner.py` settings

### Learning not working?
1. Install Ollama: https://ollama.ai/
2. Pull model: `ollama pull llama3`
3. Run `self_learn.py` manually

### System won't start?
1. Run `auto_heal.py` manually
2. Check `brain_wakeup.bat` paths
3. Verify Python is in PATH

## Status Check

Run this to verify everything:
```bash
python "The Gatekeeper\auto_heal.py" --verify
```text

## Support

All scripts are self-documenting. Check:
- `README.md` - Complete documentation
- Script comments - Inline documentation
- Logs in `D:\RPF_BRAIN\Archived\learning\`

---

**The Gatekeeper is ready. Say the word.**

