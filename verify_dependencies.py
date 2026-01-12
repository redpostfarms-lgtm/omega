#!/usr/bin/env python3
"""
Gatekeeper System - Dependency Verification
Checks that all required Python packages are installed
"""

import sys
import subprocess
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

def check_package(package_name):
    """Check if a package is installed."""
    try:
        # Try importing the package
        if package_name in ['pywin32', 'win32api']:
            try:
                import win32api
                return True, None
            except ImportError:
                return False, "win32api not available"
        elif package_name == 'pyaudio':
            try:
                import pyaudio
                return True, None
            except ImportError:
                return False, "pyaudio not available"
        elif package_name == 'PIL' or package_name == 'pillow':
            try:
                from PIL import Image
                return True, None
            except ImportError:
                return False, "Pillow not available"
        elif package_name == 'yaml' or package_name == 'pyyaml':
            try:
                import yaml
                return True, None
            except ImportError:
                return False, "PyYAML not available"
        else:
            # Try standard import
            __import__(package_name.lower().replace('-', '_'))
            return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def get_installed_packages():
    """Get list of installed packages."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            packages = {}
            for line in result.stdout.splitlines():
                if '==' in line:
                    name, version = line.split('==', 1)
                    packages[name.lower()] = version
            return packages
        return {}
    except Exception:
        return {}

def check_package_from_pip_list(package_name, installed_packages):
    """Check if package is in pip list."""
    # Normalize package name
    normalized = package_name.lower().replace('-', '_')
    
    # Check various name variations
    variations = [
        normalized,
        package_name.lower(),
        package_name.lower().replace('_', '-'),
        package_name.lower().replace('-', '_'),
    ]
    
    for var in variations:
        if var in installed_packages:
            return True, installed_packages[var]
    
    return False, None

def main():
    """Main verification function."""
    print_header("GATEKEEPER SYSTEM - DEPENDENCY VERIFICATION")
    
    print_info(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()
    
    # Get installed packages list
    print_info("Getting installed packages list...")
    installed_packages = get_installed_packages()
    print_success(f"Found {len(installed_packages)} installed packages")
    print()
    
    # Core dependencies (essential)
    print_header("CHECKING CORE DEPENDENCIES")
    
    core_packages = [
        "numpy",
        "psutil",
    ]
    
    core_status = {}
    for pkg in core_packages:
        installed, version = check_package_from_pip_list(pkg, installed_packages)
        if installed:
            print_success(f"{pkg:20} - Installed (version: {version})")
            core_status[pkg] = True
        else:
            # Try import check as backup
            can_import, error = check_package(pkg)
            if can_import:
                print_success(f"{pkg:20} - Installed (import check)")
                core_status[pkg] = True
            else:
                print_error(f"{pkg:20} - NOT INSTALLED")
                core_status[pkg] = False
    
    # GUI dependencies
    print_header("CHECKING GUI DEPENDENCIES")
    
    gui_packages = [
        "pygame",
        "tkinter",
    ]
    
    gui_status = {}
    for pkg in gui_packages:
        if pkg == "tkinter":
            try:
                import tkinter
                print_success(f"{pkg:20} - Installed (built-in)")
                gui_status[pkg] = True
            except ImportError:
                print_warning(f"{pkg:20} - Not available (may need system package)")
                gui_status[pkg] = False
        else:
            installed, version = check_package_from_pip_list(pkg, installed_packages)
            if installed:
                print_success(f"{pkg:20} - Installed (version: {version})")
                gui_status[pkg] = True
            else:
                can_import, error = check_package(pkg)
                if can_import:
                    print_success(f"{pkg:20} - Installed (import check)")
                    gui_status[pkg] = True
                else:
                    print_error(f"{pkg:20} - NOT INSTALLED")
                    gui_status[pkg] = False
    
    # Audio dependencies
    print_header("CHECKING AUDIO DEPENDENCIES")
    
    audio_packages = [
        "pyaudio",
    ]
    
    audio_status = {}
    for pkg in audio_packages:
        installed, version = check_package_from_pip_list(pkg, installed_packages)
        if installed:
            print_success(f"{pkg:20} - Installed (version: {version})")
            audio_status[pkg] = True
        else:
            can_import, error = check_package(pkg)
            if can_import:
                print_success(f"{pkg:20} - Installed (import check)")
                audio_status[pkg] = True
            else:
                print_error(f"{pkg:20} - NOT INSTALLED")
                audio_status[pkg] = False
    
    # Windows-specific dependencies
    print_header("CHECKING WINDOWS-SPECIFIC DEPENDENCIES")
    
    windows_packages = [
        "pywin32",
    ]
    
    windows_status = {}
    if sys.platform == "win32":
        for pkg in windows_packages:
            installed, version = check_package_from_pip_list(pkg, installed_packages)
            if installed:
                print_success(f"{pkg:20} - Installed (version: {version})")
                windows_status[pkg] = True
            else:
                can_import, error = check_package(pkg)
                if can_import:
                    print_success(f"{pkg:20} - Installed (import check)")
                    windows_status[pkg] = True
                else:
                    print_warning(f"{pkg:20} - NOT INSTALLED")
                    windows_status[pkg] = False
    else:
        print_info("Skipping Windows-specific packages (not Windows)")
    
    # Optional dependencies
    print_header("CHECKING OPTIONAL DEPENDENCIES")
    
    optional_packages = [
        "pillow",
        "requests",
        "pyyaml",
        "jsonschema",
    ]
    
    optional_status = {}
    for pkg in optional_packages:
        # Check pip list
        installed, version = check_package_from_pip_list(pkg, installed_packages)
        if installed:
            print_success(f"{pkg:20} - Installed (version: {version})")
            optional_status[pkg] = True
        else:
            # Try import check
            import_name = pkg.lower().replace('-', '_')
            if pkg == 'pillow':
                import_name = 'PIL'
            elif pkg == 'pyyaml':
                import_name = 'yaml'
            
            can_import, error = check_package(import_name)
            if can_import:
                print_success(f"{pkg:20} - Installed (import check)")
                optional_status[pkg] = True
            else:
                print_warning(f"{pkg:20} - NOT INSTALLED (optional)")
                optional_status[pkg] = False
    
    # Check requirements.txt packages
    print_header("CHECKING REQUIREMENTS.TXT PACKAGES")
    
    requirements_file = Path("requirements.txt")
    requirements_status = {}
    if requirements_file.exists():
        print_info(f"Found requirements.txt - checking packages...")
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            req_packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, <=, etc.)
                    pkg_name = line.split('>=')[0].split('<=')[0].split('==')[0].split('[')[0].strip()
                    if pkg_name:
                        req_packages.append(pkg_name)
            
            # Check first 20 packages from requirements.txt (to avoid too much output)
            for pkg in req_packages[:20]:
                installed, version = check_package_from_pip_list(pkg, installed_packages)
                if installed:
                    print_success(f"{pkg:30} - Installed")
                    requirements_status[pkg] = True
                else:
                    print_warning(f"{pkg:30} - NOT INSTALLED")
                    requirements_status[pkg] = False
            
            if len(req_packages) > 20:
                print_info(f"... and {len(req_packages) - 20} more packages in requirements.txt")
        except Exception as e:
            print_warning(f"Could not read requirements.txt: {e}")
    else:
        print_info("requirements.txt not found - skipping")
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_status = {**core_status, **gui_status, **audio_status, **windows_status, **optional_status}
    
    installed_count = sum(1 for v in all_status.values() if v)
    total_count = len(all_status)
    
    print_info(f"Core packages: {sum(1 for k, v in core_status.items() if v)}/{len(core_status)} installed")
    print_info(f"GUI packages: {sum(1 for k, v in gui_status.items() if v)}/{len(gui_status)} installed")
    print_info(f"Audio packages: {sum(1 for k, v in audio_status.items() if v)}/{len(audio_status)} installed")
    if sys.platform == "win32":
        print_info(f"Windows packages: {sum(1 for k, v in windows_status.items() if v)}/{len(windows_status)} installed")
    print_info(f"Optional packages: {sum(1 for k, v in optional_status.items() if v)}/{len(optional_status)} installed")
    print()
    print_info(f"Total checked: {installed_count}/{total_count} installed")
    
    # Missing packages
    missing = [k for k, v in all_status.items() if not v]
    if missing:
        print()
        print_warning("Missing packages:")
        for pkg in missing:
            print_warning(f"  - {pkg}")
        print()
        print_info("To install missing packages, run: INSTALL_DEPENDENCIES.bat")
        return 1
    else:
        print()
        print_success("All essential packages are installed!")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        print_header("VERIFICATION COMPLETE")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
