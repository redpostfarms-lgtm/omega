#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# 18650 Megapack Design Generator
# Kyber-1024 encrypted BMS, NFPA 855 compliance

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\Farm_Engineer')
BUILDS = ROOT / 'Builds'
BUILDS.mkdir(parents=True, exist_ok=True)

def generate_battery_design(capacity_kwh=2000):
    """Generate 18650 battery bank design."""
    build_dir = BUILDS / f'Battery_Bank_{capacity_kwh}kWh'
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Battery calculations
    voltage_nominal = 48
    cells_per_series = int(voltage_nominal / 3.7)  # 18650 nominal 3.7V
    capacity_per_cell_ah = 2.5  # Typical 18650 capacity
    parallel_strings = int((capacity_kwh * 1000) / (voltage_nominal * capacity_per_cell_ah))
    total_cells = cells_per_series * parallel_strings
    
    design = {
        'battery_bank': f'{capacity_kwh} kWh 18650 Pack',
        'voltage_nominal': voltage_nominal,
        'capacity_kwh': capacity_kwh,
        'cells_total': total_cells,
        'cells_per_series': cells_per_series,
        'parallel_strings': parallel_strings,
        'bms': {
            'type': 'Kyber-1024 encrypted',
            'functions': [
                'Cell balancing',
                'Overcharge protection',
                'Overdischarge protection',
                'Temperature monitoring',
                'Current limiting',
                'State of charge (SOC)',
                'State of health (SOH)'
            ],
            'encryption': 'Kyber-1024 (post-quantum)'
        },
        'cooling': {
            'passive': 'Natural convection',
            'active': 'Fan-assisted with thermal management',
            'thermal_management': 'Liquid cooling loop (optional)'
        },
        'fire_containment': {
            'standard': 'NFPA 855',
            'rating': '2-hour fire rated enclosure',
            'suppression': 'Automatic fire suppression system',
            'ventilation': 'Required per NFPA 855'
        },
        'thermal_model': {
            'max_temp_c': 45,
            'min_temp_c': 0,
            'cooling_required_kw': capacity_kwh * 0.01,  # 1% of capacity
            'heating_required_w': capacity_kwh * 5  # 5W per kWh for cold weather
        },
        'cost_breakdown': {
            'cells_per_wh': 0.11,
            'cells_total': f'${capacity_kwh * 1000 * 0.11:.2f}',
            'bms': f'${capacity_kwh * 0.05:.2f}',
            'enclosure': f'${capacity_kwh * 0.02:.2f}',
            'cooling': f'${capacity_kwh * 0.01:.2f}',
            'fire_suppression': f'${capacity_kwh * 0.01:.2f}',
            'total': f'${capacity_kwh * 0.19:.2f}'
        },
        'codes': {
            'electrical': 'NEC 2026',
            'fire': 'NFPA 855',
            'building': 'IBC 2024'
        },
        'generated_at': datetime.now().isoformat(),
        'engineer': 'BOB v1.0'
    }
    
    # Save design
    design_file = build_dir / 'design.json'
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(design, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Battery design saved to {build_dir}")
    return build_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='18650 Megapack Design Generator')
    parser.add_argument('--capacity', type=int, default=2000, help='Capacity in kWh')
    
    args = parser.parse_args()
    generate_battery_design(args.capacity)

