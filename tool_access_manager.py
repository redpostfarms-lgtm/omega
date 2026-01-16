#!/usr/bin/env python3
"""
Tool Access Manager - Smart tool access and configuration layer
Provides on-demand tool access with automatic fallback and caching
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Mapping, Type
from functools import lru_cache
import logging
import tempfile

# Import safe path manager
try:
    from safe_path_manager import SafePathManager
except ImportError:
    SafePathManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolAccessManager:
    """Manages on-demand access to tools"""
    
    def __init__(self, auto_tool_manager_path: str = 'auto_tool_manager.py'):
        self.auto_tool_manager = auto_tool_manager_path
        self.tool_cache: Dict[str, str] = {}
        self.tool_paths: Dict[str, str] = {}
        self.safe_pm: Optional[Type] = SafePathManager
        self.load_cached_tools()
    
    def load_cached_tools(self):
        """Load cached tool information"""
        cache_file = Path('tool_cache.json')
        if cache_file.exists():
            try:
                if self.safe_pm:
                    data = self.safe_pm.safe_read_json(cache_file)
                    if data and isinstance(data, dict):
                        self.tool_cache = data.get('tools', {}) or {}
                        self.tool_paths = data.get('paths', {}) or {}
                else:
                    with open(cache_file) as f:
                        data = json.load(f)
                        self.tool_cache = data.get('tools', {}) or {}
                        self.tool_paths = data.get('paths', {}) or {}
                logger.info(f"Loaded {len(self.tool_cache)} cached tools")
            except Exception as e:
                logger.warning(f"Failed to load tool cache: {e}")
                self.tool_cache = {}
                self.tool_paths = {}
    
    def save_cached_tools(self):
        """Save tool cache for future use"""
        cache: Dict[str, Dict[str, str]] = {
            'tools': self.tool_cache,
            'paths': self.tool_paths
        }
        try:
            cache_file = Path('tool_cache.json')
            if self.safe_pm:
                self.safe_pm.safe_write_json(cache, cache_file)
            else:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tool cache: {e}")
    
    @lru_cache(maxsize=32)
    def get_tool_path(self, tool_name: str) -> Optional[str]:
        """Get the path to a tool executable"""
        if tool_name in self.tool_paths:
            return self.tool_paths[tool_name]
        
        # Try to find it in PATH
        import shutil
        path = shutil.which(tool_name)
        if path:
            self.tool_paths[tool_name] = path
            self.save_cached_tools()
            return path
        
        return None
    
    def access_tool(self, tool_name: str, auto_ensure: bool = True) -> Optional[str]:
        """
        Access a tool and ensure it's available
        Returns the path to the tool if available
        """
        logger.info(f"Accessing tool: {tool_name}")
        
        # Check cache first
        if tool_name in self.tool_cache:
            return self.tool_cache[tool_name]
        
        # Try to get path
        tool_path = self.get_tool_path(tool_name)
        if tool_path:
            self.tool_cache[tool_name] = tool_path
            logger.info(f"✓ Tool available: {tool_name} at {tool_path}")
            return tool_path
        
        # If not found and auto_ensure is True, try to ensure it
        if auto_ensure:
            logger.info(f"Tool not found, attempting auto-ensure: {tool_name}")
            if self.auto_ensure_tool(tool_name):
                tool_path = self.get_tool_path(tool_name)
                if tool_path:
                    self.tool_cache[tool_name] = tool_path
                    return tool_path
        
        logger.warning(f"✗ Tool not accessible: {tool_name}")
        return None
    
    def auto_ensure_tool(self, tool_name: str) -> bool:
        """Trigger auto tool manager to ensure tool availability"""
        try:
            result = subprocess.run(
                [sys.executable, self.auto_tool_manager, '--ensure', tool_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to auto-ensure {tool_name}: {e}")
            return False
    
    def access_tools_for_project(self, project_path: str) -> Dict[str, str]:
        """Access all required tools for a project"""
        logger.info(f"Accessing tools for project: {project_path}")
        
        tools_available: Dict[str, str] = {}
        
        # Detect project type
        project_path_obj = Path(project_path)
        
        required_tools = []
        
        if (project_path_obj / 'pom.xml').exists():
            required_tools = ['java', 'maven']
        elif any((project_path_obj / f).exists() for f in ['build.gradle', 'build.gradle.kts', 'gradlew']):
            required_tools = ['java', 'gradle']
        elif (project_path_obj / 'package.json').exists():
            required_tools = ['node', 'npm']
        
        for tool in required_tools:
            path = self.access_tool(tool, auto_ensure=True)
            if path:
                tools_available[tool] = path
        
        self.save_cached_tools()
        return tools_available
    
    def run_tool(self, tool_name: str, args: Optional[List[str]] = None, auto_ensure: bool = True) -> Optional[subprocess.CompletedProcess[str]]:
        """
        Run a tool with automatic access management
        """
        tool_path = self.access_tool(tool_name, auto_ensure=auto_ensure)
        if not tool_path:
            logger.error(f"Cannot run {tool_name}: tool not accessible")
            return None
        
        command = [tool_path] + (args or [])
        logger.info(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=False,
                text=True
            )
            return result
        except Exception as e:
            logger.error(f"Error running {tool_name}: {e}")
            return None


class SmartToolRouter:
    """Smart tool selection and routing"""
    
    def __init__(self, access_manager: ToolAccessManager):
        self.access_manager = access_manager
        self.tool_equivalents = {
            'build': ['gradle', 'maven'],
            'java_compiler': ['gradle', 'maven'],
            'test_runner': ['gradle', 'maven']
        }
    
    def route_build_command(self, project_path: str) -> Optional[str]:
        """Route build command to appropriate tool"""
        project_path_obj = Path(project_path)
        
        if (project_path_obj / 'pom.xml').exists():
            return self.access_manager.access_tool('maven')
        elif any((project_path_obj / f).exists() for f in ['build.gradle', 'build.gradle.kts']):
            return self.access_manager.access_tool('gradle')
        elif (project_path_obj / 'gradlew').exists():
            return str(project_path_obj / 'gradlew')
        
        return None
    
    def route_test_command(self, project_path: str) -> Optional[str]:
        """Route test command to appropriate tool"""
        return self.route_build_command(project_path)


def get_tool_manager() -> ToolAccessManager:
    """Get or create global tool manager instance"""
    global _tool_manager
    if '_tool_manager' not in globals():
        _tool_manager = ToolAccessManager()
    return _tool_manager


# Convenient functions for common use cases
def ensure_java(version: str = '21') -> bool:
    """Ensure Java is available"""
    manager = get_tool_manager()
    return manager.access_tool('java', auto_ensure=True) is not None


def ensure_build_tool(project_path: str) -> Optional[str]:
    """Ensure build tool is available for project"""
    manager = get_tool_manager()
    router = SmartToolRouter(manager)
    return router.route_build_command(project_path)


def run_build(project_path: str, *args: str) -> Optional[subprocess.CompletedProcess[str]]:
    """Automatically build a project with appropriate tool"""
    manager = get_tool_manager()
    router = SmartToolRouter(manager)
    
    tool = router.route_build_command(project_path)
    if not tool:
        logger.error("Could not determine build tool for project")
        return None
    
    # Determine build command based on tool
    if 'maven' in tool:
        build_args = ['clean', 'install'] + list(args)
    elif 'gradle' in tool:
        build_args = ['build'] + list(args)
    else:
        build_args = list(args)
    
    os.chdir(project_path)
    return manager.run_tool(tool, build_args)


if __name__ == '__main__':
    manager = get_tool_manager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--access':
            tool = sys.argv[2] if len(sys.argv) > 2 else None
            if tool:
                path = manager.access_tool(tool)
                print(f"{tool}: {path}")
        
        elif command == '--project':
            project = sys.argv[2] if len(sys.argv) > 2 else '.'
            tools = manager.access_tools_for_project(project)
            print(json.dumps(tools, indent=2))
        
        elif command == '--run':
            tool = sys.argv[2] if len(sys.argv) > 2 else None
            args = sys.argv[3:] if len(sys.argv) > 3 else []
            if tool:
                manager.run_tool(tool, args)
    else:
        manager.load_cached_tools()
        print("Tool Cache:")
        print(json.dumps(manager.tool_cache, indent=2))
