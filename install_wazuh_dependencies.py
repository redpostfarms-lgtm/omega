#!/usr/bin/env python3
"""
Wazuh Integration Dependencies Installer
=========================================
Installs optional dependencies for Wazuh integration features.

Note: Wazuh server itself must be installed separately (not a Python package).
This script installs Python libraries that may be useful for:
- Wazuh API client
- YARA Python bindings (for file-based detection)
- Network monitoring tools (optional)

Dependencies:
- requests: For Wazuh API client (if using gatekeeper_wazuh_integration.py)
- pyyaml: For configuration file parsing (if needed)
- Optional: yara-python (for YARA rule compilation/testing)
"""

import subprocess
import sys
from pathlib import Path

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_color(message, color=Colors.RESET):
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}")

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_color("ERROR: Python 3.7+ required", Colors.RED)
        return False
    print_color(f"✓ Python {version.major}.{version.minor}.{version.micro} detected", Colors.GREEN)
    return True

def upgrade_pip():
    """Upgrade pip to latest version."""
    try:
        print_color("\n[1/4] Upgrading pip...", Colors.CYAN)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print_color("✓ pip upgraded successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_color(f"⚠ pip upgrade failed (may already be latest): {e}", Colors.YELLOW)
        return True  # Continue anyway

def install_package(package, description=""):
    """Install a Python package."""
    try:
        if description:
            print(f"  Installing {description}...", end=" ", flush=True)
        else:
            print(f"  Installing {package}...", end=" ", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print_color("✓", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_color("✗", Colors.RED)
        print_color(f"    Warning: Failed to install {package}", Colors.YELLOW)
        return False

def main():
    """Main installation function."""
    print_color("=" * 60, Colors.CYAN)
    print_color("Wazuh Integration Dependencies Installer", Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    
    if not check_python_version():
        sys.exit(1)
    
    upgrade_pip()
    
    # Required dependencies for Wazuh integration
    print_color("\n[2/4] Installing required dependencies...", Colors.CYAN)
    required_packages = [
        ("requests", "HTTP client for Wazuh API"),
        ("pyyaml", "YAML parser for configuration files"),
    ]
    
    required_success = True
    for package, desc in required_packages:
        if not install_package(package, desc):
            required_success = False
    
    if required_success:
        print_color("✓ All required dependencies installed", Colors.GREEN)
    else:
        print_color("⚠ Some required dependencies failed to install", Colors.YELLOW)
    
    # Optional dependencies
    print_color("\n[3/4] Installing optional dependencies...", Colors.CYAN)
    optional_packages = [
        ("yara-python", "YARA Python bindings (for YARA rule testing) - Note: Requires YARA library"),
    ]
    
    optional_success = True
    for package, desc in optional_packages:
        if not install_package(package, desc):
            optional_success = False
            print_color(f"    Note: {desc} is optional - continuing without it", Colors.YELLOW)
    
    # Note about YARA
    print_color("\n[INFO] YARA Python bindings require the YARA library:", Colors.YELLOW)
    print_color("  - Windows: Download from https://github.com/VirusTotal/yara/releases", Colors.YELLOW)
    print_color("  - Linux: sudo apt-get install yara libyara-dev (Debian/Ubuntu)", Colors.YELLOW)
    print_color("  - macOS: brew install yara", Colors.YELLOW)
    
    # Verification
    print_color("\n[4/4] Verifying installations...", Colors.CYAN)
    verify_packages = ["requests", "yaml"]
    verified = []
    failed = []
    
    for package in verify_packages:
        try:
            __import__(package)
            verified.append(package)
            print_color(f"  ✓ {package} verified", Colors.GREEN)
        except ImportError:
            failed.append(package)
            print_color(f"  ✗ {package} not found", Colors.RED)
    
    # Summary
    print_color("\n" + "=" * 60, Colors.CYAN)
    print_color("Installation Summary", Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    
    if len(failed) == 0:
        print_color("✓ All dependencies installed successfully!", Colors.GREEN)
    else:
        print_color(f"⚠ {len(failed)} package(s) failed to install", Colors.YELLOW)
        print_color(f"Failed: {', '.join(failed)}", Colors.YELLOW)
    
    print_color("\nNote: Wazuh server must be installed separately", Colors.YELLOW)
    print_color("See: https://documentation.wazuh.com/current/installation-guide/index.html", Colors.YELLOW)
    
    print_color("\nInstallation complete!", Colors.GREEN)

if __name__ == "__main__":
    main()
