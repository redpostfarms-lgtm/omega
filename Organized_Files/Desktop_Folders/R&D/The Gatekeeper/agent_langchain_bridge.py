# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent LangChain Bridge
Bridge between Gatekeeper agents and LangChain framework
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
LANGCHAIN_DIR = ARCHIVED / 'langchain_bridge'
LANGCHAIN_DIR.mkdir(parents=True, exist_ok=True)

class AgentLangChainBridge:
    """Bridge between Gatekeeper agents and LangChain."""
    
    def __init__(self):
        self.wrapped_agents = {}
        self.langchain_tools = []
    
    def create_langchain_agent(self, agent_name: str, agent_function: Callable, description: str = "") -> Optional[Any]:
        """
        Create a LangChain agent from a Gatekeeper agent function.
        
        Args:
            agent_name: Name of the agent
            agent_function: Function that implements the agent
            description: Description of the agent
        
        Returns:
            LangChain agent wrapper (or None if LangChain not available)
        """
        try:
            # Try to import LangChain (optional dependency)
            from langchain.agents import AgentExecutor, create_structured_chat_agent
            from langchain.tools import Tool
            from langchain.llms.base import BaseLLM
            
            # Wrap the agent function as a LangChain tool
            tool = Tool(
                name=agent_name,
                func=agent_function,
                description=description or f"Agent: {agent_name}"
            )
            
            self.langchain_tools.append(tool)
            
            # Create agent wrapper
            agent_wrapper = {
                'name': agent_name,
                'tool': tool,
                'function': agent_function,
                'type': 'langchain_tool'
            }
            
            self.wrapped_agents[agent_name] = agent_wrapper
            
            return agent_wrapper
            
        except ImportError:
            # LangChain not available - create simple wrapper
            agent_wrapper = {
                'name': agent_name,
                'function': agent_function,
                'description': description,
                'type': 'simple_wrapper',
                'note': 'LangChain not installed - using simple wrapper'
            }
            
            self.wrapped_agents[agent_name] = agent_wrapper
            
            return agent_wrapper
    
    def wrap_existing_agent(self, agent_instance: Any, agent_name: str) -> Dict[str, Any]:
        """
        Wrap an existing Gatekeeper agent instance for LangChain.
        
        Args:
            agent_instance: Existing agent instance
            agent_name: Name of the agent
        
        Returns:
            Wrapped agent dictionary
        """
        # Extract callable method (try common methods)
        agent_function = None
        
        if hasattr(agent_instance, 'process'):
            agent_function = agent_instance.process
        elif hasattr(agent_instance, 'get_response'):
            agent_function = agent_instance.get_response
        elif hasattr(agent_instance, '__call__'):
            agent_function = agent_instance
        elif hasattr(agent_instance, 'run'):
            agent_function = agent_instance.run
        
        if agent_function:
            return self.create_langchain_agent(agent_name, agent_function, f"Wrapped agent: {agent_name}")
        else:
            # Create a generic wrapper
            def generic_wrapper(*args, **kwargs):
                if hasattr(agent_instance, 'process'):
                    return agent_instance.process(*args, **kwargs)
                elif hasattr(agent_instance, 'get_response'):
                    return agent_instance.get_response(*args, **kwargs)
                else:
                    return str(agent_instance)
            
            return self.create_langchain_agent(agent_name, generic_wrapper, f"Generic wrapper for {agent_name}")
    
    def get_langchain_tools(self) -> List[Any]:
        """Get list of LangChain tools."""
        return [wrapper['tool'] for wrapper in self.wrapped_agents.values() if 'tool' in wrapper]
    
    def list_wrapped_agents(self) -> List[str]:
        """List all wrapped agents."""
        return list(self.wrapped_agents.keys())
    
    def get_wrapped_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get a wrapped agent by name."""
        return self.wrapped_agents.get(agent_name)
    
    def call_wrapped_agent(self, agent_name: str, *args, **kwargs) -> Any:
        """
        Call a wrapped agent.
        
        Args:
            agent_name: Name of the agent
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Agent result
        """
        if agent_name not in self.wrapped_agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        wrapper = self.wrapped_agents[agent_name]
        
        if 'function' in wrapper:
            return wrapper['function'](*args, **kwargs)
        elif 'tool' in wrapper:
            # LangChain tool
            return wrapper['tool'].run(*args, **kwargs)
        
        raise RuntimeError(f"Agent {agent_name} has no callable function")

