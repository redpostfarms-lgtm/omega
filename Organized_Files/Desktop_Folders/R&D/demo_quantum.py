#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Quantum Module Demo - Direct test of FarmHub quantum integration

import sys
import json
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(r'D:\RPF_BRAIN\The Gatekeeper\projects')))
sys.path.insert(0, str(Path(r'D:\RPF_BRAIN')))

print("=" * 60)
print("FARMHUB 2026 - QUANTUM MODULE DEMO")
print("=" * 60)
print()

# Test 1: Quantum Optimizer (Fallback)
print("[1/3] Testing Quantum Optimizer (Performance Optimization)...")
try:
    from agent_quantum_optimizer import QuantumOptimizer
    
    optimizer = QuantumOptimizer(dimensions=10, num_particles=30)
    
    def fitness(x):
        # Minimize sum of squares (simple optimization problem)
        return sum(xi**2 for xi in x)
    
    result = optimizer.optimize(fitness, max_iterations=50)
    print(f"   Best fitness: {optimizer.global_best_fitness:.6f}")
    print(f"   Solution found: {[round(x, 4) for x in result[:5]]}...")
    print("   [OK] Quantum optimizer working!")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

# Test 2: Quantum Optimization (Farm Resource Allocation)
print("[2/3] Testing Quantum Optimization (Farm Resource Allocation)...")
try:
    from quantum_optimization import QuantumOptimization
    
    opt = QuantumOptimization()
    
    # Example: Resource allocation
    tasks = [
        {'name': 'irrigation', 'energy': 20, 'water': 500, 'labor': 2, 'cost': 100},
        {'name': 'feeding', 'energy': 10, 'water': 200, 'labor': 1, 'cost': 50},
        {'name': 'harvesting', 'energy': 30, 'water': 100, 'labor': 3, 'cost': 200}
    ]
    
    result = opt.optimize_resource_allocation(tasks)
    print(f"   Total cost: ${result.get('total_cost', 'N/A')}")
    print(f"   Constraints met: {result.get('constraints_met', 'N/A')}")
    print(f"   Algorithm: {result.get('optimization_result', {}).get('algorithm', 'N/A')}")
    print("   [OK] Resource allocation optimization working!")
    
except ImportError:
    print("   [INFO] quantum_optimization.py not in path (using fallback)")
except Exception as e:
    print(f"   [WARNING] {e}")

print()

# Test 3: Energy Efficiency
print("[3/3] Testing Energy Efficiency Analysis...")
try:
    from quantum_optimization import QuantumOptimization
    
    opt = QuantumOptimization()
    
    systems = [
        {'name': 'Solar', 'energy_kwh': 50, 'capacity': 100},
        {'name': 'Battery', 'energy_kwh': 30, 'capacity': 80},
        {'name': 'Irrigation', 'energy_kwh': 20, 'capacity': 40}
    ]
    
    result = opt.optimize_energy_efficiency(systems)
    print(f"   Overall efficiency: {result.get('overall_efficiency', 'N/A')}")
    print(f"   Total energy: {result.get('total_energy_kwh', 'N/A')} kWh")
    print(f"   Recommendations: {len(result.get('recommendations', []))} systems need optimization")
    print("   [OK] Energy efficiency analysis working!")
    
except ImportError:
    print("   [INFO] Using quantum optimizer fallback for energy analysis")
except Exception as e:
    print(f"   [WARNING] {e}")

print()
print("=" * 60)
print("QUANTUM MODULE STATUS")
print("=" * 60)
print()
print("Available Commands in FarmHub:")
print("  quantum              - Show capabilities")
print("  quantum resource     - Optimize resource allocation")
print("  quantum energy       - Analyze energy efficiency")
print("  quantum irrigation   - Optimize irrigation schedule")
print()
print("Quantum Libraries:")
try:
    from quantum_optimization import QuantumOptimization
    opt = QuantumOptimization()
    print(f"  Qiskit: {'Available' if opt.qiskit_available else 'Not installed'}")
    print(f"  D-Wave: {'Available' if opt.dwave_available else 'Not installed'}")
except:
    print("  Using quantum-inspired algorithms (no external libraries needed)")

print()
print("=" * 60)
print("QUANTUM MODULE READY")
print("=" * 60)
