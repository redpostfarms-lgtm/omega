#!/usr/bin/env python3
"""
Real Control Panel Display Fix
================================
Actually tests and fixes the control panel display issue.
Uses actual testing and fix application.
"""

import sys
import os
from pathlib import Path
import subprocess
import time

def test_display():
    """Test if window displays"""
    print("\n[Test] Testing control panel display...")
    
    try:
        import matplotlib
        matplotlib.use('TkAgg', force=True)
        import matplotlib.pyplot as plt
        
        # Test basic window
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5, 'Test Window', ha='center', va='center')
        ax.set_title('Test')
        
        plt.ion()
        plt.show(block=False)
        plt.pause(0.2)  # Give time to display
        plt.close(fig)
        
        print("[Test] Basic window test: PASSED")
        return True
    except Exception as e:
        print(f"[Test] Basic window test: FAILED - {e}")
        return False

def test_control_panel():
    """Test control panel display"""
    print("\n[Test] Testing control panel...")
    
    try:
        base_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(base_dir))
        
        from omega_control_panel import ControlPanel
        import matplotlib.pyplot as plt
        
        panel = ControlPanel()
        print("[Test] Control panel created")
        
        # Try to create GUI
        panel.running = True
        panel._create_gui_panel()
        
        if panel.fig:
            print("[Test] GUI panel created")
            print("[Test] Window should be visible now")
            
            # Show window with block=True to ensure visibility
            print("[Test] Showing window (blocking mode)...")
            plt.show(block=True)  # This will block but window will show
            
            panel.stop()
            return True
        else:
            print("[Test] GUI panel not created")
            return False
            
    except Exception as e:
        print(f"[Test] Control panel test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_launcher():
    """Fix the launcher to use block=True"""
    print("\n[Fix] Fixing launcher...")
    
    launcher_file = Path(__file__).parent / "OMEGA_UI_LAUNCHER.py"
    
    if not launcher_file.exists():
        print("[Fix] Launcher file not found")
        return False
    
    # Read current launcher
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if "plt.show(block=True)" in content:
        print("[Fix] Launcher already uses block=True")
        return True
    
    # Fix: Replace panel.run() with direct GUI creation
    if "panel.run()" in content:
        new_content = content.replace(
            "        panel = ControlPanel()\n        panel.run()",
            '''        panel = ControlPanel()
        import matplotlib.pyplot as plt
        
        print("[OK] Control Panel initialized")
        print("[OK] Creating GUI window...")
        print()
        
        # Create GUI and show with block=True to ensure visibility
        panel.running = True
        panel._create_gui_panel()
        
        print("[OK] GUI window created")
        print("[OK] Window should be visible now")
        print()
        print("Press Ctrl+C to exit")
        print()
        
        # Show window (blocking to ensure it displays)
        plt.show(block=True)'''
        )
        
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("[Fix] Launcher fixed to use block=True")
        return True
    
    print("[Fix] Launcher structure not recognized")
    return False

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "REAL CONTROL PANEL DISPLAY FIX")
    print("=" * 80)
    print()
    
    # Test 1: Basic display
    if not test_display():
        print("\n[ERROR] Basic display test failed. Matplotlib may not be working.")
        return False
    
    # Fix launcher
    fix_launcher()
    
    # Test 2: Control panel
    print("\n[Test] Testing control panel with fix...")
    print("[Test] This will open a window - close it to continue")
    time.sleep(2)
    
    if test_control_panel():
        print("\n[SUCCESS] Control panel display test: PASSED")
        return True
    else:
        print("\n[FAILED] Control panel display test: FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
