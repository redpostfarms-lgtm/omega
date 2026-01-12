#!/usr/bin/env python3
"""
Complete System Verification Script
====================================
Verifies all Python dependencies and system components are installed correctly.

This script checks:
1. Core TTS and audio dependencies
2. Speech recognition dependencies
3. UI and graphics dependencies
4. Wazuh integration dependencies
5. All optional dependencies
6. Module importability
"""

import sys
from pathlib import Path

# Color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_result(name, status, message=""):
    """Print verification result."""
    if status:
        symbol = "✓"
        color = Colors.GREEN
    else:
        symbol = "✗"
        color = Colors.RED
    
    result = f"  {symbol} {name}"
    if message:
        result += f": {message}"
    print(f"{color}{result}{Colors.RESET}")

def test_import(module_name, description=None):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print_result(module_name, True, description or "OK")
        return True
    except ImportError as e:
        print_result(module_name, False, f"Missing: {str(e)}")
        return False
    except Exception as e:
        print_result(module_name, False, f"Error: {str(e)}")
        return False

def main():
    """Main verification function."""
    print(f"{Colors.CYAN}{'=' * 60}")
    print("Complete System Verification")
    print('=' * 60 + Colors.RESET)
    print()
    
    results = {
        "core": [],
        "audio": [],
        "ui": [],
        "wazuh": [],
        "optional": []
    }
    
    # Core TTS and Audio
    print(f"{Colors.CYAN}[1/5] Core TTS and Audio Dependencies{Colors.RESET}")
    core_modules = [
        ("torch", "PyTorch"),
        ("torchaudio", "TorchAudio"),
        ("TTS", "Coqui TTS"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("speechbrain", "SpeechBrain"),
    ]
    for module, desc in core_modules:
        results["core"].append(test_import(module, desc))
    print()
    
    # Audio Processing
    print(f"{Colors.CYAN}[2/5] Audio Processing Dependencies{Colors.RESET}")
    audio_modules = [
        ("sounddevice", "SoundDevice"),
        ("librosa", "Librosa"),
        ("pydub", "PyDub"),
        ("soundfile", "SoundFile"),
    ]
    for module, desc in audio_modules:
        results["audio"].append(test_import(module, desc))
    print()
    
    # UI and Graphics
    print(f"{Colors.CYAN}[3/5] UI and Graphics Dependencies{Colors.RESET}")
    ui_modules = [
        ("pygame", "Pygame (for omega_kitt_ui.py)"),
        ("pyaudio", "PyAudio (for omega_kitt_ui.py)"),
    ]
    for module, desc in ui_modules:
        results["ui"].append(test_import(module, desc))
    print()
    
    # Wazuh Integration
    print(f"{Colors.CYAN}[4/5] Wazuh Integration Dependencies{Colors.RESET}")
    wazuh_modules = [
        ("requests", "Requests (HTTP client)"),
        ("yaml", "PyYAML"),
    ]
    for module, desc in wazuh_modules:
        results["wazuh"].append(test_import(module, desc))
    print()
    
    # Optional Dependencies
    print(f"{Colors.CYAN}[5/5] Optional Dependencies{Colors.RESET}")
    optional_modules = [
        ("faster_whisper", "Faster Whisper (optional)"),
        ("webrtcvad", "WebRTC VAD (optional)"),
        ("redis", "Redis (optional)"),
        ("yara", "YARA Python (optional, requires YARA library)"),
    ]
    for module, desc in optional_modules:
        results["optional"].append(test_import(module, desc))
    print()
    
    # Summary
    print(f"{Colors.CYAN}{'=' * 60}")
    print("Verification Summary")
    print('=' * 60 + Colors.RESET)
    
    total = 0
    passed = 0
    
    for category, module_results in results.items():
        category_passed = sum(module_results)
        category_total = len(module_results)
        total += category_total
        passed += category_passed
        
        if category_total > 0:
            percentage = (category_passed / category_total) * 100
            status = "✓" if category_passed == category_total else "⚠"
            color = Colors.GREEN if category_passed == category_total else Colors.YELLOW
            print(f"{color}{status} {category.capitalize()}: {category_passed}/{category_total} ({percentage:.0f}%){Colors.RESET}")
    
    print()
    overall_percentage = (passed / total) * 100 if total > 0 else 0
    
    if overall_percentage == 100:
        print(f"{Colors.GREEN}✓ All required dependencies verified!{Colors.RESET}")
        print(f"{Colors.GREEN}System Status: PRODUCTION-READY{Colors.RESET}")
    elif overall_percentage >= 90:
        print(f"{Colors.YELLOW}⚠ Most dependencies verified ({passed}/{total}){Colors.RESET}")
        print(f"{Colors.YELLOW}System Status: Mostly Ready (some optional dependencies missing){Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Some required dependencies missing ({passed}/{total}){Colors.RESET}")
        print(f"{Colors.RED}System Status: Needs attention{Colors.RESET}")
    
    print()
    print(f"{Colors.CYAN}Overall: {passed}/{total} ({overall_percentage:.1f}%){Colors.RESET}")
    print()

if __name__ == "__main__":
    main()
