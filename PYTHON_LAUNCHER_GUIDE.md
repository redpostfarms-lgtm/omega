# Python Launcher & Shebang Guide for Omega

**Date:** January 2026  
**Developer:** Nick (Seattle)  
**Status:** Quick Reference Guide  
**Integration:** Works with all Omega Python scripts

---

## Overview

The Python Launcher for Windows (`py.exe` / `pyw.exe`) is essential for managing multiple Python versions on Windows. This guide covers how to use it effectively with Omega scripts.

---

## Python Launcher Basics

### What is `py.exe`?

The Python Launcher (also called `py.exe` or `py`) is a utility introduced with Python 3.3 (2012) that automatically finds and runs the appropriate Python interpreter based on version requirements.

**Key Benefit:** Solves the problem of running scripts with specific Python versions without managing PATH or typing full paths.

### Main Executables

| Executable | Purpose | Console Output |
| ------------ | --------- | ---------------- |
| `py.exe` | Console version (uses terminal window) | Yes |
| `pyw.exe` | GUI/no-console version (no terminal window) | No |

**Location:** Usually installed in `C:\Windows\` (system-wide) when you install Python from python.org.

---

## Python Launcher vs python.exe

| Feature / Aspect | `python.exe` / `pythonw.exe` | `py.exe` / `pyw.exe` (Launcher) |
| ------------------ | ------------------------------ | ---------------------------------- |
| **Location** | Inside specific Python install folder (e.g. `C:\Python312\python.exe`) | Usually `C:\Windows\py.exe` (always in PATH) |
| **Multiple versions support** | You must specify full path or manage PATH carefully | Automatically selects correct version |
| **Default behavior** | Always runs the exact Python install it's part of | Runs the default (usually latest) or specified version |
| **Shebang (#!) support** | Not used on Windows | Fully supports Unix-style shebangs |
| **Command-line version switch** | Not possible | Yes! e.g. `py -3.11`, `py -2`, `py -3.12-32` |
| **Best for** | Single-version systems, venv activation | Multi-version systems, scripts with specific requirements |

---

## Most Common Commands

### Interactive REPL

```bash
py                  # Run the default (usually latest) Python → opens REPL
py -3               # Latest Python 3.x
py -2               # Latest Python 2.x (if still installed)
py -3.11            # Specific version 3.11 (latest patch)
py -3.12-32         # 32-bit version of 3.12 (if both 32 & 64-bit exist)
```text

### Running Scripts

```bash
py script.py              # Run script using default Python
py -3.10 script.py        # Run with specific version
py -3.11 omega_automation_orchestrator.py
```text

### Package Management

```bash
py -m pip install ...     # Run pip from the chosen Python
py -3.11 -m pip install requests
```text

### List Installed Versions

```bash
py -0p                   # List all detected Python installs (very useful!)
py -0                    # List versions only (no paths)
```text

---

## Shebang Lines (#!) - The Killer Feature

The launcher reads the first line of your script (if it starts with `#!`) and uses it to decide which Python to run — just like on Linux/macOS!

**Important:** The shebang must be the very first line of your script (no blank lines or other comments before it).

### Recommended / Most Portable (Best for Almost Everything)

```python
#!/usr/bin/env python3
```text

**Why it's best:**
- Uses `env` to search your PATH for the `python3` command
- Works even if Python is installed in non-standard locations
- Works great with virtual environments (venv, poetry, pipenv, etc.)
- Fully compatible with Windows Python Launcher (`py.exe`)
- Avoids breakage when `python` points to Python 2 on legacy systems

**This is the modern standard (2026 best practice) for maximum portability.**

### Version-Specific Variations (Still Very Portable)

```python
#!/usr/bin/env python3.12      # Latest patch of Python 3.12
#!/usr/bin/env python3.11-32   # 32-bit Python 3.11 (if you have both 32/64-bit installs)
#!/usr/bin/env python          # Latest Python (major version) — avoid unless you really need 2+3 compatibility
```text

### Hardcoded Absolute Path (Less Portable — Avoid Unless Necessary)

```python
#!/usr/bin/python3
#!/usr/local/bin/python3.10
#!/opt/homebrew/bin/python3     # Common on macOS with Homebrew
```text

**Only use if you know the exact location and want to force a specific install.**
- Breaks easily when moving the script to another machine or user

### Windows-Friendly / Legacy Style (Rarely Needed Today)

```python
#!python3
#!python
```text

On Windows, shebangs are ignored unless you run via `py.exe` / Python launcher. These still work via the launcher as "virtual" shebangs, but `#!/usr/bin/env python3` is preferred because it's cross-platform.

### With Extra Arguments (Advanced / Useful Sometimes)

```python
#!/usr/bin/env python3 -u     # Unbuffered output (good for real-time logging)
#!/usr/bin/env python3 -i     # Interactive mode after script finishes (great for debugging)
#!/usr/bin/python3 -O         # Optimize mode (removes assert statements)
```text

---

## Quick Summary Table

| Shebang Line | Portability | Best For | Windows Support (via py/launcher) |
| -------------- | ------------- | ---------- | ----------------------------------- |
| `#!/usr/bin/env python3` | ★★★★★ | Modern default – everything! | Excellent |
| `#!/usr/bin/env python3.12` | ★★★★ | Force specific minor version | Excellent |
| `#!/usr/bin/python3` | ★★★ | Known fixed system install | Good (as virtual) |
| `#!/usr/bin/env python` | ★★ | Legacy/2+3 compat (avoid today) | Good |
| `#!python3` | ★★ | Windows-only shorthand | Excellent |

---

## Best Practice for Omega Scripts (2026)

**Start every executable Python script with:**

```python
#!/usr/bin/env python3
```text

**Then make the file executable (on Unix-like systems):**
```bash
chmod +x script.py
```text

**And run it directly:**
```bash
./script.py           # On Linux/macOS
py script.py          # On Windows (or double-click if associated)
```text

**It just works everywhere modern Python is installed!**

---

## Finding Your Python Launcher

### Check if Python Launcher is Installed

```bash
where py              # Windows: shows path to py.exe
which py              # Linux/macOS: shows path to py (if available)
```text

### Common Locations

- **All-users install:** `C:\Windows\py.exe` (and `pyw.exe`)
- **Per-user install:** `%LOCALAPPDATA%\Programs\Python\Launcher\py.exe`

### Verify Installation

```bash
py --version          # Shows Python Launcher version
py -0p                # Lists all detected Python installs
```text

---

## Using with Omega Automation

### Task Scheduler Integration

When setting up Omega Automation via Task Scheduler, you can use either approach:

**Option 1: Use `py.exe` directly**
```text
Program/script: C:\Windows\py.exe
Add arguments: -3.11 "D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"
```text

**Option 2: Use full Python path**
```text
Program/script: C:\Python311\python.exe
Add arguments: -u "D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"
```text

**Option 1 is preferred** because it automatically selects the correct Python version based on the shebang in your script.

### Script with Shebang

If your script starts with `#!/usr/bin/env python3`, the launcher will automatically:
1. Read the shebang
2. Find the appropriate Python version
3. Run the script with that version

**No version specification needed in Task Scheduler!**

---

## Integration with Virtual Environments

### Activating Virtual Environment

The shebang `#!/usr/bin/env python3` respects activated virtual environments:

```bash
# Activate venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/macOS

# Script with shebang will use venv Python
py script.py              # Uses venv Python if activated
```text

### Using Specific Python Version in venv

```python
#!/usr/bin/env python3.11    # Forces Python 3.11 even if venv has different version
```text

---

## Troubleshooting

### Script Not Running with Correct Python Version

**Problem:** Script runs with wrong Python version

**Solution:**
1. Check shebang line (must be first line, no blank lines before)
2. Use `py -0p` to see available Python versions
3. Specify version explicitly: `py -3.11 script.py`
4. Check if Python Launcher is installed: `where py`

### Shebang Not Working on Windows

**Problem:** Double-clicking script doesn't use shebang

**Solution:**
1. Ensure Python Launcher is installed (comes with Python installer)
2. Associate `.py` files with `py.exe` (not `python.exe`)
3. Or run via command line: `py script.py`

### Script Works on Linux/macOS but Not Windows

**Problem:** `#!/usr/bin/env python3` works on Unix but not Windows

**Solution:**
1. This is normal — Windows doesn't natively support shebangs
2. Use Python Launcher: `py script.py` instead of `python script.py`
3. Or associate `.py` files with `py.exe` in Windows file associations

---

## Examples for Omega Scripts

### Example 1: Standard Omega Script

```python
#!/usr/bin/env python3
"""
Omega Automation Script
Works on Windows (via py.exe), Linux, and macOS
"""
import sys
# ... rest of script
```text

### Example 2: Script Requiring Specific Python Version

```python
#!/usr/bin/env python3.11
"""
Omega Script requiring Python 3.11
"""
import sys
assert sys.version_info >= (3, 11), "Python 3.11+ required"
# ... rest of script
```text

### Example 3: Script with Unbuffered Output (Logging)

```python
#!/usr/bin/env python3 -u
"""
Omega Script with real-time logging
-u flag ensures unbuffered output
"""
import sys
import logging
# ... rest of script
```text

### Example 4: Windows Task Scheduler Script

```python
#!/usr/bin/env python3
"""
Omega Automation Orchestrator
Runs silently with elevated privileges via Task Scheduler
"""
import sys
import logging
# ... rest of script
```text

**Task Scheduler Configuration:**
- Program/script: `C:\Windows\py.exe`
- Add arguments: `"D:\RPF_BRAIN\The Gatekeeper\omega_automation_orchestrator.py"`

The launcher reads the shebang and uses the correct Python version automatically!

---

## Quick Reference Cheat Sheet

```bash
# List all Python versions
py -0p

# Run script with default Python
py script.py

# Run script with specific version
py -3.11 script.py

# Run module
py -m pip install requests
py -m omega_automation_orchestrator

# Check launcher version
py --version

# Find launcher location
where py
```text

---

## Related Documentation

- [Omega Windows Automation Guide](./OMEGA_WINDOWS_AUTOMATION_GUIDE.md)
- Python Official Docs: "Using Python on Windows"
- PEP 397: Python launcher for Windows

---

## Status

✅ **Quick Reference Guide** — Essential Python Launcher knowledge  
✅ **Integrated** — Works with all Omega scripts  
✅ **Best Practices** — 2026 standards for shebang lines

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Status:** Quick Reference Guide
