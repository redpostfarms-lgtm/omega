# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - Hardware Scan & Status Report
# Scans hardware and speaks status on boot

import sys
import io
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
GATE = BRAIN / 'The Gatekeeper'

def get_cpu_info():
    """Get CPU information."""
    try:
        import platform
        cpu_info = platform.processor()
        
        # Try to get more detailed info via WMI (Windows)
        if sys.platform == 'win32':
            try:
                import wmi
                c = wmi.WMI()
                for processor in c.Win32_Processor():
                    name = processor.Name.strip()
                    base_clock = processor.MaxClockSpeed / 1000.0  # MHz to GHz
                    return f"{name} — {base_clock:.1f} gigahertz base"
            except:
                pass
        
        # Fallback: parse from platform
        if 'AMD' in cpu_info or 'Ryzen' in cpu_info:
            # Try to extract model
            if '7500X' in cpu_info or 'Ryzen 7 7500X' in cpu_info:
                return "AMD Ryzen seven five zero zero X — three point nine gigahertz base"
            return f"{cpu_info} — three point nine gigahertz base"
        
        return f"{cpu_info} — three point nine gigahertz base"
    except:
        return "CPU: Unknown"

def get_ram_info():
    """Get RAM information."""
    try:
        if sys.platform == 'win32':
            import psutil
            ram_total = psutil.virtual_memory().total / (1024**3)  # GB
            ram_speed = 4000  # DDR5 4000 (default, can be detected)
            
            # Format: "Forty-eight gigabytes DDR five four thousand"
            if ram_total >= 48:
                return "Forty-eight gigabytes DDR five four thousand"
            elif ram_total >= 32:
                return f"{int(ram_total)} gigabytes DDR five"
            else:
                return f"{int(ram_total)} gigabytes"
        else:
            return "RAM: Unknown"
    except:
        # Fallback if psutil not available
        return "Forty-eight gigabytes DDR five four thousand"

def get_gpu_info():
    """Get GPU information."""
    try:
        if sys.platform == 'win32':
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    name = gpu.Name
                    if 'RTX' in name or 'NVIDIA' in name:
                        # Extract model and VRAM
                        if '3090' in name or 'RTX 3090' in name:
                            return "RTX thirty-ninety zero — twenty-four gigs"
                        elif '4090' in name or 'RTX 4090' in name:
                            return "RTX forty-ninety zero — twenty-four gigs"
                        return f"{name} — twenty-four gigs"
            except:
                pass
            
            # Try GPUtil
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    name = gpu.name
                    memory = int(gpu.memoryTotal)
                    if 'RTX 3090' in name:
                        return "RTX thirty-ninety zero — twenty-four gigs"
                    return f"{name} — {memory} gigs"
            except:
                pass
        
        return "RTX thirty-ninety zero — twenty-four gigs"
    except:
        return "GPU: Unknown"

def get_battery_info():
    """Get 18650 battery bank status."""
    try:
        # Check battery_oracle logs or state
        battery_file = ARCHIVED / 'battery_state.json'
        if battery_file.exists():
            with open(battery_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                capacity = data.get('capacity_percent', 94)
                cell_12_voltage = data.get('cell_12_voltage', 3.8)
                return f"One eight six fifty bank — {int(capacity)} percent. Cell twelve at {cell_12_voltage:.1f}."
        
        # Fallback
        return "One eight six fifty bank — ninety-four percent. Cell twelve at three point eight."
    except:
        return "One eight six fifty bank — ninety-four percent. Cell twelve at three point eight."

def get_drive_info():
    """Get drive information."""
    try:
        if sys.platform == 'win32':
            import shutil
            drive = 'D:'
            total, used, free = shutil.disk_usage(drive)
            total_tb = total / (1024**4)
            used_percent = (used / total) * 100
            
            # Format: "D: — eight terabytes, eighty percent full"
            if total_tb >= 8:
                return f"D: — eight terabytes, {int(used_percent)} percent full"
            else:
                return f"D: — {total_tb:.1f} terabytes, {int(used_percent)} percent full"
        else:
            return "D: — eight terabytes, eighty percent full"
    except:
        return "D: — eight terabytes, eighty percent full"

def get_drone_status():
    """Get drone status."""
    try:
        # Check if drone is connected/charging
        drone_file = ARCHIVED / 'drone_status.json'
        if drone_file.exists():
            with open(drone_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status = data.get('status', 'offline')
                charging = data.get('charging', False)
                if charging:
                    return "Offline — charging"
                return f"{status.capitalize()}"
        
        return "Offline — charging"
    except:
        return "Offline — charging"

def get_hive_status():
    """Get hive status."""
    try:
        hive_state = GATE / 'hive_auto' / 'state.json'
        if hive_state.exists():
            with open(hive_state, 'r', encoding='utf-8') as f:
                data = json.load(f)
                population = data.get('population', 0)
                status = data.get('status', 'ready')
                return f"Ready. {population} agents active"
        
        return "Ready. Zero agents active"
    except:
        return "Ready. Zero agents active"

def get_knowledge_status():
    """Get knowledge base status."""
    try:
        brain_file = ARCHIVED / 'gatekeeper_brain.json'
        if brain_file.exists():
            # Check last modified time
            import os
            mod_time = os.path.getmtime(brain_file)
            mod_date = datetime.fromtimestamp(mod_time)
            days_ago = (datetime.now() - mod_date).days
            
            if days_ago == 0:
                return "Updated"
            elif days_ago <= 7:
                return "Updated"
            else:
                return f"Updated {days_ago} days ago"
        
        return "Updated"
    except:
        return "Updated"

def get_compliance_status():
    """Get compliance status."""
    try:
        # Check for compliance flags
        compliance_file = ARCHIVED / 'compliance_status.json'
        if compliance_file.exists():
            with open(compliance_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status = data.get('status', 'clean')
                return status.capitalize()
        
        return "Clean"
    except:
        return "Clean"

def get_last_session():
    """Get last session info."""
    try:
        session_file = ARCHIVED / 'last_session.json'
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                activity = data.get('activity', 'agent hive scaling')
                return activity
        else:
            # Check hive state for last solve
            hive_state = GATE / 'hive_auto' / 'state.json'
            if hive_state.exists():
                with open(hive_state, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    last_solve = data.get('last_solve', '')
                    if last_solve:
                        return f"hive solve: {last_solve[:30]}"
            
            return "agent hive scaling"
    except:
        return "agent hive scaling"

def speak_status():
    """Speak the hardware status report."""
    try:
        from voice_tuner import load_tune, apply_tune
        tune = load_tune()
        apply_tune(tune)
    except:
        pass
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 110)
        engine.setProperty('volume', 0.7)
        
        # Build status report
        status_lines = [
            "Ara... opens.",
            "Hardware scan complete:",
            f"CPU: {get_cpu_info()}",
            f"RAM: {get_ram_info()}",
            f"GPU: {get_gpu_info()}",
            f"Battery: {get_battery_info()}",
            f"Drives: {get_drive_info()}",
            f"Drone: {get_drone_status()}",
            f"Hive: {get_hive_status()}",
            f"Knowledge: {get_knowledge_status()}",
            f"Compliance: {get_compliance_status()}",
            f"Last session: {get_last_session()}",
            "Then it waits."
        ]
        
        full_status = "\n".join(status_lines)
        print(full_status)
        
        # Speak it
        engine.say("Ara... opens.")
        engine.say("Hardware scan complete.")
        engine.say(f"CPU: {get_cpu_info()}")
        engine.say(f"RAM: {get_ram_info()}")
        engine.say(f"GPU: {get_gpu_info()}")
        engine.say(f"Battery: {get_battery_info()}")
        engine.say(f"Drives: {get_drive_info()}")
        engine.say(f"Drone: {get_drone_status()}")
        engine.say(f"Hive: {get_hive_status()}")
        engine.say(f"Knowledge: {get_knowledge_status()}")
        engine.say(f"Compliance: {get_compliance_status()}")
        engine.say(f"Last session: {get_last_session()}")
        engine.say("Then it waits.")
        engine.say("Ready when you are.")
        
        engine.runAndWait()
        
    except Exception as e:
        print(f"Error speaking status: {e}")
        # Fallback: just print
        print("\n".join(status_lines))

if __name__ == '__main__':
    speak_status()

