# -*- coding: utf-8 -*-
# TOOL REGISTRY & AUTO-DISCOVERY SYSTEM
# Integrates tool use patterns from LangChain, AutoGPT, SuperAGI

import os
import inspect
import sys
import io
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


class ToolType(Enum):
    """Tool categories."""
    FILE_OPERATION = "file_operation"
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    DATA_ANALYSIS = "data_analysis"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
    tool_type: ToolType
    requires_auth: bool = False
    rate_limit: Optional[int] = None
    
    def __call__(self, *args, **kwargs):
        """Execute tool."""
        return self.func(*args, **kwargs)


class ToolRegistry:
    """
    Tool registry with auto-discovery.
    Patterns from LangChain, AutoGPT, SuperAGI.
    """
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.tool_index: Dict[ToolType, List[str]] = {t: [] for t in ToolType}
        self.auto_discovery_paths = ['.', './tools', './scripts']
    
    def register(self, tool: Tool):
        """
        Register a tool.
        
        Args:
            tool: Tool object to register
        """
        self.tools[tool.name] = tool
        self.tool_index[tool.tool_type].append(tool.name)
    
    def register_function(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tool_type: ToolType = ToolType.CUSTOM
    ):
        """
        Register a function as a tool.
        
        Args:
            func: Function to register
            name: Tool name (defaults to function name)
            description: Tool description (defaults to docstring)
            tool_type: Type of tool
        """
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Tool: {tool_name}"
        
        # Extract parameters from function signature
        sig = inspect.signature(func)
        parameters = {}
        for param_name, param in sig.parameters.items():
            parameters[param_name] = {
                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                'default': param.default if param.default != inspect.Parameter.empty else None,
                'required': param.default == inspect.Parameter.empty
            }
        
        tool = Tool(
            name=tool_name,
            description=tool_desc,
            func=func,
            parameters=parameters,
            tool_type=tool_type
        )
        
        self.register(tool)
    
    def auto_discover_tools(self, directory: str = '.'):
        """
        Auto-discover tools from directory.
        Scans for Python files and registers functions.
        
        Args:
            directory: Directory to scan
        """
        dir_path = Path(directory)
        
        # Scan for Python files
        for py_file in dir_path.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            
            try:
                # Try to import and discover
                module_name = py_file.stem
                spec = None
                
                # Look for tool functions (functions with @tool decorator or tool_ prefix)
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for @tool decorator
                    if '@tool' in content or 'def tool_' in content:
                        # In production, would import and register
                        self._discover_from_file(py_file, content)
            
            except Exception as e:
                continue
    
    def _discover_from_file(self, file_path: Path, content: str):
        """Discover tools from file content."""
        # Simplified discovery - look for function definitions
        # In production, use AST parsing
        lines = content.split('\n')
        current_func = None
        
        for line in lines:
            if line.strip().startswith('def ') and ('tool_' in line or '@tool' in line):
                # Found potential tool function
                func_name = line.split('def ')[1].split('(')[0].strip()
                # Would register if properly annotated
                pass
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def list_tools(self, tool_type: Optional[ToolType] = None) -> List[str]:
        """List available tools."""
        if tool_type:
            return self.tool_index.get(tool_type, [])
        return list(self.tools.keys())
    
    def search_tools(self, query: str) -> List[Tool]:
        """Search tools by description."""
        query_lower = query.lower()
        matches = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matches.append(tool)
        
        return matches
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """
        Execute a tool.
        
        Args:
            name: Tool name
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        return tool(*args, **kwargs)
    
    def get_tool_schema(self, name: str) -> Dict[str, Any]:
        """Get JSON schema for tool."""
        tool = self.get_tool(name)
        if not tool:
            return {}
        
        return {
            'name': tool.name,
            'description': tool.description,
            'parameters': tool.parameters,
            'type': tool.tool_type.value,
            'requires_auth': tool.requires_auth
        }


# Built-in tool functions
def tool_read_file(filepath: str) -> str:
    """Read contents of a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def tool_write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"File written: {filepath}"


def tool_list_directory(path: str = '.') -> List[str]:
    """List files in directory."""
    return [str(p) for p in Path(path).iterdir()]


def tool_search_web(query: str) -> str:
    """Search the web (placeholder)."""
    return f"[Web search results for: {query}]"


def tool_execute_python(code: str) -> str:
    """Execute Python code."""
    try:
        result = eval(code)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# Initialize global registry with built-in tools
_global_registry = ToolRegistry()

# Register built-in tools
_global_registry.register_function(
    tool_read_file,
    name="read_file",
    description="Read contents of a file",
    tool_type=ToolType.FILE_OPERATION
)

_global_registry.register_function(
    tool_write_file,
    name="write_file",
    description="Write content to a file",
    tool_type=ToolType.FILE_OPERATION
)

_global_registry.register_function(
    tool_list_directory,
    name="list_directory",
    description="List files in a directory",
    tool_type=ToolType.FILE_OPERATION
)

_global_registry.register_function(
    tool_search_web,
    name="search_web",
    description="Search the web",
    tool_type=ToolType.WEB_SEARCH
)

_global_registry.register_function(
    tool_execute_python,
    name="execute_python",
    description="Execute Python code",
    tool_type=ToolType.CODE_EXECUTION
)


def get_registry() -> ToolRegistry:
    """Get global tool registry."""
    return _global_registry


# Integration with Agent class
def add_tools_to_agent(agent_class):
    """Add tool capabilities to Agent class."""
    
    def __init_with_tools(self, *args, **kwargs):
        """Enhanced __init__ with tool registry."""
        # Call original __init__
        original_init = agent_class.__init__
        original_init(self, *args, **kwargs)
        
        # Add tool registry
        self.tool_registry = ToolRegistry()
        
        # Auto-discover tools
        self.tool_registry.auto_discover_tools('.')
        
        # Register built-ins
        self.tool_registry.register_function(tool_read_file)
        self.tool_registry.register_function(tool_write_file)
        self.tool_registry.register_function(tool_list_directory)
        self.tool_registry.register_function(tool_search_web)
        self.tool_registry.register_function(tool_execute_python)
    
    def use_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Use a tool.
        
        Args:
            tool_name: Name of tool to use
            *args: Positional arguments for tool
            **kwargs: Keyword arguments for tool
            
        Returns:
            Tool execution result
        """
        try:
            result = self.tool_registry.execute_tool(tool_name, *args, **kwargs)
            self.history.append(f"Used tool '{tool_name}': {str(result)[:100]}")
            self.log_run(f"tool_{tool_name}", str(result)[:200], True)
            return result
        except Exception as e:
            self.history.append(f"Tool '{tool_name}' failed: {str(e)}")
            self.log_run(f"tool_{tool_name}", f"error: {str(e)}", False, error=str(e))
            raise
    
    def list_available_tools(self) -> List[str]:
        """List all available tools."""
        return self.tool_registry.list_tools()
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search for tools."""
        tools = self.tool_registry.search_tools(query)
        return [asdict(tool) for tool in tools]
    
    # Replace __init__
    agent_class.__init__ = __init_with_tools
    
    # Add methods
    agent_class.use_tool = use_tool
    agent_class.list_available_tools = list_available_tools
    agent_class.search_tools = search_tools
    
    return agent_class


if __name__ == '__main__':
    print("=" * 60)
    print("TOOL REGISTRY & AUTO-DISCOVERY - Test")
    print("=" * 60)
    
    registry = get_registry()
    
    print(f"\n📋 Registered tools: {len(registry.list_tools())}")
    for tool_name in registry.list_tools():
        tool = registry.get_tool(tool_name)
        print(f"  - {tool_name}: {tool.description[:60]}")
    
    print("\n🔍 Search test:")
    results = registry.search_tools("file")
    print(f"  Found {len(results)} tools matching 'file'")
    
    print("\n✅ Tool registry ready")

