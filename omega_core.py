"""
Omega AI Core - Windows Integration Layer
==========================================
Lightweight, modular Windows AI integration that runs silently in the background.
- Runs local LLM (via Ollama or LM Studio) silently
- Listens system-wide (hotkeys, clipboard, file changes)
- Acts automatically (no clicks, no app selection)
- Integrates with Microsoft Office via COM (headless)
- Can talk to external AIs (Grok, Claude, etc.) when needed
- Feels like part of Windows — not an extra app

Usage:
    python omega_core.py
"""

import os
import sys
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

base_dir = Path(__file__).parent.absolute()

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Ollama not installed. Install with: pip install ollama")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("keyboard not installed. Install with: pip install keyboard")

try:
    import win32clipboard
    import win32com.client as win32
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("pywin32 not installed. Install with: pip install pywin32")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("watchdog not installed. Install with: pip install watchdog")

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    print("win10toast not installed. Install with: pip install win10toast")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not installed. Install with: pip install requests")

LOCAL_MODEL = os.getenv('OMEGA_LOCAL_MODEL', 'llama3.2:3b')  # e.g., llama3.2:3b or your custom
WATCH_FOLDER = os.getenv('OMEGA_WATCH_FOLDER', str(Path.home() / 'Desktop'))  # auto-process new files here
HOTKEY = os.getenv('OMEGA_HOTKEY', 'ctrl+space')  # Global hotkey
CONFIG_FILE = base_dir / 'omega_core_config.json'

if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            LOCAL_MODEL = config.get('local_model', LOCAL_MODEL)
            WATCH_FOLDER = config.get('watch_folder', WATCH_FOLDER)
            HOTKEY = config.get('hotkey', HOTKEY)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")

TOAST = ToastNotifier() if TOAST_AVAILABLE else None

EXTERNAL_AI_CONFIGS = {
    'grok': {
        'api_url': 'https://api.x.ai/v1/chat/completions',
        'api_key': os.getenv('GROK_API_KEY', ''),
        'model': 'grok-beta'
    },
    'claude': {
        'api_url': 'https://api.anthropic.com/v1/messages',
        'api_key': os.getenv('CLAUDE_API_KEY', ''),
        'model': 'claude-3-opus-20240229'
    },
    'chatgpt': {
        'api_url': 'https://api.openai.com/v1/chat/completions',
        'api_key': os.getenv('OPENAI_API_KEY', ''),
        'model': 'gpt-4'
    }
}

last_clipboard = ""
running = True
clipboard_thread = None
file_observer = None


def local_llm(prompt: str) -> str:
    """Query local LLM via Ollama"""
    if not OLLAMA_AVAILABLE:
        return "[Local LLM not available - install ollama]"
    
    try:
        response = ollama.chat(model=LOCAL_MODEL, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()
    except Exception as e:
        return f"[Local LLM error: {e}]"


def external_ai(prompt: str, service: str = 'grok') -> str:
    """Query external AI service (Grok, Claude, ChatGPT)"""
    if not REQUESTS_AVAILABLE:
        return "[External AI not available - install requests]"
    
    if service not in EXTERNAL_AI_CONFIGS:
        return f"[Unknown service: {service}]"
    
    config = EXTERNAL_AI_CONFIGS[service]
    if not config.get('api_key'):
        return f"[{service.capitalize()} API key not configured]"
    
    try:
        if service == 'claude':
            headers = {
                'x-api-key': config['api_key'],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            data = {
                'model': config['model'],
                'max_tokens': 1024,
                'messages': [{'role': 'user', 'content': prompt}]
            }
        else:
            headers = {
                'Authorization': f"Bearer {config['api_key']}",
                'Content-Type': 'application/json'
            }
            data = {
                'model': config['model'],
                'messages': [{'role': 'user', 'content': prompt}]
            }
        
        resp = requests.post(config['api_url'], json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        
        if service == 'claude':
            return resp.json()['content'][0]['text'].strip()
        else:
            return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[{service.capitalize()} error: {e}]"


def office_automate(file_path: str):
    """Automate Microsoft Office tasks via COM (headless)"""
    if not WINDOWS_AVAILABLE:
        print(f"Cannot process {file_path} - Windows COM not available")
        return
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ('.xlsx', '.xls'):
            excel = win32.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            
            try:
                wb = excel.Workbooks.Open(os.path.abspath(file_path))
                sheet = wb.Sheets(1)  # First sheet
                
                data = sheet.Cells(1, 1).Value
                
                if data:
                    summary = local_llm(f"Summarize this spreadsheet data: {data}")
                    
                    sheet.Cells(1, 2).Value = f"AI Summary: {summary}"
                    
                    wb.Save()
                    wb.Close()
                    
                    if TOAST:
                        TOAST.show_toast(
                            "Omega AI",
                            f"Processed {os.path.basename(file_path)}",
                            duration=4
                        )
            except Exception as e:
                print(f"Error processing Excel file: {e}")
            finally:
                excel.Quit()
        
        elif file_ext in ('.docx', '.doc'):
            word = win32.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            
            try:
                doc = word.Documents.Open(os.path.abspath(file_path))
                
                if doc.Paragraphs.Count > 0:
                    text = doc.Paragraphs(1).Range.Text
                    
                    summary = local_llm(f"Summarize this document: {text[:1000]}")
                    
                    doc.Content.InsertAfter(f"\n\nAI Summary: {summary}")
                    
                    doc.Save()
                    doc.Close()
                    
                    if TOAST:
                        TOAST.show_toast(
                            "Omega AI",
                            f"Processed {os.path.basename(file_path)}",
                            duration=4
                        )
            except Exception as e:
                print(f"Error processing Word file: {e}")
            finally:
                word.Quit()
    
    except Exception as e:
        print(f"Office automation error: {e}")


def on_hotkey():
    """Handle global hotkey press"""
    if TOAST:
        TOAST.show_toast("Omega AI", "Listening...", duration=2)
    
    print("\n[Omega AI] Hotkey pressed - enter your question:")
    user_input = input("You: ")
    
    if not user_input.strip():
        return
    
    response = local_llm(f"Answer concisely: {user_input}")
    
    print(f"\nAI: {response}\n")
    
    if TOAST:
        display_text = response[:100] + "..." if len(response) > 100 else response
        TOAST.show_toast("Omega AI", display_text, duration=6)


def monitor_clipboard():
    """Monitor clipboard for changes and process with AI"""
    global last_clipboard
    
    if not WINDOWS_AVAILABLE:
        return
    
    while running:
        try:
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData()
            except (TypeError, UnicodeDecodeError, OSError) as e:
                data = None
            win32clipboard.CloseClipboard()
            
            if data != last_clipboard and isinstance(data, str) and len(data) > 10:
                last_clipboard = data
                
                insight = local_llm(f"Quick insight on this copied text: {data[:500]}")
                
                if TOAST:
                    display_text = insight[:150] + "..." if len(insight) > 150 else insight
                    TOAST.show_toast("Omega AI Insight", display_text, duration=5)
                
                print(f"\n[Clipboard Insight] {insight[:200]}\n")
        
        except Exception:
            pass
        
        time.sleep(3)  # Check every 3 seconds


class AIFileHandler(FileSystemEventHandler):
    """File system event handler for automatic Office file processing"""
    
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory:
            file_path = event.src_path
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ('.xlsx', '.xls', '.docx', '.doc'):
                time.sleep(1)
                office_automate(file_path)


def setup_hotkey():
    """Setup global hotkey"""
    if not KEYBOARD_AVAILABLE:
        print("Warning: keyboard module not available - hotkey disabled")
        return
    
    try:
        keyboard.add_hotkey(HOTKEY, on_hotkey)
        print(f"Global hotkey registered: {HOTKEY}")
    except Exception as e:
        print(f"Error setting up hotkey: {e}")


def setup_clipboard_monitor():
    """Setup clipboard monitoring thread"""
    global clipboard_thread
    
    if not WINDOWS_AVAILABLE:
        print("Warning: Windows COM not available - clipboard monitoring disabled")
        return
    
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()
    print("Clipboard monitoring started")


def setup_file_watcher():
    """Setup file system watcher"""
    global file_observer
    
    if not WATCHDOG_AVAILABLE:
        print("Warning: watchdog not available - file watching disabled")
        return
    
    if not os.path.exists(WATCH_FOLDER):
        print(f"Warning: Watch folder does not exist: {WATCH_FOLDER}")
        return
    
    try:
        observer = Observer()
        observer.schedule(AIFileHandler(), path=WATCH_FOLDER, recursive=False)
        observer.start()
        file_observer = observer
        print(f"File watching started on: {WATCH_FOLDER}")
    except Exception as e:
        print(f"Error setting up file watcher: {e}")


def cleanup():
    """Cleanup resources"""
    global running, file_observer
    
    running = False
    
    if file_observer:
        file_observer.stop()
        file_observer.join()
    
    if KEYBOARD_AVAILABLE:
        keyboard.unhook_all()
    
    print("\nOmega AI Core stopped")


def main():
    """Main entry point"""
    print("=" * 80)
    print(" " * 25 + "OMEGA AI CORE")
    print("=" * 80)
    print()
    print(f"Local Model: {LOCAL_MODEL}")
    print(f"Watch Folder: {WATCH_FOLDER}")
    print(f"Global Hotkey: {HOTKEY}")
    print()
    print("Starting Omega AI Core...")
    print("(Press Ctrl+C to stop)")
    print()
    
    setup_hotkey()
    setup_clipboard_monitor()
    setup_file_watcher()
    
    print()
    print("Omega AI Core is running in the background.")
    print(f"Press {HOTKEY} to activate, or watch for clipboard/file changes.")
    print()
    
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping Omega AI Core...")
    finally:
        cleanup()


if __name__ == '__main__':
    main()
