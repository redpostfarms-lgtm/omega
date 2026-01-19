#!/usr/bin/env python3
"""Test GPU detection"""
from omega_control_panel import ControlPanel

print("Testing Control Panel GPU methods...")
cp = ControlPanel(use_gradual_loading=False)
print(f"Control panel loaded successfully")
print(f"Has _get_gpu_temperature: {hasattr(cp, '_get_gpu_temperature')}")
print(f"Has _get_gpu_usage: {hasattr(cp, '_get_gpu_usage')}")

if hasattr(cp, '_get_gpu_temperature'):
    temp = cp._get_gpu_temperature()
    print(f"GPU Temperature: {temp}")

if hasattr(cp, '_get_gpu_usage'):
    usage = cp._get_gpu_usage()
    print(f"GPU Usage: {usage}")

print(f"\nIntegrated Systems ({len(cp.integrated_systems)}):")
for system in cp.integrated_systems:
    print(f"  - {system.name}: {system.status} (Temp: {system.temperature}°C)")
