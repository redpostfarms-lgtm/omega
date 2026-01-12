# -*- coding: utf-8 -*-
# STONEWALL SETUP - One-line install script

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check for required dependencies."""
    required = ['cryptography', 'requests']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    return missing


def install_dependencies():
    """Install required dependencies."""
    missing = check_dependencies()
    
    if missing:
        print(f"[Stonewall] Installing dependencies: {', '.join(missing)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
    else:
        print("[Stonewall] All dependencies installed")


def setup_stonewall():
    """Setup Stonewall VPN."""
    print("=" * 60)
    print("STONEWALL VPN - Setup")
    print("=" * 60)
    
    # Check dependencies
    install_dependencies()
    
    # Create config directory
    config_dir = Path.home() / '.stonewall'
    config_dir.mkdir(exist_ok=True)
    
    print(f"\n[OK] Stonewall installed to: {config_dir}")
    print("\nUsage:")
    print("  python -m stonewall.stonewall_core --init      # Start VPN")
    print("  python -m stonewall.stonewall_core --daemon    # Run as daemon")
    print("  python -m stonewall.stonewall_core --status    # Check status")
    print("  python -m stonewall.stonewall_core --stop      # Stop VPN")
    print("\nAgent Protection:")
    print("  from stonewall.agent_protection import ProtectedScraper")
    print("  with ProtectedScraper() as scraper:")
    print("      response = scraper.fetch('https://example.com')")
    
    print("\n[OK] Setup complete. Your machine is ready to go dark.")


if __name__ == '__main__':
    setup_stonewall()

