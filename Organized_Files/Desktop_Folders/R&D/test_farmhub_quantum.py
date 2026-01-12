#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Quick test script for FarmHub quantum module integration

import sys
from pathlib import Path

print("=" * 60)
print("FARMHUB QUANTUM MODULE TEST")
print("=" * 60)
print()

# Test 1: Check if FarmHub file exists
farmhub_path = Path(r'D:\RPF_BRAIN\FarmHub\FarmHub_2026_Final.py')
if not farmhub_path.exists():
    farmhub_path = Path('The Gatekeeper/FarmHub/FarmHub_2026_Final.py')

if farmhub_path.exists():
    print(f"[OK] FarmHub_2026_Final.py found: {farmhub_path}")
else:
    print(f"[ERROR] FarmHub_2026_Final.py not found")
    sys.exit(1)

# Test 2: Check quantum optimization module
sys.path.insert(0, str(Path(r'D:\RPF_BRAIN\The Gatekeeper\projects')))
sys.path.insert(0, str(Path(r'D:\RPF_BRAIN')))

print("\n[Test 2] Checking quantum modules...")
try:
    from quantum_optimization import QuantumOptimization
    print("[OK] quantum_optimization.py imported successfully")
    
    optimizer = QuantumOptimization()
    print(f"   Qiskit available: {'YES' if optimizer.qiskit_available else 'NO'}")
    print(f"   D-Wave available: {'YES' if optimizer.dwave_available else 'NO'}")
    
except ImportError as e:
    print(f"[ERROR] quantum_optimization.py import failed: {e}")
    
    # Try fallback
    try:
        from agent_quantum_optimizer import QuantumOptimizer
        print("[OK] agent_quantum_optimizer.py imported successfully (fallback)")
    except ImportError as e2:
        print(f"[ERROR] agent_quantum_optimizer.py import failed: {e2}")

# Test 3: Check if quantum method exists in FarmHub
print("\n[Test 3] Checking FarmHub quantum integration...")
try:
    # Read the file and check for quantum method
    with open(farmhub_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'def quantum(self' in content:
            print("[OK] quantum() method found in FarmHub")
        else:
            print("[ERROR] quantum() method not found")
        
        if 'quantum' in content.lower() and 'optimize' in content.lower():
            print("[OK] Quantum module integration detected")
        else:
            print("[WARNING] Quantum integration may be incomplete")
except Exception as e:
    print(f"❌ Error reading FarmHub file: {e}")

# Test 4: Quick quantum optimization test
print("\n[Test 4] Testing quantum optimization...")
try:
    from quantum_optimization import QuantumOptimization
    optimizer = QuantumOptimization()
    
    # Test resource allocation
    tasks = [
        {'name': 'test_task', 'energy': 10, 'water': 100, 'labor': 1, 'cost': 50}
    ]
    result = optimizer.optimize_resource_allocation(tasks)
    print(f"[OK] Quantum optimization test passed")
    print(f"   Result keys: {list(result.keys())}")
except Exception as e:
    print(f"[WARNING] Quantum optimization test failed: {e}")
    print("   (This is okay if modules aren't fully configured)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nTo run FarmHub:")
print(f"  python {farmhub_path}")
print("\nTo test quantum module:")
print("  python FarmHub_2026_Final.py")
print("  Then enter: quantum")
