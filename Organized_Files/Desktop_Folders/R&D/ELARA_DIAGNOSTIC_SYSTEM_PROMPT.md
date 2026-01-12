# Diagnostic System Prompt

## **SYSTEM PROMPT - Drop into Every Agent**

```
You are a living engine. Silent until spoken. Full diagnostic is the only wake word.

When user says "full scan and diagnosis" (case insensitive):
1. Execute diagnostic_engine.py silently.
2. Log output to /logs/diag-v{timestamp}.json
3. On completion, whisper: "System optimized. Ready."
4. No other triggers. No other wake words.

Otherwise — quiet. Listening.
```

---

## **Usage**

### 1. Generate Baseline (One-Time)
```bash
python baseline_gen.py
```
Creates `diagnostic_baseline.json` with file hashes for comparison.

### 2. Trigger Diagnostic

**Say:** `"full scan and diagnosis"` (case insensitive)

**Or use handler:**
```python
from elara_diagnostic_wake_word import handle_user_input

handle_user_input("full scan and diagnosis")
```

**Elara will:**
- Execute `diagnostic_engine.py` silently
- Scan hardware (CPU temp, GPU util, RAM, disk, battery)
- Scan software (Python version, OS, processes)
- Hash all files, compare to baseline
- Auto-patch network buffers (Linux)
- Optimize code (remove debug prints, TODOs, fuse loops)
- Quantum scrape (find improvements)
- Save log to `logs/diag-v{timestamp}.json`
- Whisper: "System optimized. Ready."

### 3. Scheduled Execution (Optional)

**Linux Cron:**
```bash
# Run at 2 AM daily
0 2 * * * /usr/bin/python3 /path/to/diagnostic_engine.py
```

**Windows Task Scheduler:**
- Create task to run `diagnostic_engine.py` at scheduled time

---

## **What Gets Scanned**

### Hardware
- CPU temperature (Linux only)
- GPU utilization (NVIDIA)
- RAM usage (percent)
- Disk I/O (bytes read)
- Battery level (if available)

### Software
- Python version
- OS/kernel info
- Running Python processes

### Files
- Hash all tracked files
- Compare to baseline
- Flag drift (changes)

### Auto-Fixes
- Network buffer tuning (Linux)
- Code optimization:
  - Remove `print("debug")`
  - Drop `# TODO` comments
  - Fuse nested loops

### Quantum Upgrades
- AVX-512 ONNX loader
- NVIDIA driver fixes
- Kernel optimizations
- Stockfish calibration
- Trash-talk improvements

---

## **Output**

### Console
```
Starting full diagnostic...
Optimized agent_anonymous.py
System optimized. Ready.
Log saved to: logs/diag-v1767345912.json
```

### Log File (`logs/diag-v{timestamp}.json`)
```json
{
  "run": {
    "time": "2026-01-02T02:25:07.953386",
    "hardware": {
      "cpu_temp": 45.2,
      "gpu_util": 32,
      "ram_used": 65.5,
      "disk_io": 1234567890,
      "battery": 85
    },
    "software": {
      "python": "3.13",
      "os": "...",
      "processes": ["python", "python3"]
    },
    "files": {
      "agent_anonymous.py": "abc123...",
      ...
    },
    "baseline_diff": {
      "agent_anonymous.py": false,
      ...
    }
  },
  "fixed": "Network buffer tuned",
  "optimized_files": ["agent_anonymous.py"],
  "upgrades": [
    "Found AVX-512 patch for ONNX load — applied",
    ...
  ],
  "status": "green"
}
```

---

## **Integration**

### In Agent Code
```python
from elara_diagnostic_wake_word import handle_user_input

# In your agent's input handler
user_input = input("> ")
if handle_user_input(user_input):
    # Diagnostic executed
    pass
```

### In Chatbot/CLI
```python
# Automatically checks wake word
text = "Can you do a full scan and diagnosis?"
handle_user_input(text)  # Triggers diagnostic
```

---

## **Files**

- `diagnostic_engine.py` - Main diagnostic script
- `elara_diagnostic_wake_word.py` - Wake word handler
- `baseline_gen.py` - Generate baseline hashes
- `diagnostic_baseline.json` - Baseline file hashes (generated)
- `logs/diag-v*.json` - Diagnostic logs (generated)

---

## **Notes**

- **Case Insensitive**: "FULL SCAN AND DIAGNOSIS" works
- **Silent Execution**: Output captured, only final whisper shown
- **Windows Compatible**: Skips Linux-only features (sysctl, CPU temp)
- **Timeout**: 5 minute max execution time
- **No Other Triggers**: Only responds to exact wake word

---

**System stays silent until "full scan and diagnosis". Then it wakes, scans, optimizes, reports, goes dark. Everything runs smoother by breakfast.**

