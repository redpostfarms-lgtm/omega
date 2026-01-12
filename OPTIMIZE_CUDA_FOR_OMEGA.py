#!/usr/bin/env python3
"""
Optimize CUDA for Omega
=======================
Configures CUDA for optimal GPU performance with Omega's components.
"""

import sys
import os
from pathlib import Path
import subprocess
import json

def check_cuda_installation():
    """Check CUDA installation and GPU availability"""
    print("=" * 80)
    print(" " * 25 + "CUDA OPTIMIZATION FOR OMEGA")
    print("=" * 80)
    print()
    
    print("[1/5] Checking CUDA installation...")
    print("-" * 80)
    
    # Check nvcc
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = [l for l in result.stdout.split('\n') if 'release' in l.lower()]
            if version_line:
                print(f"  [OK] CUDA installed: {version_line[0].strip()}")
            else:
                print(f"  [OK] CUDA compiler found")
        else:
            print(f"  [ERROR] CUDA compiler not working")
            return False
    except FileNotFoundError:
        print(f"  [ERROR] CUDA compiler (nvcc) not found")
        print(f"  [INFO] CUDA may not be in PATH")
        return False
    except Exception as e:
        print(f"  [ERROR] Error checking CUDA: {e}")
        return False
    
    # Check nvidia-smi
    print()
    print("[2/5] Checking GPU and driver...")
    print("-" * 80)
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,compute_cap,driver_version,memory.total", "--format=csv,noheader"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split('\n')[0]
            print(f"  [OK] GPU found: {gpu_info}")
        else:
            print(f"  [WARN] nvidia-smi not working")
    except FileNotFoundError:
        print(f"  [WARN] nvidia-smi not found")
    except Exception as e:
        print(f"  [WARN] Error checking GPU: {e}")
    
    return True

def check_pytorch_cuda():
    """Check if PyTorch can use CUDA"""
    print()
    print("[3/5] Checking PyTorch CUDA support...")
    print("-" * 80)
    
    try:
        import torch
        print(f"  [OK] PyTorch version: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"  [OK] CUDA available in PyTorch")
            print(f"  [OK] CUDA version: {torch.version.cuda}")
            print(f"  [OK] GPU count: {torch.cuda.device_count()}")
            if torch.cuda.device_count() > 0:
                print(f"  [OK] GPU name: {torch.cuda.get_device_name(0)}")
                print(f"  [OK] GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            print(f"  [WARN] CUDA not available in PyTorch")
            print(f"  [INFO] PyTorch may not be compiled with CUDA support")
            return False
    except ImportError:
        print(f"  [WARN] PyTorch not installed")
        return False
    except Exception as e:
        print(f"  [WARN] Error checking PyTorch CUDA: {e}")
        return False
    
    return cuda_available

def optimize_cuda_settings():
    """Configure CUDA environment variables for optimal performance"""
    print()
    print("[4/5] Optimizing CUDA settings...")
    print("-" * 80)
    
    optimizations = {
        "CUDA_LAUNCH_BLOCKING": "0",  # Async execution for better performance
        "CUDA_CACHE_DISABLE": "0",  # Enable CUDA cache
        "CUDA_FORCE_PTX_JIT": "0",  # Use pre-compiled kernels
        "TORCH_CUDA_ARCH_LIST": "",  # Auto-detect GPU architecture
    }
    
    config_file = Path(__file__).parent / "cuda_optimization_config.json"
    with open(config_file, 'w') as f:
        json.dump(optimizations, f, indent=2)
    
    print(f"  [OK] CUDA optimization config saved: {config_file.name}")
    
    # Create environment setup script
    env_script = Path(__file__).parent / "setup_cuda_env.bat"
    with open(env_script, 'w') as f:
        f.write("@echo off\n")
        f.write("REM CUDA Environment Variables for Omega\n")
        f.write("REM Set these before running Omega for optimal GPU performance\n\n")
        for key, value in optimizations.items():
            if value:
                f.write(f'set {key}={value}\n')
            else:
                f.write(f'REM {key} - Auto-detected\n')
    
    print(f"  [OK] Environment script created: {env_script.name}")
    
    return optimizations

def verify_omega_integration():
    """Verify Omega can use CUDA"""
    print()
    print("[5/5] Verifying Omega GPU integration...")
    print("-" * 80)
    
    omega_gpu_files = [
        "omega_resource_manager.py",
        "omega_full_brain.py",
        "omega_resource_optimized_components.py"
    ]
    
    gpu_integration = False
    for file_path in omega_gpu_files:
        path = Path(__file__).parent / file_path
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'cuda' in content.lower() or 'gpu' in content.lower():
                    print(f"  [OK] GPU code found in: {file_path}")
                    gpu_integration = True
    
    if not gpu_integration:
        print(f"  [WARN] GPU integration code not found in Omega files")
    
    return gpu_integration

def main():
    """Main optimization function"""
    print()
    
    cuda_ok = check_cuda_installation()
    if not cuda_ok:
        print()
        print("[ERROR] CUDA installation check failed")
        print("[INFO] Please ensure CUDA is properly installed")
        return
    
    pytorch_cuda = check_pytorch_cuda()
    if not pytorch_cuda:
        print()
        print("[WARN] PyTorch CUDA support not available")
        print("[INFO] Install PyTorch with CUDA support: pip install torch --index-url https://download.pytorch.org/whl/cu121")
    
    optimizations = optimize_cuda_settings()
    omega_ok = verify_omega_integration()
    
    print()
    print("=" * 80)
    print(" " * 25 + "OPTIMIZATION COMPLETE")
    print("=" * 80)
    print()
    
    print("CUDA Status:")
    print(f"  ✅ CUDA installed: Yes")
    print(f"  {'✅' if pytorch_cuda else '⚠️'} PyTorch CUDA: {'Available' if pytorch_cuda else 'Not available'}")
    print(f"  {'✅' if omega_ok else '⚠️'} Omega integration: {'Found' if omega_ok else 'Needs checking'}")
    print()
    
    print("Optimizations Applied:")
    print(f"  ✅ CUDA settings configured")
    print(f"  ✅ Environment script created")
    print()
    
    print("Next Steps:")
    if not pytorch_cuda:
        print("  1. Install PyTorch with CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print("  2. Use CUDA environment script: setup_cuda_env.bat")
    print("  3. Test GPU acceleration with Omega")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
