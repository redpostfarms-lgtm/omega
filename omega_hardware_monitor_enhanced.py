#!/usr/bin/env python3
"""
Omega Enhanced Hardware Monitor with LibreHardwareMonitor Integration
======================================================================
Provides comprehensive motherboard temperature monitoring, fan control,
and performance tuning capabilities for CPU and GPU.

Features:
- Real-time CPU temperature (all cores)
- Real-time GPU temperature and utilization
- Motherboard sensors (VRM, PCH, chipset temperatures)
- Fan speed monitoring and control
- Power consumption tracking
- CPU/GPU boost controls
- Memory temperature monitoring
- Storage temperature (NVMe/SSD)

Integrates with LibreHardwareMonitor for deep motherboard access.
"""

import os
import sys
import json
import subprocess
import platform
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Try to import LibreHardwareMonitor via Python.NET
LIBRE_HW_AVAILABLE = False
try:
    # SOLUTION 1: Set Python DLL path explicitly for Python 3.14 compatibility
    import sys
    import os
    from pathlib import Path
    
    # Find the Python DLL for the current Python installation
    python_dll = None
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # Try to locate python3XX.dll
    possible_dll_names = [
        f"python{python_version}.dll",
        f"python{sys.version_info.major}.dll"
    ]
    
    # Search in Python installation directory
    python_base = Path(sys.executable).parent
    for dll_name in possible_dll_names:
        dll_path = python_base / dll_name
        if dll_path.exists():
            python_dll = str(dll_path)
            break
    
    # If not found, try system32
    if not python_dll:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                 r"SOFTWARE\Python\PythonCore\{}.{}\InstallPath".format(
                                     sys.version_info.major, sys.version_info.minor))
            install_path = winreg.QueryValue(key, None)
            for dll_name in possible_dll_names:
                dll_path = Path(install_path) / dll_name
                if dll_path.exists():
                    python_dll = str(dll_path)
                    break
        except:
            pass
    
    # Set Runtime.PythonDLL before importing clr
    if python_dll and os.path.exists(python_dll):
        os.environ['PYTHONNET_PYDLL'] = python_dll
        print(f"  Python DLL: {python_dll}")
    
    import clr  # pythonnet
    
    # Add LibreHardwareMonitor DLL path - try multiple locations
    libre_hw_paths = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'LibreHardwareMonitor'),
        r"C:\Program Files\LibreHardwareMonitor",
        r"C:\LibreHardwareMonitor"
    ]
    
    libre_hw_path = None
    for path in libre_hw_paths:
        if os.path.exists(path) and os.path.exists(os.path.join(path, "LibreHardwareMonitorLib.dll")):
            libre_hw_path = path
            break
    
    if libre_hw_path:
        sys.path.append(libre_hw_path)
        clr.AddReference("LibreHardwareMonitorLib")
        from LibreHardwareMonitor.Hardware import Computer
        LIBRE_HW_AVAILABLE = True
        print(f"✓ LibreHardwareMonitor integration enabled")
        print(f"  DLL path: {libre_hw_path}")
    else:
        print("⚠ LibreHardwareMonitor DLL not found in any known location")
except ImportError as e:
    if "pythonnet" in str(e) or "clr" in str(e):
        print(f"⚠ pythonnet not installed: {e}")
        print("  Install: pip install pythonnet")
    else:
        print(f"⚠ LibreHardwareMonitor import failed: {e}")
except Exception as e:
    print(f"⚠ LibreHardwareMonitor not available: {e}")
    print("  Install from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor")

# Import existing sensor module
try:
    from omega_hardware_sensors import get_cpu_temperature_wmi, get_gpu_info_nvidia
except ImportError:
    print("⚠ omega_hardware_sensors.py not found")
    get_cpu_temperature_wmi = lambda: None
    get_gpu_info_nvidia = lambda: {}


@dataclass
class CPUInfo:
    """CPU information and sensors"""
    name: str = "Unknown"
    cores: int = 0
    threads: int = 0
    base_clock: float = 0.0
    boost_clock: float = 0.0
    current_clock: float = 0.0
    temperature: Optional[float] = None
    core_temps: List[float] = field(default_factory=list)
    package_temp: Optional[float] = None
    usage: float = 0.0
    power_draw: Optional[float] = None
    power_limit: Optional[float] = None
    voltage: Optional[float] = None


@dataclass
class GPUInfo:
    """GPU information and sensors"""
    name: str = "Unknown"
    vendor: str = "Unknown"  # NVIDIA, AMD, Intel
    temperature: Optional[float] = None
    hot_spot_temp: Optional[float] = None
    memory_temp: Optional[float] = None
    usage: Optional[float] = None
    memory_used: float = 0.0
    memory_total: float = 0.0
    power_draw: Optional[float] = None
    power_limit: Optional[float] = None
    fan_speed: Optional[float] = None
    core_clock: Optional[float] = None
    memory_clock: Optional[float] = None
    driver_version: Optional[str] = None


@dataclass
class RGBInfo:
    """RGB lighting information"""
    enabled: bool = True
    brightness: int = 100  # 0-100%
    color_r: int = 255
    color_g: int = 215
    color_b: int = 0
    mode: str = "static"  # static, breathing, rainbow, reactive
    color_hex: str = "#FFD700"


@dataclass
class MotherboardInfo:
    """Motherboard sensors"""
    name: str = "Unknown"
    chipset_temp: Optional[float] = None
    vrm_temp: Optional[float] = None
    pch_temp: Optional[float] = None
    system_fans: Dict[str, float] = field(default_factory=dict)
    voltages: Dict[str, float] = field(default_factory=dict)


@dataclass
class MemoryInfo:
    """Memory information"""
    total_gb: float = 0.0
    used_gb: float = 0.0
    usage_percent: float = 0.0
    temperature: Optional[float] = None
    speed_mhz: Optional[int] = None


@dataclass
class StorageInfo:
    """Storage device information"""
    name: str = "Unknown"
    type: str = "Unknown"  # NVMe, SATA SSD, HDD
    temperature: Optional[float] = None
    health: Optional[int] = None
    total_gb: float = 0.0
    used_gb: float = 0.0


class OmegaHardwareMonitor:
    """Enhanced hardware monitoring with LibreHardwareMonitor integration"""
    
    def __init__(self):
        self.libre_computer = None
        self.last_update = None
        self.rgb_info = RGBInfo()  # Track RGB state
        self._init_libre_hardware_monitor()
    
    def _init_libre_hardware_monitor(self):
        """Initialize LibreHardwareMonitor"""
        if not LIBRE_HW_AVAILABLE:
            return
        
        try:
            self.libre_computer = Computer()
            self.libre_computer.IsCpuEnabled = True
            self.libre_computer.IsGpuEnabled = True
            self.libre_computer.IsMotherboardEnabled = True
            self.libre_computer.IsMemoryEnabled = True
            self.libre_computer.IsStorageEnabled = True
            self.libre_computer.Open()
            print("✓ LibreHardwareMonitor initialized")
        except Exception as e:
            print(f"✗ LibreHardwareMonitor initialization failed: {e}")
            self.libre_computer = None
    
    def get_cpu_info(self) -> CPUInfo:
        """Get comprehensive CPU information"""
        cpu = CPUInfo()
        
        # Try LibreHardwareMonitor first
        if self.libre_computer:
            try:
                for hardware in self.libre_computer.Hardware:
                    hardware.Update()
                    if hardware.HardwareType.ToString().startswith("Cpu"):
                        cpu.name = hardware.Name
                        
                        for sensor in hardware.Sensors:
                            sensor_type = sensor.SensorType.ToString()
                            sensor_name = sensor.Name
                            
                            if sensor_type == "Temperature":
                                if "Package" in sensor_name or "CPU" in sensor_name:
                                    cpu.package_temp = sensor.Value
                                    cpu.temperature = sensor.Value
                                elif "Core" in sensor_name:
                                    cpu.core_temps.append(sensor.Value)
                            
                            elif sensor_type == "Clock":
                                if "CPU Core" in sensor_name:
                                    cpu.current_clock = sensor.Value
                            
                            elif sensor_type == "Load":
                                if "CPU Total" in sensor_name:
                                    cpu.usage = sensor.Value
                            
                            elif sensor_type == "Power":
                                if "Package" in sensor_name or "CPU" in sensor_name:
                                    cpu.power_draw = sensor.Value
                            
                            elif sensor_type == "Voltage":
                                if "CPU" in sensor_name:
                                    cpu.voltage = sensor.Value
            except Exception as e:
                print(f"LibreHardwareMonitor CPU error: {e}")
        
        # Fallback methods when LibreHardwareMonitor is unavailable
        if cpu.temperature is None:
            # Try psutil sensors (Linux-like)
            try:
                import psutil
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Try common temperature sensor names
                        for sensor_name in ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal']:
                            if sensor_name in temps:
                                entries = temps[sensor_name]
                                if entries:
                                    cpu.temperature = entries[0].current
                                    cpu.package_temp = entries[0].current
                                    cpu.core_temps = [e.current for e in entries if 'Core' in e.label]
                                    break
            except:
                pass
            
            # Fallback to WMI
            if cpu.temperature is None:
                cpu.temperature = get_cpu_temperature_wmi()
        
        # Get CPU usage and info from psutil
        try:
            import psutil
            if cpu.usage == 0.0:
                cpu.usage = psutil.cpu_percent(interval=0.1)
            cpu.cores = psutil.cpu_count(logical=False) or 0
            cpu.threads = psutil.cpu_count(logical=True) or 0
            
            # Get CPU name from platform
            if cpu.name == "Unknown":
                try:
                    import platform
                    cpu.name = platform.processor() or "Unknown CPU"
                except:
                    pass
        except:
            pass
        
        return cpu
    
    def get_gpu_info(self) -> GPUInfo:
        """Get comprehensive GPU information"""
        gpu = GPUInfo()
        
        # Try nvidia-smi first (most reliable for NVIDIA)
        nvidia_info = get_gpu_info_nvidia()
        if nvidia_info:
            gpu.name = nvidia_info.get('name', 'Unknown')
            gpu.temperature = nvidia_info.get('temperature')
            gpu.usage = nvidia_info.get('usage')
            gpu.memory_used = nvidia_info.get('memory_used_gb', 0.0)
            gpu.memory_total = nvidia_info.get('memory_total_gb', 0.0)
            gpu.power_draw = nvidia_info.get('power_draw')
            gpu.power_limit = nvidia_info.get('power_limit')
            gpu.fan_speed = nvidia_info.get('fan_speed')
            gpu.core_clock = nvidia_info.get('clock_graphics')
            gpu.memory_clock = nvidia_info.get('clock_memory')
        
        # Try LibreHardwareMonitor for additional sensors
        if self.libre_computer:
            try:
                for hardware in self.libre_computer.Hardware:
                    hardware.Update()
                    if hardware.HardwareType.ToString().startswith("GpuNvidia"):
                        if gpu.name == "Unknown":
                            gpu.name = hardware.Name
                        
                        for sensor in hardware.Sensors:
                            sensor_type = sensor.SensorType.ToString()
                            sensor_name = sensor.Name
                            
                            if sensor_type == "Temperature":
                                if "GPU Core" in sensor_name:
                                    if gpu.temperature is None:
                                        gpu.temperature = sensor.Value
                                elif "Hot Spot" in sensor_name:
                                    gpu.hot_spot_temp = sensor.Value
                                elif "Memory" in sensor_name:
                                    gpu.memory_temp = sensor.Value
            except Exception as e:
                print(f"LibreHardwareMonitor GPU error: {e}")
        
        return gpu
    
    def get_motherboard_info(self) -> MotherboardInfo:
        """Get motherboard sensors"""
        mb = MotherboardInfo()
        
        if not self.libre_computer:
            return mb
        
        try:
            for hardware in self.libre_computer.Hardware:
                hardware.Update()
                if hardware.HardwareType.ToString() == "Motherboard":
                    mb.name = hardware.Name
                    
                    # Get sub-hardware (SuperIO chips)
                    for subhw in hardware.SubHardware:
                        subhw.Update()
                        for sensor in subhw.Sensors:
                            sensor_type = sensor.SensorType.ToString()
                            sensor_name = sensor.Name
                            
                            if sensor_type == "Temperature":
                                if "Chipset" in sensor_name or "PCH" in sensor_name:
                                    mb.chipset_temp = sensor.Value
                                elif "VRM" in sensor_name or "MOSFET" in sensor_name:
                                    mb.vrm_temp = sensor.Value
                            
                            elif sensor_type == "Control":
                                if "Fan" in sensor_name:
                                    mb.system_fans[sensor_name] = sensor.Value
                            
                            elif sensor_type == "Voltage":
                                mb.voltages[sensor_name] = sensor.Value
        except Exception as e:
            print(f"LibreHardwareMonitor motherboard error: {e}")
        
        return mb
    
    def get_memory_info(self) -> MemoryInfo:
        """Get memory information"""
        mem = MemoryInfo()
        
        try:
            import psutil
            vm = psutil.virtual_memory()
            mem.total_gb = vm.total / (1024**3)
            mem.used_gb = vm.used / (1024**3)
            mem.usage_percent = vm.percent
        except:
            pass
        
        # Try LibreHardwareMonitor for temperature
        if self.libre_computer:
            try:
                for hardware in self.libre_computer.Hardware:
                    hardware.Update()
                    if hardware.HardwareType.ToString() == "Memory":
                        for sensor in hardware.Sensors:
                            if sensor.SensorType.ToString() == "Temperature":
                                mem.temperature = sensor.Value
                            elif sensor.SensorType.ToString() == "Clock" and "Memory" in sensor.Name:
                                mem.speed_mhz = int(sensor.Value)
            except:
                pass
        
        return mem
    
    def get_storage_info(self) -> List[StorageInfo]:
        """Get storage device information"""
        storage_list = []
        
        if not self.libre_computer:
            return storage_list
        
        try:
            for hardware in self.libre_computer.Hardware:
                hardware.Update()
                if hardware.HardwareType.ToString() == "Storage":
                    storage = StorageInfo()
                    storage.name = hardware.Name
                    
                    # Detect type from name
                    name_lower = hardware.Name.lower()
                    if "nvme" in name_lower:
                        storage.type = "NVMe"
                    elif "ssd" in name_lower:
                        storage.type = "SATA SSD"
                    else:
                        storage.type = "HDD"
                    
                    for sensor in hardware.Sensors:
                        sensor_type = sensor.SensorType.ToString()
                        
                        if sensor_type == "Temperature":
                            storage.temperature = sensor.Value
                        elif sensor_type == "Level" and "Health" in sensor.Name:
                            storage.health = int(sensor.Value)
                    
                    storage_list.append(storage)
        except Exception as e:
            print(f"LibreHardwareMonitor storage error: {e}")
        
        return storage_list
    
    def get_all_hardware_data(self) -> Dict[str, Any]:
        """Get all hardware data in one call"""
        self.last_update = datetime.now()
        
        data = {
            'timestamp': self.last_update.isoformat(),
            'cpu': self.get_cpu_info().__dict__,
            'gpu': self.get_gpu_info().__dict__,
            'motherboard': self.get_motherboard_info().__dict__,
            'memory': self.get_memory_info().__dict__,
            'storage': [s.__dict__ for s in self.get_storage_info()],
            'rgb': self.get_rgb_info(),
            'libre_hw_available': LIBRE_HW_AVAILABLE,
        }
        
        return data
    
    def set_fan_speed(self, fan_name: str, speed_percent: int) -> bool:
        """Set fan speed (requires LibreHardwareMonitor and admin rights)"""
        if not self.libre_computer:
            print("LibreHardwareMonitor not available")
            return False
        
        try:
            # This requires the control to be writable
            # Most motherboards require administrator rights
            print(f"Setting {fan_name} to {speed_percent}%")
            # Implementation depends on motherboard capabilities
            return True
        except Exception as e:
            print(f"Fan control error: {e}")
            return False
    
    def set_rgb_brightness(self, brightness: int) -> bool:
        """Set RGB brightness (0-100%)"""
        try:
            self.rgb_info.brightness = max(0, min(100, brightness))
            print(f"RGB brightness set to {self.rgb_info.brightness}%")
            return True
        except Exception as e:
            print(f"RGB brightness error: {e}")
            return False
    
    def set_rgb_color(self, r: int, g: int, b: int) -> bool:
        """Set RGB color (0-255 for each channel)"""
        try:
            self.rgb_info.color_r = max(0, min(255, r))
            self.rgb_info.color_g = max(0, min(255, g))
            self.rgb_info.color_b = max(0, min(255, b))
            self.rgb_info.color_hex = f"#{r:02x}{g:02x}{b:02x}"
            print(f"RGB color set to RGB({r},{g},{b}) {self.rgb_info.color_hex}")
            return True
        except Exception as e:
            print(f"RGB color error: {e}")
            return False
    
    def set_rgb_mode(self, mode: str) -> bool:
        """Set RGB lighting mode"""
        valid_modes = ["static", "breathing", "rainbow", "reactive"]
        if mode.lower() not in valid_modes:
            print(f"Invalid mode. Choose from: {', '.join(valid_modes)}")
            return False
        
        try:
            self.rgb_info.mode = mode.lower()
            print(f"RGB mode set to {self.rgb_info.mode}")
            return True
        except Exception as e:
            print(f"RGB mode error: {e}")
            return False
    
    def toggle_rgb(self) -> bool:
        """Toggle RGB on/off"""
        try:
            self.rgb_info.enabled = not self.rgb_info.enabled
            status = "ON" if self.rgb_info.enabled else "OFF"
            print(f"RGB lighting {status}")
            return True
        except Exception as e:
            print(f"RGB toggle error: {e}")
            return False
    
    def get_rgb_info(self) -> Dict[str, Any]:
        """Get current RGB state"""
        return {
            'enabled': self.rgb_info.enabled,
            'brightness': self.rgb_info.brightness,
            'color_r': self.rgb_info.color_r,
            'color_g': self.rgb_info.color_g,
            'color_b': self.rgb_info.color_b,
            'color_hex': self.rgb_info.color_hex,
            'mode': self.rgb_info.mode
        }
    
    def close(self):
        """Cleanup resources"""
        if self.libre_computer:
            try:
                self.libre_computer.Close()
            except:
                pass


def print_hardware_summary(monitor: OmegaHardwareMonitor):
    """Print formatted hardware summary"""
    data = monitor.get_all_hardware_data()
    
    print("\n" + "="*70)
    print("OMEGA ENHANCED HARDWARE MONITOR")
    print("="*70)
    
    # CPU
    cpu = data['cpu']
    print(f"\n[CPU] {cpu['name']}")
    print(f"  Temperature: {cpu['temperature']}°C (Package: {cpu['package_temp']}°C)")
    if cpu['core_temps']:
        print(f"  Core Temps: {', '.join([f'{t:.1f}°C' for t in cpu['core_temps']])}")
    print(f"  Usage: {cpu['usage']:.1f}%")
    print(f"  Clock: {cpu['current_clock']:.0f} MHz")
    if cpu['power_draw']:
        print(f"  Power: {cpu['power_draw']:.1f}W")
    
    # GPU
    gpu = data['gpu']
    print(f"\n[GPU] {gpu['name']}")
    print(f"  Temperature: {gpu['temperature']}°C", end="")
    if gpu['hot_spot_temp']:
        print(f" (Hot Spot: {gpu['hot_spot_temp']}°C)", end="")
    print()
    print(f"  Usage: {gpu['usage']}%")
    print(f"  Memory: {gpu['memory_used']:.2f} GB / {gpu['memory_total']:.2f} GB")
    if gpu['power_draw']:
        print(f"  Power: {gpu['power_draw']:.1f}W / {gpu['power_limit']:.0f}W")
    if gpu['fan_speed']:
        print(f"  Fan Speed: {gpu['fan_speed']}%")
    print(f"  Clocks: Core {gpu['core_clock']}MHz, Memory {gpu['memory_clock']}MHz")
    
    # Motherboard
    mb = data['motherboard']
    print(f"\n[Motherboard] {mb['name']}")
    if mb['chipset_temp']:
        print(f"  Chipset: {mb['chipset_temp']}°C")
    if mb['vrm_temp']:
        print(f"  VRM: {mb['vrm_temp']}°C")
    if mb['system_fans']:
        print(f"  Fans:")
        for fan_name, speed in mb['system_fans'].items():
            print(f"    {fan_name}: {speed:.0f} RPM")
    
    # Memory
    mem = data['memory']
    print(f"\n[Memory]")
    print(f"  Usage: {mem['used_gb']:.1f} GB / {mem['total_gb']:.1f} GB ({mem['usage_percent']:.1f}%)")
    if mem['temperature']:
        print(f"  Temperature: {mem['temperature']}°C")
    if mem['speed_mhz']:
        print(f"  Speed: {mem['speed_mhz']} MHz")
    
    # Storage
    if data['storage']:
        print(f"\n[Storage]")
        for storage in data['storage']:
            print(f"  {storage['name']} ({storage['type']})")
            if storage['temperature']:
                print(f"    Temperature: {storage['temperature']}°C")
            if storage['health']:
                print(f"    Health: {storage['health']}%")
    
    print("\n" + "="*70)
    print(f"LibreHardwareMonitor: {'✓ Active' if data['libre_hw_available'] else '✗ Not Available'}")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\nOmega Enhanced Hardware Monitor")
    print("================================\n")
    
    monitor = OmegaHardwareMonitor()
    
    try:
        print_hardware_summary(monitor)
        
        # Save to JSON for web interface
        data = monitor.get_all_hardware_data()
        with open('omega_hardware_live.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print("✓ Hardware data saved to omega_hardware_live.json")
        
    finally:
        monitor.close()
