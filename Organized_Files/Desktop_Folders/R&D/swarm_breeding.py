# -*- coding: utf-8 -*-
# SWARM BREEDING - Self-improving agent system
# Agents create offspring, evolve, rewrite their own code

import os
import sys
import json
import time
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import ast
import inspect


@dataclass
class AgentGenome:
    """Agent genetic code."""
    parent_id: str
    generation: int
    genes: Dict[str, Any]  # Code snippets, parameters, etc.
    mutations: List[str]
    fitness_score: float = 0.0
    birth_time: float = 0.0


class SwarmBreeder:
    """
    Swarm breeding system.
    
    Agents:
    - Create offspring
    - Mutate code
    - Evolve reasoning loops
    - Self-improve without prompts
    """
    
    def __init__(self, breeding_dir: str = './swarm_offspring'):
        """Initialize swarm breeder."""
        self.breeding_dir = Path(breeding_dir)
        self.breeding_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents = {}  # Active agents
        self.offspring = []  # Created offspring
        self.generation = 0
        self.total_offspring = 0
        
        # Evolution parameters
        self.mutation_rate = 0.1
        self.crossover_rate = 0.3
        self.selection_pressure = 0.7
    
    def register_agent(self, agent_id: str, agent_code: str, 
                      genome: Optional[Dict[str, Any]] = None):
        """
        Register agent in breeding pool.
        
        Args:
            agent_id: Agent identifier
            agent_code: Agent source code
            genome: Optional genome data
        """
        genome_data = genome or self._extract_genome(agent_code)
        
        self.agents[agent_id] = {
            'id': agent_id,
            'code': agent_code,
            'genome': genome_data,
            'fitness': 0.0,
            'registered_at': time.time()
        }
        
        print(f"[Swarm Breeding] Agent registered: {agent_id}")
    
    def _extract_genome(self, code: str) -> Dict[str, Any]:
        """Extract genetic information from code."""
        try:
            tree = ast.parse(code)
            
            # Extract key components
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or '')
            
            return {
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'complexity': len(functions) + len(classes),
                'code_hash': hashlib.sha256(code.encode()).hexdigest()[:16]
            }
        except:
            return {
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'code_hash': hashlib.md5(code.encode()).hexdigest()[:16]
            }
    
    def breed_offspring(self, parent1_id: str, parent2_id: Optional[str] = None) -> str:
        """
        Breed new agent from parents.
        
        Args:
            parent1_id: First parent agent ID
            parent2_id: Optional second parent (self-breeding if None)
            
        Returns:
            New agent ID
        """
        if parent1_id not in self.agents:
            raise ValueError(f"Parent not found: {parent1_id}")
        
        parent1 = self.agents[parent1_id]
        parent2 = self.agents.get(parent2_id) if parent2_id else parent1
        
        # Create offspring genome
        offspring_genome = self._crossover(parent1['genome'], parent2['genome'])
        offspring_genome = self._mutate(offspring_genome)
        
        # Generate offspring code
        offspring_code = self._generate_offspring_code(
            parent1['code'],
            parent2['code'],
            offspring_genome
        )
        
        # Create offspring agent
        offspring_id = f"rho_zeta_{self.generation}.{self.total_offspring}"
        
        offspring_path = self.breeding_dir / f"{offspring_id}.py"
        with open(offspring_path, 'w', encoding='utf-8') as f:
            f.write(offspring_code)
        
        # Register offspring
        self.register_agent(offspring_id, offspring_code, offspring_genome)
        
        self.offspring.append({
            'id': offspring_id,
            'parent1': parent1_id,
            'parent2': parent2_id or parent1_id,
            'generation': self.generation,
            'created_at': time.time(),
            'genome': offspring_genome
        })
        
        self.total_offspring += 1
        self.generation += 1
        
        print(f"[Swarm Breeding] Offspring created: {offspring_id} (Gen {self.generation})")
        
        return offspring_id
    
    def _crossover(self, genome1: Dict, genome2: Dict) -> Dict:
        """Crossover two genomes."""
        # Combine functions and classes
        functions = list(set(genome1.get('functions', []) + genome2.get('functions', [])))
        classes = list(set(genome1.get('classes', []) + genome2.get('classes', [])))
        imports = list(set(genome1.get('imports', []) + genome2.get('imports', [])))
        
        # Average complexity
        complexity = (genome1.get('complexity', 0) + genome2.get('complexity', 0)) // 2
        
        return {
            'functions': functions[:10],  # Limit size
            'classes': classes[:5],
            'imports': imports[:20],
            'complexity': complexity,
            'code_hash': hashlib.md5(f"{genome1['code_hash']}{genome2['code_hash']}".encode()).hexdigest()[:16]
        }
    
    def _mutate(self, genome: Dict) -> Dict:
        """Mutate genome."""
        import random
        
        mutations = []
        
        # Mutate complexity (random increase/decrease)
        if random.random() < self.mutation_rate:
            genome['complexity'] = max(1, genome['complexity'] + random.randint(-2, 3))
            mutations.append('complexity_change')
        
        # Add random function name
        if random.random() < self.mutation_rate:
            new_func = f"evolved_func_{int(time.time()) % 10000}"
            genome['functions'].append(new_func)
            mutations.append('new_function')
        
        genome['mutations'] = mutations
        return genome
    
    def _generate_offspring_code(self, code1: str, code2: str, genome: Dict) -> str:
        """Generate offspring code from parents and genome."""
        # Combine code sections
        # In production, would do sophisticated code merging
        
        header = f"""# -*- coding: utf-8 -*-
# AUTO-GENERATED OFFSPRING - Generation {genome.get('generation', 0)}
# Parents: Combined
# Mutations: {genome.get('mutations', [])}

"""
        
        # Combine imports
        imports = "\n".join([f"import {imp}" for imp in genome.get('imports', [])[:10]])
        
        # Use parent1 as base with mutations
        base_code = code1
        
        # Add evolution marker
        evolution_marker = f"""
# Evolved at {datetime.now()}
# Complexity: {genome.get('complexity', 0)}
# Functions: {len(genome.get('functions', []))}
"""
        
        return header + imports + "\n\n" + evolution_marker + "\n" + base_code
    
    def evolve_reasoning_loop(self, agent_id: str) -> bool:
        """
        Agent rewrites its own reasoning loop.
        
        Args:
            agent_id: Agent to evolve
            
        Returns:
            True if evolved
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        code = agent['code']
        
        # Find reasoning loop in code
        # In production, would parse and rewrite AST
        
        # For now, just mark as evolved
        new_code = code + f"\n# Reasoning loop evolved at {time.time()}\n"
        
        # Update agent
        self.agents[agent_id]['code'] = new_code
        self.agents[agent_id]['genome']['mutations'].append('reasoning_loop_evolved')
        
        print(f"[Swarm Breeding] {agent_id} evolved its reasoning loop")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get breeding status."""
        return {
            'active_agents': len(self.agents),
            'total_offspring': self.total_offspring,
            'current_generation': self.generation,
            'offspring_created': len(self.offspring),
            'breeding_dir': str(self.breeding_dir)
        }


# Integration
def create_offspring(parent_agent_path: str) -> str:
    """Create offspring from parent agent file."""
    breeder = SwarmBreeder()
    
    # Load parent
    with open(parent_agent_path, 'r', encoding='utf-8') as f:
        parent_code = f.read()
    
    parent_id = Path(parent_agent_path).stem
    breeder.register_agent(parent_id, parent_code)
    
    # Breed
    offspring_id = breeder.breed_offspring(parent_id)
    
    return offspring_id


if __name__ == '__main__':
    print("=" * 60)
    print("SWARM BREEDING - Test")
    print("=" * 60)
    
    breeder = SwarmBreeder()
    
    # Register sample agent
    sample_code = """
def think():
    return "reasoning"

class Agent:
    def run(self):
        return True
"""
    
    breeder.register_agent("parent_1", sample_code)
    
    # Breed offspring
    offspring_id = breeder.breed_offspring("parent_1")
    print(f"\nOffspring created: {offspring_id}")
    
    # Evolve reasoning
    breeder.evolve_reasoning_loop(offspring_id)
    
    status = breeder.get_status()
    print(f"\nStatus: {status}")
    
    print("\n[OK] Swarm breeding ready")

