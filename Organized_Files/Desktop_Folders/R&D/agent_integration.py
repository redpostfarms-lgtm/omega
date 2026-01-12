# -*- coding: utf-8 -*-
# AGENT INTEGRATION - Brings all enhancements together
# Integrates reasoning, tools, and task management into Agent base class

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# Import base Agent
from agent_anonymous import Agent, AgentConfig

# Import enhancements
try:
    from agent_reasoning import add_reasoning_to_agent, ReasoningEngine, ReasoningMode
    HAS_REASONING = True
except ImportError:
    HAS_REASONING = False

try:
    from agent_tools import add_tools_to_agent, get_registry, ToolRegistry
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False

try:
    from agent_tasks import add_task_management_to_agent, TaskQueue, TaskPriority
    HAS_TASKS = True
except ImportError:
    HAS_TASKS = False


# Enhanced Agent class with all features
class EnhancedAgent(Agent):
    """
    Enhanced Agent with reasoning, tools, and task management.
    All features from world's best frameworks integrated.
    """
    
    def __init__(self, goal: str, config=None, enable_reasoning=True, enable_tools=True, enable_tasks=True):
        """Initialize enhanced agent."""
        super().__init__(goal, config)
        
        # Initialize reasoning if available
        if HAS_REASONING and enable_reasoning:
            self.reasoning_engine = None  # Lazy initialization
            self.has_reasoning = True
        else:
            self.has_reasoning = False
        
        # Initialize tool registry if available
        if HAS_TOOLS and enable_tools:
            self.tool_registry = get_registry()
            self.tool_registry.auto_discover_tools('.')
            self.has_tools = True
        else:
            self.tool_registry = None
            self.has_tools = False
        
        # Initialize task queue if available
        if HAS_TASKS and enable_tasks:
            self.task_queue = TaskQueue()
            self.has_tasks = True
        else:
            self.task_queue = None
            self.has_tasks = False
    
    def reason(self, problem: str, mode: str = 'react') -> str:
        """
        Use advanced reasoning to solve problem.
        
        Args:
            problem: Problem to solve
            mode: Reasoning mode ('react', 'cot', 'tot', 'verify', 'dust')
            
        Returns:
            Reasoning result
        """
        if not self.has_reasoning:
            return f"Reasoning not available. Problem: {problem}"
        
        if self.reasoning_engine is None:
            mode_enum = {
                'react': ReasoningMode.REACT,
                'cot': ReasoningMode.COT,
                'chain_of_thought': ReasoningMode.COT,
                'tot': ReasoningMode.TOT,
                'tree_of_thought': ReasoningMode.TOT,
                'verify': ReasoningMode.VERIFY,
                'chain_of_verification': ReasoningMode.VERIFY,
                'dust': ReasoningMode.DUST,
                'reflect': ReasoningMode.REFLECT
            }.get(mode.lower(), ReasoningMode.REACT)
            
            self.reasoning_engine = ReasoningEngine(mode=mode_enum)
        
        if mode.lower() in ['react', 'react_loop']:
            result = self.reasoning_engine.react_loop(problem)
        elif mode.lower() in ['cot', 'chain_of_thought']:
            result = self.reasoning_engine.chain_of_thought(problem)
        elif mode.lower() in ['tot', 'tree_of_thought']:
            result = self.reasoning_engine.tree_of_thought(problem)
        elif mode.lower() in ['verify', 'chain_of_verification', 'cove']:
            result = self.reasoning_engine.chain_of_verification(problem)
        elif mode.lower() == 'dust':
            result = self.reasoning_engine.dust_style_reasoning(problem)
        else:
            result = self.reasoning_engine.react_loop(problem)
        
        # Log reasoning
        trace = self.reasoning_engine.get_reasoning_trace()
        self.history.append(f"Reasoning ({mode}): {result[:100]}")
        self.log_run(f"reason_{mode}", str(trace)[:500], True)
        
        return result
    
    def use_tool(self, tool_name: str, *args, **kwargs):
        """
        Use a tool.
        
        Args:
            tool_name: Name of tool
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool result
        """
        if not self.has_tools:
            raise ValueError("Tool registry not available")
        
        try:
            result = self.tool_registry.execute_tool(tool_name, *args, **kwargs)
            self.history.append(f"Used tool '{tool_name}'")
            self.log_run(f"tool_{tool_name}", str(result)[:200], True)
            return result
        except Exception as e:
            self.history.append(f"Tool '{tool_name}' failed: {str(e)}")
            self.log_run(f"tool_{tool_name}", f"error: {str(e)}", False, error=str(e))
            raise
    
    def list_tools(self):
        """List available tools."""
        if not self.has_tools:
            return []
        return self.tool_registry.list_tools()
    
    def create_plan(self, goal: str, steps=None):
        """
        Create task plan.
        
        Args:
            goal: Main goal
            steps: Optional steps (auto-generated if None)
            
        Returns:
            TaskQueue
        """
        if not self.has_tasks:
            return None
        
        queue = TaskQueue()
        
        if steps is None:
            # Decompose goal
            steps = self._decompose_goal(goal)
        
        task_ids = []
        for i, step in enumerate(steps):
            depends_on = task_ids[-1] if task_ids else None
            priority = TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM
            task_id = queue.add_task(
                description=step,
                priority=priority,
                dependencies=[depends_on] if depends_on else None
            )
            task_ids.append(task_id)
        
        self.task_queue = queue
        return queue
    
    def execute_plan(self, queue=None):
        """
        Execute task plan.
        
        Args:
            queue: Optional TaskQueue (uses self.task_queue if None)
            
        Returns:
            Execution results
        """
        if not self.has_tasks:
            return None
        
        if queue is None:
            queue = self.task_queue
        
        if queue is None:
            return None
        
        results = []
        
        while True:
            task = queue.get_next_task()
            if not task:
                break
            
            queue.mark_started(task.id)
            
            try:
                # Use reasoning to execute task
                if self.has_reasoning:
                    result = self.reason(task.description, mode='react')
                else:
                    result = f"Executed: {task.description}"
                
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
        
        return {
            'results': results,
            'statistics': queue.get_statistics(),
            'plan': queue.export_plan()
        }
    
    def _decompose_goal(self, goal: str):
        """Decompose goal into steps."""
        keywords = ["and", "then", "also", "next", "first", "second"]
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
    
    def get_capabilities(self):
        """Get agent capabilities summary."""
        return {
            'reasoning': self.has_reasoning,
            'tools': self.has_tools and len(self.list_tools()) if self.has_tools else 0,
            'task_management': self.has_tasks,
            'babel': True,  # Always available
            'self_improvement': True,  # Always available
            'dashboard': True  # Always available via agent_dashboard.py
        }


if __name__ == '__main__':
    print("=" * 60)
    print("ENHANCED AGENT - Integration Test")
    print("=" * 60)
    
    # Create enhanced agent
    agent = EnhancedAgent("test enhanced capabilities")
    
    print(f"\n🤖 Agent: {agent.name}")
    print(f"📋 Capabilities: {agent.get_capabilities()}")
    
    # Test reasoning if available
    if agent.has_reasoning:
        print("\n🧠 Testing reasoning...")
        result = agent.reason("How to optimize code?", mode='react')
        print(f"  Result: {result[:100]}...")
    
    # Test tools if available
    if agent.has_tools:
        print(f"\n🛠️  Available tools: {len(agent.list_tools())}")
        for tool in agent.list_tools()[:5]:
            print(f"  - {tool}")
    
    # Test task management if available
    if agent.has_tasks:
        print("\n📋 Testing task management...")
        plan = agent.create_plan("Research, write, and publish article")
        print(f"  Created plan with {len(plan.tasks)} tasks")
        stats = plan.get_statistics()
        print(f"  Ready tasks: {stats['ready']}")
    
    print("\n✅ Enhanced agent ready with all features integrated")

