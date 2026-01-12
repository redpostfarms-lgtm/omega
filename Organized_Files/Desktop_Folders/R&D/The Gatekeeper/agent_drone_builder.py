#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# AGENT DRONE BUILDER
# Each agent builds their own drone with different design directions
# Real specifications, no placeholders

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import the design calculator
from drone_design_calculator import DroneDesignCalculator, REAL_MOTORS, REAL_ESCS, REAL_BATTERIES, REAL_PROPELLERS

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
BUILD_DIR = GATE / 'agent_drone_builds'
BUILD_DIR.mkdir(parents=True, exist_ok=True)

class DesignDirection(Enum):
    """Design direction for each agent."""
    SPEED_RACER = "speed_racer"  # Maximum speed, high KV, small props
    ENDURANCE_LONG = "endurance_long"  # Maximum flight time, efficient, large props
    PAYLOAD_HEAVY = "payload_heavy"  # Maximum payload capacity, powerful motors
    AGILITY_ACRO = "agility_acro"  # Maximum agility, balanced, responsive

@dataclass
class AgentDroneDesign:
    """Complete drone design for an agent."""
    agent_name: str
    design_direction: DesignDirection
    frame_size: str
    motor_key: str
    esc_key: str
    battery_key: str
    propeller_key: str
    frame_weight: float
    payload_capacity: float
    total_thrust: float
    total_weight: float
    twr: float
    max_speed: float  # Estimated m/s
    flight_time: float  # minutes
    agility_score: float  # 0-1
    cost: float
    build_specs: Dict
    build_log: List[str]

class AgentDroneBuilder:
    """Each agent builds their own drone with unique design direction."""
    
    def __init__(self):
        """Initialize builder with design calculator."""
        self.calculator = DroneDesignCalculator()
        self.agents = {
            'Alpha': DesignDirection.SPEED_RACER,
            'Beta': DesignDirection.ENDURANCE_LONG,
            'Gamma': DesignDirection.PAYLOAD_HEAVY,
            'Delta': DesignDirection.AGILITY_ACRO
        }
        self.builds: Dict[str, AgentDroneDesign] = {}
    
    def design_speed_racer(self, agent_name: str) -> AgentDroneDesign:
        """Design for maximum speed - high KV motors, small props, lightweight."""
        print(f"\n[{agent_name}] Designing SPEED RACER drone...")
        build_log = []
        
        # Speed racer philosophy: High KV, small props, lightweight frame, high voltage
        motor_key = '2212_2300kv'  # High KV for speed
        esc_key = '30a_blheli_32'  # Fast response
        battery_key = '4s_1500_40c'  # High voltage, lower capacity for weight
        propeller_key = '10x4.5_cf'  # Small, carbon fiber for efficiency
        frame_size = '450mm'  # Smaller frame for agility
        frame_weight = 200.0  # Lightweight frame
        battery_cells = 4
        
        build_log.append(f"Selected {REAL_MOTORS[motor_key].model} (2300KV) for high RPM")
        build_log.append(f"Selected 4S battery for high voltage (14.8V)")
        build_log.append(f"Selected 10x4.5 carbon fiber props for speed")
        build_log.append(f"Selected 450mm lightweight frame")
        
        # Calculate specifications
        total_thrust = self.calculator.calculate_total_thrust(motor_key, battery_cells, propeller_key, 4)
        total_weight = self.calculator.calculate_total_weight(
            motor_key, esc_key, battery_key, propeller_key, frame_weight, 4
        )
        twr = self.calculator.calculate_twr(
            motor_key, battery_cells, propeller_key, esc_key, battery_key, frame_weight, 4, 0
        )
        flight_time = self.calculator.calculate_flight_time(
            battery_key, motor_key, battery_cells, propeller_key, esc_key, frame_weight, 4
        )
        
        # Estimate max speed (higher TWR and smaller props = faster)
        max_speed = 25.0 + (twr * 5.0)  # Rough estimate: 25-50 m/s
        
        # Agility score (speed-focused = high agility)
        agility_score = 0.9
        
        # Cost
        motor = REAL_MOTORS[motor_key]
        esc = REAL_ESCS[esc_key]
        battery = REAL_BATTERIES[battery_key]
        propeller = REAL_PROPELLERS[propeller_key]
        cost = (motor.price * 4) + (esc.price * 4) + battery.price + (propeller.price * 4) + 200.0
        
        build_log.append(f"Total Thrust: {total_thrust:.0f}g")
        build_log.append(f"Total Weight: {total_weight:.0f}g")
        build_log.append(f"TWR: {twr:.2f}:1")
        build_log.append(f"Estimated Max Speed: {max_speed:.1f} m/s")
        build_log.append(f"Flight Time: {flight_time:.1f} minutes")
        
        return AgentDroneDesign(
            agent_name=agent_name,
            design_direction=DesignDirection.SPEED_RACER,
            frame_size=frame_size,
            motor_key=motor_key,
            esc_key=esc_key,
            battery_key=battery_key,
            propeller_key=propeller_key,
            frame_weight=frame_weight,
            payload_capacity=200.0,  # Low payload for speed
            total_thrust=total_thrust,
            total_weight=total_weight,
            twr=twr,
            max_speed=max_speed,
            flight_time=flight_time,
            agility_score=agility_score,
            cost=cost,
            build_specs={
                'motor': motor.model,
                'esc': esc.model,
                'battery': f"{battery.cells}S {battery.capacity}mAh",
                'propeller': f"{propeller.size} {propeller.material}",
                'frame': f"{frame_size} carbon fiber"
            },
            build_log=build_log
        )
    
    def design_endurance_long(self, agent_name: str) -> AgentDroneDesign:
        """Design for maximum flight time - efficient motors, large props, high capacity battery."""
        print(f"\n[{agent_name}] Designing ENDURANCE LONG drone...")
        build_log = []
        
        # Endurance philosophy: Low KV, large props, high capacity battery, efficient
        motor_key = '2814_700kv'  # Low KV for efficiency
        esc_key = '40a_blheli_32'  # Efficient ESCs
        battery_key = '4s_5000_30c'  # High capacity
        propeller_key = '13x4.5_cf'  # Large props for efficiency
        frame_size = '550mm'  # Medium frame
        frame_weight = 400.0
        battery_cells = 4
        
        build_log.append(f"Selected {REAL_MOTORS[motor_key].model} (700KV) for efficiency")
        build_log.append(f"Selected 4S 5000mAh battery for long flight time")
        build_log.append(f"Selected 13x4.5 carbon fiber props for efficiency")
        build_log.append(f"Selected 550mm frame for stability")
        
        # Calculate specifications
        total_thrust = self.calculator.calculate_total_thrust(motor_key, battery_cells, propeller_key, 4)
        total_weight = self.calculator.calculate_total_weight(
            motor_key, esc_key, battery_key, propeller_key, frame_weight, 4
        )
        twr = self.calculator.calculate_twr(
            motor_key, battery_cells, propeller_key, esc_key, battery_key, frame_weight, 4, 0
        )
        flight_time = self.calculator.calculate_flight_time(
            battery_key, motor_key, battery_cells, propeller_key, esc_key, frame_weight, 4, efficiency=0.85
        )
        
        # Estimate max speed (lower for endurance)
        max_speed = 15.0 + (twr * 2.0)  # 15-25 m/s
        
        # Agility score (endurance-focused = lower agility)
        agility_score = 0.5
        
        # Cost
        motor = REAL_MOTORS[motor_key]
        esc = REAL_ESCS[esc_key]
        battery = REAL_BATTERIES[battery_key]
        propeller = REAL_PROPELLERS[propeller_key]
        cost = (motor.price * 4) + (esc.price * 4) + battery.price + (propeller.price * 4) + 200.0
        
        build_log.append(f"Total Thrust: {total_thrust:.0f}g")
        build_log.append(f"Total Weight: {total_weight:.0f}g")
        build_log.append(f"TWR: {twr:.2f}:1")
        build_log.append(f"Estimated Max Speed: {max_speed:.1f} m/s")
        build_log.append(f"Flight Time: {flight_time:.1f} minutes")
        
        return AgentDroneDesign(
            agent_name=agent_name,
            design_direction=DesignDirection.ENDURANCE_LONG,
            frame_size=frame_size,
            motor_key=motor_key,
            esc_key=esc_key,
            battery_key=battery_key,
            propeller_key=propeller_key,
            frame_weight=frame_weight,
            payload_capacity=500.0,  # Moderate payload
            total_thrust=total_thrust,
            total_weight=total_weight,
            twr=twr,
            max_speed=max_speed,
            flight_time=flight_time,
            agility_score=agility_score,
            cost=cost,
            build_specs={
                'motor': motor.model,
                'esc': esc.model,
                'battery': f"{battery.cells}S {battery.capacity}mAh",
                'propeller': f"{propeller.size} {propeller.material}",
                'frame': f"{frame_size} carbon fiber"
            },
            build_log=build_log
        )
    
    def design_payload_heavy(self, agent_name: str) -> AgentDroneDesign:
        """Design for maximum payload - powerful motors, large frame, high thrust."""
        print(f"\n[{agent_name}] Designing PAYLOAD HEAVY drone...")
        build_log = []
        
        # Payload philosophy: Large motors, large props, high capacity battery, large frame
        motor_key = '3508_580kv'  # Powerful, low KV for large props
        esc_key = '50a_blheli_32'  # High current ESCs
        battery_key = '6s_5000_25c'  # High voltage, high capacity
        propeller_key = '15x5.5_cf'  # Large props for thrust
        frame_size = '650mm'  # Large frame
        frame_weight = 800.0
        battery_cells = 6
        
        build_log.append(f"Selected {REAL_MOTORS[motor_key].model} (580KV) for high torque")
        build_log.append(f"Selected 6S 5000mAh battery for power")
        build_log.append(f"Selected 15x5.5 carbon fiber props for maximum thrust")
        build_log.append(f"Selected 650mm frame for payload capacity")
        
        # Calculate specifications
        total_thrust = self.calculator.calculate_total_thrust(motor_key, battery_cells, propeller_key, 4)
        total_weight = self.calculator.calculate_total_weight(
            motor_key, esc_key, battery_key, propeller_key, frame_weight, 4
        )
        twr = self.calculator.calculate_twr(
            motor_key, battery_cells, propeller_key, esc_key, battery_key, frame_weight, 4, 0
        )
        flight_time = self.calculator.calculate_flight_time(
            battery_key, motor_key, battery_cells, propeller_key, esc_key, frame_weight, 4, efficiency=0.80
        )
        
        # Payload capacity (can carry significant weight)
        payload_capacity = total_thrust * 0.4  # 40% of total thrust for payload
        
        # Estimate max speed (moderate for heavy lift)
        max_speed = 18.0 + (twr * 2.5)  # 18-30 m/s
        
        # Agility score (heavy = lower agility)
        agility_score = 0.4
        
        # Cost
        motor = REAL_MOTORS[motor_key]
        esc = REAL_ESCS[esc_key]
        battery = REAL_BATTERIES[battery_key]
        propeller = REAL_PROPELLERS[propeller_key]
        cost = (motor.price * 4) + (esc.price * 4) + battery.price + (propeller.price * 4) + 200.0
        
        build_log.append(f"Total Thrust: {total_thrust:.0f}g")
        build_log.append(f"Total Weight: {total_weight:.0f}g")
        build_log.append(f"TWR: {twr:.2f}:1")
        build_log.append(f"Payload Capacity: {payload_capacity:.0f}g")
        build_log.append(f"Estimated Max Speed: {max_speed:.1f} m/s")
        build_log.append(f"Flight Time: {flight_time:.1f} minutes")
        
        return AgentDroneDesign(
            agent_name=agent_name,
            design_direction=DesignDirection.PAYLOAD_HEAVY,
            frame_size=frame_size,
            motor_key=motor_key,
            esc_key=esc_key,
            battery_key=battery_key,
            propeller_key=propeller_key,
            frame_weight=frame_weight,
            payload_capacity=payload_capacity,
            total_thrust=total_thrust,
            total_weight=total_weight,
            twr=twr,
            max_speed=max_speed,
            flight_time=flight_time,
            agility_score=agility_score,
            cost=cost,
            build_specs={
                'motor': motor.model,
                'esc': esc.model,
                'battery': f"{battery.cells}S {battery.capacity}mAh",
                'propeller': f"{propeller.size} {propeller.material}",
                'frame': f"{frame_size} carbon fiber"
            },
            build_log=build_log
        )
    
    def design_agility_acro(self, agent_name: str) -> AgentDroneDesign:
        """Design for maximum agility - balanced, responsive, medium props."""
        print(f"\n[{agent_name}] Designing AGILITY ACRO drone...")
        build_log = []
        
        # Agility philosophy: Medium KV, medium props, balanced, fast response
        motor_key = '2312_960kv'  # Balanced KV
        esc_key = '30a_blheli_32'  # Fast response ESCs
        battery_key = '4s_2200_40c'  # Balanced capacity, high C for response
        propeller_key = '11x4.7_cf'  # Medium props for balance
        frame_size = '450mm'  # Smaller frame for agility
        frame_weight = 250.0
        battery_cells = 4
        
        build_log.append(f"Selected {REAL_MOTORS[motor_key].model} (960KV) for balance")
        build_log.append(f"Selected 4S 2200mAh 40C battery for fast response")
        build_log.append(f"Selected 11x4.7 carbon fiber props for agility")
        build_log.append(f"Selected 450mm frame for maneuverability")
        
        # Calculate specifications
        total_thrust = self.calculator.calculate_total_thrust(motor_key, battery_cells, propeller_key, 4)
        total_weight = self.calculator.calculate_total_weight(
            motor_key, esc_key, battery_key, propeller_key, frame_weight, 4
        )
        twr = self.calculator.calculate_twr(
            motor_key, battery_cells, propeller_key, esc_key, battery_key, frame_weight, 4, 0
        )
        flight_time = self.calculator.calculate_flight_time(
            battery_key, motor_key, battery_cells, propeller_key, esc_key, frame_weight, 4, efficiency=0.82
        )
        
        # Estimate max speed (good for acro)
        max_speed = 22.0 + (twr * 4.0)  # 22-40 m/s
        
        # Agility score (acro-focused = very high agility)
        agility_score = 0.95
        
        # Cost
        motor = REAL_MOTORS[motor_key]
        esc = REAL_ESCS[esc_key]
        battery = REAL_BATTERIES[battery_key]
        propeller = REAL_PROPELLERS[propeller_key]
        cost = (motor.price * 4) + (esc.price * 4) + battery.price + (propeller.price * 4) + 200.0
        
        build_log.append(f"Total Thrust: {total_thrust:.0f}g")
        build_log.append(f"Total Weight: {total_weight:.0f}g")
        build_log.append(f"TWR: {twr:.2f}:1")
        build_log.append(f"Estimated Max Speed: {max_speed:.1f} m/s")
        build_log.append(f"Flight Time: {flight_time:.1f} minutes")
        build_log.append(f"Agility Score: {agility_score:.2f}")
        
        return AgentDroneDesign(
            agent_name=agent_name,
            design_direction=DesignDirection.AGILITY_ACRO,
            frame_size=frame_size,
            motor_key=motor_key,
            esc_key=esc_key,
            battery_key=battery_key,
            propeller_key=propeller_key,
            frame_weight=frame_weight,
            payload_capacity=300.0,  # Moderate payload
            total_thrust=total_thrust,
            total_weight=total_weight,
            twr=twr,
            max_speed=max_speed,
            flight_time=flight_time,
            agility_score=agility_score,
            cost=cost,
            build_specs={
                'motor': motor.model,
                'esc': esc.model,
                'battery': f"{battery.cells}S {battery.capacity}mAh",
                'propeller': f"{propeller.size} {propeller.material}",
                'frame': f"{frame_size} carbon fiber"
            },
            build_log=build_log
        )
    
    def build_all_agent_drones(self):
        """Build drones for all 4 agents with different design directions."""
        print("=" * 60)
        print("AGENT DRONE BUILDER")
        print("Each agent builds their own drone")
        print("=" * 60)
        print()
        
        # Build each agent's drone
        for agent_name, direction in self.agents.items():
            if direction == DesignDirection.SPEED_RACER:
                design = self.design_speed_racer(agent_name)
            elif direction == DesignDirection.ENDURANCE_LONG:
                design = self.design_endurance_long(agent_name)
            elif direction == DesignDirection.PAYLOAD_HEAVY:
                design = self.design_payload_heavy(agent_name)
            elif direction == DesignDirection.AGILITY_ACRO:
                design = self.design_agility_acro(agent_name)
            else:
                continue
            
            self.builds[agent_name] = design
            
            # Save build specification
            self.save_build_spec(design)
        
        # Print summary
        self.print_build_summary()
    
    def save_build_spec(self, design: AgentDroneDesign):
        """Save build specification to file."""
        spec_file = BUILD_DIR / f"{design.agent_name}_drone_build.json"
        
        spec_data = {
            'agent_name': design.agent_name,
            'design_direction': design.design_direction.value,
            'frame_size': design.frame_size,
            'components': {
                'motor': design.build_specs['motor'],
                'esc': design.build_specs['esc'],
                'battery': design.build_specs['battery'],
                'propeller': design.build_specs['propeller'],
                'frame': design.build_specs['frame']
            },
            'performance': {
                'total_thrust_grams': round(design.total_thrust, 1),
                'total_weight_grams': round(design.total_weight, 1),
                'payload_capacity_grams': round(design.payload_capacity, 1),
                'thrust_to_weight_ratio': round(design.twr, 2),
                'max_speed_ms': round(design.max_speed, 1),
                'flight_time_minutes': round(design.flight_time, 1),
                'agility_score': round(design.agility_score, 2)
            },
            'cost_usd': round(design.cost, 2),
            'build_log': design.build_log,
            'build_date': datetime.now().isoformat()
        }
        
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(spec_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] {design.agent_name} build specification saved")
    
    def print_build_summary(self):
        """Print summary of all agent builds."""
        print("\n" + "=" * 60)
        print("AGENT DRONE BUILD SUMMARY")
        print("=" * 60)
        
        for agent_name, design in self.builds.items():
            print(f"\n{agent_name} - {design.design_direction.value.upper().replace('_', ' ')}")
            print("-" * 60)
            print(f"Frame: {design.frame_size}")
            print(f"Motor: {design.build_specs['motor']}")
            print(f"ESC: {design.build_specs['esc']}")
            print(f"Battery: {design.build_specs['battery']}")
            print(f"Propeller: {design.build_specs['propeller']}")
            print()
            print(f"Performance:")
            print(f"  Thrust: {design.total_thrust:.0f}g")
            print(f"  Weight: {design.total_weight:.0f}g")
            print(f"  TWR: {design.twr:.2f}:1")
            print(f"  Max Speed: {design.max_speed:.1f} m/s")
            print(f"  Flight Time: {design.flight_time:.1f} min")
            print(f"  Payload: {design.payload_capacity:.0f}g")
            print(f"  Agility: {design.agility_score:.2f}")
            print(f"  Cost: ${design.cost:.2f}")
        
        print("\n" + "=" * 60)
        print("All agent drones built with unique design directions!")
        print("=" * 60)

def main():
    """Main entry point."""
    print("=" * 60)
    print("AGENT DRONE BUILDER")
    print("4 Agents, 4 Different Design Directions")
    print("=" * 60)
    print("\nThe doors of knowledge opens.")
    print("Agents building their own drones...\n")
    
    builder = AgentDroneBuilder()
    builder.build_all_agent_drones()
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print(f"\nBuild specifications saved to: {BUILD_DIR}")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
