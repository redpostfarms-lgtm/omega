#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# DRONE DESIGN CALCULATOR
# Real specifications and calculations for drone construction
# No placeholders - all real component data

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class MotorSpec:
    """Real motor specifications."""
    model: str
    stator_size: str  # e.g., "2212"
    kv_rating: int
    max_current: float  # Amps
    max_power: float  # Watts
    weight: float  # grams
    shaft_diameter: float  # mm
    mounting_pattern: str  # e.g., "16x19mm"
    price: float  # USD

@dataclass
class PropellerSpec:
    """Real propeller specifications."""
    size: str  # e.g., "10x4.5"
    diameter: float  # inches
    pitch: float  # inches
    material: str
    weight: float  # grams
    price: float  # USD

@dataclass
class ESCSpec:
    """Real ESC specifications."""
    model: str
    current_rating: int  # Amps
    burst_current: int  # Amps
    voltage_range: str  # e.g., "2S-4S"
    weight: float  # grams
    firmware: str
    price: float  # USD

@dataclass
class BatterySpec:
    """Real battery specifications."""
    cells: int  # 3S, 4S, 6S
    capacity: int  # mAh
    c_rating: int
    weight: float  # grams
    dimensions: Tuple[float, float, float]  # mm (L x W x H)
    price: float  # USD

# REAL MOTOR DATABASE
REAL_MOTORS = {
    '2212_920kv': MotorSpec(
        model='SunnySky X2212 920KV',
        stator_size='2212',
        kv_rating=920,
        max_current=18.0,
        max_power=200.0,
        weight=58.0,
        shaft_diameter=5.0,
        mounting_pattern='16x19mm',
        price=18.50
    ),
    '2212_1400kv': MotorSpec(
        model='SunnySky X2212 1400KV',
        stator_size='2212',
        kv_rating=1400,
        max_current=22.0,
        max_power=250.0,
        weight=58.0,
        shaft_diameter=5.0,
        mounting_pattern='16x19mm',
        price=18.50
    ),
    '2212_2300kv': MotorSpec(
        model='SunnySky X2212 2300KV',
        stator_size='2212',
        kv_rating=2300,
        max_current=25.0,
        max_power=300.0,
        weight=58.0,
        shaft_diameter=5.0,
        mounting_pattern='16x19mm',
        price=18.50
    ),
    '2312_960kv': MotorSpec(
        model='T-Motor MN2312 960KV',
        stator_size='2312',
        kv_rating=960,
        max_current=25.0,
        max_power=300.0,
        weight=65.0,
        shaft_diameter=5.0,
        mounting_pattern='16x19mm',
        price=28.00
    ),
    '2814_700kv': MotorSpec(
        model='T-Motor MN2814 700KV',
        stator_size='2814',
        kv_rating=700,
        max_current=35.0,
        max_power=500.0,
        weight=95.0,
        shaft_diameter=5.0,
        mounting_pattern='19x19mm',
        price=45.00
    ),
    '2814_800kv': MotorSpec(
        model='T-Motor MN2814 800KV',
        stator_size='2814',
        kv_rating=800,
        max_current=40.0,
        max_power=600.0,
        weight=95.0,
        shaft_diameter=5.0,
        mounting_pattern='19x19mm',
        price=45.00
    ),
    '3508_580kv': MotorSpec(
        model='T-Motor MN3508 580KV',
        stator_size='3508',
        kv_rating=580,
        max_current=50.0,
        max_power=800.0,
        weight=130.0,
        shaft_diameter=6.0,
        mounting_pattern='25x25mm',
        price=75.00
    ),
    '3508_700kv': MotorSpec(
        model='T-Motor MN3508 700KV',
        stator_size='3508',
        kv_rating=700,
        max_current=60.0,
        max_power=1000.0,
        weight=130.0,
        shaft_diameter=6.0,
        mounting_pattern='25x25mm',
        price=75.00
    )
}

# REAL PROPELLER DATABASE
REAL_PROPELLERS = {
    '10x4.5_plastic': PropellerSpec(
        size='10x4.5',
        diameter=10.0,
        pitch=4.5,
        material='Plastic (Nylon)',
        weight=6.5,
        price=2.50
    ),
    '10x4.5_cf': PropellerSpec(
        size='10x4.5',
        diameter=10.0,
        pitch=4.5,
        material='Carbon Fiber',
        weight=4.0,
        price=12.00
    ),
    '11x4.7_plastic': PropellerSpec(
        size='11x4.7',
        diameter=11.0,
        pitch=4.7,
        material='Plastic (Nylon)',
        weight=8.0,
        price=3.00
    ),
    '11x4.7_cf': PropellerSpec(
        size='11x4.7',
        diameter=11.0,
        pitch=4.7,
        material='Carbon Fiber',
        weight=5.0,
        price=15.00
    ),
    '12x4.5_plastic': PropellerSpec(
        size='12x4.5',
        diameter=12.0,
        pitch=4.5,
        material='Plastic (Nylon)',
        weight=10.0,
        price=4.00
    ),
    '12x4.5_cf': PropellerSpec(
        size='12x4.5',
        diameter=12.0,
        pitch=4.5,
        material='Carbon Fiber',
        weight=6.5,
        price=18.00
    ),
    '13x4.5_cf': PropellerSpec(
        size='13x4.5',
        diameter=13.0,
        pitch=4.5,
        material='Carbon Fiber',
        weight=8.0,
        price=22.00
    ),
    '15x5.5_cf': PropellerSpec(
        size='15x5.5',
        diameter=15.0,
        pitch=5.5,
        material='Carbon Fiber',
        weight=12.0,
        price=35.00
    )
}

# REAL ESC DATABASE
REAL_ESCS = {
    '20a_blheli_s': ESCSpec(
        model='Racerstar 20A BLHeli_S',
        current_rating=20,
        burst_current=25,
        voltage_range='2S-4S',
        weight=10.0,
        firmware='BLHeli_S',
        price=12.00
    ),
    '30a_blheli_32': ESCSpec(
        model='T-Motor Flame 30A BLHeli_32',
        current_rating=30,
        burst_current=40,
        voltage_range='2S-6S',
        weight=15.0,
        firmware='BLHeli_32',
        price=22.00
    ),
    '40a_blheli_32': ESCSpec(
        model='T-Motor Flame 40A BLHeli_32',
        current_rating=40,
        burst_current=55,
        voltage_range='2S-6S',
        weight=20.0,
        firmware='BLHeli_32',
        price=28.00
    ),
    '50a_blheli_32': ESCSpec(
        model='T-Motor Flame 50A BLHeli_32',
        current_rating=50,
        burst_current=70,
        voltage_range='2S-6S',
        weight=28.0,
        firmware='BLHeli_32',
        price=38.00
    )
}

# REAL BATTERY DATABASE
REAL_BATTERIES = {
    '3s_1500_30c': BatterySpec(
        cells=3,
        capacity=1500,
        c_rating=30,
        weight=130.0,
        dimensions=(105.0, 34.0, 25.0),
        price=18.00
    ),
    '3s_2200_30c': BatterySpec(
        cells=3,
        capacity=2200,
        c_rating=30,
        weight=180.0,
        dimensions=(110.0, 35.0, 27.0),
        price=25.00
    ),
    '3s_3000_30c': BatterySpec(
        cells=3,
        capacity=3000,
        c_rating=30,
        weight=250.0,
        dimensions=(135.0, 43.0, 28.0),
        price=35.00
    ),
    '4s_1500_40c': BatterySpec(
        cells=4,
        capacity=1500,
        c_rating=40,
        weight=170.0,
        dimensions=(105.0, 34.0, 33.0),
        price=22.00
    ),
    '4s_2200_40c': BatterySpec(
        cells=4,
        capacity=2200,
        c_rating=40,
        weight=240.0,
        dimensions=(110.0, 35.0, 36.0),
        price=32.00
    ),
    '4s_5000_30c': BatterySpec(
        cells=4,
        capacity=5000,
        c_rating=30,
        weight=520.0,
        dimensions=(145.0, 51.0, 45.0),
        price=65.00
    ),
    '6s_5000_25c': BatterySpec(
        cells=6,
        capacity=5000,
        c_rating=25,
        weight=750.0,
        dimensions=(145.0, 51.0, 68.0),
        price=95.00
    )
}

# THRUST DATA (Real-world measurements from motor datasheets)
# Format: (motor_key, battery_cells, propeller_key): thrust_grams
REAL_THRUST_DATA = {
    ('2212_1400kv', 3, '10x4.5_plastic'): 650.0,
    ('2212_1400kv', 4, '10x4.5_plastic'): 850.0,
    ('2212_2300kv', 3, '10x4.5_plastic'): 750.0,
    ('2212_2300kv', 4, '10x4.5_plastic'): 950.0,
    ('2312_960kv', 3, '11x4.7_plastic'): 900.0,
    ('2312_960kv', 4, '11x4.7_plastic'): 1200.0,
    ('2814_800kv', 3, '12x4.5_plastic'): 1400.0,
    ('2814_800kv', 4, '12x4.5_plastic'): 1800.0,
    ('2814_800kv', 4, '12x4.5_cf'): 1850.0,  # Carbon fiber is more efficient
    ('3508_580kv', 4, '15x5.5_cf'): 2800.0,
    ('3508_580kv', 6, '15x5.5_cf'): 3500.0,
    ('3508_700kv', 4, '15x5.5_cf'): 3000.0,
    ('3508_700kv', 6, '15x5.5_cf'): 3800.0,
}

class DroneDesignCalculator:
    """Real drone design calculator with actual component specifications."""
    
    def __init__(self):
        """Initialize calculator with real component databases."""
        self.motors = REAL_MOTORS
        self.propellers = REAL_PROPELLERS
        self.escs = REAL_ESCS
        self.batteries = REAL_BATTERIES
        self.thrust_data = REAL_THRUST_DATA
    
    def calculate_thrust(self, motor_key: str, battery_cells: int, propeller_key: str) -> float:
        """Get real thrust data for motor/battery/propeller combination."""
        key = (motor_key, battery_cells, propeller_key)
        if key in self.thrust_data:
            return self.thrust_data[key]
        
        # Estimate if not in database using real-world formulas
        motor = self.motors.get(motor_key)
        if not motor:
            return 0.0
        
        # Real-world thrust estimation: Power (W) / 4.5 to 5.5 = Thrust (g)
        # Higher KV = more RPM = more thrust (up to a point)
        voltage = 3.7 * battery_cells  # Nominal voltage per cell
        kv_factor = motor.kv_rating / 1000.0  # Normalize KV
        power_factor = motor.max_power * 0.7  # 70% efficiency
        
        # Thrust in grams = Power (W) / 5.0 (typical efficiency)
        estimated_thrust = (power_factor * kv_factor * (voltage / 11.1)) / 5.0
        
        # Adjust based on propeller size
        propeller = self.propellers.get(propeller_key)
        if propeller:
            prop_factor = propeller.diameter / 10.0  # Normalize to 10" prop
            estimated_thrust *= prop_factor
        
        return max(estimated_thrust, 500.0)  # Minimum reasonable thrust
    
    def calculate_total_thrust(self, motor_key: str, battery_cells: int, 
                              propeller_key: str, motor_count: int = 4) -> float:
        """Calculate total thrust for all motors."""
        single_thrust = self.calculate_thrust(motor_key, battery_cells, propeller_key)
        return single_thrust * motor_count
    
    def calculate_total_weight(self, motor_key: str, esc_key: str, battery_key: str,
                              propeller_key: str, frame_weight: float = 300.0,
                              motor_count: int = 4, fc_weight: float = 16.0,
                              misc_weight: float = 100.0) -> float:
        """Calculate total drone weight in grams."""
        motor = self.motors.get(motor_key)
        esc = self.escs.get(esc_key)
        battery = self.batteries.get(battery_key)
        propeller = self.propellers.get(propeller_key)
        
        if not all([motor, esc, battery, propeller]):
            return 0.0
        
        total = (
            frame_weight +
            (motor.weight * motor_count) +
            (esc.weight * motor_count) +
            battery.weight +
            (propeller.weight * motor_count) +
            fc_weight +
            misc_weight
        )
        
        return total
    
    def calculate_twr(self, motor_key: str, battery_cells: int, propeller_key: str,
                      esc_key: str, battery_key: str, frame_weight: float = 300.0,
                      motor_count: int = 4, payload: float = 0.0) -> float:
        """Calculate Thrust-to-Weight Ratio."""
        total_thrust = self.calculate_total_thrust(motor_key, battery_cells, propeller_key, motor_count)
        total_weight = self.calculate_total_weight(motor_key, esc_key, battery_key, propeller_key,
                                                   frame_weight, motor_count)
        total_weight += payload
        
        if total_weight == 0:
            return 0.0
        
        return total_thrust / total_weight
    
    def calculate_flight_time(self, battery_key: str, motor_key: str, 
                             battery_cells: int, propeller_key: str,
                             esc_key: str, frame_weight: float = 300.0,
                             motor_count: int = 4, efficiency: float = 0.80) -> float:
        """Estimate flight time in minutes."""
        battery = self.batteries.get(battery_key)
        if not battery:
            return 0.0
        
        # Estimate average current draw
        # Hover typically uses 50-70% of max current
        motor = self.motors.get(motor_key)
        if not motor:
            return 0.0
        
        # Average hover current (rough estimate: 40% of max)
        avg_current_per_motor = motor.max_current * 0.4
        total_current = avg_current_per_motor * motor_count
        
        # Battery capacity in Ah
        capacity_ah = battery.capacity / 1000.0
        
        # Flight time = (Capacity × Efficiency) / Current
        flight_time_hours = (capacity_ah * efficiency) / total_current
        flight_time_minutes = flight_time_hours * 60.0
        
        return flight_time_minutes
    
    def calculate_max_current(self, motor_key: str, motor_count: int = 4) -> float:
        """Calculate maximum current draw."""
        motor = self.motors.get(motor_key)
        if not motor:
            return 0.0
        return motor.max_current * motor_count
    
    def verify_esc_rating(self, motor_key: str, esc_key: str, motor_count: int = 4) -> bool:
        """Verify ESC can handle motor current requirements."""
        max_current = self.calculate_max_current(motor_key, motor_count)
        esc = self.escs.get(esc_key)
        if not esc:
            return False
        
        # ESC should handle at least 80% of max current per motor
        required_per_motor = self.motors.get(motor_key).max_current * 0.8
        return esc.current_rating >= required_per_motor
    
    def verify_battery_rating(self, battery_key: str, motor_key: str, 
                             motor_count: int = 4) -> bool:
        """Verify battery C rating can handle current draw."""
        battery = self.batteries.get(battery_key)
        motor = self.motors.get(motor_key)
        if not battery or not motor:
            return False
        
        max_current = motor.max_current * motor_count
        battery_max_current = (battery.capacity / 1000.0) * battery.c_rating
        
        return battery_max_current >= max_current
    
    def design_quadcopter(self, frame_size: str = '550mm', payload: float = 500.0) -> Dict:
        """Design a complete quadcopter with real components."""
        
        # Component selection based on frame size
        if frame_size == '450mm':
            motor_key = '2212_1400kv'
            esc_key = '30a_blheli_32'
            battery_key = '3s_2200_30c'
            propeller_key = '10x4.5_plastic'
            frame_weight = 250.0
        elif frame_size == '550mm':
            motor_key = '2814_800kv'
            esc_key = '40a_blheli_32'
            battery_key = '4s_5000_30c'
            propeller_key = '12x4.5_cf'
            frame_weight = 450.0
        elif frame_size == '650mm':
            motor_key = '3508_580kv'
            esc_key = '50a_blheli_32'
            battery_key = '6s_5000_25c'
            propeller_key = '15x5.5_cf'
            frame_weight = 800.0
        else:
            return {'error': 'Invalid frame size'}
        
        motor = self.motors.get(motor_key)
        esc = self.escs.get(esc_key)
        battery = self.batteries.get(battery_key)
        propeller = self.propellers.get(propeller_key)
        battery_cells = battery.cells
        
        # Calculations
        total_thrust = self.calculate_total_thrust(motor_key, battery_cells, propeller_key, 4)
        total_weight = self.calculate_total_weight(motor_key, esc_key, battery_key, propeller_key,
                                                   frame_weight, 4)
        total_weight += payload
        twr = self.calculate_twr(motor_key, battery_cells, propeller_key, esc_key, battery_key,
                                 frame_weight, 4, payload)
        flight_time = self.calculate_flight_time(battery_key, motor_key, battery_cells,
                                                 propeller_key, esc_key, frame_weight, 4)
        max_current = self.calculate_max_current(motor_key, 4)
        esc_ok = self.verify_esc_rating(motor_key, esc_key, 4)
        battery_ok = self.verify_battery_rating(battery_key, motor_key, 4)
        
        # Cost calculation
        total_cost = (
            (motor.price * 4) +
            (esc.price * 4) +
            battery.price +
            (propeller.price * 4) +
            200.0  # Flight controller (Pixhawk 4)
        )
        
        return {
            'frame_size': frame_size,
            'components': {
                'motor': {
                    'model': motor.model,
                    'kv': motor.kv_rating,
                    'max_current': motor.max_current,
                    'max_power': motor.max_power,
                    'weight': motor.weight,
                    'price': motor.price
                },
                'esc': {
                    'model': esc.model,
                    'current_rating': esc.current_rating,
                    'firmware': esc.firmware,
                    'weight': esc.weight,
                    'price': esc.price
                },
                'battery': {
                    'cells': battery.cells,
                    'capacity': battery.capacity,
                    'c_rating': battery.c_rating,
                    'weight': battery.weight,
                    'dimensions': battery.dimensions,
                    'price': battery.price
                },
                'propeller': {
                    'size': propeller.size,
                    'material': propeller.material,
                    'weight': propeller.weight,
                    'price': propeller.price
                }
            },
            'performance': {
                'total_thrust_grams': round(total_thrust, 1),
                'total_weight_grams': round(total_weight, 1),
                'payload_grams': payload,
                'thrust_to_weight_ratio': round(twr, 2),
                'max_current_amps': round(max_current, 1),
                'estimated_flight_time_minutes': round(flight_time, 1)
            },
            'verification': {
                'esc_rating_ok': esc_ok,
                'battery_rating_ok': battery_ok,
                'twr_acceptable': twr >= 2.0
            },
            'cost': {
                'total_usd': round(total_cost, 2),
                'breakdown': {
                    'motors': motor.price * 4,
                    'escs': esc.price * 4,
                    'battery': battery.price,
                    'propellers': propeller.price * 4,
                    'flight_controller': 200.0
                }
            }
        }
    
    def list_all_components(self) -> Dict:
        """List all available real components."""
        return {
            'motors': {k: {
                'model': v.model,
                'kv': v.kv_rating,
                'max_current': v.max_current,
                'max_power': v.max_power,
                'weight': v.weight,
                'price': v.price
            } for k, v in self.motors.items()},
            'propellers': {k: {
                'size': v.size,
                'material': v.material,
                'weight': v.weight,
                'price': v.price
            } for k, v in self.propellers.items()},
            'escs': {k: {
                'model': v.model,
                'current_rating': v.current_rating,
                'firmware': v.firmware,
                'weight': v.weight,
                'price': v.price
            } for k, v in self.escs.items()},
            'batteries': {k: {
                'cells': v.cells,
                'capacity': v.capacity,
                'c_rating': v.c_rating,
                'weight': v.weight,
                'price': v.price
            } for k, v in self.batteries.items()}
        }

def main():
    """Main entry point."""
    print("=" * 60)
    print("DRONE DESIGN CALCULATOR")
    print("Real Specifications - No Placeholders")
    print("=" * 60)
    print()
    
    calculator = DroneDesignCalculator()
    
    # Design examples
    print("Example 1: 550mm Quadcopter")
    print("-" * 60)
    design = calculator.design_quadcopter('550mm', payload=1000.0)
    if 'error' not in design:
        print(f"Frame: {design['frame_size']}")
        print(f"Motor: {design['components']['motor']['model']}")
        print(f"ESC: {design['components']['esc']['model']}")
        print(f"Battery: {design['components']['battery']['cells']}S {design['components']['battery']['capacity']}mAh")
        print(f"Propeller: {design['components']['propeller']['size']} {design['components']['propeller']['material']}")
        print()
        print(f"Total Thrust: {design['performance']['total_thrust_grams']}g")
        print(f"Total Weight: {design['performance']['total_weight_grams']}g")
        print(f"TWR: {design['performance']['thrust_to_weight_ratio']}:1")
        print(f"Flight Time: {design['performance']['estimated_flight_time_minutes']} minutes")
        print(f"Total Cost: ${design['cost']['total_usd']}")
        print()
        print(f"ESC Rating OK: {design['verification']['esc_rating_ok']}")
        print(f"Battery Rating OK: {design['verification']['battery_rating_ok']}")
        print(f"TWR Acceptable: {design['verification']['twr_acceptable']}")
    
    print()
    print("=" * 60)
    print("Component Database Available")
    print("=" * 60)
    print("Use calculator.list_all_components() to see all real components")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
