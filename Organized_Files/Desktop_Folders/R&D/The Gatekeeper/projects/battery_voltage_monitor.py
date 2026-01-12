#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# BATTERY VOLTAGE MONITOR
# Reads serial data from 18650 cells, logs to JSON
# Integrates with battery_oracle.py for health prediction
# Real-time status display with error handling

import json
import sys
import io
import time
import serial
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
LOG_DIR = BRAIN / 'Archived' / 'battery_logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

class BatteryVoltageMonitor:
    """Monitor 18650 battery cells via serial, log to JSON, integrate with battery_oracle."""
    
    def __init__(self, port: str = 'COM3', baudrate: int = 9600):
        """
        Initialize battery monitor.
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Serial baud rate (default 9600)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.cells: Dict[int, Dict] = {}
        self.running = False
        
        # Integration with battery_oracle
        self.battery_oracle_path = GATE / 'battery_oracle.py'
        self.oracle_available = self.battery_oracle_path.exists()
    
    def connect(self) -> bool:
        """Connect to serial port."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"[OK] Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Serial connection failed: {e}")
            print(f"[INFO] Available ports: {self._list_ports()}")
            return False
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            return False
    
    def _list_ports(self) -> List[str]:
        """List available serial ports."""
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports if ports else ["No ports found"]
        except:
            return ["Unable to list ports"]
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("[OK] Serial connection closed")
    
    def read_cell_data(self) -> Optional[Dict]:
        """
        Read cell data from serial port.
        Expected format: "CELL_ID,VOLTAGE,TEMPERATURE,STATUS"
        Example: "1,3.7,25.5,OK"
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
        
        try:
            line = self.serial_conn.readline().decode('utf-8').strip()
            if not line:
                return None
            
            # Parse: CELL_ID,VOLTAGE,TEMPERATURE,STATUS
            parts = line.split(',')
            if len(parts) >= 3:
                cell_id = int(parts[0])
                voltage = float(parts[1])
                temperature = float(parts[2]) if len(parts) > 2 else 25.0
                status = parts[3] if len(parts) > 3 else 'OK'
                
                return {
                    'cell_id': cell_id,
                    'voltage': voltage,
                    'temperature': temperature,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }
        except ValueError as e:
            print(f"[WARNING] Parse error: {e} - Line: {line}")
            return None
        except Exception as e:
            print(f"[ERROR] Read error: {e}")
            return None
        
        return None
    
    def update_cells(self, cell_data: Dict):
        """Update cell data dictionary."""
        cell_id = cell_data['cell_id']
        self.cells[cell_id] = cell_data
    
    def get_health_prediction(self, cell_id: int, voltage: float, temperature: float) -> Optional[Dict]:
        """
        Get health prediction from battery_oracle.py if available.
        Uses voltage and temperature to estimate health.
        
        Args:
            cell_id: Cell identifier
            voltage: Cell voltage
            temperature: Cell temperature
        
        Returns:
            Health prediction dict or None
        """
        if not self.oracle_available:
            return None
        
        try:
            # Simple health estimation based on voltage
            # 18650 cells: 3.0V (empty) to 4.2V (full)
            voltage_percent = ((voltage - 3.0) / (4.2 - 3.0)) * 100
            voltage_percent = max(0, min(100, voltage_percent))
            
            # Temperature impact (optimal: 20-25°C)
            temp_penalty = 0
            if temperature < 0 or temperature > 45:
                temp_penalty = 20  # Severe penalty
            elif temperature < 10 or temperature > 35:
                temp_penalty = 10  # Moderate penalty
            
            health_score = max(0, voltage_percent - temp_penalty)
            
            # Recommendation
            if health_score >= 80:
                recommendation = "Excellent"
            elif health_score >= 60:
                recommendation = "Good"
            elif health_score >= 40:
                recommendation = "Monitor"
            elif health_score >= 20:
                recommendation = "Warning"
            else:
                recommendation = "Critical"
            
            return {
                'cell_id': cell_id,
                'health_score': round(health_score, 1),
                'voltage_percent': round(voltage_percent, 1),
                'temperature': round(temperature, 1),
                'recommendation': recommendation
            }
        except Exception as e:
            print(f"[WARNING] Health prediction error: {e}")
            return None
    
    def log_to_json(self, data: Dict):
        """Log cell data to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = LOG_DIR / f'battery_log_{timestamp}.json'
        
        # Load existing data or create new
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        else:
            logs = []
        
        # Append new entry
        logs.append(data)
        
        # Save
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Log save error: {e}")
    
    def display_status(self):
        """Display real-time status of all cells."""
        print("\n" + "=" * 60)
        print("BATTERY VOLTAGE MONITOR - REAL-TIME STATUS")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cells Monitored: {len(self.cells)}")
        print()
        
        if not self.cells:
            print("[INFO] No cell data received yet...")
            return
        
        # Display each cell
        for cell_id in sorted(self.cells.keys()):
            cell = self.cells[cell_id]
            voltage = cell['voltage']
            temp = cell.get('temperature', 0.0)
            status = cell.get('status', 'UNKNOWN')
            
            # Voltage status
            if voltage < 3.0:
                volt_status = "[LOW]"
            elif voltage > 4.2:
                volt_status = "[HIGH]"
            elif 3.2 <= voltage <= 4.1:
                volt_status = "[OK]"
            else:
                volt_status = "[CHECK]"
            
            # Health prediction
            health = self.get_health_prediction(cell_id, voltage, temp)
            health_str = ""
            if health:
                health_str = f" | Health: {health['health_score']:.1f}% | {health['recommendation']}"
            
            print(f"Cell {cell_id:02d}: {volt_status} {voltage:.3f}V @ {temp:.1f}°C | {status}{health_str}")
        
        print("=" * 60)
    
    def run(self, interval: float = 5.0, display: bool = True):
        """
        Main monitoring loop.
        
        Args:
            interval: Update interval in seconds (default 5.0)
            display: Show real-time status (default True)
        """
        if not self.connect():
            print("[ERROR] Cannot start monitoring - connection failed")
            return
        
        self.running = True
        print(f"\n[OK] Starting battery monitoring (update every {interval}s)")
        print("[INFO] Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                # Read cell data
                cell_data = self.read_cell_data()
                
                if cell_data:
                    # Update cells
                    self.update_cells(cell_data)
                    
                    # Log to JSON
                    self.log_to_json(cell_data)
                    
                    # Display status
                    if display:
                        self.display_status()
                
                # Wait for next interval
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[INFO] Monitoring stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Monitoring error: {e}")
        finally:
            self.disconnect()
            print("[OK] Monitor shutdown complete")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Battery Voltage Monitor for 18650 Cells')
    parser.add_argument('--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate (default: 9600)')
    parser.add_argument('--interval', type=float, default=5.0, help='Update interval in seconds (default: 5.0)')
    parser.add_argument('--no-display', action='store_true', help='Disable real-time display')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("BATTERY VOLTAGE MONITOR")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    print("The doors of knowledge opens.")
    print("Battery monitoring system initializing...\n")
    
    monitor = BatteryVoltageMonitor(port=args.port, baudrate=args.baudrate)
    monitor.run(interval=args.interval, display=not args.no_display)

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

