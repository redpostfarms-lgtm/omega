# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent Tool Use Framework
Framework for agents to discover and call available tools
"""

import importlib
import inspect
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
ARCHIVED = BRAIN / 'Archived'
TOOLS_DIR = ARCHIVED / 'agent_tools'
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

class AgentToolUse:
    """Framework for agents to discover and use tools."""
    
    def __init__(self):
        self.registered_tools = {}
        self.tool_call_history = []
        self._discover_tools()
    
    def _discover_tools(self):
        """Auto-discover tools in The Gatekeeper directory."""
        tool_patterns = {
            'battery_oracle.py': ['BatteryOracle', 'predict_battery_health'],
            'grant_machine.py': ['GrantMachine', 'generate_grant'],
            'drone_brain.py': ['DroneBrain', 'plan_flight'],
            'solar_forecaster.py': ['SolarForecaster', 'forecast_solar'],
            'agent_doc.py': ['AgentDoc', 'get_response'],
            'agent_aqua.py': ['AgentAqua', 'get_response'],
        }
        
        for filename, class_method in tool_patterns.items():
            tool_path = GATE / filename
            if tool_path.exists():
                try:
                    self._register_tool_from_file(filename, class_method[0], class_method[1])
                except Exception as e:
                    print(f"Warning: Could not register tool {filename}: {e}")
    
    def _register_tool_from_file(self, filename: str, class_name: str, method_name: str):
        """Register a tool from a Python file."""
        module_name = filename.replace('.py', '')
        tool_id = module_name
        
        self.registered_tools[tool_id] = {
            'file': filename,
            'module': module_name,
            'class': class_name,
            'method': method_name,
            'description': f"Tool from {filename}",
            'status': 'available'
        }
    
    def register_tool(self, tool_id: str, tool_function: Callable, description: str = ""):
        """
        Register a tool function.
        
        Args:
            tool_id: Unique identifier for the tool
            tool_function: Callable function
            description: Human-readable description
        """
        self.registered_tools[tool_id] = {
            'function': tool_function,
            'description': description,
            'signature': str(inspect.signature(tool_function)),
            'status': 'available'
        }
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools."""
        return self.registered_tools.copy()
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self.registered_tools.get(tool_id)
    
    def call_tool(self, tool_id: str, *args, **kwargs) -> Any:
        """
        Call a tool with arguments.
        
        Args:
            tool_id: Tool identifier
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Tool result
        """
        if tool_id not in self.registered_tools:
            raise ValueError(f"Tool {tool_id} not found")
        
        tool = self.registered_tools[tool_id]
        
        # Record tool call
        call_record = {
            'tool_id': tool_id,
            'args': str(args),
            'kwargs': str(kwargs),
            'timestamp': json.dumps({"time": __import__('time').time()})
        }
        self.tool_call_history.append(call_record)
        
        # Limit history size
        if len(self.tool_call_history) > 1000:
            self.tool_call_history = self.tool_call_history[-1000:]
        
        # Save tool call log
        self._save_tool_call_log(call_record)
        
        # Call the tool
        if 'function' in tool:
            # Direct function call
            return tool['function'](*args, **kwargs)
        elif 'module' in tool:
            # Import and call from module
            try:
                module = importlib.import_module(tool['module'])
                tool_class = getattr(module, tool['class'])
                tool_instance = tool_class()
                tool_method = getattr(tool_instance, tool['method'])
                return tool_method(*args, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error calling tool {tool_id}: {e}")
        
        raise RuntimeError(f"Tool {tool_id} has no callable implementation")
    
    def search_tools(self, query: str) -> List[str]:
        """
        Search for tools by description or ID.
        
        Args:
            query: Search query
        
        Returns:
            List of matching tool IDs
        """
        query_lower = query.lower()
        matches = []
        
        for tool_id, tool_info in self.registered_tools.items():
            if query_lower in tool_id.lower():
                matches.append(tool_id)
            elif query_lower in tool_info.get('description', '').lower():
                matches.append(tool_id)
        
        return matches
    
    def _save_tool_call_log(self, call_record: Dict[str, Any]):
        """Save tool call log to disk."""
        log_file = TOOLS_DIR / 'tool_calls.json'
        
        # Load existing logs
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        else:
            logs = []
        
        logs.append(call_record)
        
        # Keep last 1000 calls
        logs = logs[-1000:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def get_tool_call_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent tool call history."""
        return self.tool_call_history[-limit:]
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        tool_counts = {}
        for call in self.tool_call_history:
            tool_id = call['tool_id']
            tool_counts[tool_id] = tool_counts.get(tool_id, 0) + 1
        
        return {
            'total_tools': len(self.registered_tools),
            'total_calls': len(self.tool_call_history),
            'tool_usage': tool_counts,
            'most_used': max(tool_counts.items(), key=lambda x: x[1])[0] if tool_counts else None
        }

