#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# IRRIGATION AUTOMATION SYSTEM
# Automated watering schedules, soil moisture-based triggers, water usage optimization
# Integrates with IoT sensors and weather data

import json
import sys
import io
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
IRRIGATION_DIR = BRAIN / 'Archived' / 'irrigation'
IRRIGATION_DIR.mkdir(parents=True, exist_ok=True)

class IrrigationAutomation:
    """Automated irrigation system with soil moisture triggers."""
    
    def __init__(self):
        """Initialize irrigation system."""
        self.zones = {}
        self.schedules = {}
        self.history = []
        
        # Default thresholds
        self.moisture_threshold_low = 40.0  # percent
        self.moisture_threshold_high = 60.0  # percent
        self.watering_duration_default = 30.0  # minutes
        
        # Weather integration
        self.weather_data = {}
        self.et_calculations = {}  # Evapotranspiration
        
        # Soil moisture sensors (multi-depth)
        self.sensor_depths = [10, 30, 60]  # cm depths
        self.sensor_readings = {}
        
        # Variable rate application
        self.variable_rate_enabled = False
        self.zone_requirements = {}
    
    def register_zone(self, zone_id: str, name: str, area_sqft: float, crop_type: str):
        """Register an irrigation zone."""
        self.zones[zone_id] = {
            'name': name,
            'area_sqft': area_sqft,
            'crop_type': crop_type,
            'sensor_id': None,
            'valve_id': None,
            'enabled': True,
            'last_watered': None,
            'total_water_used': 0.0,  # gallons
            'registered_at': datetime.now().isoformat()
        }
        print(f"[OK] Zone registered: {zone_id} ({name}) - {area_sqft} sq ft, {crop_type}")
    
    def link_sensor(self, zone_id: str, sensor_id: str):
        """Link soil moisture sensor to zone."""
        if zone_id not in self.zones:
            print(f"[ERROR] Zone {zone_id} not found")
            return False
        
        self.zones[zone_id]['sensor_id'] = sensor_id
        print(f"[OK] Sensor {sensor_id} linked to zone {zone_id}")
        return True
    
    def link_valve(self, zone_id: str, valve_id: str):
        """Link irrigation valve to zone."""
        if zone_id not in self.zones:
            print(f"[ERROR] Zone {zone_id} not found")
            return False
        
        self.zones[zone_id]['valve_id'] = valve_id
        print(f"[OK] Valve {valve_id} linked to zone {zone_id}")
        return True
    
    def get_soil_moisture(self, sensor_id: str) -> Optional[float]:
        """Get current soil moisture from sensor."""
        # In real implementation, would read from IoT sensor hub
        # For now, simulate or read from sensor data file
        
        sensor_data_file = BRAIN / 'Archived' / 'sensor_data' / 'sensor_log_*.json'
        # Would read latest sensor reading
        
        # Simulate for demo
        return 45.0  # Default
    
    def get_multi_depth_moisture(self, zone_id: str) -> Dict:
        """Get soil moisture at multiple depths (10cm, 30cm, 60cm)."""
        zone = self.zones.get(zone_id)
        if not zone:
            return {'error': 'Zone not found'}
        
        sensor_id = zone.get('sensor_id')
        if not sensor_id:
            return {'error': 'No sensor linked'}
        
        # Multi-depth readings (in real implementation, would read from multi-depth sensor)
        return {
            'zone_id': zone_id,
            'depths_cm': self.sensor_depths,
            'moisture_10cm': 42.0,  # Would read from sensor
            'moisture_30cm': 48.0,
            'moisture_60cm': 52.0,
            'average': 47.3,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_et(self, zone_id: str, weather_data: Optional[Dict] = None) -> float:
        """Calculate evapotranspiration (ET) using enhanced Penman-Monteith equation."""
        zone = self.zones.get(zone_id)
        crop_type = zone.get('crop_type', 'general') if zone else 'general'
        
        if weather_data:
            temp = weather_data.get('temperature', 20.0)  # Celsius
            humidity = weather_data.get('humidity', 60.0)  # Percent
            wind_speed = weather_data.get('wind_speed', 2.0)  # m/s
            solar_rad = weather_data.get('solar_radiation', 500.0)  # W/m²
            pressure = weather_data.get('pressure', 101.3)  # kPa
        else:
            # Default values
            temp = 20.0
            humidity = 60.0
            wind_speed = 2.0
            solar_rad = 500.0
            pressure = 101.3
        
        # Enhanced Penman-Monteith equation
        # Constants
        T = temp + 273.15  # Convert to Kelvin
        G = 0.0  # Ground heat flux (assumed 0 for daily calculations)
        
        # Saturation vapor pressure (es) - Tetens equation
        es = 0.6108 * (10 ** (7.5 * temp / (temp + 237.3)))
        
        # Actual vapor pressure (ea)
        ea = es * (humidity / 100.0)
        
        # Slope of saturation vapor pressure curve (Δ)
        delta = (4098 * es) / ((temp + 237.3) ** 2)
        
        # Psychrometric constant (γ)
        gamma = 0.000665 * pressure
        
        # Net radiation (Rn) - simplified
        # Convert solar radiation from W/m² to MJ/m²/day
        Rs = solar_rad * 0.0864  # W/m² to MJ/m²/day
        Rns = 0.77 * Rs  # Net shortwave radiation
        Rnl = 4.903e-9 * (T ** 4) * (0.34 - 0.14 * (ea ** 0.5)) * ((1.35 * Rs / (Rs + 0.000001)) - 0.35)
        Rn = Rns - Rnl  # Net radiation
        
        # Crop coefficient (Kc) - varies by crop and growth stage
        crop_coefficients = {
            'corn': 1.2,
            'wheat': 1.15,
            'soybeans': 1.1,
            'tomatoes': 1.2,
            'lettuce': 1.0,
            'potatoes': 1.1,
            'general': 1.0
        }
        Kc = crop_coefficients.get(crop_type.lower(), 1.0)
        
        # Penman-Monteith equation
        # ET = (0.408*Δ*(Rn-G) + γ*(900/(T+273))*u2*(es-ea)) / (Δ + γ*(1+0.34*u2))
        numerator = (0.408 * delta * (Rn - G)) + (gamma * (900 / T) * wind_speed * (es - ea))
        denominator = delta + (gamma * (1 + 0.34 * wind_speed))
        
        if denominator > 0:
            et0 = numerator / denominator  # Reference ET (mm/day)
            etc = et0 * Kc  # Crop-specific ET
            et0_value = et0
        else:
            # Fallback to simplified method
            etc = (solar_rad * 0.0023 * (temp + 17.8) * ((100 - humidity) / 100) ** 0.5) / 10
            et0_value = etc / Kc  # Estimate reference ET
        
        # Store ET calculation
        if zone_id not in self.et_calculations:
            self.et_calculations[zone_id] = []
        self.et_calculations[zone_id].append({
            'et_mm_per_day': round(etc, 2),
            'et0_reference': round(et0_value, 2),
            'crop_coefficient': Kc,
            'timestamp': datetime.now().isoformat(),
            'weather': weather_data
        })
        
        # Keep last 30 calculations
        if len(self.et_calculations[zone_id]) > 30:
            self.et_calculations[zone_id] = self.et_calculations[zone_id][-30:]
        
        return round(etc, 2)
    
    def set_variable_rate_application(self, zone_id: str, enabled: bool, rates: Optional[Dict] = None):
        """Enable variable rate application for a zone."""
        if zone_id not in self.zones:
            return False
        
        self.variable_rate_enabled = enabled
        if rates:
            self.zone_requirements[zone_id] = rates
        
        print(f"[OK] Variable rate application {'enabled' if enabled else 'disabled'} for {zone_id}")
        return True
    
    def monitor_flow_and_pressure(self, zone_id: str) -> Dict:
        """Monitor flow rate and pressure for leak detection."""
        zone = self.zones.get(zone_id)
        if not zone:
            return {'error': 'Zone not found'}
        
        # In real implementation, would read from flow/pressure sensors
        flow_rate = 2.0  # GPM
        pressure = 45.0  # PSI
        
        # Leak detection (flow higher than expected for given pressure)
        expected_flow = pressure * 0.05  # Simplified relationship
        leak_detected = flow_rate > expected_flow * 1.2
        
        return {
            'zone_id': zone_id,
            'flow_rate_gpm': flow_rate,
            'pressure_psi': pressure,
            'leak_detected': leak_detected,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_watering_duration(self, zone_id: str, current_moisture: float, 
                                   target_moisture: float = 55.0, use_et: bool = True) -> float:
        """Calculate required watering duration with ET adjustment."""
        if zone_id not in self.zones:
            return 0.0
        
        zone = self.zones[zone_id]
        area = zone['area_sqft']
        crop_type = zone['crop_type']
        
        # Base duration calculation
        moisture_deficit = target_moisture - current_moisture
        if moisture_deficit <= 0:
            return 0.0
        
        # ET adjustment
        et_adjustment = 1.0
        if use_et and self.et_calculations:
            latest_et = list(self.et_calculations.values())[-1]
            # Adjust based on ET (higher ET = more water needed)
            et_adjustment = 1.0 + (latest_et / 10.0)  # Scale ET to adjustment factor
        
        # Variable rate adjustment
        rate_adjustment = 1.0
        if self.variable_rate_enabled and zone_id in self.zone_requirements:
            rate_adjustment = self.zone_requirements[zone_id].get('water_multiplier', 1.0)
        
        # Water requirement by crop (inches per week)
        crop_requirements = {
            'corn': 1.5,
            'wheat': 1.0,
            'tomatoes': 2.0,
            'lettuce': 1.5,
            'potatoes': 1.5
        }
        
        weekly_requirement = crop_requirements.get(crop_type.lower(), 1.5)  # inches
        
        # Calculate deficit
        moisture_deficit = target_moisture - current_moisture
        if moisture_deficit <= 0:
            return 0.0
        
        # Convert to watering duration (simplified)
        # 1 inch = ~0.623 gallons per sq ft
        gallons_needed = (moisture_deficit / 100) * weekly_requirement * area * 0.623
        
        # Assume flow rate of 2 GPM per zone
        flow_rate = 2.0  # gallons per minute
        duration_minutes = gallons_needed / flow_rate
        
        # Cap at reasonable limits
        duration_minutes = max(5.0, min(120.0, duration_minutes))
        
        return round(duration_minutes, 1)
    
    def should_water(self, zone_id: str) -> tuple[bool, str]:
        """Determine if zone needs watering."""
        if zone_id not in self.zones:
            return False, "Zone not found"
        
        zone = self.zones[zone_id]
        if not zone['enabled']:
            return False, "Zone disabled"
        
        sensor_id = zone.get('sensor_id')
        if not sensor_id:
            return False, "No sensor linked"
        
        # Get current moisture
        moisture = self.get_soil_moisture(sensor_id)
        if moisture is None:
            return False, "Sensor reading unavailable"
        
        # Check threshold
        if moisture < self.moisture_threshold_low:
            return True, f"Soil moisture low: {moisture:.1f}%"
        elif moisture < self.moisture_threshold_high:
            return True, f"Soil moisture below optimal: {moisture:.1f}%"
        else:
            return False, f"Soil moisture adequate: {moisture:.1f}%"
    
    def water_zone(self, zone_id: str, duration: Optional[float] = None, manual: bool = False) -> Dict:
        """Water a zone."""
        if zone_id not in self.zones:
            return {'error': 'Zone not found'}
        
        zone = self.zones[zone_id]
        
        # Check if should water (unless manual)
        if not manual:
            should, reason = self.should_water(zone_id)
            if not should:
                return {'skipped': True, 'reason': reason}
        
        # Get current moisture
        sensor_id = zone.get('sensor_id')
        current_moisture = self.get_soil_moisture(sensor_id) if sensor_id else 50.0
        
        # Calculate duration if not provided
        if duration is None:
            duration = self.calculate_watering_duration(zone_id, current_moisture)
        
        # Calculate water usage
        flow_rate = 2.0  # GPM
        water_used = duration * flow_rate  # gallons
        
        # Simulate watering (in real implementation, would control valve)
        valve_id = zone.get('valve_id')
        if valve_id:
            print(f"[INFO] Opening valve {valve_id} for {duration} minutes...")
            # Would send command to valve controller
            time.sleep(0.1)  # Simulate
        
        # Record watering
        watering_record = {
            'zone_id': zone_id,
            'duration_minutes': duration,
            'water_used_gallons': round(water_used, 2),
            'moisture_before': round(current_moisture, 1),
            'moisture_after': round(current_moisture + 10, 1),  # Simulate increase
            'manual': manual,
            'timestamp': datetime.now().isoformat()
        }
        
        self.history.append(watering_record)
        zone['last_watered'] = datetime.now().isoformat()
        zone['total_water_used'] += water_used
        
        print(f"[OK] Zone {zone_id} watered: {duration} min, {water_used:.1f} gallons")
        
        return watering_record
    
    def create_schedule(self, zone_id: str, days: List[int], time_str: str, duration: float):
        """
        Create watering schedule.
        
        Args:
            zone_id: Zone identifier
            days: List of days (0=Monday, 6=Sunday)
            time_str: Time in HH:MM format
            duration: Duration in minutes
        """
        if zone_id not in self.zones:
            return False
        
        schedule_id = f"{zone_id}_schedule_{len(self.schedules)}"
        self.schedules[schedule_id] = {
            'zone_id': zone_id,
            'days': days,
            'time': time_str,
            'duration': duration,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"[OK] Schedule created: {schedule_id} for zone {zone_id}")
        return True
    
    def check_schedules(self):
        """Check and execute scheduled waterings."""
        now = datetime.now()
        current_day = now.weekday()  # 0=Monday
        current_time = now.strftime('%H:%M')
        
        for schedule_id, schedule in self.schedules.items():
            if not schedule['enabled']:
                continue
            
            if current_day in schedule['days'] and current_time == schedule['time']:
                zone_id = schedule['zone_id']
                duration = schedule['duration']
                
                # Check if already watered today
                zone = self.zones[zone_id]
                if zone['last_watered']:
                    last_watered = datetime.fromisoformat(zone['last_watered'])
                    if last_watered.date() == now.date():
                        continue  # Already watered today
                
                # Execute watering
                self.water_zone(zone_id, duration=duration, manual=False)
    
    def get_water_usage_report(self, days: int = 7) -> Dict:
        """Get water usage report."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_history = [
            h for h in self.history
            if datetime.fromisoformat(h['timestamp']) >= cutoff_date
        ]
        
        total_water = sum(h['water_used_gallons'] for h in recent_history)
        total_duration = sum(h['duration_minutes'] for h in recent_history)
        
        by_zone = {}
        for record in recent_history:
            zone_id = record['zone_id']
            if zone_id not in by_zone:
                by_zone[zone_id] = {
                    'water_used': 0.0,
                    'duration': 0.0,
                    'count': 0
                }
            by_zone[zone_id]['water_used'] += record['water_used_gallons']
            by_zone[zone_id]['duration'] += record['duration_minutes']
            by_zone[zone_id]['count'] += 1
        
        return {
            'period_days': days,
            'total_water_gallons': round(total_water, 2),
            'total_duration_minutes': round(total_duration, 1),
            'total_waterings': len(recent_history),
            'by_zone': by_zone,
            'generated_at': datetime.now().isoformat()
        }
    
    def save_data(self):
        """Save irrigation data."""
        data_file = IRRIGATION_DIR / 'irrigation_data.json'
        data = {
            'zones': self.zones,
            'schedules': self.schedules,
            'history': self.history[-100:],  # Last 100 records
            'updated_at': datetime.now().isoformat()
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Irrigation Automation System')
    parser.add_argument('--register-zone', nargs=4, metavar=('ID', 'NAME', 'AREA', 'CROP'),
                       help='Register irrigation zone')
    parser.add_argument('--water', nargs=2, metavar=('ZONE_ID', 'DURATION'),
                       help='Water a zone (duration in minutes, or "auto")')
    parser.add_argument('--schedule', nargs=4, metavar=('ZONE_ID', 'DAYS', 'TIME', 'DURATION'),
                       help='Create schedule (days: 0-6, time: HH:MM)')
    parser.add_argument('--usage', type=int, default=7, help='Water usage report (days)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IRRIGATION AUTOMATION SYSTEM")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    print("The doors of knowledge opens.")
    print("Irrigation automation system initializing...\n")
    
    irrigation = IrrigationAutomation()
    
    if args.register_zone:
        zone_id, name, area, crop = args.register_zone
        irrigation.register_zone(zone_id, name, float(area), crop)
        irrigation.save_data()
    
    elif args.water:
        zone_id, duration_str = args.water
        duration = None if duration_str == 'auto' else float(duration_str)
        result = irrigation.water_zone(zone_id, duration=duration, manual=True)
        print(json.dumps(result, indent=2))
        irrigation.save_data()
    
    elif args.schedule:
        zone_id, days_str, time_str, duration_str = args.schedule
        days = [int(d) for d in days_str.split(',')]
        duration = float(duration_str)
        irrigation.create_schedule(zone_id, days, time_str, duration)
        irrigation.save_data()
    
    elif args.usage:
        report = irrigation.get_water_usage_report(days=args.usage)
        print(json.dumps(report, indent=2))
    
    else:
        print("Usage examples:")
        print("  --register-zone zone1 'Field A' 1000 corn")
        print("  --water zone1 auto")
        print("  --water zone1 30")
        print("  --schedule zone1 '0,2,4' '06:00' 30")
        print("  --usage 7")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

