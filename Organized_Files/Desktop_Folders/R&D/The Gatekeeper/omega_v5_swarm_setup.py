# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# OMEGA V5 SWARM SETUP - Install All Dependencies

"""
Setup script for Omega V5 Swarm
Installs all required dependencies for 8 layers
"""

import sys
import io
import subprocess
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

# All required packages
REQUIRED_PACKAGES = [
    # Layer 2: CUDA Fuzzer Kit
    'cupy-cuda11x',  # GPU acceleration (for CUDA 11.x)
    'aiodns',  # Async DNS
    'scapy',  # Network packet manipulation
    'z3-solver',  # Z3 theorem prover
    
    # Layer 3: Proxy Rotation
    'aiohttp',  # Async HTTP client
    
    # Layer 5: Auto-Report Template
    'jinja2',  # Template engine
    
    # Additional
    'torch',  # PyTorch (for GPU)
    'numpy',  # Numerical computing
]

# Optional packages (for kernel-fuzzer)
OPTIONAL_PACKAGES = [
    'gitpython',  # For cloning kernel-fuzzer
]


def install_package(package: str) -> bool:
    """Install a package."""
    try:
        print(f"  Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ✓ {package} installed")
        return True
    except subprocess.CalledProcessError:
        print(f"    ✗ {package} failed")
        return False
    except Exception as e:
        print(f"    ✗ {package} error: {e}")
        return False


def clone_kernel_fuzzer():
    """Clone kernel-fuzzer repository."""
    kernel_fuzzer_dir = GATE / 'kernel-fuzzer'
    
    if kernel_fuzzer_dir.exists():
        print("  kernel-fuzzer already exists")
        return True
    
    try:
        print("  Cloning kernel-fuzzer...")
        subprocess.check_call(['git', 'clone', 'https://github.com/uber/kernel-fuzzer.git', str(kernel_fuzzer_dir)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("    ✓ kernel-fuzzer cloned")
        return True
    except subprocess.CalledProcessError:
        print("    ✗ kernel-fuzzer clone failed (git not available or repo not accessible)")
        return False
    except Exception as e:
        print(f"    ✗ kernel-fuzzer error: {e}")
        return False


def setup_proxies():
    """Set up proxy template."""
    swarm_dir = GATE / 'omega_swarm'
    swarm_dir.mkdir(parents=True, exist_ok=True)
    
    proxy_file = swarm_dir / 'proxies.txt'
    if not proxy_file.exists():
        proxy_template = swarm_dir / 'proxies_template.txt'
        with open(proxy_template, 'w', encoding='utf-8') as f:
            f.write("# Proxy format: ip:port:username:password\n")
            f.write("# Or: ip:port (if no auth)\n")
            f.write("# Add your proxies from Luminati/IPRoyal here\n")
            f.write("# Example:\n")
            f.write("# 192.168.1.1:8080:user:pass\n")
            f.write("# 192.168.1.2:8080\n")
        
        print("  Proxy template created: omega_swarm/proxies_template.txt")
        print("    Add your proxies to omega_swarm/proxies.txt")


def main():
    """Main setup function."""
    print("=" * 80)
    print("  OMEGA V5 SWARM SETUP")
    print("  Installing all 8 layers")
    print("=" * 80)
    print()
    
    # Install required packages
    print("Installing required packages...")
    print()
    installed = 0
    for package in REQUIRED_PACKAGES:
        if install_package(package):
            installed += 1
        print()
    
    print(f"Installed {installed}/{len(REQUIRED_PACKAGES)} required packages")
    print()
    
    # Install optional packages
    print("Installing optional packages...")
    print()
    for package in OPTIONAL_PACKAGES:
        install_package(package)
        print()
    
    # Clone kernel-fuzzer
    print("Setting up kernel-fuzzer...")
    print()
    clone_kernel_fuzzer()
    print()
    
    # Setup proxies
    print("Setting up proxy rotation...")
    print()
    setup_proxies()
    print()
    
    print("=" * 80)
    print("  SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Add proxies to: omega_swarm/proxies.txt")
    print("2. Configure targets")
    print("3. Run: python omega_v5_swarm.py")
    print()
    print("Killswitch: touch omega_swarm/kill.omega to stop")
    print()


if __name__ == '__main__':
    main()
