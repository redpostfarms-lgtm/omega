# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent Task Decomposition
Break down complex tasks into smaller, manageable subtasks
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
TASKS_DIR = ARCHIVED / 'task_decomposition'
TASKS_DIR.mkdir(parents=True, exist_ok=True)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class AgentTaskDecomposition:
    """Break down complex tasks into manageable subtasks."""
    
    def __init__(self):
        self.active_tasks = {}
        self.task_dependencies = {}
    
    def decompose_task(self, task: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: The main task description
            max_depth: Maximum decomposition depth
        
        Returns:
            Dictionary with task structure
        """
        task_id = f"task_{int(time.time())}"
        
        # Simple decomposition strategy: break by keywords
        subtasks = self._break_down_by_keywords(task)
        
        task_structure = {
            'task_id': task_id,
            'main_task': task,
            'subtasks': subtasks,
            'status': TaskStatus.PENDING.value,
            'created_at': time.time(),
            'max_depth': max_depth
        }
        
        self.active_tasks[task_id] = task_structure
        
        # Save task structure
        self._save_task_structure(task_id, task_structure)
        
        return task_structure
    
    def _break_down_by_keywords(self, task: str) -> List[Dict[str, Any]]:
        """Break down task using keyword analysis."""
        subtasks = []
        
        # Common task patterns
        if ' and ' in task.lower():
            parts = task.split(' and ')
            for i, part in enumerate(parts, 1):
                subtasks.append({
                    'id': f"subtask_{i}",
                    'task': part.strip(),
                    'status': TaskStatus.PENDING.value,
                    'dependencies': []
                })
        elif ' then ' in task.lower():
            parts = task.split(' then ')
            dependencies = []
            for i, part in enumerate(parts, 1):
                subtask = {
                    'id': f"subtask_{i}",
                    'task': part.strip(),
                    'status': TaskStatus.PENDING.value,
                    'dependencies': dependencies.copy()
                }
                subtasks.append(subtask)
                dependencies.append(f"subtask_{i}")
        else:
            # Single task - no decomposition needed
            subtasks.append({
                'id': 'subtask_1',
                'task': task,
                'status': TaskStatus.PENDING.value,
                'dependencies': []
            })
        
        return subtasks
    
    def create_subtasks(self, task_id: str, subtasks: List[str], dependencies: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        Create subtasks for a task.
        
        Args:
            task_id: Parent task ID
            subtasks: List of subtask descriptions
            dependencies: Dictionary mapping subtask IDs to their dependencies
        
        Returns:
            List of created subtasks
        """
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        created_subtasks = []
        
        for i, subtask_desc in enumerate(subtasks, 1):
            subtask_id = f"{task_id}_subtask_{i}"
            subtask_deps = dependencies.get(subtask_id, []) if dependencies else []
            
            subtask = {
                'id': subtask_id,
                'task': subtask_desc,
                'status': TaskStatus.PENDING.value,
                'dependencies': subtask_deps,
                'created_at': time.time()
            }
            
            created_subtasks.append(subtask)
            
            # Add to parent task
            if 'subtasks' not in self.active_tasks[task_id]:
                self.active_tasks[task_id]['subtasks'] = []
            self.active_tasks[task_id]['subtasks'].append(subtask)
        
        # Save updated task structure
        self._save_task_structure(task_id, self.active_tasks[task_id])
        
        return created_subtasks
    
    def track_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Track progress of a task and its subtasks.
        
        Args:
            task_id: Task ID
        
        Returns:
            Progress report
        """
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.active_tasks[task_id]
        subtasks = task.get('subtasks', [])
        
        total = len(subtasks)
        completed = sum(1 for st in subtasks if st['status'] == TaskStatus.COMPLETED.value)
        in_progress = sum(1 for st in subtasks if st['status'] == TaskStatus.IN_PROGRESS.value)
        failed = sum(1 for st in subtasks if st['status'] == TaskStatus.FAILED.value)
        blocked = sum(1 for st in subtasks if st['status'] == TaskStatus.BLOCKED.value)
        
        progress_percentage = (completed / total * 100) if total > 0 else 0
        
        # Determine overall status
        if completed == total:
            overall_status = TaskStatus.COMPLETED.value
        elif failed > 0:
            overall_status = TaskStatus.FAILED.value
        elif in_progress > 0:
            overall_status = TaskStatus.IN_PROGRESS.value
        elif blocked > 0:
            overall_status = TaskStatus.BLOCKED.value
        else:
            overall_status = TaskStatus.PENDING.value
        
        task['status'] = overall_status
        
        progress_report = {
            'task_id': task_id,
            'main_task': task['main_task'],
            'status': overall_status,
            'progress_percentage': progress_percentage,
            'subtasks': {
                'total': total,
                'completed': completed,
                'in_progress': in_progress,
                'failed': failed,
                'blocked': blocked,
                'pending': total - completed - in_progress - failed - blocked
            },
            'subtask_details': subtasks
        }
        
        return progress_report
    
    def update_subtask_status(self, task_id: str, subtask_id: str, status: TaskStatus):
        """Update status of a subtask."""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.active_tasks[task_id]
        subtasks = task.get('subtasks', [])
        
        for subtask in subtasks:
            if subtask['id'] == subtask_id:
                subtask['status'] = status.value
                subtask['updated_at'] = time.time()
                break
        
        # Save updated task structure
        self._save_task_structure(task_id, task)
    
    def get_next_available_subtask(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the next available subtask that can be executed (dependencies met)."""
        if task_id not in self.active_tasks:
            return None
        
        task = self.active_tasks[task_id]
        subtasks = task.get('subtasks', [])
        
        # Find subtasks with pending status and all dependencies completed
        for subtask in subtasks:
            if subtask['status'] == TaskStatus.PENDING.value:
                # Check if all dependencies are completed
                dependencies_met = True
                for dep_id in subtask.get('dependencies', []):
                    dep_subtask = next((st for st in subtasks if st['id'] == dep_id), None)
                    if dep_subtask and dep_subtask['status'] != TaskStatus.COMPLETED.value:
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    return subtask
        
        return None
    
    def _save_task_structure(self, task_id: str, task_structure: Dict[str, Any]):
        """Save task structure to disk."""
        task_file = TASKS_DIR / f"{task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_structure, f, indent=2, ensure_ascii=False)

