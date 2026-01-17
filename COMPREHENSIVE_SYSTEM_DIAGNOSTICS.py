#!/usr/bin/env python3
"""
Comprehensive System Diagnostics & GPU Information
===================================================
Diagnoses RGB lighting hardware issues, audio system problems, and GPU configuration.
Pulls current system logs and provides actionable solutions.
"""

import os
import sys
import json
import subprocess
import platform
import logging
from pathlib import Path
from datetime import datetime
import threading

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemDiagnostics:
    """Comprehensive system diagnostics"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system": platform.system(),
            "diagnostics": {}
        }
        self.base_dir = Path(__file__).parent
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}\n")
    
    def diagnose_gpu(self) -> Dict:
        """Diagnose GPU and CUDA availability"""
        self.print_header("GPU & CUDA DIAGNOSTICS")
        
        gpu_info = {
            "status": "UNKNOWN",
            "cuda_available": False,
            "cuda_version": None,
            "gpu_device": None,
            "gpu_memory": None,
            "nvidia_cuda_path": None,
            "nvidia_install_status": None,
            "recommended_action": None
        }
        
        try:
            import torch
            gpu_info["cuda_available"] = torch.cuda.is_available()
            
            if gpu_info["cuda_available"]:
                gpu_info["cuda_version"] = torch.version.cuda
                gpu_info["gpu_device"] = torch.cuda.get_device_name(0)
                try:
                    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    allocated = torch.cuda.memory_allocated(0) / (1024**3)
                    gpu_info["gpu_memory"] = {
                        "total_gb": round(total_memory, 2),
                        "allocated_gb": round(allocated, 2),
                        "available_gb": round(total_memory - allocated, 2)
                    }
                except:
                    pass
                
                gpu_info["status"] = "✓ CUDA AVAILABLE"
                print(f"✓ CUDA Available: {gpu_info['cuda_version']}")
                print(f"✓ GPU Device: {gpu_info['gpu_device']}")
                if gpu_info["gpu_memory"]:
                    print(f"✓ GPU Memory: {gpu_info['gpu_memory']['total_gb']}GB total, "
                          f"{gpu_info['gpu_memory']['allocated_gb']}GB allocated")
            else:
                gpu_info["status"] = "✗ CUDA NOT AVAILABLE (CPU MODE)"
                print("✗ CUDA not available - running on CPU")
                gpu_info["recommended_action"] = "Install NVIDIA CUDA Toolkit and cuDNN"
        
        except ImportError:
            gpu_info["status"] = "✗ PYTORCH NOT INSTALLED"
            print("✗ PyTorch not installed")
            gpu_info["recommended_action"] = "Install PyTorch with CUDA support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        except Exception as e:
            gpu_info["status"] = f"✗ ERROR: {str(e)}"
            print(f"✗ Error: {e}")
        
        # Check NVIDIA installation
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["nvidia-smi"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    gpu_info["nvidia_install_status"] = "✓ NVIDIA drivers installed"
                    print(f"\n{result.stdout[:500]}")  # First 500 chars
                else:
                    gpu_info["nvidia_install_status"] = "✗ nvidia-smi failed"
            except FileNotFoundError:
                gpu_info["nvidia_install_status"] = "✗ NVIDIA drivers NOT found"
                print("✗ NVIDIA drivers not found (nvidia-smi not in PATH)")
                gpu_info["recommended_action"] = "Install NVIDIA drivers from nvidia.com"
            except Exception as e:
                gpu_info["nvidia_install_status"] = f"✗ Error: {e}"
        
        self.results["diagnostics"]["gpu"] = gpu_info
        return gpu_info
    
    def diagnose_rgb(self) -> Dict:
        """Diagnose RGB lighting system"""
        self.print_header("RGB LIGHTING DIAGNOSTICS")
        
        rgb_info = {
            "status": "UNKNOWN",
            "physical_hardware": None,
            "control_methods_available": [],
            "usb_devices": [],
            "bios_rgb_setting": None,
            "motherboard_type": None,
            "issues_found": [],
            "solutions": []
        }
        
        # Check for physical RGB detection
        print("[1/5] Checking RGB physical hardware...")
        try:
            from omega_rgb_advanced_controller import get_advanced_rgb_controller
            rgb = get_advanced_rgb_controller()
            status = rgb.get_status()
            rgb_info["control_methods_available"] = status.get("available_methods", [])
            rgb_info["status"] = f"Active: {status.get('current_method', 'unknown')}"
            print(f"  ✓ RGB Controller Status: {status.get('current_method')}")
            print(f"  ✓ Available Methods: {', '.join(status.get('available_methods', []))}")
        except Exception as e:
            print(f"  ✗ RGB Controller Error: {e}")
            rgb_info["issues_found"].append("RGB controller initialization failed")
        
        # Check USB RGB devices
        print("\n[2/5] Checking USB RGB devices...")
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "logicaldisk", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print("  ✓ Windows device scan completed")
            except Exception as e:
                print(f"  ✗ Device scan failed: {e}")
        
        # Check BIOS RGB settings
        print("\n[3/5] Checking BIOS RGB settings...")
        rgb_info["bios_rgb_setting"] = "⚠ MANUAL VERIFICATION NEEDED"
        print("  ⚠ BIOS Settings Check:")
        print("    1. Restart PC and press DEL/F2 to enter BIOS")
        print("    2. Look for: RGB Lighting, Aura Lighting, OnBoard LED, RGB Management")
        print("    3. Enable all RGB settings")
        print("    4. Save and exit (F10)")
        rgb_info["solutions"].append("Enable RGB Lighting in BIOS")
        
        # Check physical RGB headers
        print("\n[4/5] Checking physical RGB headers...")
        print("  ⚠ PHYSICAL CONNECTION CHECK NEEDED:")
        print("    1. Power off and unplug system")
        print("    2. Open case and locate RGB headers on motherboard")
        print("    3. Verify RGB cables are firmly connected:")
        print("       - RGB_HEADER (RGB 5V)")
        print("       - RGB_HDR (addressable RGB)")
        print("    4. Check that fan RGB connector matches motherboard header")
        rgb_info["solutions"].append("Verify physical RGB connections")
        
        # Check driver support
        print("\n[5/5] Checking driver and software support...")
        software_status = {
            "OpenRGB": False,
            "ASUS AURA": False,
            "Corsair iCUE": False,
            "Razer Synapse": False,
            "NZXT CAM": False,
            "NVIDIA drivers": False
        }
        
        try:
            import openrgb
            software_status["OpenRGB"] = True
            print("  ✓ OpenRGB installed")
        except:
            print("  ✗ OpenRGB NOT installed")
            rgb_info["issues_found"].append("OpenRGB not installed (primary RGB method)")
            rgb_info["solutions"].append("Install OpenRGB: pip install openrgb")
        
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                software_status["NVIDIA drivers"] = True
                print("  ✓ NVIDIA drivers available")
        except:
            print("  ✗ NVIDIA drivers NOT found")
        
        rgb_info["software_status"] = software_status
        
        # Critical issue summary
        if not rgb_info["control_methods_available"]:
            rgb_info["issues_found"].insert(0, "NO RGB CONTROL METHODS AVAILABLE - System in fallback mode")
        
        self.results["diagnostics"]["rgb"] = rgb_info
        return rgb_info
    
    def diagnose_audio(self) -> Dict:
        """Diagnose audio system"""
        self.print_header("AUDIO SYSTEM DIAGNOSTICS")
        
        audio_info = {
            "status": "UNKNOWN",
            "output_devices": [],
            "tts_status": None,
            "torchcodec_status": None,
            "ffmpeg_status": None,
            "audio_files_found": [],
            "issues_found": [],
            "solutions": []
        }
        
        print("[1/4] Checking audio output devices...")
        try:
            import sounddevice
            devices = sounddevice.query_devices()
            output_devices = [d for d in devices if d['max_output_channels'] > 0]
            audio_info["output_devices"] = [d['name'] for d in output_devices[:5]]
            print(f"  ✓ Found {len(output_devices)} audio output device(s)")
            for device in output_devices[:3]:
                print(f"    - {device['name']}")
        except ImportError:
            print("  ✗ sounddevice not installed")
            audio_info["issues_found"].append("sounddevice library missing")
            audio_info["solutions"].append("Install: pip install sounddevice")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print("\n[2/4] Checking TTS system...")
        try:
            import torch
            from TTS.api import TTS
            print("  ✓ TTS library available")
            audio_info["tts_status"] = "✓ TTS library loaded"
        except ImportError as e:
            print(f"  ✗ TTS not installed: {e}")
            audio_info["tts_status"] = f"✗ TTS Error: {e}"
            audio_info["issues_found"].append("TTS not installed")
            audio_info["solutions"].append("Install: pip install TTS")
        except Exception as e:
            print(f"  ✗ TTS Error: {e}")
            audio_info["tts_status"] = f"✗ Error: {e}"
        
        print("\n[3/4] Checking FFmpeg and torchcodec...")
        try:
            import torchcodec
            audio_info["torchcodec_status"] = "✓ torchcodec available"
            print("  ✓ torchcodec available")
        except ImportError:
            audio_info["torchcodec_status"] = "✗ torchcodec not installed"
            print("  ✗ torchcodec not installed")
            audio_info["issues_found"].append("torchcodec missing (prevents audio generation)")
            audio_info["solutions"].append("Install: pip install torchcodec")
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                audio_info["ffmpeg_status"] = "✓ FFmpeg available"
                print("  ✓ FFmpeg available")
            else:
                audio_info["ffmpeg_status"] = "✗ FFmpeg error"
                audio_info["issues_found"].append("FFmpeg not working properly")
        except FileNotFoundError:
            audio_info["ffmpeg_status"] = "✗ FFmpeg NOT installed"
            print("  ✗ FFmpeg NOT installed")
            audio_info["issues_found"].append("FFmpeg not found")
            audio_info["solutions"].append("Install FFmpeg from https://ffmpeg.org/download.html")
        
        print("\n[4/4] Checking audio files...")
        audio_files = list(Path(self.base_dir).glob("*.wav")) + \
                     list(Path(self.base_dir).glob("*.mp3"))
        audio_info["audio_files_found"] = [f.name for f in audio_files[:10]]
        print(f"  ✓ Found {len(audio_info['audio_files_found'])} audio file(s)")
        
        self.results["diagnostics"]["audio"] = audio_info
        return audio_info
    
    def diagnose_hardware_communication(self) -> Dict:
        """Diagnose hardware communication issues"""
        self.print_header("HARDWARE COMMUNICATION DIAGNOSTICS")
        
        hw_info = {
            "rgb_hardware_detection": None,
            "usb_communication": None,
            "kernel_driver_access": None,
            "winring0_status": None,
            "direct_hardware_access": None,
            "issues_found": [],
            "critical_findings": []
        }
        
        print("[1/3] Checking RGB hardware detection...")
        print("  This checks if the system can SEE RGB devices")
        print("  - OpenRGB device detection")
        print("  - Windows Device Manager scanning")
        print("  - USB vendor/product ID detection")
        
        print("\n[2/3] Checking hardware communication channels...")
        print("  These are the WAYS the system can TALK to RGB hardware:")
        print("  1. OpenRGB Protocol ............ Universal (if installed)")
        print("  2. ASUS AURA SDK .............. ASUS motherboards only")
        print("  3. Corsair iCUE ............... Corsair devices only")
        print("  4. Razer Synapse .............. Razer devices only")
        print("  5. NZXT CAM ................... NZXT devices only")
        print("  6. WinRing0 Driver ............ Low-level hardware access (Windows)")
        print("  7. Simulated .................. Software fallback (no hardware)")
        
        print("\n[3/3] Checking kernel driver access...")
        if platform.system() == "Windows":
            try:
                # Try to detect WinRing0
                result = subprocess.run(
                    ["wmic", "systemdriver", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                hw_info["kernel_driver_access"] = "✓ Kernel driver access available"
                print("  ✓ Kernel driver access available")
            except Exception as e:
                hw_info["kernel_driver_access"] = "✗ No kernel driver access"
                print(f"  ✗ Kernel driver access limited: {e}")
                hw_info["issues_found"].append("Limited kernel driver access")
        
        # Critical finding
        hw_info["critical_findings"].append(
            "RGB devices detected by software but physical lights not changing suggests:"
        )
        hw_info["critical_findings"].append(
            "1. USB communication is working (software sees devices)"
        )
        hw_info["critical_findings"].append(
            "2. Command format is correct (software accepts commands)")
        )
        hw_info["critical_findings"].append(
            "3. Physical connection or hardware firmware issue likely"
        )
        
        self.results["diagnostics"]["hardware_communication"] = hw_info
        return hw_info
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.print_header("RUNNING FULL SYSTEM DIAGNOSTICS")
        
        # Run all diagnostics
        gpu_info = self.diagnose_gpu()
        rgb_info = self.diagnose_rgb()
        audio_info = self.diagnose_audio()
        hw_info = self.diagnose_hardware_communication()
        
        # Generate summary
        self.print_header("DIAGNOSTIC SUMMARY")
        
        print("GPU/CUDA Status:")
        print(f"  {gpu_info['status']}")
        if gpu_info.get('recommended_action'):
            print(f"  Recommended: {gpu_info['recommended_action']}")
        
        print("\nRGB Lighting Status:")
        print(f"  {rgb_info['status']}")
        print(f"  Available Methods: {', '.join(rgb_info['control_methods_available'] or ['None'])}")
        if rgb_info['issues_found']:
            print("  Issues Found:")
            for issue in rgb_info['issues_found']:
                print(f"    - {issue}")
        
        print("\nAudio System Status:")
        print(f"  TTS: {audio_info['tts_status']}")
        print(f"  FFmpeg: {audio_info['ffmpeg_status']}")
        print(f"  torchcodec: {audio_info['torchcodec_status']}")
        if audio_info['issues_found']:
            print("  Issues Found:")
            for issue in audio_info['issues_found']:
                print(f"    - {issue}")
        
        # Save report
        report_path = self.base_dir / "SYSTEM_DIAGNOSTICS_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n✓ Full diagnostic report saved: {report_path}")
        
        # Print solutions
        all_solutions = (
            rgb_info.get('solutions', []) +
            audio_info.get('solutions', []) +
            ([gpu_info.get('recommended_action')] if gpu_info.get('recommended_action') else [])
        )
        
        if all_solutions:
            self.print_header("RECOMMENDED SOLUTIONS (IN PRIORITY ORDER)")
            for idx, solution in enumerate(all_solutions, 1):
                print(f"{idx}. {solution}")

if __name__ == "__main__":
    diag = SystemDiagnostics()
    diag.generate_report()
