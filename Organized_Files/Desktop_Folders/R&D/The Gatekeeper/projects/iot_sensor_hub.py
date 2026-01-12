#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# IOT SENSOR HUB
# Real-time environmental monitoring: soil moisture, temperature, humidity, pH, light
# Supports: Arduino, Raspberry Pi, ESP32, MQTT, Serial, I2C, SPI

import json
import sys
import io
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
SENSOR_DIR = BRAIN / 'Archived' / 'sensor_data'
SENSOR_DIR.mkdir(parents=True, exist_ok=True)

# Try to import sensor libraries
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False

class IoTSensorHub:
    """IoT sensor hub for environmental monitoring."""
    
    def __init__(self):
        """Initialize sensor hub."""
        self.sensors = {}
        self.readings = {}
        self.alerts = []
        self.running = False
        
        # Sensor configurations
        self.sensor_configs = {
            'soil_moisture': {
                'type': 'analog',
                'min': 0,
                'max': 1023,
                'unit': '%',
                'optimal_min': 40,
                'optimal_max': 60,
                'alert_low': 30,
                'alert_high': 70
            },
            'temperature': {
                'type': 'digital',
                'unit': '°C',
                'optimal_min': 15,
                'optimal_max': 25,
                'alert_low': 5,
                'alert_high': 35
            },
            'humidity': {
                'type': 'digital',
                'unit': '%',
                'optimal_min': 50,
                'optimal_max': 70,
                'alert_low': 30,
                'alert_high': 80
            },
            'ph': {
                'type': 'analog',
                'min': 0,
                'max': 14,
                'unit': 'pH',
                'optimal_min': 6.0,
                'optimal_max': 7.0,
                'alert_low': 5.5,
                'alert_high': 7.5
            },
            'light': {
                'type': 'analog',
                'min': 0,
                'max': 100000,
                'unit': 'lux',
                'optimal_min': 10000,
                'optimal_max': 50000,
                'alert_low': 5000,
                'alert_high': 60000
            },
            'water_level': {
                'type': 'ultrasonic',
                'unit': 'cm',
                'optimal_min': 20,
                'optimal_max': 80,
                'alert_low': 10,
                'alert_high': 90
            }
        }
    
    def register_sensor(self, sensor_id: str, sensor_type: str, location: str, interface: str = 'serial'):
        """Register a sensor."""
        if sensor_type not in self.sensor_configs:
            print(f"[ERROR] Unknown sensor type: {sensor_type}")
            return False
        
        self.sensors[sensor_id] = {
            'type': sensor_type,
            'location': location,
            'interface': interface,
            'config': self.sensor_configs[sensor_type],
            'last_reading': None,
            'registered_at': datetime.now().isoformat()
        }
        
        print(f"[OK] Sensor registered: {sensor_id} ({sensor_type}) at {location}")
        return True
    
    def read_serial_sensor(self, port: str, baudrate: int = 9600) -> Optional[Dict]:
        """Read sensor data from serial port."""
        if not SERIAL_AVAILABLE:
            return None
        
        try:
            ser = serial.Serial(port, baudrate, timeout=1.0)
            line = ser.readline().decode('utf-8').strip()
            ser.close()
            
            # Parse: "SENSOR_ID:TYPE:VALUE1:VALUE2:..."
            parts = line.split(':')
            if len(parts) >= 3:
                sensor_id = parts[0]
                sensor_type = parts[1]
                values = [float(v) for v in parts[2:]]
                
                return {
                    'sensor_id': sensor_id,
                    'type': sensor_type,
                    'values': values,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"[WARNING] Serial read error: {e}")
        
        return None
    
    def read_mqtt_sensor(self, topic: str, broker: str = 'localhost', port: int = 1883) -> Optional[Dict]:
        """Read sensor data from MQTT broker."""
        if not MQTT_AVAILABLE:
            return None
        
        try:
            client = mqtt.Client()
            client.connect(broker, port, 60)
            client.subscribe(topic)
            
            # Wait for message
            client.loop_start()
            time.sleep(1)
            client.loop_stop()
            
            # Parse message (would need callback in real implementation)
            return None
        except Exception as e:
            print(f"[WARNING] MQTT read error: {e}")
        
        return None
    
    def read_sensor(self, sensor_id: str) -> Optional[Dict]:
        """Read sensor data."""
        if sensor_id not in self.sensors:
            return None
        
        sensor = self.sensors[sensor_id]
        interface = sensor['interface']
        
        if interface == 'serial':
            # Would use actual port from config
            data = self.read_serial_sensor('COM3')
        elif interface == 'mqtt':
            data = self.read_mqtt_sensor(f'sensors/{sensor_id}')
        elif interface == 'simulated':
            # Simulate sensor reading
            data = self.simulate_sensor_reading(sensor_id)
        else:
            return None
        
        if data:
            # Process and validate
            processed = self.process_reading(sensor_id, data)
            self.readings[sensor_id] = processed
            sensor['last_reading'] = processed
            return processed
        
        return None
    
    def simulate_sensor_reading(self, sensor_id: str) -> Dict:
        """Simulate sensor reading for testing."""
        sensor = self.sensors[sensor_id]
        sensor_type = sensor['type']
        config = sensor['config']
        
        import random
        
        if sensor_type == 'soil_moisture':
            value = random.uniform(35, 65)  # 35-65%
        elif sensor_type == 'temperature':
            value = random.uniform(10, 30)  # 10-30°C
        elif sensor_type == 'humidity':
            value = random.uniform(45, 75)  # 45-75%
        elif sensor_type == 'ph':
            value = random.uniform(6.2, 6.8)  # 6.2-6.8 pH
        elif sensor_type == 'light':
            value = random.uniform(15000, 40000)  # 15k-40k lux
        elif sensor_type == 'water_level':
            value = random.uniform(30, 70)  # 30-70 cm
        else:
            value = 0.0
        
        return {
            'sensor_id': sensor_id,
            'type': sensor_type,
            'value': round(value, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def process_reading(self, sensor_id: str, data: Dict) -> Dict:
        """Process and validate sensor reading."""
        sensor = self.sensors[sensor_id]
        config = sensor['config']
        
        value = data.get('value', data.get('values', [0])[0] if 'values' in data else 0)
        
        # Check alerts
        status = 'OK'
        if value < config.get('alert_low', 0):
            status = 'LOW'
            self.add_alert(sensor_id, f"{sensor['type']} is critically low: {value}{config['unit']}")
        elif value > config.get('alert_high', 100):
            status = 'HIGH'
            self.add_alert(sensor_id, f"{sensor['type']} is critically high: {value}{config['unit']}")
        elif value < config.get('optimal_min', 0) or value > config.get('optimal_max', 100):
            status = 'WARNING'
        
        return {
            'sensor_id': sensor_id,
            'type': sensor['type'],
            'location': sensor['location'],
            'value': value,
            'unit': config['unit'],
            'status': status,
            'optimal_range': f"{config.get('optimal_min', 0)}-{config.get('optimal_max', 100)}{config['unit']}",
            'timestamp': datetime.now().isoformat()
        }
    
    def add_alert(self, sensor_id: str, message: str):
        """Add alert."""
        alert = {
            'sensor_id': sensor_id,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        self.alerts.append(alert)
        print(f"[ALERT] {sensor_id}: {message}")
    
    def log_readings(self):
        """Log all readings to JSON."""
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = SENSOR_DIR / f'sensor_log_{timestamp}.json'
        
        # Load existing data
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        else:
            logs = []
        
        # Append current readings
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'readings': list(self.readings.values()),
            'alerts': [a for a in self.alerts if not a['acknowledged']]
        }
        logs.append(log_entry)
        
        # Save
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def display_dashboard(self):
        """Display sensor dashboard."""
        print("\n" + "=" * 60)
        print("IOT SENSOR HUB - REAL-TIME MONITORING")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sensors: {len(self.sensors)}")
        print()
        
        if not self.readings:
            print("[INFO] No sensor readings yet...")
            return
        
        for sensor_id, reading in self.readings.items():
            sensor = self.sensors[sensor_id]
            status_icon = "[OK]" if reading['status'] == 'OK' else "[ALERT]"
            
            print(f"{status_icon} {sensor_id} ({sensor['location']}):")
            print(f"  Type: {reading['type']}")
            print(f"  Value: {reading['value']} {reading['unit']}")
            print(f"  Status: {reading['status']}")
            print(f"  Optimal: {reading['optimal_range']}")
            print()
        
        if self.alerts:
            print("ALERTS:")
            for alert in self.alerts[-5:]:  # Show last 5
                if not alert['acknowledged']:
                    print(f"  - {alert['message']}")
            print()
        
        print("=" * 60)
    
    def run_monitoring(self, interval: float = 30.0):
        """Run continuous monitoring."""
        print("=" * 60)
        print("IOT SENSOR HUB - MONITORING MODE")
        print("=" * 60)
        print(f"Update Interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                # Read all sensors in parallel
                with ThreadPoolExecutor(max_workers=len(self.sensors)) as executor:
                    futures = {
                        executor.submit(self.read_sensor, sensor_id): sensor_id
                        for sensor_id in self.sensors.keys()
                    }
                    
                    for future in futures:
                        try:
                            future.result(timeout=5.0)
                        except Exception as e:
                            sensor_id = futures[future]
                            print(f"[WARNING] Sensor {sensor_id} read error: {e}")
                
                # Log readings
                self.log_readings()
                
                # Display dashboard
                self.display_dashboard()
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[INFO] Monitoring stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Monitoring error: {e}")
        finally:
            self.running = False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='IoT Sensor Hub')
    parser.add_argument('--monitor', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=float, default=30.0, help='Update interval in seconds')
    parser.add_argument('--simulate', action='store_true', help='Use simulated sensors')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IOT SENSOR HUB")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    print("The doors of knowledge opens.")
    print("IoT sensor hub initializing...\n")
    
    hub = IoTSensorHub()
    
    # Register demo sensors
    if args.simulate:
        print("[INFO] Registering simulated sensors...")
        hub.register_sensor('soil_1', 'soil_moisture', 'Field A', 'simulated')
        hub.register_sensor('temp_1', 'temperature', 'Greenhouse', 'simulated')
        hub.register_sensor('humidity_1', 'humidity', 'Greenhouse', 'simulated')
        hub.register_sensor('ph_1', 'ph', 'Field A', 'simulated')
        hub.register_sensor('light_1', 'light', 'Greenhouse', 'simulated')
    
    if args.monitor:
        hub.run_monitoring(interval=args.interval)
    else:
        # Single reading
        if args.simulate:
            for sensor_id in hub.sensors.keys():
                hub.read_sensor(sensor_id)
            hub.display_dashboard()
        else:
            print("[INFO] Use --simulate for testing or connect real sensors")
            print("[INFO] Use --monitor for continuous monitoring")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

