#!/usr/bin/env python3
# Quick quantum module test
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r'D:\RPF_BRAIN\The Gatekeeper\projects')))
sys.path.insert(0, str(Path(r'D:\RPF_BRAIN')))

print("Testing Quantum Optimizer...")
try:
    from agent_quantum_optimizer import QuantumOptimizer
    
    opt = QuantumOptimizer(dimensions=5, num_particles=10)
    
    def fitness(x):
        return sum(xi**2 for xi in x)
    
    result = opt.optimize(fitness, max_iterations=20)
    print(f"Quantum test complete!")
    print(f"Best fitness: {opt.global_best_fitness:.6f}")
    print(f"Best solution (first 3 dims): {result[:3]}")
    print("[OK] Quantum module working!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
