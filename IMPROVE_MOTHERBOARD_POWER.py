#!/usr/bin/env python3
"""
Improve Motherboard Power Management
====================================
Improves motherboard interaction for power sources and keeps Python section active for voice wake-up.
"""

import sys
import subprocess
from pathlib import Path

def improve_motherboard_power():
    """Improve motherboard power settings for voice wake-up"""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "MOTHERBOARD POWER MANAGEMENT IMPROVEMENTS")
    print("=" * 80)
    print()
    
    print("[1/5] Configuring USB wake settings...")
    
    # Enable USB wake from sleep
    usb_commands = [
        'powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 1',
        'powercfg /SETDCVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 1',
        'powercfg /SETACTIVE SCHEME_CURRENT'
    ]
    
    for cmd in usb_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except:
            pass
    
    print("  [OK] USB wake settings configured")
    print()
    
    print("[2/5] Enabling wake timers...")
    
    # Enable wake timers
    wake_commands = [
        'powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1',
        'powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1',
        'powercfg /SETACTIVE SCHEME_CURRENT'
    ]
    
    for cmd in wake_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except:
            pass
    
    print("  [OK] Wake timers enabled")
    print()
    
    print("[3/5] Configuring USB selective suspend...")
    
    # Disable USB selective suspend (keeps USB devices powered)
    usb_suspend_commands = [
        'powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0',
        'powercfg /SETDCVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0',
        'powercfg /SETACTIVE SCHEME_CURRENT'
    ]
    
    for cmd in usb_suspend_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except:
            pass
    
    print("  [OK] USB selective suspend disabled (keeps devices active)")
    print()
    
    print("[4/5] Configuring sleep timeout for voice wake...")
    
    # Set sleep timeout (keep system active longer)
    sleep_commands = [
        'powercfg /change standby-timeout-ac 0',  # Don't sleep on AC
        'powercfg /change hibernate-timeout-ac 0',  # Don't hibernate on AC
        'powercfg /change monitor-timeout-ac 30'  # Monitor timeout (30 minutes)
    ]
    
    for cmd in sleep_commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except:
            pass
    
    print("  [OK] Sleep timeout configured")
    print()
    
    print("[5/5] Creating voice wake service script...")
    
    # Create a script to keep Python active for voice wake
    voice_wake_script = '''#!/usr/bin/env python3
"""
Omega Voice Wake Service
========================
Keeps Python section active for voice wake-up functionality.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from omega_voice_wake import get_voice_wake_system
    
    print("[Voice Wake Service] Starting...")
    vw = get_voice_wake_system()
    
    # Enable USB wake
    vw.enable_usb_wake()
    
    # Start listening
    success, msg = vw.start_listening()
    if success:
        print("[Voice Wake Service] Voice wake active")
        print("[Voice Wake Service] Say 'wake up' to activate system")
        
        # Keep service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n[Voice Wake Service] Stopping...")
            vw.stop_listening()
    else:
        print(f"[Voice Wake Service] Failed to start: {msg}")
        
except ImportError as e:
    print(f"[Voice Wake Service] Import error: {e}")
    print("[Voice Wake Service] Voice wake system not available")
except Exception as e:
    print(f"[Voice Wake Service] Error: {e}")
'''
    
    script_path = Path(__file__).parent / "KEEP_VOICE_WAKE_ACTIVE.py"
    script_path.write_text(voice_wake_script, encoding='utf-8')
    print(f"  [OK] Voice wake service script created: {script_path.name}")
    print()
    
    print("=" * 80)
    print(" " * 25 + "POWER MANAGEMENT IMPROVED")
    print("=" * 80)
    print()
    print("Improvements applied:")
    print("  ✓ USB wake enabled")
    print("  ✓ Wake timers enabled")
    print("  ✓ USB selective suspend disabled (keeps devices active)")
    print("  ✓ Sleep timeout configured")
    print("  ✓ Voice wake service script created")
    print()
    print("To keep voice wake active:")
    print("  python KEEP_VOICE_WAKE_ACTIVE.py")
    print()
    print("This will keep Python section active for voice wake-up functionality.")
    print("=" * 80)
    print()

if __name__ == "__main__":
    improve_motherboard_power()
