#!/usr/bin/env python3
"""
Test Launcher Now
================
Run this to test the launcher and see what happens
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def test_launcher():
    """Test the launcher directly"""
    print("=" * 80)
    print(" " * 25 + "TESTING LAUNCHER NOW")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent.absolute()
    launcher_file = base_dir / "OMEGA_UI_LAUNCHER.py"
    
    print(f"Launcher file: {launcher_file}")
    print(f"Exists: {launcher_file.exists()}")
    print()
    
    print("Starting launcher in 2 seconds...")
    print("Watch for:")
    print("  1. Console output")
    print("  2. Window appearing")
    print("  3. Process in Task Manager")
    print()
    
    time.sleep(2)
    
    print("Launching now...")
    print("=" * 80)
    print()
    
    try:
        # Run the launcher
        process = subprocess.Popen(
            [sys.executable, str(launcher_file)],
            cwd=str(base_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Process started: PID {process.pid}")
        print(f"Process is running: {process.poll() is None}")
        print()
        print("Waiting 10 seconds to see if window appears...")
        print("(Press Ctrl+C to interrupt)")
        print()
        
        try:
            # Wait a bit to see if process stays alive
            time.sleep(10)
            
            # Check if still running
            if process.poll() is None:
                print(f"Process is still running (PID {process.pid})")
                print("Window should be visible now")
                print()
                print("Process will continue running until window is closed")
                print("Press Enter to kill process...")
                input()
                process.terminate()
                process.wait(timeout=5)
                print("Process terminated")
            else:
                return_code = process.poll()
                print(f"Process exited with code: {return_code}")
                stdout, stderr = process.communicate()
                if stdout:
                    print("STDOUT:")
                    print(stdout)
                if stderr:
                    print("STDERR:")
                    print(stderr)
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted - terminating process...")
            process.terminate()
            process.wait(timeout=5)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_launcher()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
