#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BASELINE GENERATOR
# Generate diagnostic_baseline.json with file hashes

import os
import json
import hashlib
from pathlib import Path


def hash_file(path: str) -> str:
    """Hash file for integrity check."""
    try:
        if not os.path.exists(path):
            return 'MISSING'
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return f'ERROR:{str(e)}'


def generate_baseline():
    """Generate baseline file hashes."""
    # Files to hash
    files = [
        'main.py',
        'agent_anonymous.py',
        'elara_integrated_system.py',
        'elara_game_engine.py',
        'agent_swarm_isolated.py',
        'elara_visual_checkers.py',
        'strategy_core_converter.py',
        'diagnostic_engine.py',
    ]
    
    # Check if stonewall exists
    if os.path.exists('stonewall'):
        files.append('stonewall/setup.py')
    
    # Generate hashes
    baseline = {}
    for file in files:
        if os.path.exists(file):
            baseline[file] = hash_file(file)
            print(f"[OK] {file}: {baseline[file][:16]}...")
        else:
            baseline[file] = 'MISSING'
            print(f"[MISS] {file}")
    
    # Save baseline
    baseline_path = Path('diagnostic_baseline.json')
    with open(baseline_path, 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"\n[OK] Baseline saved to: {baseline_path}")
    print(f"[OK] {len([f for f in baseline.values() if f != 'MISSING'])} files hashed")


if __name__ == '__main__':
    generate_baseline()

