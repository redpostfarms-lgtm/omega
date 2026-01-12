#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Irrigation 40-Acre Design Generator
# Center-pivot + drip hybrid, NDVI-controlled

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\Farm_Engineer')
BUILDS = ROOT / 'Builds'
BUILDS.mkdir(parents=True, exist_ok=True)

def generate_irrigation_design(acres=40):
    """Generate irrigation system design."""
    build_dir = BUILDS / f'Irrigation_{acres}ac'
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Irrigation calculations
    flow_gpm = 1200
    center_pivot_acres = acres * 0.7  # 70% center pivot
    drip_acres = acres * 0.3  # 30% drip
    
    design = {
        'irrigation_system': f'{acres}-acre Center-Pivot + Drip Hybrid',
        'total_acres': acres,
        'flow_gpm': flow_gpm,
        'center_pivot': {
            'acres': center_pivot_acres,
            'type': 'Center-pivot with variable rate',
            'control': 'NDVI-based zone control',
            'coverage': '70% of total area'
        },
        'drip': {
            'acres': drip_acres,
            'type': 'Pressure-compensated drip tape',
            'spacing_inches': 12,
            'coverage': '30% of total area'
        },
        'pump_system': {
            'flow_gpm': flow_gpm,
            'pressure_psi': 60,
            'power_hp': int(flow_gpm * 60 / 1714),  # Simplified calculation
            'type': 'Centrifugal or submersible'
        },
        'control_system': {
            'ndvi_control': True,
            'variable_rate': True,
            'automation': 'Fully automated with weather integration'
        },
        'cost_estimate': {
            'center_pivot': f'${center_pivot_acres * 800:.2f}',
            'drip_system': f'${drip_acres * 1200:.2f}',
            'pump_system': f'${flow_gpm * 10:.2f}',
            'control_system': f'${acres * 50:.2f}',
            'total': f'${center_pivot_acres * 800 + drip_acres * 1200 + flow_gpm * 10 + acres * 50:.2f}'
        },
        'codes': {
            'irrigation': 'ASABE Standards',
            'water_rights': 'Colorado State Engineer',
            'electrical': 'NEC 2026'
        },
        'generated_at': datetime.now().isoformat(),
        'engineer': 'BOB v1.0'
    }
    
    # Save design
    design_file = build_dir / 'design.json'
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(design, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Irrigation design saved to {build_dir}")
    return build_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Irrigation 40-Acre Design Generator')
    parser.add_argument('--acres', type=int, default=40, help='Total acres')
    
    args = parser.parse_args()
    generate_irrigation_design(args.acres)

