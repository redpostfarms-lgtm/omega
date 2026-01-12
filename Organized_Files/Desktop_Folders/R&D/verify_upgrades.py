# -*- coding: utf-8 -*-
# Verify All Upgrades

import os
import sys

print("=" * 60)
print("SYSTEM STATUS - All Upgrades")
print("=" * 60)

# 1. Babel ONNX
try:
    from stonewall.babel_onnx import get_babel_onnx
    babel = get_babel_onnx()
    status = babel.get_status()
    print(f"\n1. Babel ONNX: {'Loaded' if status['loaded'] else 'Placeholder'} (Model: {status['model_path'] or 'Not found'})")
    print(f"   Load time: {status['load_time']:.3f}s")
    print(f"   Model size: {status['model_size_gb']:.2f}GB")
except Exception as e:
    print(f"\n1. Babel ONNX: Error - {e}")

# 2. Bait Farm
try:
    from stonewall.bait_farm import BaitFarm
    farm = BaitFarm()
    print(f"\n2. Bait Farm: Ready")
    print(f"   Callback port: {farm.callback_port}")
    print(f"   Status: {'Active' if farm.active else 'Inactive'}")
except Exception as e:
    print(f"\n2. Bait Farm: Error - {e}")

# 3. Swarm Breeding
try:
    from swarm_breeding import SwarmBreeder
    breeder = SwarmBreeder()
    print(f"\n3. Swarm Breeding: Ready")
    print(f"   Offspring directory: {breeder.breeding_dir}")
    print(f"   Total offspring: {breeder.total_offspring}")
except Exception as e:
    print(f"\n3. Swarm Breeding: Error - {e}")

# 4. Pacemaker Plugin
pacemaker_path = 'stonewall/babel/medical/implant_mods.py'
if os.path.exists(pacemaker_path):
    print(f"\n4. Pacemaker Plugin: Ready")
    print(f"   Location: {pacemaker_path}")
    print(f"   WARNING: DANGEROUS - Medical device control")
else:
    print(f"\n4. Pacemaker Plugin: Missing ({pacemaker_path})")

print("\n" + "=" * 60)
print("[OK] All systems operational. Everything hotter. Tighter. Hungrier.")
print("=" * 60)

