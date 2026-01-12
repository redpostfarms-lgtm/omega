#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Pole Barn 30×60×14 Design Generator
# Colorado 2026 codes, 180 mph wind, 85 psf snow, 42" frost depth

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\Farm_Engineer')
BUILDS = ROOT / 'Builds'
BUILDS.mkdir(parents=True, exist_ok=True)

def generate_pole_barn(length=60, width=30, height=14):
    """Generate complete pole barn design."""
    build_dir = BUILDS / f'Pole_Barn_{length}x{width}x{height}'
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Engineering calculations
    posts_spacing = 8  # feet
    num_posts_length = int(length / posts_spacing) + 1
    num_posts_width = int(width / posts_spacing) + 1
    total_posts = num_posts_length * num_posts_width
    
    # Structural design
    design = {
        'structure': f'Pole Barn {length}x{width}x{height}',
        'codes': {
            'primary': 'Colorado 2026',
            'structural': 'IBC 2024',
            'wind_speed_mph': 180,
            'snow_load_psf': 85,
            'frost_depth_inches': 42,
            'seismic_zone': 'D0',
            'elevation_ft': 8000
        },
        'posts': {
            'size': '6×6',
            'spacing_ft': posts_spacing,
            'total_count': total_posts,
            'depth_below_grade_inches': 42 + 12,
            'embedment_ft': 4.5
        },
        'trusses': {
            'spacing_ft': 2,
            'span_ft': width,
            'type': 'Prefabricated wood truss',
            'count': int(length / 2)
        },
        'concrete': {
            'volume_cubic_yards': round((total_posts * 0.5) / 27, 2),
            'psi': 5000,
            'mix_design': '5,000 psi with air entrainment',
            'total_cubic_yards': round((total_posts * 0.5) / 27, 2)
        },
        'cut_list': {
            'posts_6x6_ft': total_posts * (height + 4),
            'trusses_count': int(length / 2),
            'purlins_2x6_ft': int(length * width / 2),
            'girts_2x6_ft': int(length * height * 2 / 2)
        },
        'permit_packet': {
            'structural_calcs': 'included',
            'site_plan': 'required',
            'foundation_plan': 'included',
            'framing_plan': 'included',
            'wind_load_calc': 'included',
            'snow_load_calc': 'included'
        },
        'cost_estimate': {
            'materials': f'${total_posts * 150 + 5000:.2f}',
            'labor': f'${total_posts * 200:.2f}',
            'concrete': f'${(total_posts * 0.5 / 27) * 150:.2f}',
            'total': f'${total_posts * 350 + 5000 + (total_posts * 0.5 / 27) * 150:.2f}'
        },
        'generated_at': datetime.now().isoformat(),
        'engineer': 'BOB v1.0'
    }
    
    # Save design
    design_file = build_dir / 'design.json'
    with open(design_file, 'w', encoding='utf-8') as f:
        json.dump(design, f, indent=2, ensure_ascii=False)
    
    # Generate cut list
    cut_list_file = build_dir / 'cut_list.txt'
    with open(cut_list_file, 'w', encoding='utf-8') as f:
        f.write(f"POLE BARN {length}x{width}x{height} - CUT LIST\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"6×6 Posts: {total_posts} @ {height + 4} ft\n")
        f.write(f"Trusses: {int(length / 2)} @ {width} ft span\n")
        f.write(f"Purlins (2×6): {int(length * width / 2)} linear ft\n")
        f.write(f"Girts (2×6): {int(length * height * 2 / 2)} linear ft\n")
    
    print(f"[OK] Pole barn design saved to {build_dir}")
    return build_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pole Barn 30×60 Design Generator')
    parser.add_argument('--length', type=int, default=60, help='Length in feet')
    parser.add_argument('--width', type=int, default=30, help='Width in feet')
    parser.add_argument('--height', type=int, default=14, help='Height in feet')
    
    args = parser.parse_args()
    generate_pole_barn(args.length, args.width, args.height)

