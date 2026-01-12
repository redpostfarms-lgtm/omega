#!/usr/bin/env python3
"""
Simple Diagnostic - KISS Principle
==================================
Step by step, simple tests to find the problem
"""

import sys
from pathlib import Path

def test_1_basic_matplotlib():
    """Test 1: Can matplotlib create a basic window?"""
    print("TEST 1: Basic Matplotlib Window")
    print("-" * 60)
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'TEST WINDOW\nIf you see this, matplotlib works!', 
                ha='center', va='center', fontsize=16)
        ax.set_title('Test Window')
        
        print("✓ Matplotlib imported")
        print("✓ Window created")
        print("Showing window (block=True)...")
        print("Close the window to continue...")
        
        plt.show(block=True)
        print("✓ Window closed successfully")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_control_panel_import():
    """Test 2: Can we import ControlPanel?"""
    print("\nTEST 2: Import ControlPanel")
    print("-" * 60)
    try:
        base_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(base_dir))
        
        from omega_control_panel import ControlPanel
        print("✓ ControlPanel imported")
        
        panel = ControlPanel()
        print("✓ ControlPanel instance created")
        print(f"  running = {panel.running}")
        print(f"  has _create_gui_panel = {hasattr(panel, '_create_gui_panel')}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_create_gui_panel():
    """Test 3: Can we create the GUI panel?"""
    print("\nTEST 3: Create GUI Panel")
    print("-" * 60)
    try:
        base_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(base_dir))
        
        from omega_control_panel import ControlPanel
        import matplotlib.pyplot as plt
        
        panel = ControlPanel()
        panel.running = True
        
        print("Calling _create_gui_panel()...")
        panel._create_gui_panel()
        print("✓ GUI panel created")
        print(f"  has fig = {hasattr(panel, 'fig') and panel.fig is not None}")
        print(f"  has ani = {hasattr(panel, 'ani') and panel.ani is not None}")
        
        if hasattr(panel, 'fig') and panel.fig is not None:
            print("Showing window (block=True)...")
            print("Close the window to continue...")
            plt.show(block=True)
            print("✓ Window closed successfully")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_run_method():
    """Test 4: Does run() method work?"""
    print("\nTEST 4: Run Method")
    print("-" * 60)
    print("This test will call panel.run()")
    print("The window should appear and stay open")
    print("Close the window to continue...")
    print()
    
    try:
        base_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(base_dir))
        
        from omega_control_panel import ControlPanel
        
        panel = ControlPanel()
        print("Calling panel.run()...")
        print("=" * 60)
        panel.run()
        print("=" * 60)
        print("✓ panel.run() completed")
        return True
    except KeyboardInterrupt:
        print("\n✓ Interrupted (expected)")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_launcher():
    """Test 5: Does the launcher work?"""
    print("\nTEST 5: Launcher")
    print("-" * 60)
    print("This test will run OMEGA_UI_LAUNCHER.py")
    print("The window should appear and stay open")
    print("Close the window to continue...")
    print()
    
    try:
        base_dir = Path(__file__).parent.absolute()
        launcher_file = base_dir / "OMEGA_UI_LAUNCHER.py"
        
        if not launcher_file.exists():
            print(f"✗ Launcher file not found: {launcher_file}")
            return False
        
        print(f"Running: {launcher_file}")
        print("=" * 60)
        
        import subprocess
        process = subprocess.run(
            [sys.executable, str(launcher_file)],
            cwd=str(base_dir)
        )
        
        print("=" * 60)
        print(f"✓ Launcher completed with code: {process.returncode}")
        return process.returncode == 0
    except KeyboardInterrupt:
        print("\n✓ Interrupted (expected)")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests step by step"""
    print("=" * 60)
    print(" " * 15 + "SIMPLE DIAGNOSTIC - KISS PRINCIPLE")
    print("=" * 60)
    print()
    print("Testing step by step to find the problem...")
    print()
    
    tests = [
        ("Basic Matplotlib", test_1_basic_matplotlib),
        ("Import ControlPanel", test_2_control_panel_import),
        ("Create GUI Panel", test_3_create_gui_panel),
        ("Run Method", test_4_run_method),
        ("Launcher", test_5_launcher),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            if not result:
                print(f"\n✗ Test '{name}' FAILED - stopping here")
                break
        except KeyboardInterrupt:
            print(f"\n✓ Test '{name}' interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Test '{name}' CRASHED: {e}")
            results.append((name, False))
            break
    
    print("\n" + "=" * 60)
    print(" " * 20 + "RESULTS SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    if all(result for _, result in results):
        print("All tests passed!")
    else:
        print("Some tests failed - this identifies where the problem is")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
