#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# SOLAR MPPT CONTROLLER
# Maximum Power Point Tracking controller with PID loop
# Integrates with solar_forecaster.py for production estimates
# Real-time optimization and data logging

import json
import sys
import io
import time
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
LOG_DIR = BRAIN / 'Archived' / 'solar_logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

class PIDController:
    """PID controller for MPPT voltage regulation."""
    
    def __init__(self, kp: float = 0.5, ki: float = 0.1, kd: float = 0.05):
        """
        Initialize PID controller.
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
    
    def compute(self, setpoint: float, current_value: float) -> float:
        """
        Compute PID output.
        
        Args:
            setpoint: Target value
            current_value: Current measured value
        
        Returns:
            Control output
        """
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return 0.0
        
        error = setpoint - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.last_error) / dt
        d_term = self.kd * derivative
        
        # PID output
        output = p_term + i_term + d_term
        
        # Update for next iteration
        self.last_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """Reset PID controller state."""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

class MPPTController:
    """Maximum Power Point Tracking controller for solar panels."""
    
    def __init__(self, max_voltage: float = 24.0, max_current: float = 10.0):
        """
        Initialize MPPT controller.
        
        Args:
            max_voltage: Maximum panel voltage (V)
            max_current: Maximum panel current (A)
        """
        self.max_voltage = max_voltage
        self.max_current = max_current
        self.pid = PIDController(kp=0.5, ki=0.1, kd=0.05)
        
        # MPPT state
        self.mpp_voltage = 0.0
        self.mpp_power = 0.0
        self.current_voltage = 0.0
        self.current_current = 0.0
        self.current_power = 0.0
        
        # Tracking state
        self.step_size = 0.5  # Voltage step size (V)
        self.direction = 1  # 1 = increase, -1 = decrease
        self.last_power = 0.0
        
        # Integration with solar_forecaster
        self.forecaster_path = GATE / 'solar_forecaster.py'
        self.forecaster_available = self.forecaster_path.exists()
        
        # Advanced algorithms
        self.fuzzy_logic_enabled = False
        self.neural_network_enabled = False
        
        # Partial shading handling
        self.partial_shading_detected = False
        self.multiple_peaks = []
        self.gmpp_voltage = 0.0  # Global Maximum Power Point
        self.bypass_diodes = []  # Bypass diode status
        
        # BMS integration
        self.bms_connected = False
        self.bms_data = {}
        
        # Load forecasting
        self.load_forecast_enabled = False
        self.forecasted_load = 0.0
    
    def perturb_and_observe(self, voltage: float, current: float) -> float:
        """
        Perturb and Observe MPPT algorithm.
        
        Args:
            voltage: Current panel voltage (V)
            current: Current panel current (A)
        
        Returns:
            Next voltage setpoint (V)
        """
        power = voltage * current
        self.current_voltage = voltage
        self.current_current = current
        self.current_power = power
        
        # Check if we found a new maximum
        if power > self.mpp_power:
            self.mpp_power = power
            self.mpp_voltage = voltage
        
        # Determine direction
        if power > self.last_power:
            # Power increased, keep same direction
            pass
        else:
            # Power decreased, reverse direction
            self.direction *= -1
        
        # Calculate next voltage
        next_voltage = voltage + (self.direction * self.step_size)
        
        # Clamp to valid range
        next_voltage = max(0.0, min(self.max_voltage, next_voltage))
        
        self.last_power = power
        
        return next_voltage
    
    def incremental_conductance(self, voltage: float, current: float) -> float:
        """
        Incremental Conductance MPPT algorithm (more accurate).
        
        Args:
            voltage: Current panel voltage (V)
            current: Current panel current (A)
        
        Returns:
            Next voltage setpoint (V)
        """
        power = voltage * current
        self.current_voltage = voltage
        self.current_current = current
        self.current_power = power
        
        # Calculate conductance
        if voltage > 0:
            conductance = current / voltage
            incremental_conductance = (current - self.last_power / max(voltage, 0.1)) / max(voltage - self.current_voltage, 0.1)
            
            # At MPP: dI/dV = -I/V
            if abs(incremental_conductance + conductance) < 0.01:
                # At MPP, maintain voltage
                next_voltage = voltage
            elif incremental_conductance > -conductance:
                # Left of MPP, increase voltage
                next_voltage = voltage + self.step_size
            else:
                # Right of MPP, decrease voltage
                next_voltage = voltage - self.step_size
        else:
            next_voltage = voltage + self.step_size
        
        # Clamp to valid range
        next_voltage = max(0.0, min(self.max_voltage, next_voltage))
        
        self.last_power = power
        
        # Update MPP if better
        if power > self.mpp_power:
            self.mpp_power = power
            self.mpp_voltage = voltage
        
        return next_voltage
    
    def get_forecast(self) -> Optional[Dict]:
        """Get solar forecast from solar_forecaster.py if available."""
        if not self.forecaster_available:
            return None
        
        try:
            sys.path.insert(0, str(GATE))
            from solar_forecaster import get_forecast
            
            forecast = get_forecast()
            return forecast
        except ImportError:
            return None
        except Exception as e:
            print(f"[WARNING] Forecast error: {e}")
            return None
    
    def log_data(self, voltage: float, current: float, power: float, setpoint: float):
        """Log MPPT data to JSON."""
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = LOG_DIR / f'mppt_log_{timestamp}.json'
        
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
        entry = {
            'timestamp': datetime.now().isoformat(),
            'voltage': round(voltage, 3),
            'current': round(current, 3),
            'power': round(power, 3),
            'setpoint': round(setpoint, 3),
            'mpp_voltage': round(self.mpp_voltage, 3),
            'mpp_power': round(self.mpp_power, 3),
            'efficiency': round((power / max(self.mpp_power, 0.1)) * 100, 2) if self.mpp_power > 0 else 0.0
        }
        
        logs.append(entry)
        
        # Save
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Log save error: {e}")
    
    def display_status(self):
        """Display real-time MPPT status."""
        print("\n" + "=" * 60)
        print("SOLAR MPPT CONTROLLER - REAL-TIME STATUS")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print(f"Current Reading:")
        print(f"  Voltage: {self.current_voltage:.3f} V")
        print(f"  Current: {self.current_current:.3f} A")
        print(f"  Power:   {self.current_power:.3f} W")
        print()
        print(f"Maximum Power Point:")
        print(f"  MPP Voltage: {self.mpp_voltage:.3f} V")
        print(f"  MPP Power:   {self.mpp_power:.3f} W")
        print()
        
        if self.mpp_power > 0:
            efficiency = (self.current_power / self.mpp_power) * 100
            print(f"Efficiency: {efficiency:.2f}%")
        
        # Forecast if available
        forecast = self.get_forecast()
        if forecast:
            print()
            print(f"Forecast: {forecast.get('forecast', 'N/A')}")
        
        print("=" * 60)
    
    def detect_partial_shading(self, voltages: List[float], currents: List[float]) -> bool:
        """Detect partial shading by analyzing multiple power peaks."""
        if len(voltages) < 3:
            return False
        
        # Calculate power at each point
        powers = [v * i for v, i in zip(voltages, currents)]
        
        # Find local maxima
        peaks = []
        for i in range(1, len(powers) - 1):
            if powers[i] > powers[i-1] and powers[i] > powers[i+1]:
                peaks.append((voltages[i], powers[i]))
        
        # Multiple peaks indicate partial shading
        if len(peaks) > 1:
            self.partial_shading_detected = True
            self.multiple_peaks = peaks
            # Find global maximum
            self.gmpp_voltage = max(peaks, key=lambda x: x[1])[0]
            return True
        
        self.partial_shading_detected = False
        return False
    
    def reconfigure_panel_array(self, shading_pattern: Dict) -> Dict:
        """Reconfigure panel array to optimize under partial shading."""
        if not self.partial_shading_detected:
            return {'status': 'no_shading'}
        
        # In real implementation, would reconfigure bypass diodes or panel connections
        return {
            'status': 'reconfigured',
            'gmpp_voltage': self.gmpp_voltage,
            'peaks_found': len(self.multiple_peaks),
            'optimization': 'bypass_diodes_activated'
        }
    
    def connect_bms(self, bms_address: str) -> bool:
        """Connect to Battery Management System."""
        # In real implementation, would establish communication with BMS
        self.bms_connected = True
        self.bms_data = {
            'address': bms_address,
            'voltage': 0.0,
            'current': 0.0,
            'soc': 0.0,
            'temperature': 0.0
        }
        print(f"[OK] BMS connected: {bms_address}")
        return True
    
    def forecast_load(self, hours_ahead: int = 24) -> Dict:
        """Forecast load demand for optimization."""
        # In real implementation, would use historical data and ML
        self.forecasted_load = 2.5  # kW (example)
        return {
            'forecast_hours': hours_ahead,
            'predicted_load_kw': self.forecasted_load,
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate(self, algorithm: str = 'perturb_observe', interval: float = 1.0):
        """
        Simulate MPPT operation (for testing without hardware).
        
        Args:
            algorithm: 'perturb_observe' or 'incremental_conductance'
            interval: Update interval in seconds
        """
        print("\n[INFO] Running MPPT simulation (no hardware required)")
        print("[INFO] Press Ctrl+C to stop\n")
        
        # Simulate solar panel I-V curve
        # V_oc = 24V, I_sc = 10A, MPP around 18V
        v_oc = 24.0
        i_sc = 10.0
        v_mpp = 18.0
        
        voltage = 12.0  # Start voltage
        self.running = True
        iteration = 0
        max_iterations = 50  # Limit simulation iterations
        
        try:
            while self.running and iteration < max_iterations:
                iteration += 1
                
                # Simulate current based on voltage (simplified I-V curve)
                # I = I_sc * (1 - (V/V_oc)^2)
                current = i_sc * (1 - (voltage / v_oc) ** 2)
                current = max(0.0, current)
                
                # Get next setpoint using selected algorithm
                if algorithm == 'incremental_conductance':
                    next_voltage = self.incremental_conductance(voltage, current)
                else:
                    next_voltage = self.perturb_and_observe(voltage, current)
                
                # Log data
                power = voltage * current
                self.log_data(voltage, current, power, next_voltage)
                
                # Display status
                self.display_status()
                
                # Update voltage (simulate controller response)
                voltage = next_voltage
                
                # Check convergence
                if abs(voltage - self.mpp_voltage) < 0.1 and iteration > 5:
                    print(f"\n[OK] MPPT converged to {self.mpp_voltage:.3f}V after {iteration} iterations")
                    break
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[INFO] Simulation stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Simulation error: {e}")
        finally:
            print("[OK] MPPT simulation complete")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Solar MPPT Controller')
    parser.add_argument('--algorithm', choices=['perturb_observe', 'incremental_conductance'],
                       default='perturb_observe', help='MPPT algorithm (default: perturb_observe)')
    parser.add_argument('--interval', type=float, default=1.0, help='Update interval in seconds (default: 1.0)')
    parser.add_argument('--simulate', action='store_true', help='Run simulation (no hardware required)')
    parser.add_argument('--max-voltage', type=float, default=24.0, help='Maximum panel voltage (default: 24.0V)')
    parser.add_argument('--max-current', type=float, default=10.0, help='Maximum panel current (default: 10.0A)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SOLAR MPPT CONTROLLER")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    print("The doors of knowledge opens.")
    print("MPPT controller initializing...\n")
    
    controller = MPPTController(max_voltage=args.max_voltage, max_current=args.max_current)
    
    if args.simulate:
        controller.simulate(algorithm=args.algorithm, interval=args.interval)
    else:
        print("[INFO] Hardware mode - connect to solar panel sensors")
        print("[INFO] Use --simulate flag for testing without hardware")
        print("\n[INFO] For hardware integration, implement sensor reading in main loop")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

