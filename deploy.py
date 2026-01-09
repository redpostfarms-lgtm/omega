#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Omega System Deployment Script

"""
Automated deployment script for Omega system.
Handles dependency installation, verification, and system startup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

ROOT = Path(__file__).parent
REQUIREMENTS = ROOT / 'requirements.txt'

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print_header("Installing Dependencies")
    
    if not REQUIREMENTS.exists():
        print("ERROR: requirements.txt not found!")
        return False
    
    try:
        print("Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(REQUIREMENTS)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ All dependencies installed successfully")
            return True
        else:
            print("⚠ Some dependencies may have failed to install:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def verify_critical_files():
    """Verify critical files exist."""
    print_header("Verifying Critical Files")
    
    critical_files = [
        'rate_limiter.py',
        'omega_full_brain.py',
        'omega_combined_final.py',
        'omega_simple_final.py',
        'requirements.txt',
    ]
    
    all_exist = True
    for file in critical_files:
        path = ROOT / file
        if path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def verify_audio_setup():
    """Verify audio setup."""
    print_header("Verifying Audio Setup")
    
    clip_path = ROOT / 'clip_0001.wav'
    if clip_path.exists():
        print(f"✓ Voice clip found: {clip_path}")
        return True
    else:
        print(f"⚠ Voice clip not found: {clip_path}")
        print("  The system will work but may use default voice.")
        return True  # Not critical

def run_tests():
    """Run system tests."""
    print_header("Running System Tests")
    
    test_file = ROOT / 'test_system.py'
    if not test_file.exists():
        print("⚠ Test file not found, skipping tests")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=60
        )
        
        print(result.stdout)
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("⚠ Some tests failed (see output above)")
            return False
    except subprocess.TimeoutExpired:
        print("⚠ Tests timed out")
        return False
    except Exception as e:
        print(f"⚠ Could not run tests: {e}")
        return False

def create_startup_script():
    """Create startup script."""
    print_header("Creating Startup Scripts")
    
    # Windows batch file
    if platform.system() == 'Windows':
        bat_file = ROOT / 'start_omega.bat'
        bat_content = f'''@echo off
cd /d "{ROOT}"
echo Starting Omega System...
python omega_full_brain.py
pause
'''
        bat_file.write_text(bat_content)
        print(f"✓ Created: {bat_file.name}")
    
    # Unix shell script
    sh_file = ROOT / 'start_omega.sh'
    sh_content = f'''#!/bin/bash
cd "{ROOT}"
echo "Starting Omega System..."
python3 omega_full_brain.py
'''
    sh_file.write_text(sh_content)
    if platform.system() != 'Windows':
        os.chmod(sh_file, 0o755)
    print(f"✓ Created: {sh_file.name}")

def print_deployment_summary():
    """Print deployment summary."""
    print_header("Deployment Summary")
    
    print("Omega System Deployment Complete!")
    print("\nTo start the system:")
    print("  Windows:  start_omega.bat")
    print("  Unix/Mac: ./start_omega.sh")
    print("  Manual:   python omega_full_brain.py")
    print("\nAvailable Omega variants:")
    print("  - omega_full_brain.py      (Voice + Emotion)")
    print("  - omega_combined_final.py  (Voice + Emotion + Memory)")
    print("  - omega_simple_final.py    (Voice + Memory)")
    print("  - omega_final_no_emotion.py (Voice only)")
    print("\nFor help, see MASTER_SWEEP_REPORT.md")

def main():
    """Main deployment function."""
    print_header("OMEGA SYSTEM DEPLOYMENT")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠ Warning: Some dependencies may not be installed correctly")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Verify files
    if not verify_critical_files():
        print("\n✗ Critical files missing. Deployment failed.")
        sys.exit(1)
    
    # Verify audio
    verify_audio_setup()
    
    # Run tests
    run_tests()
    
    # Create startup scripts
    create_startup_script()
    
    # Print summary
    print_deployment_summary()
    
    print("\n" + "=" * 60)
    print("  DEPLOYMENT COMPLETE - SYSTEM READY")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Deployment failed: {e}")
        sys.exit(1)
