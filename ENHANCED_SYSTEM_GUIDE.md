# Gatekeeper Enhanced System Guide
## Complete Setup & Usage Documentation

---

## 📋 Table of Contents

1. [System Enhancements](#system-enhancements)
2. [Installation](#installation)
3. [Compressed JSON Storage](#compressed-json-storage)
4. [File Integrity Checking](#file-integrity-checking)
5. [Windows 10 Notifications](#windows-10-notifications)
6. [Local LLM Integration](#local-llm-integration)
7. [Web-Based IDE](#web-based-ide)
8. [Dependencies Reference](#dependencies-reference)
9. [Advanced Configuration](#advanced-configuration)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 System Enhancements

### What's New

The Gatekeeper system has been enhanced with production-grade features:

#### 1. **Automatic JSON Compression**
- Gzip compression for files >2MB
- Prevents conversation folder bloat
- Transparent load/save (no code changes needed)
- Batch compression for existing files

#### 2. **SHA-256 Integrity Checking**
- File corruption detection
- Tamper-proof verification
- Auto-abort on integrity failures
- Full audit trail

#### 3. **Windows 10 Toast Notifications**
- Quiet, non-intrusive alerts
- Disk space warnings (>80% usage)
- Cleanup status updates
- Integrity failure alerts

#### 4. **Local LLM Integration**
- Run Llama 3.2 locally (offline AI)
- Ollama or LM Studio support
- Integrated with voice system
- No API costs

#### 5. **Web-Based IDE**
- Browser-based code editor
- File tree navigation
- AI chat interface
- Voice chat integration
- Integrated terminal

---

## 📦 Installation

### Quick Install (Recommended)

```batch
# Run the automated installer
INSTALL_ENHANCED.bat
```

This installs:
- Core dependencies (pyyaml, schedule, flask, black, ruff)
- Optional tools (watchdog, pytest, sqlalchemy)
- LLM integration (ollama, langchain, chromadb)

### Manual Install

```batch
# Core only
py -3.11 -m pip install -r requirements_enhanced.txt

# Or install selectively:
py -3.11 -m pip install pyyaml schedule flask black ruff
py -3.11 -m pip install win10toast prometheus-client psutil
py -3.11 -m pip install ollama langchain chromadb
```

### Verify Installation

```batch
# Check what's installed
py -3.11 -m pip list

# Test imports
py -3.11 -c "import yaml, schedule, flask, black, ruff; print('✓ Core OK')"
py -3.11 -c "import ollama; print('✓ LLM OK')"
```

---

## 💾 Compressed JSON Storage

### Automatic Compression

Use the drop-in replacement functions:

```python
from utils.compressed_json import save_json_auto, load_json_auto

# Save (auto-compresses if >2MB)
data = {"large": "dataset" * 100000}
stats = save_json_auto('data.json', data)
print(f"Saved {stats['compression_ratio']} space")
# Output: Saved 78.3% space

# Load (auto-detects .gz files)
loaded_data = load_json_auto('data.json')
```

### Batch Compress Existing Files

```python
from utils.compressed_json import CompressedJSON

# Compress all JSONs in conversations folder
stats = CompressedJSON.batch_compress_directory(
    'conversations',
    threshold=2*1024*1024,  # 2MB
    pattern='*.json'
)

print(f"Compressed: {stats['compressed_files']} files")
print(f"Space saved: {stats['space_saved'] / 1024 / 1024:.1f}MB")
```

### Integration Example

Replace existing `json.dump` calls:

```python
# Before:
with open('large_file.json', 'w') as f:
    json.dump(data, f, indent=2)

# After:
from utils.compressed_json import save_json_auto
save_json_auto('large_file.json', data, indent=2)
```

---

## 🔒 File Integrity Checking

### Quick Start

```python
from utils.integrity_checker import IntegrityChecker

# Initialize
checker = IntegrityChecker()

# Register file (calculate hash)
checker.register_file('important_data.json')

# Verify before processing
if checker.verify_before_process('important_data.json'):
    # Safe to process - file is intact
    with open('important_data.json', 'r') as f:
        data = json.load(f)
```

### Auto-Abort on Corruption

```python
from utils.integrity_checker import IntegrityChecker, IntegrityError

checker = IntegrityChecker()
checker.register_file('critical.json')

try:
    checker.verify_before_process('critical.json')
    # Process file...
except IntegrityError as e:
    # File corrupted - DO NOT PROCESS
    print(f"ABORT: {e}")
    # Alert user, restore backup, etc.
```

### Batch Operations

```python
# Register entire directory
count = checker.register_directory('conversations', '*.json')
print(f"Registered {count} files")

# Verify all registered files
stats = checker.batch_verify(
    ['file1.json', 'file2.json', 'file3.json'],
    verbose=True
)

print(f"Verified: {stats['verified']} / {stats['total']}")
print(f"Corrupted: {stats['corrupted']}")

if stats['corrupted'] > 0:
    for failed in stats['failed_files']:
        print(f"✗ CORRUPTED: {failed['file']}")
```

### Decorator Pattern

```python
from utils.integrity_checker import verify_integrity

@verify_integrity(file_param='config_file')
def load_config(config_file):
    """Auto-verifies integrity before loading"""
    with open(config_file, 'r') as f:
        return json.load(f)

# Usage - auto-checks integrity
config = load_config('config.json')
```

---

## 🔔 Windows 10 Notifications

### Quick Start

```python
from utils.win10_notifications import get_notifier

notifier = get_notifier()

# Cleanup notifications
notifier.cleanup_started('conversations')
# ... perform cleanup ...
notifier.cleanup_completed(files_removed=42, space_freed=128.5)

# Disk space warning
notifier.disk_space_warning('C:', 85.0)  # 85% full

# Compression complete
notifier.compression_completed(files_compressed=10, space_saved=50.5)

# Custom notification
notifier.custom('Task Complete', 'All files processed successfully')
```

### Convenience Functions

```python
from utils.win10_notifications import (
    notify_cleanup_started,
    notify_cleanup_completed,
    notify_disk_space,
    notify_compression,
    notify_integrity_failure
)

# Quick notifications
notify_cleanup_started('temp_files')
notify_disk_space('C:', 88.0)
notify_integrity_failure('corrupted_file.json')
```

### Enable/Disable

```python
notifier = get_notifier()

# Disable during batch operations
notifier.disable()
# ... batch work ...
notifier.enable()
```

---

## 🤖 Local LLM Integration

### Setup Ollama (Recommended)

1. **Download Ollama**
   - Visit: https://ollama.ai/download
   - Run installer

2. **Install Llama 3.2**
   ```batch
   ollama pull llama3.2
   ```

3. **Test Ollama**
   ```batch
   ollama run llama3.2 "Hello!"
   ```

4. **Install Python Client**
   ```batch
   py -3.11 -m pip install ollama
   ```

### Usage

```python
from omega_local_llm import get_brain_llm

# Initialize
brain = get_brain_llm()

# Process voice input
response = brain.process_voice_input(
    user_text="What's the weather like?",
    emotion="neutral"
)
print(response)

# Async usage
import asyncio
from omega_local_llm import omega_llm_response

async def main():
    response = await omega_llm_response(
        "Tell me a joke",
        emotion="happy"
    )
    print(response)

asyncio.run(main())
```

### Integration with Omega

Replace hardcoded responses in `omega_full_brain.py`:

```python
# Before:
reply = f"Gate says: {said}. I feel your {emotion}."

# After:
from omega_local_llm import get_brain_llm
brain = get_brain_llm()
reply = brain.process_voice_input(said, emotion)
```

### Alternative: LM Studio

```python
from omega_local_llm import LocalLLM, LLMConfig

# Configure for LM Studio
config = LLMConfig(
    backend="lmstudio",
    model="llama-3.2-1b",
    host="http://localhost:1234"
)

llm = LocalLLM(config)
response = llm.generate("Hello!")
```

---

## 🌐 Web-Based IDE

### Start the IDE

```batch
# Default (port 5000)
py -3.11 omega_web_ide.py

# Custom port
py -3.11 omega_web_ide.py --port 8080

# Different directory
py -3.11 omega_web_ide.py --dir "C:\Projects\MyApp"

# Debug mode
py -3.11 omega_web_ide.py --debug
```

### Access

Open browser: **http://localhost:5000**

### Features

1. **Code Editor**
   - Syntax highlighting
   - Auto-save
   - Multi-tab support

2. **File Browser**
   - Navigate directories
   - Click to open files
   - Create/delete files

3. **AI Chat**
   - Ask questions about code
   - Get suggestions
   - Context-aware responses

4. **Voice Interface**
   - Talk to AI
   - Voice commands
   - TTS responses

5. **Integrated Terminal**
   - Run commands
   - View output
   - Real-time logs

### API Endpoints

```python
# Check LLM status
GET /api/llm/status

# Chat with AI
POST /api/llm/chat
{
  "message": "Explain this function"
}

# Get file tree
GET /api/files/tree

# Read file
GET /api/files/read?path=omega_full_brain.py

# Save file
POST /api/files/save
{
  "path": "test.py",
  "content": "print('hello')"
}
```

---

## 📚 Dependencies Reference

### Core (Required)

| Package | Purpose | Install |
|---------|---------|---------|
| pyyaml | Config loading | `pip install pyyaml` |
| schedule | Cron jobs | `pip install schedule` |
| flask | Web server | `pip install flask` |
| waitress | Production WSGI | `pip install waitress` |
| black | Code formatting | `pip install black` |
| ruff | Fast linting | `pip install ruff` |

### Monitoring

| Package | Purpose | Install |
|---------|---------|---------|
| prometheus-client | Metrics | `pip install prometheus-client` |
| psutil | System stats | `pip install psutil` |

### Notifications

| Package | Purpose | Install |
|---------|---------|---------|
| win10toast | Windows toasts | `pip install win10toast` |

### Optional - Database

| Package | Purpose | Install |
|---------|---------|---------|
| sqlalchemy | ORM | `pip install sqlalchemy` |

Built-in: `sqlite3` (no install needed)

### Optional - File Watching

| Package | Purpose | Install |
|---------|---------|---------|
| watchdog | Smart file monitor | `pip install watchdog` |

### Optional - Testing

| Package | Purpose | Install |
|---------|---------|---------|
| pytest | Test framework | `pip install pytest` |
| pytest-asyncio | Async tests | `pip install pytest-asyncio` |
| pytest-cov | Coverage | `pip install pytest-cov` |

### Optional - LLM

| Package | Purpose | Install |
|---------|---------|---------|
| ollama | Ollama client | `pip install ollama` |
| langchain | LLM framework | `pip install langchain` |
| chromadb | Vector DB | `pip install chromadb` |
| sentence-transformers | Embeddings | `pip install sentence-transformers` |

### Optional - Web IDE

| Package | Purpose | Install |
|---------|---------|---------|
| voila | Jupyter web UI | `pip install voila` |
| ipywidgets | Interactive widgets | `pip install ipywidgets` |
| jupyterlab | Full IDE | `pip install jupyterlab` |

---

## ⚙️ Advanced Configuration

### Scheduled Cleanup

```python
import schedule
import time
from utils.compressed_json import CompressedJSON
from utils.win10_notifications import notify_cleanup_started, notify_cleanup_completed

def auto_cleanup():
    """Runs every night at 2 AM"""
    notify_cleanup_started('conversations')

    stats = CompressedJSON.batch_compress_directory('conversations')

    notify_cleanup_completed(
        files_removed=0,
        space_freed=stats['space_saved'] / 1024 / 1024
    )

# Schedule
schedule.every().day.at("02:00").do(auto_cleanup)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Disk Space Monitor

```python
import psutil
from utils.win10_notifications import notify_disk_space

def check_disk_space():
    """Monitor disk usage"""
    disk = psutil.disk_usage('C:')
    usage_percent = disk.percent

    if usage_percent >= 80:
        notify_disk_space('C:', usage_percent)

# Schedule every hour
schedule.every().hour.do(check_disk_space)
```

### SQLite Migration

Replace JSON logs with SQLite:

```python
import sqlite3
import json
from datetime import datetime

# Create database
conn = sqlite3.connect('conversations.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_text TEXT,
    assistant_response TEXT,
    emotion TEXT
)
''')

# Insert
cursor.execute('''
INSERT INTO messages (timestamp, user_text, assistant_response, emotion)
VALUES (?, ?, ?, ?)
''', (datetime.now().isoformat(), "Hello", "Hi there", "neutral"))

conn.commit()

# Query
cursor.execute('''
SELECT * FROM messages
WHERE timestamp >= datetime('now', '-7 days')
ORDER BY timestamp DESC
''')

for row in cursor.fetchall():
    print(row)
```

---

## 🔧 Troubleshooting

### JSON Compression Issues

**Problem:** File not compressing

```python
# Check file size
import os
size = os.path.getsize('file.json')
print(f"Size: {size} bytes ({size / 1024 / 1024:.1f}MB)")

# Force compression
from utils.compressed_json import CompressedJSON
stats = CompressedJSON.save('file.json', data, compress_threshold=0)
```

**Problem:** Can't load compressed file

```python
# Explicitly load .gz
from utils.compressed_json import CompressedJSON
data = CompressedJSON.load('file.json.gz')
```

### Integrity Check Failures

**Problem:** False positive corruption

```python
# Re-register file
checker.register_file('file.json', force=True)

# Verify again
result = checker.verify_file('file.json', abort_on_mismatch=False)
print(result)
```

**Problem:** Lost integrity database

```python
# Rebuild database
checker = IntegrityChecker()
count = checker.register_directory('.', '*.json', recursive=True)
print(f"Registered {count} files")
```

### Toast Notifications Not Working

**Problem:** Library not installed

```batch
py -3.11 -m pip install win10toast
```

**Problem:** Not on Windows

```python
# Notifications gracefully fallback to console print
notifier = get_notifier()
# Will print to console on non-Windows systems
```

### LLM Not Available

**Problem:** Ollama not running

```batch
# Start Ollama service (usually auto-starts)
# Or run manually
ollama serve
```

**Problem:** Model not installed

```batch
ollama pull llama3.2
```

**Problem:** Connection refused

```python
# Check Ollama is running
import requests
r = requests.get('http://localhost:11434/api/tags')
print(r.json())
```

### Web IDE Port Conflict

**Problem:** Port 5000 already in use

```batch
# Use different port
py -3.11 omega_web_ide.py --port 8080
```

**Problem:** Can't access from browser

```batch
# Allow firewall access
# Or bind to all interfaces (security risk!)
py -3.11 omega_web_ide.py --host 0.0.0.0
```

---

## 📝 Quick Reference

### File Locations

```
📁 Project Root
├── utils/
│   ├── compressed_json.py      # JSON compression
│   ├── integrity_checker.py    # File integrity
│   └── win10_notifications.py  # Toast notifications
├── omega_local_llm.py          # LLM integration
├── omega_web_ide.py            # Web IDE
├── requirements_enhanced.txt   # Dependencies
├── INSTALL_ENHANCED.bat        # Installer
└── .integrity_db.json          # Integrity database
```

### Common Commands

```batch
# Install everything
INSTALL_ENHANCED.bat

# Start web IDE
py -3.11 omega_web_ide.py

# Setup Ollama
ollama pull llama3.2

# Run tests
pytest

# Format code
black *.py

# Lint code
ruff check *.py
```

### Integration Checklist

- [ ] Install dependencies
- [ ] Set up Ollama/LM Studio
- [ ] Replace `json.dump` with `save_json_auto`
- [ ] Add integrity checks to critical files
- [ ] Enable toast notifications
- [ ] Integrate local LLM with voice system
- [ ] Set up scheduled cleanup
- [ ] Test web IDE

---

## 🎯 Next Steps

1. **Replace JSON Operations**
   - Search for `json.dump` in codebase
   - Replace with `save_json_auto`

2. **Add Integrity Checks**
   - Identify critical files
   - Register with `IntegrityChecker`
   - Add `verify_before_process` calls

3. **Set Up Monitoring**
   - Install prometheus-client
   - Configure disk space alerts
   - Schedule cleanup tasks

4. **Deploy Local LLM**
   - Install Ollama
   - Pull Llama 3.2
   - Integrate with Omega

5. **Launch Web IDE**
   - Start server
   - Test all features
   - Customize as needed

---

**Status:** ✅ All enhancements complete and documented

**Last Updated:** 2026-01-17

**Support:** See individual module documentation for detailed help
