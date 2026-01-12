# -*- coding: utf-8 -*-
# TASK MANAGEMENT SYSTEM - Dynamic queues, priorities, dependencies
# Patterns from BabyAGI, AutoGPT, SuperAGI

import json
import sys
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    """Task definition with dependencies and metadata."""
    id: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = None  # Task IDs this depends on
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = str(datetime.now())
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to execute (dependencies met)."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS]:
            return False
        return all(dep_id in completed_tasks for dep_id in self.dependencies)


class TaskQueue:
    """
    Dynamic task queue with priorities and dependency resolution.
    Patterns from BabyAGI, AutoGPT, SuperAGI.
    """
    
    def __init__(self):
        """Initialize task queue."""
        self.tasks: Dict[str, Task] = {}
        self.execution_order: List[str] = []
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
    
    def add_task(
        self,
        description: str,
        task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        max_attempts: int = 3
    ) -> str:
        """
        Add a task to the queue.
        
        Args:
            description: Task description
            task_id: Optional task ID (auto-generated if None)
            priority: Task priority
            dependencies: List of task IDs this depends on
            max_attempts: Maximum retry attempts
            
        Returns:
            Task ID
        """
        if task_id is None:
            task_id = f"task_{len(self.tasks)}_{datetime.now().timestamp():.0f}"
        
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            max_attempts=max_attempts
        )
        
        self.tasks[task_id] = task
        return task_id
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready to execute (dependencies met)."""
        ready = []
        
        for task in self.tasks.values():
            if task.is_ready(self.completed_tasks):
                ready.append(task)
        
        # Sort by priority (lower number = higher priority)
        ready.sort(key=lambda t: (t.priority.value, t.created_at))
        
        return ready
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task to execute."""
        ready = self.get_ready_tasks()
        return ready[0] if ready else None
    
    def mark_started(self, task_id: str):
        """Mark task as started."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = str(datetime.now())
            task.attempts += 1
    
    def mark_completed(self, task_id: str, result: Any = None):
        """Mark task as completed."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = str(datetime.now())
            task.result = result
            self.completed_tasks.add(task_id)
            self.execution_order.append(task_id)
    
    def mark_failed(self, task_id: str, error: str):
        """Mark task as failed."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.error = error
            task.attempts += 1
            
            if task.attempts >= task.max_attempts:
                task.status = TaskStatus.FAILED
                self.failed_tasks.add(task_id)
            else:
                # Retry
                task.status = TaskStatus.PENDING
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks blocked by unresolved dependencies."""
        blocked = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                unmet = [dep for dep in task.dependencies if dep not in self.completed_tasks]
                if unmet:
                    task.status = TaskStatus.BLOCKED
                    blocked.append(task)
        
        return blocked
    
    def resolve_dependencies(self) -> Dict[str, List[str]]:
        """
        Build dependency graph and resolve execution order.
        
        Returns:
            Dictionary mapping task_id to list of dependencies
        """
        graph = {}
        
        for task_id, task in self.tasks.items():
            graph[task_id] = task.dependencies
        
        return graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'total_tasks': len(self.tasks),
            'pending': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'ready': len(self.get_ready_tasks()),
            'in_progress': len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'blocked': len(self.get_blocked_tasks())
        }
    
    def export_plan(self) -> Dict[str, Any]:
        """Export execution plan."""
        return {
            'tasks': {tid: asdict(task) for tid, task in self.tasks.items()},
            'execution_order': self.execution_order,
            'completed': list(self.completed_tasks),
            'failed': list(self.failed_tasks),
            'statistics': self.get_statistics()
        }


# Integration with Agent class
def add_task_management_to_agent(agent_class):
    """Add task management to Agent class."""
    
    def create_task_plan(self, goal: str, steps: Optional[List[str]] = None) -> TaskQueue:
        """
        Create task plan from goal.
        
        Args:
            goal: Main goal
            steps: Optional list of steps (auto-generated if None)
            
        Returns:
            TaskQueue with tasks
        """
        queue = TaskQueue()
        
        if steps is None:
            # Auto-generate steps
            steps = self._decompose_goal(goal)
        
        # Create tasks
        task_ids = []
        for i, step in enumerate(steps):
            depends_on = task_ids[-1] if task_ids else None
            task_id = queue.add_task(
                description=step,
                priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                dependencies=[depends_on] if depends_on else None
            )
            task_ids.append(task_id)
        
        return queue
    
    def execute_task_queue(self, queue: TaskQueue) -> Dict[str, Any]:
        """
        Execute task queue until complete or blocked.
        
        Args:
            queue: TaskQueue to execute
            
        Returns:
            Execution results
        """
        results = []
        
        while True:
            task = queue.get_next_task()
            if not task:
                break
            
            queue.mark_started(task.id)
            
            try:
                # Execute task
                result = self._execute_task(task.description)
                queue.mark_completed(task.id, result)
                results.append({
                    'task_id': task.id,
                    'description': task.description,
                    'status': 'completed',
                    'result': result
                })
            except Exception as e:
                queue.mark_failed(task.id, str(e))
                results.append({
                    'task_id': task.id,
                    'description': task.description,
                    'status': 'failed',
                    'error': str(e)
                })
                
                # If critical task failed, stop
                if task.priority == TaskPriority.CRITICAL:
                    break
        
        return {
            'results': results,
            'statistics': queue.get_statistics(),
            'plan': queue.export_plan()
        }
    
    def _decompose_goal(self, goal: str) -> List[str]:
        """Decompose goal into steps."""
        # Simplified decomposition
        keywords = ["and", "then", "also", "next", "first", "second", "finally"]
        steps = []
        current = goal
        
        for keyword in keywords:
            if keyword in current.lower():
                idx = current.lower().find(keyword)
                steps.append(current[:idx].strip())
                current = current[idx + len(keyword):].strip()
        
        if current:
            steps.append(current)
        
        return steps if len(steps) > 1 else [goal]
    
    def _execute_task(self, description: str) -> Any:
        """Execute a task description."""
        # Simplified - would use reasoning engine in production
        return f"Executed: {description}"
    
    # Add methods
    agent_class.create_task_plan = create_task_plan
    agent_class.execute_task_queue = execute_task_queue
    
    return agent_class


if __name__ == '__main__':
    print("=" * 60)
    print("TASK MANAGEMENT SYSTEM - Test")
    print("=" * 60)
    
    queue = TaskQueue()
    
    # Add tasks with dependencies
    task1 = queue.add_task("Research topic", priority=TaskPriority.HIGH)
    task2 = queue.add_task("Write draft", dependencies=[task1], priority=TaskPriority.HIGH)
    task3 = queue.add_task("Review and edit", dependencies=[task2], priority=TaskPriority.MEDIUM)
    task4 = queue.add_task("Publish", dependencies=[task3], priority=TaskPriority.LOW)
    
    print(f"\n📋 Created {len(queue.tasks)} tasks")
    print(f"Ready tasks: {len(queue.get_ready_tasks())}")
    
    # Simulate execution
    next_task = queue.get_next_task()
    if next_task:
        print(f"\n▶ Next task: {next_task.description}")
        queue.mark_started(next_task.id)
        queue.mark_completed(next_task.id, "Research complete")
    
    print(f"\n📊 Statistics: {queue.get_statistics()}")
    print("\n✅ Task management ready")

