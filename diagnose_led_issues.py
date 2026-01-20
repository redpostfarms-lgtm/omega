"""
🔍 LED Control Diagnostic & Resolution Finder
Analyzes why RED waves aren't working and provides solutions
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "=" * 70)
print("  🔍 LED CONTROL DIAGNOSTIC - Finding Resolution")
print("=" * 70 + "\n")

# Configuration
openrgb_path = Path(r"C:\Users\Drakalich\OpenRGB\OpenRGB Windows 64-bit\OpenRGB.exe")
issues_found = []
solutions = []

print("[1] ENVIRONMENT ANALYSIS")
print("-" * 70)

# Check 1: OpenRGB Installation
print("\n✓ Checking OpenRGB installation...")
if openrgb_path.exists():
    print(f"  ✓ Found: {openrgb_path}")
    print(f"  Size: {openrgb_path.stat().st_size:,} bytes")
else:
    print(f"  ✗ NOT FOUND: {openrgb_path}")
    issues_found.append("OpenRGB executable not found")
    solutions.append("Install OpenRGB to: C:\\Users\\Drakalich\\OpenRGB")

# Check 2: OpenRGB Process
print("\n✓ Checking if OpenRGB is running...")
try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-Process OpenRGB -ErrorAction SilentlyContinue | Select-Object Id, ProcessName",
        ],
        capture_output=True,
        text=True,
        timeout=3,
    )
    if "OpenRGB" in result.stdout:
        print("  ✓ OpenRGB process is running")
    else:
        print("  ✗ OpenRGB is NOT running")
        issues_found.append("OpenRGB process not running")
        solutions.append("Run: .\\START_OPENRGB_SERVER.ps1")
except Exception as e:
    print(f"  ⚠️ Could not check process: {e}")

# Check 3: OpenRGB Server Port
print("\n✓ Checking OpenRGB server port (6742)...")
try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-NetTCPConnection -LocalPort 6742 -State Listen -ErrorAction SilentlyContinue",
        ],
        capture_output=True,
        text=True,
        timeout=3,
    )
    if "6742" in result.stdout:
        print("  ✓ Server listening on port 6742")
    else:
        print("  ✗ No server on port 6742")
        issues_found.append("OpenRGB server not listening")
        solutions.append("Start OpenRGB with: --server flag")
except Exception as e:
    print(f"  ⚠️ Could not check port: {e}")

print("\n[2] HARDWARE DETECTION")
print("-" * 70)

# Check 4: Device Detection via OpenRGB
print("\n✓ Querying OpenRGB devices...")
try:
    result = subprocess.run(
        [str(openrgb_path), "--list-devices"], capture_output=True, text=True, timeout=10
    )

    if result.returncode == 0:
        output = result.stdout
        print("  ✓ OpenRGB responded")

        # Parse device info
        if "ASUS" in output or "AURA" in output:
            print("\n  📌 ASUS/AURA Device Detected:")
            for line in output.split("\n"):
                if any(keyword in line for keyword in ["Type:", "Location:", "Zones:", "Modes:"]):
                    print(f"    {line.strip()}")

            # Check for zones
            if "Aura Addressable" in output:
                print("\n  ✓ Addressable LED zones found!")
            else:
                print("\n  ⚠️ No addressable LED zones detected")
                issues_found.append("No addressable LED zones found")
                solutions.append("Check if LED strip is properly connected to motherboard")
        else:
            print("  ✗ No ASUS/AURA devices detected")
            issues_found.append("AURA device not detected by OpenRGB")
            solutions.append("Ensure AURA LED Controller drivers are installed")
    else:
        print(f"  ✗ OpenRGB error (code {result.returncode})")
        if "I2C" in result.stdout or "SMBus" in result.stdout:
            print("  ⚠️ I2C/SMBus initialization failed")
            issues_found.append("I2C/SMBus not initialized")
            solutions.append("Run OpenRGB as Administrator to initialize WinRing0 driver")
except Exception as e:
    print(f"  ✗ Could not query devices: {e}")
    issues_found.append(f"Device query failed: {e}")

# Check 5: Armoury Crate Conflict
print("\n✓ Checking for Armoury Crate conflicts...")
try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-Process ArmouryCrate, LightingService -ErrorAction SilentlyContinue | Select-Object ProcessName",
        ],
        capture_output=True,
        text=True,
        timeout=3,
    )
    if result.stdout.strip():
        print("  ⚠️ Armoury Crate is running")
        print("  This may conflict with OpenRGB")
        issues_found.append("Armoury Crate running (may block OpenRGB)")
        solutions.append("Close Armoury Crate before using OpenRGB")
    else:
        print("  ✓ No Armoury Crate conflicts")
except Exception as e:
    print(f"  ⚠️ Could not check: {e}")

print("\n[3] PYTHON API CHECK")
print("-" * 70)

# Check 6: Python openrgb library
print("\n✓ Checking openrgb-python library...")
try:
    import openrgb

    print(
        f"  ✓ openrgb-python installed (version: {openrgb.__version__ if hasattr(openrgb, '__version__') else 'unknown'})"
    )
except ImportError:
    print("  ✗ openrgb-python NOT installed")
    issues_found.append("Python openrgb library missing")
    solutions.append("Install: pip install openrgb-python")

print("\n" + "=" * 70)
print("  📊 DIAGNOSTIC RESULTS")
print("=" * 70 + "\n")

if not issues_found:
    print("✅ NO ISSUES FOUND - System appears configured correctly\n")
    print("Possible causes if LED still not working:")
    print("  1. LED strip not connected to correct motherboard header")
    print("  2. Wrong zone being controlled (try all 3 zones)")
    print("  3. LED strip requires 5V RGB (not 12V or ARGB)")
    print("  4. Physical hardware issue with LED strip")
else:
    print(f"⚠️ FOUND {len(issues_found)} ISSUE(S):\n")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")

    print(f"\n💡 RECOMMENDED SOLUTIONS:\n")
    for i, solution in enumerate(solutions, 1):
        print(f"  {i}. {solution}")

print("\n" + "=" * 70)
print("  🔧 NEXT STEPS")
print("=" * 70 + "\n")

if "Run OpenRGB as Administrator" in " ".join(solutions):
    print("PRIORITY 1: Run OpenRGB as Administrator")
    print("  → This initializes WinRing0 driver for I2C/SMBus access")
    print("  → Command: .\\START_OPENRGB_SERVER.ps1\n")

if "Close Armoury Crate" in " ".join(solutions):
    print("PRIORITY 2: Close Armoury Crate")
    print("  → Stop-Process -Name ArmouryCrate -Force")
    print("  → Stop-Process -Name LightingService -Force\n")

if "openrgb-python" in " ".join(solutions):
    print("PRIORITY 3: Install Python library")
    print("  → pip install openrgb-python\n")

print("After fixing issues, test with:")
print("  1. python test_openrgb_zones.py  (find correct zone)")
print("  2. python test_openrgb_red_wave.py  (run RED wave)")

print("\n" + "=" * 70)
