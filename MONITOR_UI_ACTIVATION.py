#!/usr/bin/env python3
"""
Monitor UI Activation Sequence
==============================
This script monitors the UI activation process and analyzes what happens.
"""

import sys
import os
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime

def find_python_processes():
    """Find all Python processes"""
    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                python_procs.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'create_time': proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return python_procs

def monitor_activation():
    """Monitor the UI activation sequence"""
    print("=" * 80)
    print(" " * 20 + "MONITORING UI ACTIVATION SEQUENCE")
    print("=" * 80)
    print()
    print(f"Monitoring started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check initial state
    print("STEP 1: Initial Process State")
    print("-" * 80)
    initial_procs = find_python_processes()
    print(f"Found {len(initial_procs)} Python processes initially")
    for proc in initial_procs:
        if 'OMEGA_UI_LAUNCHER' in proc['cmdline'] or 'omega_control_panel' in proc['cmdline']:
            print(f"  PID {proc['pid']}: {proc['name']} - {proc['cmdline'][:100]}")
    print()
    
    # Step 2: Wait for user to click shortcut (they'll tell us when)
    print("STEP 2: Waiting for shortcut activation...")
    print("(Click the Omega shortcut now)")
    print()
    
    # Monitor for 10 seconds after activation
    start_time = time.time()
    activation_detected = False
    launcher_process = None
    control_panel_process = None
    
    while time.time() - start_time < 15:  # Monitor for 15 seconds
        current_procs = find_python_processes()
        
        # Check for new processes
        for proc in current_procs:
            cmdline = proc['cmdline']
            if 'OMEGA_UI_LAUNCHER' in cmdline:
                if not activation_detected:
                    print(f"[ACTIVATION DETECTED] PID {proc['pid']} - {proc['name']}")
                    print(f"  Command: {cmdline[:150]}")
                    activation_detected = True
                    launcher_process = proc
                    start_time = time.time()  # Reset timer
                
        # Check if process is still running
        if launcher_process:
            try:
                proc = psutil.Process(launcher_process['pid'])
                if not proc.is_running():
                    print(f"\n[PROCESS EXITED] PID {launcher_process['pid']} has exited")
                    break
            except psutil.NoSuchProcess:
                print(f"\n[PROCESS TERMINATED] PID {launcher_process['pid']} no longer exists")
                break
        
        time.sleep(0.5)
    
    print()
    print("STEP 3: Final Process State")
    print("-" * 80)
    final_procs = find_python_processes()
    print(f"Found {len(final_procs)} Python processes")
    omega_procs = [p for p in final_procs if 'OMEGA' in p['cmdline'].upper() or 'omega' in p['cmdline'].lower()]
    if omega_procs:
        print("Omega-related processes:")
        for proc in omega_procs:
            print(f"  PID {proc['pid']}: {proc['name']}")
            print(f"    Command: {proc['cmdline'][:150]}")
    else:
        print("  No Omega processes found")
    
    print()
    print("=" * 80)
    print("MONITORING COMPLETE")
    print("=" * 80)

def analyze_code_flow():
    """Analyze the code activation sequence"""
    print("\n" + "=" * 80)
    print(" " * 20 + "CODE FLOW ANALYSIS")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent.absolute()
    launcher_file = base_dir / "OMEGA_UI_LAUNCHER.py"
    control_panel_file = base_dir / "omega_control_panel.py"
    
    print("ACTIVATION SEQUENCE:")
    print("-" * 80)
    print()
    print("1. User clicks Omega.lnk shortcut")
    print("   -> Launches: python.exe OMEGA_UI_LAUNCHER.py")
    print()
    
    if launcher_file.exists():
        print("2. OMEGA_UI_LAUNCHER.py executes:")
        with open(launcher_file, 'r') as f:
            lines = f.readlines()
            print("   Key steps:")
            for i, line in enumerate(lines, 1):
                if 'launch_omega_ui' in line or 'ControlPanel' in line or 'panel.run()' in line:
                    print(f"   Line {i}: {line.strip()[:70]}")
    print()
    
    if control_panel_file.exists():
        print("3. omega_control_panel.py - ControlPanel.run() executes:")
        with open(control_panel_file, 'r') as f:
            lines = f.readlines()
            print("   Key steps:")
            for i, line in enumerate(lines, 1):
                if 'def run(self)' in line or '_create_gui_panel' in line or 'plt.show' in line:
                    print(f"   Line {i}: {line.strip()[:70]}")
    print()
    
    print("EXPECTED BEHAVIOR:")
    print("-" * 80)
    print("1. Process starts and creates ControlPanel instance")
    print("2. run() method is called")
    print("3. _create_gui_panel() creates FuncAnimation")
    print("4. plt.show(block=True) is called - should block until window closed")
    print("5. Window should stay open and remain interactive")
    print()
    
    print("POTENTIAL ISSUES TO CHECK:")
    print("-" * 80)
    print("1. Does plt.show(block=True) actually block?")
    print("2. Does the window appear on screen?")
    print("3. Does the process stay alive?")
    print("4. Are there any exceptions being silently caught?")
    print("5. Is matplotlib backend correctly set?")
    print()

if __name__ == "__main__":
    try:
        analyze_code_flow()
        print("\nReady to monitor. Run this script while clicking the shortcut.")
        print("Or run: python MONITOR_UI_ACTIVATION.py --watch")
        print()
        
        if '--watch' in sys.argv:
            monitor_activation()
        else:
            print("To monitor activation, run with --watch flag:")
            print("  python MONITOR_UI_ACTIVATION.py --watch")
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted")
    except Exception as e:
        print(f"\n[ERROR] Monitoring failed: {e}")
        import traceback
        traceback.print_exc()
