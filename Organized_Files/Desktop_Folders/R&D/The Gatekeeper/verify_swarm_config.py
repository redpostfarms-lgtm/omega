# -*- coding: utf-8 -*-
# Quick config verification

from omega_v5_swarm_config import load_config

config = load_config()
print("=" * 80)
print("  SWARM CONFIG VERIFICATION")
print("=" * 80)
print()
print(f"Targets: {len(config.get('targets', []))}")
for i, target in enumerate(config.get('targets', []), 1):
    print(f"  {i}. {target}")
print()
print(f"Base Payloads: {len(config.get('base_payloads', []))}")
print()
print("=" * 80)
print("  CONFIG READY")
print("=" * 80)
