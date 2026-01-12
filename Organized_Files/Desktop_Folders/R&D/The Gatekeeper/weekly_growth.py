# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER – WEEKLY 5-MIN GROWTH LOOP
# 10:24 PM every Wednesday. 2025-12-31.
# No clutter. One circle. Five pipelines.
# Say yes to grow the pie.

import time
import sys
import io
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN\The Gatekeeper')
SUM = BRAIN / 'weekly_delta.txt'

PIPELINES = {
    'science': 'Physics + quantum + battery chem',
    'math': 'Calc, stats, error bars',
    'english': 'USDA docs, pitch decks, clean English',
    'programming': 'Python, git, automation scripts',
    'ops': 'Office, Adobe, drone, solar forecasts'
}

# File patterns to count for each pipeline
PIPELINE_PATTERNS = {
    'science': ['*physics*', '*quantum*', '*battery*', '*18650*', '*solar*'],
    'math': ['*calc*', '*stat*', '*derivative*', '*equation*'],
    'english': ['*grant*', '*usda*', '*pitch*', '*doc*', '*template*'],
    'programming': ['*.py', '*script*', '*automation*', '*git*'],
    'ops': ['*office*', '*adobe*', '*drone*', '*forecast*', '*briefing*']
}

def count_pipeline_items(pipe):
    """Count items in a pipeline based on file patterns."""
    count = 0
    patterns = PIPELINE_PATTERNS.get(pipe, [])
    
    for pattern in patterns:
        # Search in Gatekeeper directory and Archived
        for path in [BRAIN, BRAIN.parent / 'Archived']:
            if path.exists():
                count += len(list(path.rglob(pattern)))
    
    return count

def scan_delta():
    """Scan changes in all pipelines."""
    changes = {}
    
    for pipe, name in PIPELINES.items():
        # Last week's size vs today
        old = BRAIN / f'{pipe}_size.txt'
        new_size = count_pipeline_items(pipe)
        
        try:
            last = int(old.read_text().strip())
        except:
            last = 0
        
        changes[pipe] = f'{last} → {new_size} items'
        old.write_text(str(new_size))
    
    return changes

def print_circle():
    """Print the weekly growth circle."""
    print('\n🧠 GATEKEEPER – 5-MIN GROWTH')
    print('Weekly circle: 10:24 PM MST')
    print('=' * 50)
    
    deltas = scan_delta()
    
    for pipe, name in PIPELINES.items():
        delta = deltas.get(pipe, '0 → 0 items')
        print(f'  {pipe:<12} {delta}')
    
    print('\n' + '=' * 50)
    print('Grow? (yes/no) ', end='')

if __name__ == '__main__':
    # First run – baseline
    if not (BRAIN / 'initialized').exists():
        print("=" * 60)
        print("Gatekeeper Weekly Growth - Initial Setup")
        print("=" * 60)
        print("\nCreating baseline for all pipelines...")
        
        for p in PIPELINES:
            size_file = BRAIN / f'{p}_size.txt'
            current_size = count_pipeline_items(p)
            size_file.write_text(str(current_size))
            print(f"  {p}: {current_size} items")
        
        (BRAIN / 'initialized').touch()
        print('\n✅ Initial scan done. First circle next Wednesday at 10:24 PM.')
        print("Run with --weekly flag to start the loop.")
        sys.exit(0)
    
    # Weekly run – 22:24 every Wednesday
    if '--weekly' in sys.argv:
        print("=" * 60)
        print("Gatekeeper Weekly Growth Loop")
        print("=" * 60)
        print("Waiting for Wednesday 10:24 PM...")
        print("(Press Ctrl+C to exit)\n")
        
        while True:
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            current_day = now.strftime('%a')
            
            if current_time == '22:24' and current_day == 'Wed':
                print_circle()
                ans = input().strip().lower()
                
                if ans == 'yes':
                    print('\n✅ Pie grows. Pipelines updated.')
                    # Could trigger learning or updates here
                else:
                    print('\n⏸️  No change. Stays steady.')
                
                # Wait until next minute to avoid multiple triggers
                time.sleep(60)
            else:
                # Check every 10 seconds
                time.sleep(10)
    else:
        # Manual run - show current status
        print("=" * 60)
        print("Gatekeeper Weekly Growth - Manual Check")
        print("=" * 60)
        print_circle()
        ans = input().strip().lower()
        
        if ans == 'yes':
            print('\n✅ Pie grows. Pipelines updated.')
        else:
            print('\n⏸️  No change. Stays steady.')

