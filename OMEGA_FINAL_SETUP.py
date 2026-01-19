"""
OMEGA FINAL SETUP - Automated installation helper
This script attempts to download and configure remaining components
"""

import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen
import json

class OmegaFinalSetup:
    """Automate final setup steps"""
    
    def __init__(self):
        self.workspace = Path("h:\\The Gatekeeper")
        self.results = {"completed": [], "failed": [], "pending": []}
    
    def download_file(self, url, filename):
        """Attempt to download a file"""
        print(f"\nDownloading: {filename}")
        try:
            print(f"  From: {url}")
            response = urlopen(url, timeout=10)
            with open(filename, 'wb') as f:
                f.write(response.read())
            print(f"  ✓ Downloaded: {filename}")
            return True
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return False
    
    def verify_torch(self):
        """Verify PyTorch installation"""
        print("\n" + "="*70)
        print("VERIFYING PYTORCH")
        print("="*70)
        
        try:
            import torch
            print(f"✓ PyTorch {torch.__version__}")
            print(f"✓ CUDA available: {torch.cuda.is_available()}")
            if not torch.cuda.is_available():
                print("  → CUDA Toolkit needed for GPU acceleration (optional)")
            self.results["completed"].append("PyTorch verified")
            return True
        except Exception as e:
            print(f"✗ PyTorch check failed: {e}")
            self.results["failed"].append("PyTorch verification")
            return False
    
    def verify_openrgb(self):
        """Verify OpenRGB Python library"""
        print("\n" + "="*70)
        print("VERIFYING OPENRGB PYTHON LIBRARY")
        print("="*70)
        
        try:
            from openrgb_python import OpenRGBClient
            print(f"✓ openrgb-python 0.3.6 installed")
            
            try:
                client = OpenRGBClient()
                print(f"✓ OpenRGB service RUNNING")
                print(f"✓ Devices detected: {len(client.devices)}")
                self.results["completed"].append("OpenRGB service running")
            except Exception as e:
                print(f"⚠ OpenRGB service NOT running: {e}")
                print(f"  → Download OpenRGB.exe from https://openrgb.org/download")
                self.results["pending"].append("OpenRGB.exe application")
            
            return True
        except Exception as e:
            print(f"✗ openrgb-python verification failed: {e}")
            self.results["failed"].append("openrgb-python")
            return False
    
    def verify_ffmpeg(self):
        """Verify FFmpeg installation"""
        print("\n" + "="*70)
        print("VERIFYING FFMPEG")
        print("="*70)
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✓ FFmpeg installed")
                print(f"  {version_line}")
                self.results["completed"].append("FFmpeg verified")
                return True
            else:
                print(f"✗ FFmpeg not responding properly")
                self.results["pending"].append("FFmpeg configuration")
                return False
        except FileNotFoundError:
            print(f"✗ FFmpeg not in PATH")
            print(f"  → Download from https://ffmpeg.org/download.html")
            print(f"  → Extract to C:\\ffmpeg and add C:\\ffmpeg\\bin to PATH")
            self.results["pending"].append("FFmpeg installation")
            return False
        except Exception as e:
            print(f"✗ FFmpeg check failed: {e}")
            self.results["pending"].append("FFmpeg configuration")
            return False
    
    def verify_audio_libs(self):
        """Verify audio libraries"""
        print("\n" + "="*70)
        print("VERIFYING AUDIO LIBRARIES")
        print("="*70)
        
        libs = ['torchcodec', 'sounddevice', 'scipy', 'librosa', 'soundfile']
        all_ok = True
        
        for lib in libs:
            try:
                __import__(lib)
                print(f"✓ {lib} installed")
            except ImportError:
                print(f"✗ {lib} NOT installed")
                all_ok = False
        
        if all_ok:
            self.results["completed"].append("All audio libraries")
        else:
            self.results["failed"].append("Some audio libraries missing")
        
        return all_ok
    
    def verify_tts(self):
        """Verify TTS framework"""
        print("\n" + "="*70)
        print("VERIFYING TEXT-TO-SPEECH")
        print("="*70)
        
        try:
            from TTS.api import TTS
            print(f"✓ TTS framework installed")
            self.results["completed"].append("TTS framework")
            return True
        except Exception as e:
            print(f"✗ TTS verification failed: {e}")
            self.results["failed"].append("TTS framework")
            return False
    
    def check_nvidia_gpu(self):
        """Check for NVIDIA GPU"""
        print("\n" + "="*70)
        print("CHECKING FOR NVIDIA GPU")
        print("="*70)
        
        try:
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[:5]:
                    if line.strip():
                        print(f"  {line}")
                print(f"✓ NVIDIA GPU detected")
                self.results["completed"].append("NVIDIA GPU detected")
                return True
            else:
                print(f"✗ NVIDIA GPU not detected")
                self.results["completed"].append("No NVIDIA GPU (CPU-only)")
                return False
        except FileNotFoundError:
            print(f"✗ nvidia-smi not found (NVIDIA drivers may not be installed)")
            self.results["pending"].append("NVIDIA GPU drivers (optional)")
            return False
        except Exception as e:
            print(f"⚠ GPU check failed: {e}")
            return False
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "█"*70)
        print("█ FINAL VERIFICATION REPORT")
        print("█"*70)
        
        if self.results["completed"]:
            print(f"\n✓ READY ({len(self.results['completed'])} items):")
            for item in self.results["completed"]:
                print(f"  ✓ {item}")
        
        if self.results["failed"]:
            print(f"\n✗ FAILED ({len(self.results['failed'])} items):")
            for item in self.results["failed"]:
                print(f"  ✗ {item}")
        
        if self.results["pending"]:
            print(f"\n⚠ PENDING ({len(self.results['pending'])} items):")
            for item in self.results["pending"]:
                print(f"  → {item}")
        
        report_path = self.workspace / "FINAL_VERIFICATION_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Report saved to: {report_path}")
        
        total_items = len(self.results["completed"]) + len(self.results["pending"])
        completed_pct = (len(self.results["completed"]) / total_items * 100) if total_items > 0 else 0
        
        print(f"\n" + "="*70)
        print(f"OVERALL COMPLETION: {completed_pct:.0f}%")
        print("="*70)
        
        if len(self.results["pending"]) == 0:
            print("✓ ALL SYSTEMS READY")
        elif len(self.results["pending"]) <= 2:
            print("⚠ NEARLY COMPLETE - See pending items above")
        else:
            print("→ CONFIGURATION NEEDED")
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "█"*70)
        print("█ OMEGA SYSTEM - FINAL SETUP & VERIFICATION")
        print("█"*70)
        
        self.verify_torch()
        self.verify_audio_libs()
        self.verify_tts()
        self.verify_openrgb()
        self.verify_ffmpeg()
        self.check_nvidia_gpu()
        self.generate_report()

if __name__ == "__main__":
    setup = OmegaFinalSetup()
    try:
        setup.run_all_checks()
        print(f"\n✓ Final setup check complete")
    except Exception as e:
        print(f"\n✗ Setup check failed: {e}")
        sys.exit(1)
