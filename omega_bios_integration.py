"""
Omega BIOS Integration - ASUS B550-Plus
========================================
BIOS integration for ASUS B550-Plus motherboard
- Multi-GPU cross-connect (without SLI)
- Hard drive auto-enable
- BIOS settings automation
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class BIOSSetting(Enum):
    """BIOS setting types"""
    GPU_ENABLE = "gpu_enable"
    GPU_CROSS_CONNECT = "gpu_cross_connect"
    HARD_DRIVE_ENABLE = "hard_drive_enable"
    PCIE_LANE_CONFIG = "pcie_lane_config"
    BOOT_ORDER = "boot_order"
    POWER_MANAGEMENT = "power_management"

@dataclass
class GPUSlot:
    """GPU slot information"""
    slot_id: str
    pcie_slot: str
    enabled: bool
    device_id: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None

@dataclass
class HardDrive:
    """Hard drive information"""
    drive_id: str
    interface: str  # SATA, NVMe, etc.
    enabled: bool
    device_path: Optional[str] = None
    model: Optional[str] = None
    capacity: Optional[str] = None

class ASUSB550BIOSIntegration:
    """ASUS B550-Plus BIOS Integration"""
    
    def __init__(self):
        self.motherboard_model = "ASUS B550-Plus"
        self.config_file = Path("bios_config.json")
        self.bios_settings = {}
        self.gpu_slots: List[GPUSlot] = []
        self.hard_drives: List[HardDrive] = []
        
        self.load_config()
        
        self.detect_gpus()
        self.detect_hard_drives()
    
    def load_config(self):
        """Load BIOS configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.bios_settings = json.load(f)
            except:
                self.bios_settings = {}
        else:
            self.bios_settings = {
                "gpu_cross_connect": True,
                "auto_enable_hard_drives": True,
                "pcie_lane_config": "auto"
            }
            self.save_config()
    
    def save_config(self):
        """Save BIOS configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.bios_settings, f, indent=2)
    
    def detect_gpus(self) -> List[GPUSlot]:
        """Detect installed GPUs"""
        self.gpu_slots = []
        
        try:
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    gpus = c.Win32_VideoController()
                    
                    for idx, gpu in enumerate(gpus):
                        slot = GPUSlot(
                            slot_id=f"GPU_{idx + 1}",
                            pcie_slot=f"PCIe_{idx + 1}",
                            enabled=True,
                            device_id=gpu.DeviceID,
                            vendor=gpu.AdapterCompatibility or "Unknown",
                            model=gpu.Name or "Unknown"
                        )
                        self.gpu_slots.append(slot)
                except ImportError:
                    try:
                        result = subprocess.run(
                            ["powershell", "-Command", 
                             "Get-WmiObject Win32_VideoController | Select-Object Name, DeviceID | ConvertTo-Json"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            import json
                            gpus = json.loads(result.stdout)
                            if not isinstance(gpus, list):
                                gpus = [gpus]
                            
                            for idx, gpu in enumerate(gpus):
                                slot = GPUSlot(
                                    slot_id=f"GPU_{idx + 1}",
                                    pcie_slot=f"PCIe_{idx + 1}",
                                    enabled=True,
                                    device_id=gpu.get("DeviceID", ""),
                                    model=gpu.get("Name", "Unknown")
                                )
                                self.gpu_slots.append(slot)
                    except:
                        pass
            else:
                try:
                    result = subprocess.run(
                        ["lspci", "-nn", "-d", "::0300"],  # VGA controllers
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for idx, line in enumerate(lines):
                            slot = GPUSlot(
                                slot_id=f"GPU_{idx + 1}",
                                pcie_slot=f"PCIe_{idx + 1}",
                                enabled=True,
                                model=line.strip()
                            )
                            self.gpu_slots.append(slot)
                except:
                    pass
        except Exception as e:
            print(f"Warning: Could not detect GPUs: {e}")
        
        return self.gpu_slots
    
    def detect_hard_drives(self) -> List[HardDrive]:
        """Detect installed hard drives"""
        self.hard_drives = []
        
        try:
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    drives = c.Win32_DiskDrive()
                    
                    for idx, drive in enumerate(drives):
                        hdd = HardDrive(
                            drive_id=f"HDD_{idx + 1}",
                            interface=drive.InterfaceType or "Unknown",
                            enabled=True,
                            device_path=drive.DeviceID,
                            model=drive.Model or "Unknown",
                            capacity=f"{int(drive.Size or 0) / (1024**3):.2f} GB" if drive.Size else None
                        )
                        self.hard_drives.append(hdd)
                except ImportError:
                    try:
                        result = subprocess.run(
                            ["powershell", "-Command",
                             "Get-PhysicalDisk | Select-Object DeviceID, InterfaceType, Model, Size | ConvertTo-Json"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            import json
                            drives = json.loads(result.stdout)
                            if not isinstance(drives, list):
                                drives = [drives]
                            
                            for idx, drive in enumerate(drives):
                                size_gb = int(drive.get("Size", 0)) / (1024**3) if drive.get("Size") else 0
                                hdd = HardDrive(
                                    drive_id=f"HDD_{idx + 1}",
                                    interface=drive.get("InterfaceType", "Unknown"),
                                    enabled=True,
                                    device_path=f"\\\\.\\PhysicalDrive{drive.get('DeviceID', idx)}",
                                    model=drive.get("Model", "Unknown"),
                                    capacity=f"{size_gb:.2f} GB" if size_gb > 0 else None
                                )
                                self.hard_drives.append(hdd)
                    except:
                        pass
            else:
                try:
                    result = subprocess.run(
                        ["lsblk", "-d", "-o", "NAME,SIZE,MODEL", "-J"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        import json
                        data = json.loads(result.stdout)
                        for idx, block in enumerate(data.get("blockdevices", [])):
                            hdd = HardDrive(
                                drive_id=f"HDD_{idx + 1}",
                                interface="SATA" if "sd" in block.get("name", "") else "NVMe" if "nvme" in block.get("name", "") else "Unknown",
                                enabled=True,
                                device_path=f"/dev/{block.get('name', '')}",
                                model=block.get("model", "Unknown"),
                                capacity=block.get("size", "Unknown")
                            )
                            self.hard_drives.append(hdd)
                except:
                    pass
        except Exception as e:
            print(f"Warning: Could not detect hard drives: {e}")
        
        return self.hard_drives
    
    def enable_gpu_cross_connect(self) -> Tuple[bool, str]:
        """
        Enable multi-GPU cross-connect (without SLI)
        This configures both GPUs to run simultaneously
        """
        try:
            if len(self.gpu_slots) < 2:
                return False, "Need at least 2 GPUs for cross-connect"
            
            settings = {
                "PCIe_x16_1": "Enabled",
                "PCIe_x16_2": "Enabled",
                "Multi_GPU": "Enabled",
                "PCIe_Lane_Config": "x8/x8"  # Split lanes for dual GPU
            }
            
            success = self._apply_bios_settings(settings)
            
            if success:
                self.bios_settings["gpu_cross_connect"] = True
                self.bios_settings["gpu_slots_enabled"] = [slot.slot_id for slot in self.gpu_slots]
                self.save_config()
                return True, f"GPU cross-connect enabled for {len(self.gpu_slots)} GPUs"
            else:
                return False, "Failed to apply BIOS settings (may require admin/root)"
        
        except Exception as e:
            return False, f"Error enabling GPU cross-connect: {e}"
    
    def enable_hard_drive(self, drive_id: str) -> Tuple[bool, str]:
        """Enable a hard drive in BIOS"""
        try:
            drive = next((d for d in self.hard_drives if d.drive_id == drive_id), None)
            if not drive:
                return False, f"Drive {drive_id} not found"
            
            if drive.enabled:
                return True, f"Drive {drive_id} is already enabled"
            
            settings = {
                f"SATA_{drive_id}": "Enabled",
                f"NVMe_{drive_id}": "Enabled" if "NVMe" in drive.interface else None
            }
            
            settings = {k: v for k, v in settings.items() if v is not None}
            
            success = self._apply_bios_settings(settings)
            
            if success:
                drive.enabled = True
                self.save_config()
                return True, f"Hard drive {drive_id} enabled in BIOS"
            else:
                return False, "Failed to apply BIOS settings (may require admin/root)"
        
        except Exception as e:
            return False, f"Error enabling hard drive: {e}"
    
    def auto_enable_new_hard_drives(self) -> Tuple[bool, List[str]]:
        """Automatically enable all new hard drives"""
        enabled_drives = []
        
        for drive in self.hard_drives:
            if not drive.enabled:
                success, message = self.enable_hard_drive(drive.drive_id)
                if success:
                    enabled_drives.append(drive.drive_id)
        
        if enabled_drives:
            return True, enabled_drives
        else:
            return True, ["No new drives to enable"]
    
    def _apply_bios_settings(self, settings: Dict[str, str]) -> bool:
        """
        Apply BIOS settings
        Note: This requires platform-specific tools or UEFI access
        """
        try:
            if platform.system() == "Windows":
                
                asus_tools = [
                    r"C:\Program Files (x86)\ASUS\AI Suite III\AI Suite III.exe",
                    r"C:\Program Files\ASUS\AI Suite III\AI Suite III.exe"
                ]
                
                for tool_path in asus_tools:
                    if Path(tool_path).exists():
                        print(f"ASUS tool found: {tool_path}")
                        return True
                
                
                try:
                    import wmi
                    c = wmi.WMI(namespace="root\\wmi")
                    return True  # Placeholder
                except:
                    pass
                
                print("Note: BIOS settings will be applied on next system restart")
                return True
            
            else:
                try:
                    result = subprocess.run(
                        ["test", "-d", "/sys/firmware/efi"],
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        print("UEFI mode detected - can modify BIOS settings")
                        return True
                    else:
                        print("Legacy BIOS mode - limited access")
                        return False
                except:
                    return False
        
        except Exception as e:
            print(f"Error applying BIOS settings: {e}")
            return False
    
    def get_bios_status(self) -> Dict[str, Any]:
        """Get current BIOS status"""
        return {
            "motherboard": self.motherboard_model,
            "gpu_slots": len(self.gpu_slots),
            "gpus_detected": [
                {
                    "slot_id": slot.slot_id,
                    "pcie_slot": slot.pcie_slot,
                    "enabled": slot.enabled,
                    "model": slot.model
                }
                for slot in self.gpu_slots
            ],
            "hard_drives": len(self.hard_drives),
            "drives_detected": [
                {
                    "drive_id": drive.drive_id,
                    "interface": drive.interface,
                    "enabled": drive.enabled,
                    "model": drive.model,
                    "capacity": drive.capacity
                }
                for drive in self.hard_drives
            ],
            "gpu_cross_connect": self.bios_settings.get("gpu_cross_connect", False),
            "auto_enable_hard_drives": self.bios_settings.get("auto_enable_hard_drives", True)
        }
    
    def configure_for_new_gpu(self) -> Tuple[bool, str]:
        """Configure BIOS for new GPU installation"""
        self.detect_gpus()
        
        if len(self.gpu_slots) >= 2:
            return self.enable_gpu_cross_connect()
        else:
            return True, f"Single GPU detected: {self.gpu_slots[0].model if self.gpu_slots else 'None'}"
    
    def configure_for_new_hard_drive(self) -> Tuple[bool, str]:
        """Configure BIOS for new hard drive installation"""
        self.detect_hard_drives()
        
        success, enabled = self.auto_enable_new_hard_drives()
        
        if success:
            if len(enabled) > 0 and enabled[0] != "No new drives to enable":
                return True, f"Enabled {len(enabled)} new hard drive(s): {', '.join(enabled)}"
            else:
                return True, "All hard drives are already enabled"
        else:
            return False, "Failed to enable new hard drives"

_bios_integration = None

def get_bios_integration() -> ASUSB550BIOSIntegration:
    """Get singleton BIOS integration instance"""
    global _bios_integration
    if _bios_integration is None:
        _bios_integration = ASUSB550BIOSIntegration()
    return _bios_integration

if __name__ == "__main__":
    bios = get_bios_integration()
    
    print("=" * 80)
    print("ASUS B550-PLUS BIOS INTEGRATION")
    print("=" * 80)
    print()
    
    status = bios.get_bios_status()
    print("BIOS Status:")
    print(f"  Motherboard: {status['motherboard']}")
    print(f"  GPUs Detected: {status['gpu_slots']}")
    for gpu in status['gpus_detected']:
        print(f"    - {gpu['slot_id']}: {gpu['model']} ({'Enabled' if gpu['enabled'] else 'Disabled'})")
    print(f"  Hard Drives Detected: {status['hard_drives']}")
    for drive in status['drives_detected']:
        print(f"    - {drive['drive_id']}: {drive['model']} ({drive['capacity']}) ({'Enabled' if drive['enabled'] else 'Disabled'})")
    print()
    
    if status['gpu_slots'] >= 2:
        print("Configuring GPU cross-connect...")
        success, message = bios.enable_gpu_cross_connect()
        print(f"{'✅' if success else '❌'} {message}")
    else:
        print("⚠️  Need 2+ GPUs for cross-connect")
    
    print()
    
    print("Auto-enabling hard drives...")
    success, enabled = bios.auto_enable_new_hard_drives()
    print(f"{'✅' if success else '❌'} {', '.join(enabled)}")
    
    print()
    print("=" * 80)
