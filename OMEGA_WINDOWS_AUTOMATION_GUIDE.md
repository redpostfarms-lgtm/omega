# Omega Windows Automation Guide - Multi-AI System

**Date:** January 2026  
**Developer:** Nick (Seattle)  
**Status:** Production-Ready  
**Integration:** Works with Omega Control Panel and Agent Council

---

## Overview

This guide enables Omega to run automated actions on Windows 11 without manual clicks, UAC prompts, or app selections—especially for Microsoft Office integration and seamless communication between local/cloud AIs.

**Key Features:**
- Silent elevated runs (bypass UAC prompts safely)
- Local LLM integration (Ollama, custom models)
- Microsoft Office automation (COM API, no GUI clicks)
- Multi-AI orchestration (local + cloud AIs)
- Background service support
- Task Scheduler integration

---

## Prerequisites

- Windows 11 (tested, works on Windows 10+)
- Python 3.10+ installed
- Admin access (one-time setup)
- Microsoft Office installed (for Office automation)
- Local LLM backend (optional: Ollama, LM Studio, etc.)

---

## Step 1: Enable Silent Elevated Runs (Bypass UAC Prompts Safely)

Windows security (UAC) prevents fully silent elevation without setup, but you can configure safe, reliable automation using Task Scheduler for elevated runs.

### Method 1: Task Scheduler Setup (Recommended)

**Step-by-Step:**

1. **Open Task Scheduler** → Right-click → Create Task

2. **General Tab:**
   - Name: `OmegaAutomation` (or `MyAIOrchestrator`)
   - Check: **Run whether user is logged on or not**
   - Check: **Run with highest privileges**
   - Configure for: **Windows 11** (or your Windows version)

3. **Triggers Tab:**
   - **New** → Trigger: **At startup** (or **At log on**)
   - Repeat task: **Enabled** (optional, set interval if needed)
   - Stop task if it runs longer than: **Unchecked** (or set reasonable time)

4. **Actions Tab:**
   - **New** → Action: **Start a program**
   - Program/script: `C:\Python311\python.exe` (or your Python path)
   - Add arguments: `-u "D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"`
   - Start in: `D:\RPF_BRAIN\The Gatekeeper`

5. **Conditions Tab:**
   - Uncheck: **Start the task only if the computer is on AC power**
   - Check: **Wake the computer to run this task** (if needed)

6. **Settings Tab:**
   - Allow task to be run on demand: **Checked**
   - Run task as soon as possible after a scheduled start is missed: **Checked**
   - If the task fails, restart every: **1 minute** (optional)
   - Attempt to restart up to: **3 times** (optional)
   - Stop the task if it runs longer than: **Unchecked**

7. **Save** → Enter admin password once (this is the only UAC prompt you'll see)

### Create Desktop Shortcut (On-Demand Execution)

**Shortcut Target:**
```
schtasks /run /tn "OmegaAutomation"
```

**Full Command:**
```cmd
schtasks /run /tn "OmegaAutomation"
```

**Create Shortcut Script:**
```python
# create_omega_shortcut.py
import os
import win32com.client

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
shortcut_path = os.path.join(desktop, 'Omega Automation.lnk')

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = "schtasks"
shortcut.Arguments = '/run /tn "OmegaAutomation"'
shortcut.IconLocation = "python.exe,0"
shortcut.save()
```

### Method 2: PowerShell Script (Alternative)

```powershell
# Setup-OmegaAutomation.ps1 (Run as Admin)
$taskName = "OmegaAutomation"
$scriptPath = "D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"
$pythonPath = (Get-Command python).Source

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "-u `"$scriptPath`"" -WorkingDirectory "D:\RPF_BRAIN\The Gatekeeper"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Omega Multi-AI Automation System"
```

---

## Step 2: Core Automation Script Framework

This Python script sets up a multi-agent orchestrator with local LLM support, Office integration via COM API (no GUI clicks), and API calls to other AIs.

### Installation

```bash
# Install required packages
pip install pywin32 crewai ollama requests python-dotenv

# For Office automation
pip install pywin32

# For multi-agent orchestration (choose one or both)
pip install crewai
# OR
pip install langchain autogen

# For local LLM (choose one)
# Ollama (recommended for local)
# Download from: https://ollama.ai
ollama pull llama2  # or your preferred model

# OR LM Studio (alternative)
pip install openai  # for OpenAI-compatible API
```

### Core Orchestrator Script

**File:** `omega_automation_orchestrator.py`

```python
"""
Omega Multi-AI Automation Orchestrator
Runs silently with elevated privileges via Task Scheduler
"""
import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging (runs headlessly, log to file)
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "omega_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available - local LLM features disabled")

try:
    import win32com.client as win32
    OFFICE_AVAILABLE = True
except ImportError:
    OFFICE_AVAILABLE = False
    logger.warning("pywin32 not available - Office automation disabled")

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI not available - using simple orchestration")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - external AI features disabled")

from dotenv import load_dotenv
load_dotenv()


class LocalLLMClient:
    """Local LLM client (Ollama or OpenAI-compatible API)"""
    
    def __init__(self, model: str = "llama2", base_url: Optional[str] = None):
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
    def query(self, prompt: str, system: Optional[str] = None) -> str:
        """Query local LLM"""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama not available")
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Local LLM query failed: {e}")
            raise


class ExternalAIClient:
    """External AI client (Grok, Claude, GPT, etc.)"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "grok-beta"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        
    def query(self, prompt: str) -> str:
        """Query external AI"""
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests not available")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"External AI query failed: {e}")
            raise


class OfficeAutomation:
    """Microsoft Office automation via COM API (no GUI clicks)"""
    
    def __init__(self):
        if not OFFICE_AVAILABLE:
            raise RuntimeError("pywin32 not available")
        self.excel = None
        self.word = None
        
    def open_excel(self, visible: bool = False):
        """Open Excel application (headless)"""
        try:
            self.excel = win32.Dispatch("Excel.Application")
            self.excel.Visible = visible
            self.excel.DisplayAlerts = False  # Suppress dialogs
            logger.info("Excel application opened")
            return self.excel
        except Exception as e:
            logger.error(f"Failed to open Excel: {e}")
            raise
    
    def process_excel_file(self, file_path: str, process_func):
        """Process Excel file with custom function"""
        if not self.excel:
            self.open_excel(visible=False)
        
        try:
            wb = self.excel.Workbooks.Open(file_path)
            result = process_func(wb)
            wb.Save()
            wb.Close()
            logger.info(f"Processed Excel file: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Excel processing failed: {e}")
            raise
    
    def close_excel(self):
        """Close Excel application"""
        if self.excel:
            try:
                self.excel.Quit()
                self.excel = None
                logger.info("Excel application closed")
            except Exception as e:
                logger.warning(f"Error closing Excel: {e}")
    
    def open_word(self, visible: bool = False):
        """Open Word application (headless)"""
        try:
            self.word = win32.Dispatch("Word.Application")
            self.word.Visible = visible
            self.word.DisplayAlerts = 0  # Suppress dialogs
            logger.info("Word application opened")
            return self.word
        except Exception as e:
            logger.error(f"Failed to open Word: {e}")
            raise
    
    def process_word_document(self, file_path: str, process_func):
        """Process Word document with custom function"""
        if not self.word:
            self.open_word(visible=False)
        
        try:
            doc = self.word.Documents.Open(file_path)
            result = process_func(doc)
            doc.Save()
            doc.Close()
            logger.info(f"Processed Word document: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Word processing failed: {e}")
            raise
    
    def close_word(self):
        """Close Word application"""
        if self.word:
            try:
                self.word.Quit()
                self.word = None
                logger.info("Word application closed")
            except Exception as e:
                logger.warning(f"Error closing Word: {e}")
    
    def cleanup(self):
        """Cleanup all Office applications"""
        self.close_excel()
        self.close_word()


class OmegaOrchestrator:
    """Main orchestrator for multi-AI system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.local_llm = None
        self.external_ai = None
        self.office = None
        
        # Initialize components
        if config.get("local_llm", {}).get("enabled", False):
            llm_config = config["local_llm"]
            self.local_llm = LocalLLMClient(
                model=llm_config.get("model", "llama2"),
                base_url=llm_config.get("base_url")
            )
            logger.info("Local LLM initialized")
        
        if config.get("external_ai", {}).get("enabled", False):
            ai_config = config["external_ai"]
            self.external_ai = ExternalAIClient(
                api_url=ai_config["api_url"],
                api_key=ai_config["api_key"],
                model=ai_config.get("model", "grok-beta")
            )
            logger.info("External AI initialized")
        
        if config.get("office", {}).get("enabled", False):
            try:
                self.office = OfficeAutomation()
                logger.info("Office automation initialized")
            except Exception as e:
                logger.warning(f"Office automation not available: {e}")
    
    def process_task(self, task_description: str) -> Dict[str, Any]:
        """Process a task using available AI agents"""
        logger.info(f"Processing task: {task_description}")
        results = {}
        
        # Step 1: Analyze with local LLM
        if self.local_llm:
            try:
                local_response = self.local_llm.query(
                    prompt=task_description,
                    system="You are Omega, an intelligent assistant. Analyze tasks and provide solutions."
                )
                results["local_llm"] = local_response
                logger.info("Local LLM analysis completed")
            except Exception as e:
                logger.error(f"Local LLM failed: {e}")
        
        # Step 2: Consult external AI
        if self.external_ai:
            try:
                external_response = self.external_ai.query(
                    f"Analyze and provide insights: {task_description}"
                )
                results["external_ai"] = external_response
                logger.info("External AI consultation completed")
            except Exception as e:
                logger.error(f"External AI failed: {e}")
        
        # Step 3: Combine results
        if results:
            combined = self._combine_results(results)
            results["combined"] = combined
        
        return results
    
    def _combine_results(self, results: Dict[str, Any]) -> str:
        """Combine results from multiple AI sources"""
        combined_parts = []
        if "local_llm" in results:
            combined_parts.append(f"Local Analysis: {results['local_llm']}")
        if "external_ai" in results:
            combined_parts.append(f"External Insights: {results['external_ai']}")
        return "\n\n".join(combined_parts)
    
    def process_office_task(self, file_path: str, task_type: str = "excel") -> Dict[str, Any]:
        """Process Office file with AI assistance"""
        if not self.office:
            raise RuntimeError("Office automation not available")
        
        logger.info(f"Processing Office file: {file_path} ({task_type})")
        results = {}
        
        if task_type == "excel":
            def process_excel(wb):
                # Example: Read cell A1, process with AI, write to B1
                sheet = wb.Sheets(1)
                value = sheet.Cells(1, 1).Value
                
                # Process with AI
                if self.local_llm:
                    processed = self.local_llm.query(f"Analyze this data: {value}")
                    sheet.Cells(1, 2).Value = processed
                    results["processed_value"] = processed
                
                return "Excel processing completed"
            
            self.office.process_excel_file(file_path, process_excel)
        
        elif task_type == "word":
            def process_word(doc):
                # Example: Get first paragraph, enhance with AI
                if doc.Paragraphs.Count > 0:
                    text = doc.Paragraphs(1).Range.Text
                    
                    if self.local_llm:
                        enhanced = self.local_llm.query(f"Enhance this text: {text}")
                        results["enhanced_text"] = enhanced
                
                return "Word processing completed"
            
            self.office.process_word_document(file_path, process_word)
        
        return results
    
    def cleanup(self):
        """Cleanup resources"""
        if self.office:
            self.office.cleanup()


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config_file = Path(__file__).parent / "omega_automation_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "local_llm": {
            "enabled": os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true",
            "model": os.getenv("LOCAL_LLM_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        },
        "external_ai": {
            "enabled": os.getenv("EXTERNAL_AI_ENABLED", "false").lower() == "true",
            "api_url": os.getenv("EXTERNAL_AI_URL", ""),
            "api_key": os.getenv("EXTERNAL_AI_KEY", ""),
            "model": os.getenv("EXTERNAL_AI_MODEL", "grok-beta")
        },
        "office": {
            "enabled": os.getenv("OFFICE_ENABLED", "true").lower() == "true"
        },
        "tasks": []
    }


def main():
    """Main entry point"""
    logger.info("Omega Automation Orchestrator starting...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded")
        
        # Initialize orchestrator
        orchestrator = OmegaOrchestrator(config)
        logger.info("Orchestrator initialized")
        
        # Process configured tasks
        tasks = config.get("tasks", [])
        if tasks:
            for task in tasks:
                try:
                    if task.get("type") == "office":
                        result = orchestrator.process_office_task(
                            task["file_path"],
                            task.get("task_type", "excel")
                        )
                    else:
                        result = orchestrator.process_task(task["description"])
                    
                    logger.info(f"Task completed: {task.get('name', 'unnamed')}")
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        
        # Cleanup
        orchestrator.cleanup()
        logger.info("Omega Automation Orchestrator completed")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---

## Step 3: Configuration File

**File:** `omega_automation_config.json`

```json
{
  "local_llm": {
    "enabled": true,
    "model": "llama2",
    "base_url": "http://localhost:11434"
  },
  "external_ai": {
    "enabled": true,
    "api_url": "https://api.x.ai/v1/chat/completions",
    "api_key": "your-grok-api-key-here",
    "model": "grok-beta"
  },
  "office": {
    "enabled": true
  },
  "tasks": [
    {
      "name": "Process Excel Data",
      "type": "office",
      "task_type": "excel",
      "file_path": "C:\\Data\\reports.xlsx",
      "schedule": "daily"
    },
    {
      "name": "Daily Analysis",
      "type": "analysis",
      "description": "Analyze system performance and generate report"
    }
  ]
}
```

**Environment Variables (Alternative):**

Create `.env` file:

```env
# Local LLM (Ollama)
LOCAL_LLM_ENABLED=true
LOCAL_LLM_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# External AI (Grok, Claude, GPT, etc.)
EXTERNAL_AI_ENABLED=true
EXTERNAL_AI_URL=https://api.x.ai/v1/chat/completions
EXTERNAL_AI_KEY=your-api-key-here
EXTERNAL_AI_MODEL=grok-beta

# Office Automation
OFFICE_ENABLED=true
```

---

## Step 4: Integration with Omega Control Panel

Integrate automation with the existing Omega Control Panel web interface.

### Add Automation Endpoints

**File:** `omega_control_panel_web.py` (add to existing file)

```python
# Add to omega_control_panel_web.py

@app.route('/api/automation/status')
@login_required
@role_required('admin', 'operator')
def automation_status():
    """Get automation system status"""
    try:
        # Check if orchestrator is running
        # Check Task Scheduler status
        import subprocess
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'OmegaAutomation'],
            capture_output=True,
            text=True
        )
        is_running = "Ready" in result.stdout
        
        return jsonify({
            "status": "running" if is_running else "stopped",
            "task_scheduler": "configured" if is_running else "not_found"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/automation/trigger', methods=['POST'])
@login_required
@role_required('admin')
def trigger_automation():
    """Manually trigger automation task"""
    try:
        import subprocess
        result = subprocess.run(
            ['schtasks', '/run', '/tn', 'OmegaAutomation'],
            capture_output=True,
            text=True
        )
        return jsonify({"success": True, "message": "Automation triggered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

## Advanced Features

### Run as Background Service

Use NSSM (Non-Sucking Service Manager) to run as Windows service:

1. Download NSSM: https://nssm.cc/download
2. Install service:
```cmd
nssm install OmegaAutomation "C:\Python311\python.exe" "-u D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"
nssm set OmegaAutomation AppDirectory "D:\RPF_BRAIN\The Gatekeeper"
nssm start OmegaAutomation
```

### GUI Automation Fallback

If an app lacks COM API, use `pywinauto`:

```bash
pip install pywinauto
```

```python
from pywinauto import Application
app = Application().start("notepad.exe")
app.Notepad.Edit.type_keys("Hello from Omega")
```

### Integration with Agent Council

Integrate with existing `omega_agent_council.py`:

```python
# In omega_automation_orchestrator.py
from omega_agent_council import AgentCouncil

# Use existing agent council
council = AgentCouncil()
orchestrator = OmegaOrchestrator(config)
orchestrator.agent_council = council  # Integrate with existing system
```

---

## Troubleshooting

### UAC Still Prompting

- Ensure Task Scheduler task is set to "Run with highest privileges"
- Check that "Run whether user is logged on or not" is selected
- Verify admin password was entered during task creation

### Office COM Errors

- Ensure Office is installed (not just Office 365 web)
- Try running as admin once to initialize COM
- Check if Office apps are already open (close first)

### Local LLM Not Responding

- Verify Ollama is running: `ollama serve`
- Test model: `ollama run llama2`
- Check base_url in configuration

### External AI Errors

- Verify API key is correct
- Check network connectivity
- Verify API endpoint URL
- Check rate limits

---

## Status

✅ **Production-Ready** — Comprehensive automation system  
✅ **Integrated** — Works with Omega Control Panel  
✅ **Safe** — Uses Task Scheduler (Microsoft-approved method)  
✅ **Flexible** — Supports multiple AI backends and Office apps

---

## Related Documentation

- [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md)
- [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md)
- Omega Agent Council Documentation
- Omega Control Panel Documentation

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Status:** Production-Ready
