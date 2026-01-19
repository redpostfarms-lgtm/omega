"""
Omega System Status Check
Quick diagnostic tool for all Omega components
"""

import os
import sys
import subprocess
from pathlib import Path

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_status(name, condition, details=""):
    """Check and display status"""
    status = "✓" if condition else "✗"
    color = GREEN if condition else RED
    print(f"{color}{status}{RESET} {name}")
    if details:
        print(f"  {details}")

def main():
    print(f"\n{CYAN}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}{'OMEGA SYSTEM STATUS':^60}{RESET}")
    print(f"{CYAN}{BOLD}{'='*60}{RESET}\n")
    
    print(f"{YELLOW}Python Environment:{RESET}")
    venv_path = Path(".venv311/Scripts/python.exe")
    check_status("Python 3.11 venv", venv_path.exists(), str(venv_path))
    
    print(f"\n{YELLOW}Core Components:{RESET}")
    files = [
        ("Control Panel Web", "omega_control_panel_web.py"),
        ("Control Panel Core", "omega_control_panel.py"),
        ("Omega Voice", "speak_omega_voice.py"),
        ("Voice API", "omega_voice_api.py"),
        ("Voice Samples", "clip_0001.wav")
    ]
    
    for name, filepath in files:
        check_status(name, os.path.exists(filepath), filepath)
    
    print(f"\n{YELLOW}Web Server:{RESET}")
    try:
        result = subprocess.run(
            ["powershell", "-Command", 
             "Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet"],
            capture_output=True,
            text=True,
            timeout=5
        )
        server_running = "True" in result.stdout
        check_status("Server on port 5000", server_running, 
                    "http://localhost:5000" if server_running else "Not running")
    except:
        check_status("Server on port 5000", False, "Unable to check")
    
    print(f"\n{YELLOW}Running Processes:{RESET}")
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-Process python* | Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True,
            text=True,
            timeout=5
        )
        count = result.stdout.strip()
        check_status(f"Python processes: {count}", True)
    except:
        check_status("Python processes", False, "Unable to check")
    
    print(f"\n{YELLOW}Dependencies:{RESET}")
    deps = ["flask", "pyttsx3", "psutil", "GPUtil"]
    for dep in deps:
        try:
            result = subprocess.run(
                [str(venv_path), "-m", "pip", "show", dep],
                capture_output=True,
                timeout=5
            )
            installed = result.returncode == 0
            check_status(dep, installed)
        except:
            check_status(dep, False, "Unable to check")
    
    print(f"\n{CYAN}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}{'Quick Actions':^60}{RESET}")
    print(f"{CYAN}{BOLD}{'='*60}{RESET}\n")
    
    print(f"  {GREEN}Start Omega:{RESET} START_OMEGA_COMPLETE.bat")
    print(f"  {GREEN}Open Web UI:{RESET} http://localhost:5000")
    print(f"  {GREEN}Mobile View:{RESET} http://localhost:5000/mobile")
    print(f"  {GREEN}Test Voice:{RESET} python speak_omega_voice.py")
    print(f"  {GREEN}Stop Server:{RESET} Ctrl+C in server terminal\n")
    
    print(f"{CYAN}{BOLD}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
