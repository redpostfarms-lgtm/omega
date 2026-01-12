#!/usr/bin/env python3
"""
Gatekeeper System - Complete Dependency Installer
Installs all required dependencies for The Gatekeeper system
"""

import subprocess
import sys
import os
from pathlib import Path

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print_info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required")
        return False
    
    print_success("Python version check passed")
    return True

def upgrade_pip():
    """Upgrade pip to latest version."""
    print_info("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("pip upgraded successfully")
        return True
    except subprocess.CalledProcessError:
        print_warning("Failed to upgrade pip, continuing anyway...")
        return False

def install_package(package, description=None):
    """Install a single package."""
    if description:
        print_info(f"Installing {description} ({package})...")
    else:
        print_info(f"Installing {package}...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success(f"{package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to install {package}")
        return False

def install_from_requirements(file_path):
    """Install packages from requirements file."""
    if not Path(file_path).exists():
        print_warning(f"Requirements file not found: {file_path}")
        return False
    
    print_info(f"Installing packages from {file_path}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success(f"Packages from {file_path} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to install packages from {file_path}")
        return False

def install_dev_dependencies():
    """Install development dependencies from requirements-dev.txt."""
    dev_req_file = root_dir / 'requirements-dev.txt'
    if not dev_req_file.exists():
        print_warning(f"requirements-dev.txt not found: {dev_req_file}")
        return False
    
    print_info(f"Installing development dependencies from {dev_req_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(dev_req_file)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success(f"Development dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to install development dependencies")
        return False

def main():
    """Main installation function."""
    print_header("GATEKEEPER SYSTEM - DEPENDENCY INSTALLER")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Upgrade pip
    upgrade_pip()
    
    # Core dependencies
    print_header("INSTALLING CORE DEPENDENCIES")
    
    core_packages = [
        ("numpy", "NumPy - Numerical computing"),
        ("psutil", "psutil - System and process utilities"),
    ]
    
    core_success = 0
    for package, description in core_packages:
        if install_package(package, description):
            core_success += 1
    
    # GUI dependencies
    print_header("INSTALLING GUI DEPENDENCIES")
    
    gui_packages = [
        ("pygame", "Pygame - Game development and UI"),
        ("tkinter", "Tkinter - GUI toolkit (usually built-in)"),
    ]
    
    gui_success = 0
    for package, description in gui_packages:
        try:
            if package == "tkinter":
                # Tkinter is usually built-in, just check
                import tkinter
                print_success("tkinter is available (built-in)")
                gui_success += 1
            elif install_package(package, description):
                gui_success += 1
        except ImportError:
            print_warning("tkinter not available (may need system package)")
    
    # Audio dependencies
    print_header("INSTALLING AUDIO DEPENDENCIES")
    
    audio_packages = [
        ("pyaudio", "PyAudio - Audio I/O"),
    ]
    
    audio_success = 0
    for package, description in audio_packages:
        if install_package(package, description):
            audio_success += 1
    
    # Windows-specific dependencies
    print_header("INSTALLING WINDOWS-SPECIFIC DEPENDENCIES")
    
    windows_packages = [
        ("pywin32", "pywin32 - Windows API access"),
    ]
    
    windows_success = 0
    if sys.platform == "win32":
        for package, description in windows_packages:
            if install_package(package, description):
                windows_success += 1
    else:
        print_info("Skipping Windows-specific packages (not Windows)")
    
    # Optional dependencies
    print_header("INSTALLING OPTIONAL DEPENDENCIES")
    
    optional_packages = [
        ("pillow", "Pillow - Image processing"),
        ("requests", "requests - HTTP library"),
        ("pyyaml", "PyYAML - YAML parser"),
        ("jsonschema", "jsonschema - JSON validation"),
    ]
    
    optional_success = 0
    for package, description in optional_packages:
        if install_package(package, description):
            optional_success += 1
    
    # Install from requirements files if they exist (in order of priority)
    requirements_files = ["requirements.txt", "requirements_gatekeeper.txt"]
    installed_from_req = False
    for req_file in requirements_files:
        requirements_file = Path(req_file)
        if requirements_file.exists():
            print_header(f"INSTALLING FROM {req_file.upper()}")
            if install_from_requirements(req_file):
                installed_from_req = True
                print_info(f"Installed dependencies from {req_file}")
                # Only install from first found requirements file to avoid duplicates
                break
    
    if not installed_from_req:
        print_warning("No requirements.txt file found - installed basic dependencies only")
    
    # Summary
    print_header("INSTALLATION SUMMARY")
    
    total_packages = len(core_packages) + len(gui_packages) + len(audio_packages)
    if sys.platform == "win32":
        total_packages += len(windows_packages)
    total_packages += len(optional_packages)
    
    total_success = core_success + gui_success + audio_success + windows_success + optional_success
    
    print_info(f"Core packages: {core_success}/{len(core_packages)}")
    print_info(f"GUI packages: {gui_success}/{len(gui_packages)}")
    print_info(f"Audio packages: {audio_success}/{len(audio_packages)}")
    if sys.platform == "win32":
        print_info(f"Windows packages: {windows_success}/{len(windows_packages)}")
    print_info(f"Optional packages: {optional_success}/{len(optional_packages)}")
    print_info(f"Total: {total_success}/{total_packages} packages installed")
    
    if total_success == total_packages:
        print_success("All packages installed successfully!")
        return 0
    else:
        print_warning(f"Some packages failed to install ({total_packages - total_success} failures)")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print_header("INSTALLATION COMPLETE")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
