#!/usr/bin/env python3
"""
OMEGA SYSTEM - FINAL INSTALLATION & VERIFICATION
==================================================
Complete installation check, remaining tasks, and final verification
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

class OmegaInstallationFinalizer:
    """Complete and verify all installations"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_checks": {},
            "installed_packages": {},
            "missing_components": [],
            "ready_to_use": [],
            "next_steps": []
        }
    
    def check_python_packages(self):
        """Check all installed Python packages"""
        print("\n" + "="*70)
        print("CHECKING PYTHON PACKAGES")
        print("="*70)
        
        packages = {
            "torch": "PyTorch (AI/ML)",
            "torchaudio": "Audio processing",
            "torchcodec": "Audio encoding",
            "sounddevice": "Audio I/O",
            "librosa": "Audio analysis",
            "scipy": "Scientific computing",
            "soundfile": "Audio file handling",
            "openrgb_python": "RGB control",
        }
        
        try:
            from TTS.api import TTS
            packages["TTS"] = "Text-to-speech"
        except:
            pass
        
        for pkg_name, description in packages.items():
            try:
                __import__(pkg_name.replace("-", "_"))
                print(f"✓ {pkg_name:20} - {description}")
                self.results["installed_packages"][pkg_name] = "installed"
            except ImportError:
                print(f"✗ {pkg_name:20} - {description}")
                self.results["installed_packages"][pkg_name] = "missing"
    
    def check_rgb_system(self):
        """Check RGB system status"""
        print("\n" + "="*70)
        print("RGB SYSTEM CHECK")
        print("="*70)
        
        try:
            from omega_rgb_advanced_controller import get_advanced_rgb_controller
            rgb = get_advanced_rgb_controller()
            status = rgb.get_status()
            
            current_method = status.get('current_method', 'Unknown')
            available_methods = status.get('available_methods', [])
            
            print(f"✓ RGB Controller loaded")
            print(f"  Current Method: {current_method}")
            print(f"  Available Methods: {available_methods}")
            
            self.results["system_checks"]["rgb"] = {
                "status": "loaded",
                "method": current_method,
                "available": available_methods
            }
            
            if current_method != "Simulated":
                print(f"  ✓ HARDWARE CONTROL ACTIVE")
                self.results["ready_to_use"].append("RGB Hardware Control")
            else:
                print(f"  ⚠ Using Simulated mode (needs OpenRGB app)")
                self.results["missing_components"].append("OpenRGB Application (service)")
                
        except Exception as e:
            print(f"✗ RGB Controller error: {e}")
            self.results["system_checks"]["rgb"] = "error"
    
    def check_audio_system(self):
        """Check audio system"""
        print("\n" + "="*70)
        print("AUDIO SYSTEM CHECK")
        print("="*70)
        
        audio_ok = True
        
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"✓ FFmpeg installed")
                self.results["ready_to_use"].append("FFmpeg (Audio Encoding)")
            else:
                print(f"✗ FFmpeg not responding")
                audio_ok = False
                self.results["missing_components"].append("FFmpeg")
        except FileNotFoundError:
            print(f"✗ FFmpeg NOT found in PATH")
            audio_ok = False
            self.results["missing_components"].append("FFmpeg")
        except Exception as e:
            print(f"✗ FFmpeg check error: {e}")
            audio_ok = False
            self.results["missing_components"].append("FFmpeg")
        
        # Check audio libraries
        audio_libs = ['torchcodec', 'sounddevice', 'scipy', 'librosa', 'soundfile']
        for lib in audio_libs:
            try:
                __import__(lib)
                print(f"✓ {lib:20} installed")
            except ImportError:
                print(f"✗ {lib:20} NOT installed")
        
        # Check TTS
        try:
            from TTS.api import TTS
            print(f"✓ TTS framework installed")
            if audio_ok:
                self.results["ready_to_use"].append("Audio Generation (TTS)")
        except ImportError:
            print(f"✗ TTS NOT installed")
        
        self.results["system_checks"]["audio"] = "ok" if audio_ok else "ffmpeg_missing"
    
    def check_gpu_system(self):
        """Check GPU/CUDA"""
        print("\n" + "="*70)
        print("GPU/CUDA CHECK")
        print("="*70)
        
        try:
            import torch
            print(f"✓ PyTorch {torch.__version__} installed")
            
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                print(f"✓ CUDA AVAILABLE")
                print(f"  Version: {torch.version.cuda}")
                print(f"  Device: {torch.cuda.get_device_name(0)}")
                try:
                    props = torch.cuda.get_device_properties(0)
                    mem_gb = props.total_memory / (1024**3)
                    print(f"  Memory: {mem_gb:.1f} GB")
                except:
                    pass
                self.results["ready_to_use"].append("GPU Acceleration (CUDA)")
                self.results["system_checks"]["gpu"] = "available"
            else:
                print(f"✗ CUDA NOT available (CPU-only)")
                
                # Check if nvidia-smi works
                try:
                    result = subprocess.run(['nvidia-smi'], 
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        print(f"  ℹ NVIDIA drivers installed, but CUDA Toolkit missing")
                        self.results["missing_components"].append("CUDA Toolkit (for GPU)")
                    else:
                        print(f"  ℹ NVIDIA drivers not responding")
                        self.results["missing_components"].append("NVIDIA GPU Drivers")
                except FileNotFoundError:
                    print(f"  ℹ No NVIDIA GPU detected")
                except:
                    pass
                
                self.results["system_checks"]["gpu"] = "cuda_offline"
                
        except ImportError:
            print(f"✗ PyTorch NOT installed")
            self.results["system_checks"]["gpu"] = "pytorch_missing"
    
    def generate_summary(self):
        """Generate final summary"""
        print("\n" + "█"*70)
        print("█ FINAL SUMMARY")
        print("█"*70)
        
        print(f"\nREADY TO USE ({len(self.results['ready_to_use'])}):")
        for item in self.results['ready_to_use']:
            print(f"  ✓ {item}")
        
        if self.results['missing_components']:
            print(f"\nSTILL NEEDED ({len(self.results['missing_components'])}):")
            for item in self.results['missing_components']:
                print(f"  ✗ {item}")
        
        # Generate next steps
        if "OpenRGB Application (service)" in self.results['missing_components']:
            self.results['next_steps'].append("Download OpenRGB from https://openrgb.org/download and run OpenRGB.exe")
        
        if "FFmpeg" in self.results['missing_components']:
            self.results['next_steps'].append("Download FFmpeg from https://ffmpeg.org/download.html and add to PATH")
        
        if "CUDA Toolkit (for GPU)" in self.results['missing_components'] or \
           "NVIDIA GPU Drivers" in self.results['missing_components']:
            self.results['next_steps'].append("Download CUDA Toolkit and NVIDIA drivers from nvidia.com")
        
        if self.results['next_steps']:
            print(f"\nNEXT STEPS:")
            for i, step in enumerate(self.results['next_steps'], 1):
                print(f"  {i}. {step}")
        else:
            print(f"\n✓ ALL SYSTEMS READY!")
        
        # Completion status
        total_systems = 3
        ready_count = len([x for x in self.results['ready_to_use'] if any(
            sys in x for sys in ['RGB', 'FFmpeg', 'CUDA']
        )])
        
        print(f"\n" + "="*70)
        print(f"COMPLETION STATUS: {ready_count}/{total_systems} systems ready")
        print("="*70)
        
        if ready_count == 3:
            print("✓ SYSTEM FULLY OPERATIONAL")
        elif ready_count >= 2:
            print("⚠ MOST SYSTEMS READY - See next steps above")
        else:
            print("→ CONFIGURATION NEEDED - Follow installation guide")
    
    def save_report(self):
        """Save detailed report"""
        report_file = Path("FINAL_INSTALLATION_REPORT.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n✓ Detailed report saved to: {report_file}")
    
    def run(self):
        """Run complete verification"""
        print("\n" + "█"*70)
        print("█ OMEGA SYSTEM - FINAL INSTALLATION VERIFICATION")
        print("█"*70)
        
        self.check_python_packages()
        self.check_rgb_system()
        self.check_audio_system()
        self.check_gpu_system()
        self.generate_summary()
        self.save_report()
        
        return self.results

if __name__ == "__main__":
    finalizer = OmegaInstallationFinalizer()
    results = finalizer.run()
    
    # Exit with status
    ready_systems = len([x for x in results['ready_to_use'] if any(
        sys in x for sys in ['RGB', 'FFmpeg', 'CUDA']
    )])
    
    sys.exit(0 if ready_systems >= 2 else 1)
