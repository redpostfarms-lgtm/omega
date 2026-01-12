# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Multi-Agent Coordination System
Coordinates multiple agents to work together on complex tasks
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
COORDINATION_DIR = ARCHIVED / 'agent_coordination'
COORDINATION_DIR.mkdir(parents=True, exist_ok=True)

class MultiAgentCoordinator:
    """Coordinates multiple agents to work together on complex tasks."""
    
    def __init__(self):
        self.agents = {}
        self.active_tasks = {}
        self.task_results = {}
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]):
        """Register an agent with the coordinator."""
        self.agents[agent_id] = {
            'type': agent_type,
            'capabilities': capabilities,
            'status': 'idle',
            'current_task': None,
            'completed_tasks': 0
        }
    
    def coordinate_agents(self, task: str, agents: List[str], strategy: str = 'parallel') -> Dict[str, Any]:
        """
        Coordinate multiple agents to solve a task.
        
        Args:
            task: The task description
            agents: List of agent IDs to coordinate
            strategy: 'parallel' or 'sequential'
        
        Returns:
            Dictionary with results from all agents
        """
        task_id = f"task_{int(time.time())}"
        self.active_tasks[task_id] = {
            'task': task,
            'agents': agents,
            'strategy': strategy,
            'status': 'in_progress',
            'start_time': time.time()
        }
        
        results = {}
        
        if strategy == 'parallel':
            results = self._coordinate_parallel(task, agents)
        elif strategy == 'sequential':
            results = self._coordinate_sequential(task, agents)
        
        self.active_tasks[task_id]['status'] = 'completed'
        self.active_tasks[task_id]['end_time'] = time.time()
        self.active_tasks[task_id]['results'] = results
        
        # Save coordination log
        self._save_coordination_log(task_id, results)
        
        return results
    
    def _coordinate_parallel(self, task: str, agents: List[str]) -> Dict[str, Any]:
        """Coordinate agents in parallel."""
        results = {}
        
        def run_agent(agent_id):
            if agent_id in self.agents:
                self.agents[agent_id]['status'] = 'working'
                self.agents[agent_id]['current_task'] = task
                # In real implementation, call the agent's process method
                result = self._call_agent(agent_id, task)
                self.agents[agent_id]['status'] = 'idle'
                self.agents[agent_id]['current_task'] = None
                self.agents[agent_id]['completed_tasks'] += 1
                return agent_id, result
            return agent_id, None
        
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {executor.submit(run_agent, agent_id): agent_id for agent_id in agents}
            for future in as_completed(futures):
                agent_id, result = future.result()
                results[agent_id] = result
        
        return results
    
    def _coordinate_sequential(self, task: str, agents: List[str]) -> Dict[str, Any]:
        """Coordinate agents sequentially, passing results between them."""
        results = {}
        previous_result = None
        
        for agent_id in agents:
            if agent_id in self.agents:
                self.agents[agent_id]['status'] = 'working'
                self.agents[agent_id]['current_task'] = task
                
                # Combine task with previous result
                combined_task = task
                if previous_result:
                    combined_task = f"{task}\nPrevious agent result: {previous_result}"
                
                result = self._call_agent(agent_id, combined_task)
                results[agent_id] = result
                previous_result = result
                
                self.agents[agent_id]['status'] = 'idle'
                self.agents[agent_id]['current_task'] = None
                self.agents[agent_id]['completed_tasks'] += 1
        
        return results
    
    def distribute_tasks(self, tasks: List[str], agents: List[str]) -> Dict[str, Any]:
        """
        Distribute multiple tasks among available agents.
        
        Args:
            tasks: List of tasks to distribute
            agents: List of agent IDs available
        
        Returns:
            Dictionary mapping tasks to agent results
        """
        task_assignments = {}
        results = {}
        
        # Simple round-robin assignment
        for i, task in enumerate(tasks):
            agent_id = agents[i % len(agents)]
            if agent_id not in task_assignments:
                task_assignments[agent_id] = []
            task_assignments[agent_id].append(task)
        
        # Execute tasks in parallel per agent
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {}
            for agent_id, agent_tasks in task_assignments.items():
                for task in agent_tasks:
                    future = executor.submit(self._call_agent, agent_id, task)
                    futures[future] = (agent_id, task)
            
            for future in as_completed(futures):
                agent_id, task = futures[future]
                result = future.result()
                results[task] = {
                    'agent': agent_id,
                    'result': result
                }
        
        return results
    
    def merge_results(self, results: Dict[str, Any], merge_strategy: str = 'consensus') -> Any:
        """
        Merge results from multiple agents.
        
        Args:
            results: Dictionary of agent_id -> result
            merge_strategy: 'consensus', 'vote', 'aggregate', 'first'
        
        Returns:
            Merged result
        """
        if merge_strategy == 'consensus':
            # Find the most common result
            result_counts = {}
            for agent_id, result in results.items():
                result_str = str(result)
                result_counts[result_str] = result_counts.get(result_str, 0) + 1
            
            if result_counts:
                most_common = max(result_counts, key=result_counts.get)
                # Return the actual result, not the string
                for agent_id, result in results.items():
                    if str(result) == most_common:
                        return result
            return list(results.values())[0] if results else None
        
        elif merge_strategy == 'vote':
            # Simple voting - return result with most votes
            return self.merge_results(results, 'consensus')
        
        elif merge_strategy == 'aggregate':
            # Aggregate all results
            return list(results.values())
        
        elif merge_strategy == 'first':
            # Return first result
            return list(results.values())[0] if results else None
        
        return results
    
    def _call_agent(self, agent_id: str, task: str) -> Any:
        """Call an agent to process a task."""
        # This would integrate with actual agent implementations
        # For now, return a placeholder
        if agent_id in self.agents:
            return f"Agent {agent_id} processed: {task[:50]}..."
        return None
    
    def _save_coordination_log(self, task_id: str, results: Dict[str, Any]):
        """Save coordination log to disk."""
        log_file = COORDINATION_DIR / f"{task_id}.json"
        log_data = {
            'task_id': task_id,
            'task': self.active_tasks[task_id]['task'],
            'agents': self.active_tasks[task_id]['agents'],
            'strategy': self.active_tasks[task_id]['strategy'],
            'results': results,
            'timestamp': time.time()
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get status of the coordinator and all agents."""
        return {
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a['status'] == 'working'),
            'idle_agents': sum(1 for a in self.agents.values() if a['status'] == 'idle'),
            'active_tasks': len([t for t in self.active_tasks.values() if t['status'] == 'in_progress']),
            'agents': self.agents,
            'recent_tasks': list(self.active_tasks.keys())[-10:]
        }

