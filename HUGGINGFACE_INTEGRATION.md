# Hugging Face CLI Integration

## Installation Complete ✅

**Date:** January 19, 2026  
**Environment:** Virtual Environment (Python 3.14.2)  
**Location:** `H:/The Gatekeeper/.venv/`

## Installed Components

- `huggingface_hub[cli]` - Core Hugging Face Hub library with CLI tools
- `InquirerPy` - Interactive CLI prompts
- `pfzy` - Fuzzy matching for CLI

## Authentication

To login to your Hugging Face account:

```powershell
& "H:/The Gatekeeper/.venv/Scripts/python.exe" -m huggingface_hub.commands.huggingface_cli login
```

Or using the `hf` command (if added to PATH):

```bash
hf auth login
```

## Hugging Face Jobs - Cloud Computing Commands

### 1. Run Python Code Directly

```bash
hf jobs run python:3.12 python -c 'print("Hello from the cloud!")'
```

**Use Case:** Quick Python script execution in the cloud

---

### 2. Use GPUs Without Setup

```bash
hf jobs run --flavor a10g-small pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
  python -c "import torch; print(torch.cuda.get_device_name())"
```

**Use Case:** Run GPU-accelerated workloads
**Flavors Available:**
- `a10g-small` - NVIDIA A10G GPU
- `a100-large` - NVIDIA A100 GPU
- Additional flavors available via `hf jobs list-flavors`

---

### 3. Run from Hugging Face Spaces (Docker)

```bash
hf jobs run hf.co/spaces/lhoestq/duckdb duckdb -c "select 'hello world'"
```

**Use Case:** Run existing Spaces as containerized jobs

---

### 4. Scheduled Jobs (Cron)

```bash
hf jobs scheduled run "*/5 * * * *" python:3.12 \
  python -c "import time; print('Hello, it'\''s ' + time.ctime())"
```

**Use Case:** Periodic execution (every 5 minutes in this example)

**Cron Format:**
- `* * * * *` = minute hour day month weekday
- `*/5 * * * *` = Every 5 minutes
- `0 */6 * * *` = Every 6 hours
- `0 0 * * *` = Daily at midnight

---

## Command Reference

### Job Management

```bash
# List all jobs
hf jobs list

# Check job status
hf jobs status <job-id>

# View job logs
hf jobs logs <job-id>

# Cancel a running job
hf jobs cancel <job-id>

# Delete a job
hf jobs delete <job-id>
```

### Additional Commands

```bash
# List available compute flavors
hf jobs list-flavors

# Get help
hf jobs --help
hf jobs run --help
```

---

## Integration with The Gatekeeper

### Use Cases for Our System

1. **AI Model Training**
   - Train models on GPU hardware without local setup
   - Schedule periodic model retraining

2. **Data Processing**
   - Run large-scale data transformations
   - Process audio/voice resources in the cloud

3. **Testing & CI/CD**
   - Run automated tests on cloud infrastructure
   - Deploy and test in isolated containers

4. **Scheduled Tasks**
   - Periodic data synchronization
   - Automated reporting
   - System health checks

### Example: Run Omega Security Scan in Cloud

```bash
hf jobs run python:3.12 \
  --volume /workspace:/workspace \
  python -c "
import sys
sys.path.append('/workspace')
from omega_forensic_security import ForensicSecurityAnalyzer
analyzer = ForensicSecurityAnalyzer()
results = analyzer.scan_all_files()
print('Security scan complete!')
"
```

---

## Environment Variables for Jobs

Jobs can access environment variables for sensitive data:

```bash
hf jobs run python:3.12 \
  --env API_KEY=$API_KEY \
  python script.py
```

---

## Pricing & Limits

- Free tier available for testing
- Pay-per-use for production workloads
- GPU time billed by the minute
- Check current pricing: <https://huggingface.co/pricing>

---

## Claude/Cursor 4.5 Authentication Notes

**Issue:** Claude and Cursor may have authentication conflicts  
**Resolution:**
1. Use separate API keys for each service
2. Store keys in environment variables
3. Use `.env` files for local development
4. For cloud jobs, use Hugging Face Secrets

**Example `.env` setup:**

```env
ANTHROPIC_API_KEY=sk-ant-...
CURSOR_API_KEY=...
OPENAI_API_KEY=sk-...
```

**Load in Python:**

```python
from dotenv import load_dotenv
import os

load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
cursor_key = os.getenv("CURSOR_API_KEY")
```

---

## Quick Start Checklist

- [x] ✅ Hugging Face CLI installed
- [ ] 🔑 Login with `hf auth login`
- [ ] 🧪 Test with simple job: `hf jobs run python:3.12 python -c 'print("Hello")'`
- [ ] 🚀 Run first GPU job
- [ ] ⏰ Schedule a cron job
- [ ] 📊 Monitor jobs with `hf jobs list`

---

## Resources

- **Documentation:** <https://huggingface.co/docs/huggingface_hub/guides/cli>
- **Jobs Guide:** <https://huggingface.co/docs/hub/computing>
- **API Reference:** <https://huggingface.co/docs/huggingface_hub/package_reference/hf_api>
- **Community:** <https://discuss.huggingface.co/>

---

## Status

**Installation:** ✅ Complete  
**Authentication:** ⏳ Pending (requires user login)  
**Integration:** ✅ Documentation complete  
**Ready for Use:** ✅ Yes

---

**Last Updated:** January 19, 2026, 01:41 UTC  
**System:** The Gatekeeper - Omega Security Platform
