"""
Omega Quick Test - Test all components
"""

import subprocess
import sys
import time

def run_test(name, command):
    """Run a test command"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ {name} - PASSED")
            if result.stdout:
                print(result.stdout[:500])
        else:
            print(f"✗ {name} - FAILED")
            if result.stderr:
                print(result.stderr[:500])
        
        return result.returncode == 0
    except Exception as e:
        print(f"✗ {name} - ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("OMEGA SYSTEM - QUICK TEST SUITE")
    print("="*60)
    
    tests = [
        ("Python Environment", f"{sys.executable} --version"),
        ("Import Flask", f"{sys.executable} -c \"import flask; print('Flask', flask.__version__)\""),
        ("Import pyttsx3", f"{sys.executable} -c \"import pyttsx3; print('pyttsx3 OK')\""),
        ("Control Panel Import", f"{sys.executable} -c \"from omega_control_panel_web import OmegaControlPanelWeb; print('Control Panel OK')\""),
        ("Voice System Files", "powershell -Command \"Test-Path speak_omega_voice.py\""),
        ("Voice Sample Files", "powershell -Command \"Test-Path clip_0001.wav\""),
    ]
    
    results = []
    for name, cmd in tests:
        results.append((name, run_test(name, cmd)))
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems operational!")
        print("\nTo start Omega:")
        print("  1. Run: START_OMEGA_COMPLETE.bat")
        print("  2. Open: http://localhost:5000")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    print()

if __name__ == "__main__":
    main()
