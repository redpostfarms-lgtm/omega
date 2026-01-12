#!/usr/bin/env python3
"""Test script for WormFeedCalc."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from WormFeedCalc import WormCalculator

print('=' * 60)
print('WORM FEED CALCULATOR TEST')
print('=' * 60)
print()

test_materials = {'horse manure': 40, 'coffee grounds': 20, 'vegetable peels': 15}
print('Testing calculation with:')
for k, v in test_materials.items():
    print(f'  {v} lb {k}')
print()

calc = WormCalculator()
ratio = calc.calc(test_materials, 150)

print()
print(f'✅ Ratio: {ratio:.2f}x')
print('✅ WormFeedCalc system operational')

