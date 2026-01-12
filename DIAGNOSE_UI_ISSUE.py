#!/usr/bin/env python3
"""
Diagnostic Script for UI Window Closing Issue
==============================================
This script will diagnose why the UI window closes when launched from shortcut.
"""

import sys
import traceback
from pathlib import Path

def diagnose_ui_issue():
    """Diagnose the UI window closing issue"""
    print("=" * 80)
    print(" " * 20 + "UI WINDOW CLOSING DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Step 1: Check matplotlib backend
    print("STEP 1: Checking Matplotlib Backend...")
    try:
        import matplotlib
        print(f"  Matplotlib version: {matplotlib.__version__}")
        backend_before = matplotlib.get_backend()
        print(f"  Current backend: {backend_before}")
        
        # Try to set TkAgg
        try:
            matplotlib.use('TkAgg', force=True)
            backend_after = matplotlib.get_backend()
            print(f"  Backend after force TkAgg: {backend_after}")
        except Exception as e:
            print(f"  [WARNING] Failed to set TkAgg: {e}")
    except Exception as e:
        print(f"  [ERROR] Failed to import matplotlib: {e}")
        return False
    
    print()
    
    # Step 2: Check tkinter availability
    print("STEP 2: Checking Tkinter Availability...")
    try:
        import tkinter
        print("  [OK] tkinter is available")
        try:
            root = tkinter.Tk()
            root.withdraw()  # Hide the test window
            root.destroy()
            print("  [OK] tkinter window creation test passed")
        except Exception as e:
            print(f"  [ERROR] tkinter window test failed: {e}")
            return False
    except ImportError:
        print("  [ERROR] tkinter is not available")
        return False
    
    print()
    
    # Step 3: Test basic matplotlib window
    print("STEP 3: Testing Basic Matplotlib Window...")
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Test Window\nShould Stay Open', 
                ha='center', va='center', fontsize=16)
        ax.set_title('Diagnostic Test Window')
        plt.ion()
        plt.show(block=False)
        plt.pause(0.1)
        print("  [OK] Basic matplotlib window created")
        print("  [INFO] Test window should be visible now")
        print("  [INFO] Closing test window in 3 seconds...")
        import time
        time.sleep(3)
        plt.close(fig)
        print("  [OK] Test window closed successfully")
    except Exception as e:
        print(f"  [ERROR] Basic matplotlib test failed: {e}")
        traceback.print_exc()
        return False
    
    print()
    
    # Step 4: Test control panel import
    print("STEP 4: Testing Control Panel Import...")
    try:
        base_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(base_dir))
        from omega_control_panel import ControlPanel
        print("  [OK] ControlPanel imported successfully")
        
        # Check if run method exists
        if hasattr(ControlPanel, 'run'):
            print("  [OK] ControlPanel.run() method exists")
        else:
            print("  [ERROR] ControlPanel.run() method not found")
            return False
            
        # Check if _create_gui_panel exists
        if hasattr(ControlPanel, '_create_gui_panel'):
            print("  [OK] ControlPanel._create_gui_panel() method exists")
        else:
            print("  [ERROR] ControlPanel._create_gui_panel() method not found")
            return False
    except Exception as e:
        print(f"  [ERROR] Failed to import ControlPanel: {e}")
        traceback.print_exc()
        return False
    
    print()
    
    # Step 5: Test creating control panel instance
    print("STEP 5: Testing Control Panel Instance Creation...")
    try:
        panel = ControlPanel()
        print("  [OK] ControlPanel instance created")
        
        # Check running attribute
        if hasattr(panel, 'running'):
            print(f"  [OK] panel.running attribute exists (value: {panel.running})")
        else:
            print("  [WARNING] panel.running attribute not found")
    except Exception as e:
        print(f"  [ERROR] Failed to create ControlPanel instance: {e}")
        traceback.print_exc()
        return False
    
    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()
    print("All basic checks passed. The issue may be in the run() method")
    print("or how the event loop is being handled.")
    print()
    print("Next steps:")
    print("  1. Check if run() method properly handles the event loop")
    print("  2. Check if FuncAnimation is keeping the window alive")
    print("  3. Test actual run() method with timeout")
    
    return True

if __name__ == "__main__":
    try:
        success = diagnose_ui_issue()
        if success:
            print("\n[OK] Diagnostic completed successfully")
            sys.exit(0)
        else:
            print("\n[ERROR] Diagnostic found issues")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Diagnostic failed: {e}")
        traceback.print_exc()
        sys.exit(1)
