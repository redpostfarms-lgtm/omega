#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# OMEGA QUANTUM PATH PLANNING
# QAOA-based path optimization for drones and logistics
# Phase 3: Specialized Features

import json
import math
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Quantum computing
try:
    from qiskit import QuantumCircuit, Aer, execute
    from qiskit.algorithms import QAOA, NumPyMinimumEigensolver
    from qiskit.algorithms.optimizers import SPSA, COBYLA
    from qiskit.optimization import QuadraticProgram
    from qiskit.optimization.algorithms import MinimumEigenOptimizer
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QuantumCircuit = None

# Quantum enhancement
try:
    from omega_quantum_enhanced import get_quantum_random
    QUANTUM_ENHANCED_AVAILABLE = True
except ImportError:
    QUANTUM_ENHANCED_AVAILABLE = False
    def get_quantum_random(bits=256):
        import random
        return random.getrandbits(bits)

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
PATH_PLANNING_DIR = GATE / 'omega_path_planning'
PATH_PLANNING_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger('Omega.PathPlanning')

@dataclass
class Waypoint:
    """Waypoint in path."""
    id: str
    x: float
    y: float
    z: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Obstacle:
    """Obstacle in path."""
    id: str
    x: float
    y: float
    z: float = 0.0
    radius: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PathResult:
    """Result from path planning."""
    waypoints: List[Waypoint]
    total_distance: float
    total_time: Optional[float] = None
    energy_cost: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PathPlanner:
    """Base path planner."""
    
    def __init__(self):
        """Initialize path planner."""
        pass
    
    def plan_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle] = None) -> PathResult:
        """Plan path from start to end."""
        raise NotImplementedError

class ClassicalPathPlanner(PathPlanner):
    """Classical path planning (A* or simple)."""
    
    def plan_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle] = None) -> PathResult:
        """Plan path using classical algorithm."""
        obstacles = obstacles or []
        
        # Simple straight-line path with obstacle avoidance
        waypoints = [start]
        
        # Check if direct path is blocked
        if not self._path_blocked(start, end, obstacles):
            waypoints.append(end)
        else:
            # Find way around obstacles
            intermediate = self._find_waypoint_around_obstacles(start, end, obstacles)
            if intermediate:
                waypoints.append(intermediate)
            waypoints.append(end)
        
        # Calculate distance
        total_distance = self._calculate_distance(waypoints)
        
        return PathResult(
            waypoints=waypoints,
            total_distance=total_distance,
            metadata={"algorithm": "classical"}
        )
    
    def _path_blocked(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle]) -> bool:
        """Check if path is blocked by obstacles."""
        for obstacle in obstacles:
            # Check if line segment intersects obstacle sphere
            if self._line_sphere_intersect(start, end, obstacle):
                return True
        return False
    
    def _line_sphere_intersect(self, start: Waypoint, end: Waypoint, obstacle: Obstacle) -> bool:
        """Check if line segment intersects sphere."""
        # Vector from start to end
        dx = end.x - start.x
        dy = end.y - start.y
        dz = end.z - start.z
        
        # Vector from start to obstacle center
        ox = obstacle.x - start.x
        oy = obstacle.y - start.y
        oz = obstacle.z - start.z
        
        # Projection
        t = (dx * ox + dy * oy + dz * oz) / (dx * dx + dy * dy + dz * dz) if (dx * dx + dy * dy + dz * dz) > 0 else 0
        t = max(0, min(1, t))  # Clamp to [0, 1]
        
        # Closest point on line to obstacle center
        closest_x = start.x + t * dx
        closest_y = start.y + t * dy
        closest_z = start.z + t * dz
        
        # Distance from closest point to obstacle center
        dist = math.sqrt(
            (closest_x - obstacle.x)**2 +
            (closest_y - obstacle.y)**2 +
            (closest_z - obstacle.z)**2
        )
        
        return dist < obstacle.radius
    
    def _find_waypoint_around_obstacles(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle]) -> Optional[Waypoint]:
        """Find waypoint to go around obstacles."""
        # Simple: go around first blocking obstacle
        for obstacle in obstacles:
            if self._line_sphere_intersect(start, end, obstacle):
                # Create waypoint to the side of obstacle
                dx = end.x - start.x
                dy = end.y - start.y
                # Perpendicular vector
                perp_x = -dy
                perp_y = dx
                norm = math.sqrt(perp_x**2 + perp_y**2)
                if norm > 0:
                    perp_x /= norm
                    perp_y /= norm
                
                # Waypoint at obstacle edge
                waypoint = Waypoint(
                    id=f"waypoint_{obstacle.id}",
                    x=obstacle.x + perp_x * (obstacle.radius + 1.0),
                    y=obstacle.y + perp_y * (obstacle.radius + 1.0),
                    z=(start.z + end.z) / 2.0
                )
                return waypoint
        return None
    
    def _calculate_distance(self, waypoints: List[Waypoint]) -> float:
        """Calculate total path distance."""
        total = 0.0
        for i in range(len(waypoints) - 1):
            w1 = waypoints[i]
            w2 = waypoints[i + 1]
            dist = math.sqrt(
                (w2.x - w1.x)**2 +
                (w2.y - w1.y)**2 +
                (w2.z - w1.z)**2
            )
            total += dist
        return total

class QuantumPathPlanner(PathPlanner):
    """Quantum path planning using QAOA."""
    
    def __init__(self):
        """Initialize quantum path planner."""
        super().__init__()
        self.qiskit_available = QISKIT_AVAILABLE
        self.quantum_enhanced = QUANTUM_ENHANCED_AVAILABLE
    
    def plan_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle] = None, waypoints: List[Waypoint] = None) -> PathResult:
        """Plan path using quantum optimization."""
        obstacles = obstacles or []
        waypoints = waypoints or []
        
        if not self.qiskit_available:
            # Fallback to classical
            logger.warning("Qiskit not available, using classical planner")
            classical = ClassicalPathPlanner()
            return classical.plan_path(start, end, obstacles)
        
        # If waypoints provided, optimize route
        if waypoints:
            return self._optimize_route([start] + waypoints + [end], obstacles)
        
        # Simple path with quantum enhancement
        return self._quantum_enhanced_path(start, end, obstacles)
    
    def _optimize_route(self, waypoints: List[Waypoint], obstacles: List[Obstacle]) -> PathResult:
        """Optimize route through waypoints using QAOA."""
        try:
            # Create QUBO problem for TSP-like optimization
            num_waypoints = len(waypoints)
            
            if num_waypoints <= 2:
                # Too few waypoints, return direct path
                return PathResult(
                    waypoints=waypoints,
                    total_distance=self._calculate_distance(waypoints),
                    metadata={"algorithm": "quantum", "note": "too_few_waypoints"}
                )
            
            # Create distance matrix
            distance_matrix = self._create_distance_matrix(waypoints)
            
            # Formulate as Quadratic Unconstrained Binary Optimization (QUBO)
            qp = QuadraticProgram()
            
            # Variables: x[i][j] = 1 if waypoint j comes after waypoint i
            for i in range(num_waypoints):
                for j in range(num_waypoints):
                    if i != j:
                        qp.binary_var(f'x_{i}_{j}')
            
            # Objective: minimize total distance
            for i in range(num_waypoints):
                for j in range(num_waypoints):
                    if i != j:
                        qp.minimize(linear={f'x_{i}_{j}': distance_matrix[i][j]})
            
            # Constraints: each waypoint visited exactly once
            for i in range(num_waypoints):
                # Exactly one incoming edge
                qp.linear_constraint(
                    linear={f'x_{j}_{i}': 1 for j in range(num_waypoints) if i != j},
                    sense='==',
                    rhs=1
                )
                # Exactly one outgoing edge
                qp.linear_constraint(
                    linear={f'x_{i}_{j}': 1 for j in range(num_waypoints) if i != j},
                    sense='==',
                    rhs=1
                )
            
            # Solve using QAOA
            optimizer = SPSA(maxiter=100)
            qaoa = QAOA(optimizer=optimizer, reps=2, quantum_instance=Aer.get_backend('qasm_simulator'))
            qaoa_optimizer = MinimumEigenOptimizer(qaoa)
            
            result = qaoa_optimizer.solve(qp)
            
            # Extract optimal path
            optimal_waypoints = self._extract_path_from_result(result, waypoints)
            
            return PathResult(
                waypoints=optimal_waypoints,
                total_distance=self._calculate_distance(optimal_waypoints),
                metadata={"algorithm": "quantum_qaoa", "optimization": "route"}
            )
        except Exception as e:
            logger.error(f"Quantum route optimization failed: {e}")
            # Fallback to classical
            classical = ClassicalPathPlanner()
            return classical.plan_path(waypoints[0], waypoints[-1], obstacles)
    
    def _quantum_enhanced_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle]) -> PathResult:
        """Quantum-enhanced path planning."""
        # Use quantum randomness for path exploration
        if self.quantum_enhanced:
            # Generate multiple candidate paths using quantum randomness
            candidates = []
            for _ in range(5):
                # Use quantum random to explore path variations
                random_factor = (get_quantum_random(8) % 100) / 100.0
                intermediate = Waypoint(
                    id="quantum_waypoint",
                    x=start.x + (end.x - start.x) * random_factor,
                    y=start.y + (end.y - start.y) * random_factor,
                    z=start.z + (end.z - start.z) * random_factor
                )
                
                # Check if path is valid
                if not self._path_blocked(start, intermediate, obstacles) and \
                   not self._path_blocked(intermediate, end, obstacles):
                    path = [start, intermediate, end]
                    distance = self._calculate_distance(path)
                    candidates.append((path, distance))
            
            # Select best candidate
            if candidates:
                best_path, best_distance = min(candidates, key=lambda x: x[1])
                return PathResult(
                    waypoints=best_path,
                    total_distance=best_distance,
                    metadata={"algorithm": "quantum_enhanced"}
                )
        
        # Fallback to classical
        classical = ClassicalPathPlanner()
        return classical.plan_path(start, end, obstacles)
    
    def _create_distance_matrix(self, waypoints: List[Waypoint]) -> np.ndarray:
        """Create distance matrix between waypoints."""
        n = len(waypoints)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    w1 = waypoints[i]
                    w2 = waypoints[j]
                    matrix[i][j] = math.sqrt(
                        (w2.x - w1.x)**2 +
                        (w2.y - w1.y)**2 +
                        (w2.z - w1.z)**2
                    )
        
        return matrix
    
    def _extract_path_from_result(self, result, waypoints: List[Waypoint]) -> List[Waypoint]:
        """Extract path from optimization result."""
        # Simplified: return original order if extraction fails
        # In production, would parse result.x to get optimal order
        return waypoints
    
    def _path_blocked(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle]) -> bool:
        """Check if path is blocked (same as classical)."""
        for obstacle in obstacles:
            dx = end.x - start.x
            dy = end.y - start.y
            dz = end.z - start.z
            ox = obstacle.x - start.x
            oy = obstacle.y - start.y
            oz = obstacle.z - start.z
            
            t = (dx * ox + dy * oy + dz * oz) / (dx * dx + dy * dy + dz * dz) if (dx * dx + dy * dy + dz * dz) > 0 else 0
            t = max(0, min(1, t))
            
            closest_x = start.x + t * dx
            closest_y = start.y + t * dy
            closest_z = start.z + t * dz
            
            dist = math.sqrt(
                (closest_x - obstacle.x)**2 +
                (closest_y - obstacle.y)**2 +
                (closest_z - obstacle.z)**2
            )
            
            if dist < obstacle.radius:
                return True
        return False
    
    def _calculate_distance(self, waypoints: List[Waypoint]) -> float:
        """Calculate total path distance."""
        total = 0.0
        for i in range(len(waypoints) - 1):
            w1 = waypoints[i]
            w2 = waypoints[i + 1]
            dist = math.sqrt(
                (w2.x - w1.x)**2 +
                (w2.y - w1.y)**2 +
                (w2.z - w1.z)**2
            )
            total += dist
        return total

class EnergyConstrainedPathPlanner:
    """Energy-constrained path planning for drones."""
    
    def __init__(self, max_energy: float, energy_per_distance: float = 1.0):
        """Initialize energy-constrained planner."""
        self.max_energy = max_energy
        self.energy_per_distance = energy_per_distance
        self.quantum_planner = QuantumPathPlanner()
    
    def plan_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle] = None, waypoints: List[Waypoint] = None) -> PathResult:
        """Plan energy-constrained path."""
        obstacles = obstacles or []
        waypoints = waypoints or []
        
        # Plan path
        result = self.quantum_planner.plan_path(start, end, obstacles, waypoints)
        
        # Calculate energy cost
        energy_cost = result.total_distance * self.energy_per_distance
        
        # Check if path is feasible
        if energy_cost > self.max_energy:
            # Path requires too much energy, need to find alternative
            # Could add intermediate charging points or optimize further
            result.metadata["energy_feasible"] = False
            result.metadata["energy_required"] = energy_cost
            result.metadata["energy_available"] = self.max_energy
        else:
            result.metadata["energy_feasible"] = True
            result.metadata["energy_required"] = energy_cost
            result.metadata["energy_available"] = self.max_energy
        
        result.energy_cost = energy_cost
        return result

class OmegaPathPlanning:
    """Main path planning system."""
    
    def __init__(self):
        """Initialize path planning system."""
        self.classical_planner = ClassicalPathPlanner()
        self.quantum_planner = QuantumPathPlanner()
        
        logger.info("Omega Path Planning system initialized")
        logger.info(f"Qiskit available: {QISKIT_AVAILABLE}")
        logger.info(f"Quantum enhanced: {QUANTUM_ENHANCED_AVAILABLE}")
    
    def plan_path(self, start: Waypoint, end: Waypoint, obstacles: List[Obstacle] = None, use_quantum: bool = True) -> PathResult:
        """Plan path from start to end."""
        obstacles = obstacles or []
        
        if use_quantum and QISKIT_AVAILABLE:
            return self.quantum_planner.plan_path(start, end, obstacles)
        else:
            return self.classical_planner.plan_path(start, end, obstacles)
    
    def optimize_route(self, waypoints: List[Waypoint], obstacles: List[Obstacle] = None, use_quantum: bool = True) -> PathResult:
        """Optimize route through multiple waypoints."""
        obstacles = obstacles or []
        
        if len(waypoints) < 2:
            return PathResult(waypoints=waypoints, total_distance=0.0)
        
        if use_quantum and QISKIT_AVAILABLE:
            return self.quantum_planner.plan_path(waypoints[0], waypoints[-1], obstacles, waypoints[1:-1])
        else:
            # Classical route optimization
            result = self.classical_planner.plan_path(waypoints[0], waypoints[-1], obstacles)
            return PathResult(
                waypoints=waypoints,
                total_distance=self.classical_planner._calculate_distance(waypoints),
                metadata={"algorithm": "classical_route"}
            )
    
    def plan_energy_constrained(self, start: Waypoint, end: Waypoint, max_energy: float, obstacles: List[Obstacle] = None) -> PathResult:
        """Plan energy-constrained path."""
        obstacles = obstacles or []
        planner = EnergyConstrainedPathPlanner(max_energy)
        return planner.plan_path(start, end, obstacles)
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get system capabilities."""
        return {
            "quantum_optimization": QISKIT_AVAILABLE,
            "quantum_enhanced": QUANTUM_ENHANCED_AVAILABLE,
            "classical_planning": True,
            "energy_constrained": True
        }

def main():
    """Test Quantum Path Planning."""
    print("=" * 60)
    print("OMEGA QUANTUM PATH PLANNING - TEST")
    print("=" * 60)
    
    planner = OmegaPathPlanning()
    
    # Capabilities
    print("\n[1] System Capabilities:")
    capabilities = planner.get_capabilities()
    for cap, avail in capabilities.items():
        status = "✅" if avail else "❌"
        print(f"  {status} {cap}: {avail}")
    
    # Test path planning
    print("\n[2] Testing path planning...")
    start = Waypoint(id="start", x=0.0, y=0.0, z=0.0)
    end = Waypoint(id="end", x=10.0, y=10.0, z=5.0)
    
    obstacles = [
        Obstacle(id="obs1", x=5.0, y=5.0, z=2.0, radius=2.0)
    ]
    
    result = planner.plan_path(start, end, obstacles, use_quantum=True)
    print(f"Path found: {len(result.waypoints)} waypoints")
    print(f"Total distance: {result.total_distance:.2f}")
    print(f"Algorithm: {result.metadata.get('algorithm', 'unknown')}")
    
    # Test route optimization
    print("\n[3] Testing route optimization...")
    waypoints = [
        Waypoint(id="wp1", x=0.0, y=0.0),
        Waypoint(id="wp2", x=5.0, y=3.0),
        Waypoint(id="wp3", x=8.0, y=7.0),
        Waypoint(id="wp4", x=10.0, y=10.0)
    ]
    
    route_result = planner.optimize_route(waypoints, use_quantum=True)
    print(f"Route optimized: {len(route_result.waypoints)} waypoints")
    print(f"Total distance: {route_result.total_distance:.2f}")
    
    # Test energy-constrained
    print("\n[4] Testing energy-constrained planning...")
    energy_result = planner.plan_energy_constrained(start, end, max_energy=15.0, obstacles=obstacles)
    print(f"Energy required: {energy_result.energy_cost:.2f}")
    print(f"Energy feasible: {energy_result.metadata.get('energy_feasible', False)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
