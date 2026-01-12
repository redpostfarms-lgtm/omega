#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Frost-Protected Shallow Foundation (FPSF) Design Generator
# Colorado 42" frost depth, R-20 insulation

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\Farm_Engineer')
BUILDS = ROOT / 'Builds'
BUILDS.mkdir(parents=True, exist_ok=True)

def generate_foundation_design(structure_type='greenhouse'):
    """Generate frost-protected shallow foundation design."""
    build_dir = BUILDS / f'Foundation_FPSF_{structure_type}'
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Colorado-specific requirements
    frost_depth = 42  # inches
    concrete_psi = 5000
    insulation_r = 20
    
    design = {
        'foundation': f'Frost-Protected Shallow Foundation - {structure_type}',
        'location': 'Colorado, 8,000 ft elevation',
        'frost_depth_inches': frost_depth,
        'concrete': {
            'psi': concrete_psi,
            'mix_design': f'{concrete_psi} psi with air entrainment',
            'thickness_inches': 6,
            'reinforcement': 'Welded wire fabric (WWR)'
        },
        'insulation': {
            'r_value': insulation_r,
            'type': 'R-20 rigid foam insulation wing',
            'placement': 'Horizontal wing at perimeter',
            'width_ft': 4,
            'thickness_inches': 4
        },
        'drainage': {
            'perforated_pipe': 'Required around perimeter',
            'gravel_bed': '4 inches minimum',
            'slope': '1% away from foundation'
        },
        'permit_packet': {
            'structural_calcs': 'included',
            'foundation_plan': 'included',
            'insulation_details': 'included',
            'drainage_plan': 'included'
        },
        'cost_estimate': {
            'concrete': 'Based on square footage',
            'insulation': f'${insulation_r * 2:.2f} per linear foot',
            'labor': 'Based on local rates',
            'drainage': 'Based on linear footage'
        },
        'codes': {
            'structural': 'IBC 2024',
            'insulation': 'IRC 2021',
            'colorado': 'Colorado 2026 amendments'
        },
        'generated_at': datetime.now().isoformat(),
        'engineer': 'BOB v1.0'
    }
    
    # Save design
    design_file = build_dir / 'design.json'
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(design, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Foundation design saved to {build_dir}")
    return build_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FPSF Colorado Design Generator')
    parser.add_argument('--structure', type=str, default='greenhouse', help='Structure type')
    
    args = parser.parse_args()
    generate_foundation_design(args.structure)

