"""
Enhanced Hardware Sensor Module
================================
Direct motherboard and GPU sensor access for Windows systems.
Uses WMI for CPU temperature and nvidia-smi for comprehensive GPU data.
"""

import subprocess
import platform
from typing import Dict, Optional, Any

def get_cpu_temperature_wmi() -> Optional[float]:
    """Get CPU temperature from Windows WMI sensors"""
    if platform.system() != "Windows":
        return None
    
    try:
        import psutil
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()  # type: ignore[attr-defined]
            for name, entries in temps.items():
                name_lower = name.lower()
                if any(keyword in name_lower for keyword in ['cpu', 'core', 'processor', 'package']):
                    for entry in entries:
                        if entry.current and entry.current > 0:
                            return round(entry.current, 1)
    except Exception:
        pass
    
    try:
        import subprocess
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" | Select-Object -First 1 -ExpandProperty CurrentTemperature'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            temp_kelvin = float(result.stdout.strip()) / 10.0
            temp_celsius = temp_kelvin - 273.15
            if 0 < temp_celsius < 150:  # Sanity check
                return round(temp_celsius, 1)
    except Exception:
        pass
    
    try:
        import wmi
        w = wmi.WMI(namespace="root\\WMI")
        
        temperature_info = w.MSAcpi_ThermalZoneTemperature()
        if temperature_info:
            temp_kelvin = temperature_info[0].CurrentTemperature / 10.0
            temp_celsius = temp_kelvin - 273.15
            if temp_celsius > 0 and temp_celsius < 150:  # Sanity check
                return round(temp_celsius, 1)
    except Exception:
        pass
    
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensors = w.Sensor()
        for sensor in sensors:
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                return float(sensor.Value)
    except Exception:
        pass
    
    try:
        import wmi
        w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
        sensors = w.Sensor()
        for sensor in sensors:
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                return float(sensor.Value)
    except Exception:
        pass
    
    try:
        import wmi
        c = wmi.WMI()
        for temp_probe in c.Win32_TemperatureProbe():
            if temp_probe.CurrentReading:
                temp_celsius = (temp_probe.CurrentReading / 10.0) - 273.15
                if temp_celsius > 0 and temp_celsius < 150:
                    return round(temp_celsius, 1)
    except Exception:
        pass
    
    return None


def get_gpu_info_nvidia() -> Dict[str, Any]:
    """Get comprehensive GPU information from NVIDIA card (RTX 3050)"""
    gpu_info = {
        'name': 'Unknown',
        'temperature': None,
        'usage': None,
        'memory_used_mb': 0,
        'memory_total_mb': 0,
        'memory_used_gb': 0.0,
        'memory_total_gb': 0.0,
        'memory_percent': 0.0,
        'power_draw': None,
        'power_limit': None,
        'fan_speed': None,
        'clock_graphics': None,
        'clock_memory': None,
    }
    
    try:
        query_fields = [
            'name',
            'temperature.gpu',
            'utilization.gpu',
            'utilization.memory',
            'memory.used',
            'memory.total',
            'power.draw',
            'power.limit',
            'fan.speed',
            'clocks.gr',
            'clocks.mem',
        ]
        
        query = ','.join(query_fields)
        result = subprocess.run(
            ['nvidia-smi', f'--query-gpu={query}', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            values = [v.strip() for v in result.stdout.strip().split(',')]
            
            if len(values) >= 11:
                gpu_info['name'] = values[0]
                gpu_info['temperature'] = float(values[1]) if values[1] != 'N/A' else None
                gpu_info['usage'] = float(values[2]) if values[2] != 'N/A' else None
                gpu_info['memory_usage_percent'] = float(values[3]) if values[3] != 'N/A' else None
                
                memory_used_mb = float(values[4]) if values[4] != 'N/A' else 0
                memory_total_mb = float(values[5]) if values[5] != 'N/A' else 0
                
                gpu_info['memory_used_mb'] = memory_used_mb
                gpu_info['memory_total_mb'] = memory_total_mb
                gpu_info['memory_used_gb'] = round(memory_used_mb / 1024, 2)
                gpu_info['memory_total_gb'] = round(memory_total_mb / 1024, 2)
                
                if memory_total_mb > 0:
                    gpu_info['memory_percent'] = round((memory_used_mb / memory_total_mb) * 100, 1)
                
                gpu_info['power_draw'] = float(values[6]) if values[6] != 'N/A' else None
                gpu_info['power_limit'] = float(values[7]) if values[7] != 'N/A' else None
                gpu_info['fan_speed'] = float(values[8]) if values[8] != 'N/A' else None
                
                gpu_info['clock_graphics'] = float(values[9]) if values[9] != 'N/A' else None
                gpu_info['clock_memory'] = float(values[10]) if values[10] != 'N/A' else None
                
    except Exception as e:
        pass
    
    return gpu_info


def get_all_hardware_temps() -> Dict[str, Any]:
    """Get all hardware temperature and sensor data"""
    return {
        'cpu_temp': get_cpu_temperature_wmi(),
        'gpu_info': get_gpu_info_nvidia()
    }


if __name__ == "__main__":
    """Test the sensor module"""
    print("=" * 60)
    print("HARDWARE SENSOR TEST")
    print("=" * 60)
    
    print("\n[CPU Temperature]")
    cpu_temp = get_cpu_temperature_wmi()
    if cpu_temp:
        print(f"  Temperature: {cpu_temp}°C")
    else:
        print("  Temperature: Not available via motherboard sensors")
        print("")
        print("  📌 To enable CPU temperature:")
        print("     1. Download OpenHardwareMonitor or LibreHardwareMonitor")
        print("     2. Run it in administrator mode")
        print("     3. Keep it running in background")
        print("     OR")
        print("     Install HWiNFO64 with Shared Memory Support")
        print("")
        print("  ℹ️  Your motherboard doesn't expose CPU temp via ACPI/WMI")
    
    print("\n[GPU Information - GeForce RTX 3050]")
    gpu_info = get_gpu_info_nvidia()
    print(f"  Name: {gpu_info['name']}")
    print(f"  Temperature: {gpu_info['temperature']}°C")
    print(f"  Usage: {gpu_info['usage']}%")
    print(f"  Memory: {gpu_info['memory_used_gb']} GB / {gpu_info['memory_total_gb']} GB ({gpu_info['memory_percent']}%)")
    if gpu_info['power_draw']:
        print(f"  Power: {gpu_info['power_draw']} W / {gpu_info['power_limit']} W")
    if gpu_info['fan_speed']:
        print(f"  Fan Speed: {gpu_info['fan_speed']}%")
    if gpu_info['clock_graphics']:
        print(f"  GPU Clock: {gpu_info['clock_graphics']} MHz")
    if gpu_info['clock_memory']:
        print(f"  Memory Clock: {gpu_info['clock_memory']} MHz")
    
    print("\n" + "=" * 60)
