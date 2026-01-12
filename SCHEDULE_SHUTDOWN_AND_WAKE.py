#!/usr/bin/env python3
"""
Schedule Shutdown and Wake
==========================
Shutdown now and schedule wake for 11:10 (5 minutes from 11:05)
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from omega_windows_power import get_power_manager

def main():
    pm = get_power_manager()
    now = datetime.now()
    
    # Schedule wake for 11:10 today
    wake_time = datetime(now.year, now.month, now.day, 11, 10)
    
    print("=" * 80)
    print("SCHEDULING SHUTDOWN AND WAKE")
    print("=" * 80)
    print()
    print(f"Current time: {now.strftime('%H:%M')}")
    print(f"Wake scheduled for: {wake_time.strftime('%H:%M')}")
    print()
    
    # Schedule wake first
    print("Scheduling wake for 11:10...")
    success1, msg1 = pm.schedule_wake(wake_time, "Scheduled wake - 5 minutes")
    print(f"[{'OK' if success1 else 'ERROR'}] {msg1}")
    print()
    
    if not success1:
        print("Failed to schedule wake. Aborting shutdown.")
        return
    
    # Use hibernate instead of shutdown (hibernate can wake, shutdown cannot)
    print("Hibernating now (wake-capable)...")
    print("Note: Using hibernate instead of shutdown so wake timer will work")
    success2, msg2 = pm.hibernate()
    print(f"[{'OK' if success2 else 'ERROR'}] {msg2}")
    
    if success2:
        print()
        print("System will hibernate now and wake at 11:10")
        print("=" * 80)

if __name__ == "__main__":
    main()
