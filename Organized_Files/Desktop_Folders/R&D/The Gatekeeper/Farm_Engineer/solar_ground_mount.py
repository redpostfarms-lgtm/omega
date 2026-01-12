#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Solar Ground Mount Design Generator
# 38° tilt, 120 mph wind, 150 psf snow

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\Farm_Engineer')
BUILDS = ROOT / 'Builds'
BUILDS.mkdir(parents=True, exist_ok=True)

def generate_solar_design(capacity_kw=500):
    """Generate solar ground mount design."""
    build_dir = BUILDS / f'Solar_Ground_Mount_{capacity_kw}kW'
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Solar calculations
    panel_wattage = 1500  # 1.5 kW panels
    num_panels = int(capacity_kw * 1000 / panel_wattage)
    tilt_angle = 38  # degrees south
    wind_load = 120  # mph
    snow_load = 150  # psf
    
    design = {
        'solar_array': f'{capacity_kw} kW Ground Mount',
        'panels': {
            'count': num_panels,
            'wattage_per_panel': panel_wattage,
            'tilt_angle_degrees': tilt_angle,
            'orientation': 'South',
            'azimuth': 180
        },
        'structural': {
            'wind_load_mph': wind_load,
            'snow_load_psf': snow_load,
            'foundation_type': 'Ground screw or concrete pier',
            'racking_system': 'Fixed-tilt aluminum racking',
            'mounting': 'Fixed-tilt, non-tracking'
        },
        'electrical': {
            'voltage': '600V DC',
            'inverter_type': 'String inverter or microinverters',
            'conduit': 'Schedule 40 PVC or EMT',
            'disconnect': 'Required per NEC 2026',
            'grounding': 'Per NEC 690.47'
        },
        'cost_estimate': {
            'panels': f'${num_panels * 300:.2f}',
            'racking': f'${num_panels * 50:.2f}',
            'inverter': f'${capacity_kw * 200:.2f}',
            'installation': f'${capacity_kw * 500:.2f}',
            'total': f'${num_panels * 350 + capacity_kw * 700:.2f}'
        },
        'codes': {
            'electrical': 'NEC 2026',
            'structural': 'IBC 2024',
            'wind': 'ASCE 7-22'
        },
        'generated_at': datetime.now().isoformat(),
        'engineer': 'BOB v1.0'
    }
    
    # Save design
    design_file = build_dir / 'design.json'
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(design, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Solar design saved to {build_dir}")
    return build_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solar Ground Mount Design Generator')
    parser.add_argument('--capacity', type=int, default=500, help='Capacity in kW')
    
    args = parser.parse_args()
    generate_solar_design(args.capacity)

