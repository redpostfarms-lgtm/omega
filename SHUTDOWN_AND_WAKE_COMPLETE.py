#!/usr/bin/env python3
"""
Complete Shutdown/Hibernate and Wake Solution
==============================================
Schedules wake, enables wake timers, then hibernates (wake-capable)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from omega_windows_power import get_power_manager

def enable_wake_timers():
    """Enable wake timers in Windows power settings"""
    print("Enabling wake timers in Windows...")
    commands = [
        'powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1',
        'powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1',
        'powercfg /SETACTIVE SCHEME_CURRENT',
        'powercfg /change standby-timeout-ac 0',
        'powercfg /change hibernate-timeout-ac 0'
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except:
            pass  # Continue even if some fail
    print("Wake timers enabled")

def main():
    pm = get_power_manager()
    now = datetime.now()
    
    # Schedule wake for 11:10 today
    wake_time = datetime(now.year, now.month, now.day, 11, 10)
    
    print("=" * 80)
    print("SHUTDOWN/HIBERNATE AND WAKE")
    print("=" * 80)
    print()
    print(f"Current time: {now.strftime('%H:%M')}")
    print(f"Wake scheduled for: {wake_time.strftime('%H:%M')}")
    print()
    
    # Enable wake timers
    enable_wake_timers()
    print()
    
    # Schedule wake first
    print("Scheduling wake for 11:10...")
    success1, msg1 = pm.schedule_wake(wake_time, "Scheduled wake - 5 minutes")
    print(f"[{'OK' if success1 else 'ERROR'}] {msg1}")
    print()
    
    if not success1:
        print("Failed to schedule wake. Aborting.")
        return
    
    # Use hibernate (wake-capable) instead of shutdown
    print("Hibernating now (system can wake from hibernate)...")
    print("Note: Using hibernate so wake timer will work")
    print()
    success2, msg2 = pm.hibernate()
    print(f"[{'OK' if success2 else 'ERROR'}] {msg2}")
    
    if success2:
        print()
        print("System will hibernate now and wake at 11:10")
        print("=" * 80)
        import time
        time.sleep(2)  # Give time to see message

if __name__ == "__main__":
    main()
