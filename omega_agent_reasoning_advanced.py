"""
Advanced Agent Reasoning for The Gatekeeper
============================================
ReAct (Reason + Act) pattern using LangChain and LangGraph

Features:
- Multi-step reasoning
- Tool calling (file ops, health checks, calculations)
- Agent workflow graphs
- Conversation memory
- Self-reflection and error correction

Requirements:
- langchain>=0.1.0
- langgraph>=0.0.20
- langchain-community>=0.0.10
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.memory import ConversationBufferMemory
    from langchain_core.language_models.base import BaseLanguageModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available for advanced reasoning")


class AgentState(Enum):
    """Agent execution states"""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ReasoningStep:
    """Single step in reasoning process"""
    state: AgentState
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict] = None
    observation: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            'state': self.state.value,
            'thought': self.thought,
            'action': self.action,
            'action_input': self.action_input,
            'observation': self.observation,
            'timestamp': self.timestamp.isoformat()
        }


class ToolRegistry:
    """Registry of available tools for the agent"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools: List[Tool] = []
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""
        # File operations
        self.register_tool(
            name="read_file",
            func=self._read_file,
            description="Read contents of a file. Input: {'path': 'file/path.txt'}"
        )

        self.register_tool(
            name="list_files",
            func=self._list_files,
            description="List files in a directory. Input: {'path': 'directory/path'}"
        )

        self.register_tool(
            name="search_files",
            func=self._search_files,
            description="Search for files matching pattern. Input: {'pattern': '*.py', 'path': 'dir'}"
        )

        # System health
        self.register_tool(
            name="check_health",
            func=self._check_health,
            description="Check system health (disk, CPU, memory). Input: {}"
        )

        self.register_tool(
            name="forecast_disk",
            func=self._forecast_disk,
            description="Forecast disk usage for N days. Input: {'days': 7}"
        )

        # Calculations
        self.register_tool(
            name="calculate",
            func=self._calculate,
            description="Perform calculations. Input: {'expression': '2 + 2'}"
        )

        # Information
        self.register_tool(
            name="get_current_time",
            func=self._get_current_time,
            description="Get current date and time. Input: {}"
        )

    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool"""
        tool = Tool(name=name, func=func, description=description)
        self.tools.append(tool)
        self.logger.info(f"Registered tool: {name}")

    def get_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return self.tools

    # Tool implementations
    def _read_file(self, input_str: str) -> str:
        """Read file contents"""
        try:
            input_dict = json.loads(input_str) if isinstance(input_str, str) else input_str
            path = input_dict.get('path', input_str)
            file_path = Path(path)

            if not file_path.exists():
                return f"Error: File not found: {path}"

            if file_path.stat().st_size > 1_000_000:  # 1MB limit
                return f"Error: File too large: {path}"

            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _list_files(self, input_str: str) -> str:
        """List files in directory"""
        try:
            input_dict = json.loads(input_str) if isinstance(input_str, str) else input_str
            path = input_dict.get('path', input_str)
            dir_path = Path(path)

            if not dir_path.exists():
                return f"Error: Directory not found: {path}"

            if not dir_path.is_dir():
                return f"Error: Not a directory: {path}"

            files = [f.name for f in dir_path.iterdir()]
            return '\n'.join(files[:100])  # Limit to 100 files
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _search_files(self, input_str: str) -> str:
        """Search for files matching pattern"""
        try:
            input_dict = json.loads(input_str) if isinstance(input_str, str) else input_str
            pattern = input_dict.get('pattern', '*.py')
            path = input_dict.get('path', '.')

            dir_path = Path(path)
            if not dir_path.exists():
                return f"Error: Directory not found: {path}"

            matches = list(dir_path.glob(pattern))[:50]  # Limit to 50 matches
            return '\n'.join(str(m) for m in matches)
        except Exception as e:
            return f"Error searching files: {str(e)}"

    def _check_health(self, input_str: str) -> str:
        """Check system health"""
        try:
            # Try to import health analyzer
            try:
                from omega_predictive_health import get_health_analyzer
                analyzer = get_health_analyzer()
                summary = analyzer.get_health_summary()
                return json.dumps(summary, indent=2)
            except ImportError:
                import psutil
                disk = psutil.disk_usage('C:\\')
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                return json.dumps({
                    'disk_percent': disk.percent,
                    'cpu_percent': cpu,
                    'memory_percent': memory.percent
                }, indent=2)
        except Exception as e:
            return f"Error checking health: {str(e)}"

    def _forecast_disk(self, input_str: str) -> str:
        """Forecast disk usage"""
        try:
            input_dict = json.loads(input_str) if isinstance(input_str, str) else input_str
            days = input_dict.get('days', 7)

            from omega_predictive_health import get_health_analyzer
            analyzer = get_health_analyzer()
            forecast = analyzer.forecast_disk_usage(days=days)

            if forecast:
                return json.dumps(forecast.to_dict(), indent=2)
            else:
                return "Forecast unavailable (need more historical data)"
        except ImportError:
            return "Error: Predictive health module not available"
        except Exception as e:
            return f"Error forecasting: {str(e)}"

    def _calculate(self, input_str: str) -> str:
        """Perform safe calculation"""
        try:
            input_dict = json.loads(input_str) if isinstance(input_str, str) else input_str
            expression = input_dict.get('expression', input_str)

            # Safe evaluation (limited to math operations)
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"

            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error calculating: {str(e)}"

    def _get_current_time(self, input_str: str) -> str:
        """Get current time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SimpleLLM(BaseLanguageModel):
    """Simple LLM wrapper for local models"""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        # Try to import local LLM
        try:
            from omega_local_llm import get_brain_llm
            self.llm = get_brain_llm()
            self.available = self.llm.available
        except ImportError:
            self.llm = None
            self.available = False
            self.logger.warning("Local LLM not available")

    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke the LLM"""
        if not self.available:
            return "LLM unavailable. Please install ollama and omega_local_llm."

        try:
            return self.llm.llm.generate(prompt)
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _generate(self, prompts, **kwargs):
        """LangChain compatibility"""
        return [self.invoke(p) for p in prompts]

    @property
    def _llm_type(self) -> str:
        return "simple_local_llm"


class ReActAgent:
    """
    ReAct (Reason + Act) agent with tools

    Implements the ReAct pattern:
    1. Thought: Think about what to do
    2. Action: Choose and execute a tool
    3. Observation: Observe the result
    4. Reflection: Reflect on progress
    5. Repeat until solved or max steps

    Usage:
        agent = ReActAgent()
        result = agent.solve("Check disk usage and predict when it will be full")
    """

    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        max_steps: int = 10,
        verbose: bool = True
    ):
        """
        Initialize ReAct agent

        Args:
            llm: Language model (uses SimpleLLM if None)
            max_steps: Maximum reasoning steps
            verbose: Print reasoning process
        """
        self.logger = logging.getLogger(__name__)
        self.max_steps = max_steps
        self.verbose = verbose

        # Initialize LLM
        if llm is None:
            self.llm = SimpleLLM()
        else:
            self.llm = llm

        if not LANGCHAIN_AVAILABLE:
            self.logger.error("LangChain not available")
            self.available = False
            return

        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self.tools = self.tool_registry.get_tools()

        # Reasoning history
        self.reasoning_steps: List[ReasoningStep] = []

        # Memory
        self.memory = ConversationBufferMemory(memory_key="chat_history")

        # Create ReAct prompt
        self.prompt = self._create_react_prompt()

        # Create agent (if LangChain available)
        try:
            self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=self.memory,
                verbose=self.verbose,
                max_iterations=self.max_steps,
                handle_parsing_errors=True
            )
            self.available = True
        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            self.available = False

    def _create_react_prompt(self) -> PromptTemplate:
        """Create ReAct prompt template"""
        template = """You are an intelligent assistant that can use tools to accomplish tasks.

You have access to the following tools:

{tools}

Use the following format:

Thought: Think about what you need to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (as JSON)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Remember to always use the exact format above.

Question: {input}

{agent_scratchpad}"""

        return PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template=template
        )

    def solve(self, problem: str) -> str:
        """
        Solve a problem using ReAct reasoning

        Args:
            problem: Problem description

        Returns:
            Solution or explanation
        """
        if not self.available:
            return "Agent unavailable. Install langchain and dependencies."

        try:
            self.reasoning_steps.clear()

            # Add initial thinking step
            self.reasoning_steps.append(ReasoningStep(
                state=AgentState.THINKING,
                thought=f"Starting to solve: {problem}"
            ))

            # Run agent
            result = self.agent_executor.invoke({"input": problem})

            # Add completion step
            self.reasoning_steps.append(ReasoningStep(
                state=AgentState.COMPLETED,
                thought="Problem solved",
                observation=result.get('output', 'No output')
            ))

            return result.get('output', 'No solution found')

        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            self.reasoning_steps.append(ReasoningStep(
                state=AgentState.ERROR,
                thought=f"Error occurred: {str(e)}"
            ))
            return f"Error: {str(e)}"

    def get_reasoning_trace(self) -> List[Dict]:
        """Get the reasoning trace"""
        return [step.to_dict() for step in self.reasoning_steps]

    def save_trace(self, filepath: str):
        """Save reasoning trace to file"""
        trace = self.get_reasoning_trace()
        with open(filepath, 'w') as f:
            json.dump(trace, f, indent=2)
        self.logger.info(f"Saved reasoning trace to {filepath}")

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        self.reasoning_steps.clear()


# Global instance
_agent_instance: Optional[ReActAgent] = None


def get_react_agent() -> ReActAgent:
    """Get or create global ReAct agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ReActAgent()
    return _agent_instance


def solve_with_reasoning(problem: str) -> str:
    """
    Solve problem with reasoning (convenience function)

    Args:
        problem: Problem description

    Returns:
        Solution
    """
    agent = get_react_agent()
    return agent.solve(problem)


if __name__ == "__main__":
    # Demo/test mode
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Agent Reasoning Demo")
    parser.add_argument('problem', nargs='?', help='Problem to solve')
    parser.add_argument('--trace', action='store_true', help='Show reasoning trace')
    parser.add_argument('--save-trace', help='Save trace to file')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    agent = get_react_agent()

    if not agent.available:
        print("\n❌ Agent unavailable")
        print("Install dependencies:")
        print("  py -3.11 -m pip install langchain langgraph langchain-community")
        sys.exit(1)

    print("\n🤖 Advanced ReAct Agent Ready")
    print(f"Available tools: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")

    if args.problem:
        print(f"\n💭 Solving: {args.problem}")
        print("\n" + "="*60)

        solution = agent.solve(args.problem)

        print("\n" + "="*60)
        print(f"\n✅ Solution:\n{solution}\n")

        if args.trace:
            print("\n🔍 Reasoning Trace:")
            for i, step in enumerate(agent.reasoning_steps, 1):
                print(f"\n  Step {i} [{step.state.value}]:")
                print(f"    Thought: {step.thought}")
                if step.action:
                    print(f"    Action: {step.action}")
                if step.observation:
                    print(f"    Observation: {step.observation[:100]}...")

        if args.save_trace:
            agent.save_trace(args.save_trace)
            print(f"\n💾 Trace saved to: {args.save_trace}")

    else:
        print("\nUsage:")
        print('  py -3.11 omega_agent_reasoning_advanced.py "Check disk usage"')
        print('  py -3.11 omega_agent_reasoning_advanced.py "List Python files" --trace')
        print('  py -3.11 omega_agent_reasoning_advanced.py "Forecast disk" --save-trace trace.json')
        print("\nExample problems:")
        print("  - Check system health and tell me if there are any issues")
        print("  - What is the disk usage forecast for the next 7 days?")
        print("  - List all Python files in the current directory")
        print("  - Calculate 15% of 250")
