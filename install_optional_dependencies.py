#!/usr/bin/env python3
"""
Gatekeeper System - Optional Dependencies Installer
Installs optional packages that were not installed
"""

import subprocess
import sys
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

def install_package(package, description=None):
    """Install a single package."""
    if description:
        print_info(f"Installing {description} ({package})...")
    else:
        print_info(f"Installing {package}...")
    
    try:
        # Use --quiet to reduce output, but show errors
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            print_success(f"{package} installed successfully")
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            print_warning(f"Failed to install {package}: {error_msg[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"Timeout installing {package} (took too long)")
        return False
    except Exception as e:
        print_error(f"Error installing {package}: {e}")
        return False

def main():
    """Main installation function."""
    print_header("GATEKEEPER SYSTEM - OPTIONAL DEPENDENCIES INSTALLER")
    
    print_info(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()
    
    # Optional packages that were missing
    print_header("INSTALLING OPTIONAL PACKAGES")
    
    optional_packages = [
        ("torchcodec", "torchcodec - Audio decoding for TTS"),
        ("faster-whisper", "faster-whisper - Fast offline speech recognition"),
        ("webrtcvad", "webrtcvad - Voice Activity Detection"),
        ("aiofiles", "aiofiles - Async file I/O"),
        ("aiohttp", "aiohttp - Async HTTP client"),
    ]
    
    success_count = 0
    failed_packages = []
    
    for package, description in optional_packages:
        if install_package(package, description):
            success_count += 1
        else:
            failed_packages.append(package)
        print()  # Blank line between packages
    
    # Additional optional packages from requirements.txt
    print_header("INSTALLING ADDITIONAL OPTIONAL PACKAGES")
    
    additional_optional = [
        ("mauve-text", "mauve-text - MAUVE evaluation metric"),
        ("datasets", "datasets - Evaluation datasets"),
        ("accelerate", "accelerate - Distributed/accelerated inference"),
        ("plotly", "plotly - Interactive visualizations"),
        ("pandas", "pandas - Data manipulation"),
        ("pyjwt[crypto]", "pyjwt - JWT token generation/verification"),
        ("redis", "redis - JWKS caching"),
        ("tqdm", "tqdm - Progress bars"),
        ("WMI", "WMI - Windows Management Instrumentation"),
        ("pyautogui", "pyautogui - GUI automation"),
        ("pynput", "pynput - Input simulation"),
        ("dnspython", "dnspython - DNS operations"),
        ("cryptography", "cryptography - Secure encryption"),
        ("openrgb-python", "openrgb-python - RGB lighting control"),
    ]
    
    for package, description in additional_optional:
        if install_package(package, description):
            success_count += 1
        else:
            failed_packages.append(package)
        print()
    
    # Summary
    print_header("INSTALLATION SUMMARY")
    
    total_packages = len(optional_packages) + len(additional_optional)
    
    print_info(f"Successfully installed: {success_count}/{total_packages} packages")
    
    if failed_packages:
        print_warning(f"Failed to install {len(failed_packages)} packages:")
        for pkg in failed_packages:
            print_warning(f"  - {pkg}")
        print()
        print_info("These packages are optional and may not be critical for basic functionality")
    else:
        print_success("All optional packages installed successfully!")
    
    print()
    print_header("INSTALLATION COMPLETE")
    
    return 0 if not failed_packages else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
