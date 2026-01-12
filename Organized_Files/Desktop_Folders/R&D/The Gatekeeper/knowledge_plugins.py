# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Knowledge Plugins System
Plugin system for extensible knowledge management
"""

import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
PLUGINS_DIR = ARCHIVED / 'knowledge_plugins'
PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgePlugins:
    """Plugin system for knowledge management."""
    
    def __init__(self):
        self.registered_plugins = {}
        self.plugin_config_file = PLUGINS_DIR / 'plugin_config.json'
        self._load_config()
    
    def _load_config(self):
        """Load plugin configuration."""
        if self.plugin_config_file.exists():
            try:
                with open(self.plugin_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.registered_plugins = config.get('plugins', {})
            except:
                self.registered_plugins = {}
        else:
            self.registered_plugins = {}
    
    def _save_config(self):
        """Save plugin configuration."""
        config = {
            'plugins': self.registered_plugins,
            'updated_at': __import__('time').time()
        }
        with open(self.plugin_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def register_plugin(self, plugin_id: str, plugin_module: str, plugin_class: str, description: str = ""):
        """
        Register a plugin.
        
        Args:
            plugin_id: Unique plugin identifier
            plugin_module: Module path (e.g., 'knowledge_tags')
            plugin_class: Class name (e.g., 'KnowledgeTags')
            description: Plugin description
        """
        self.registered_plugins[plugin_id] = {
            'module': plugin_module,
            'class': plugin_class,
            'description': description,
            'status': 'registered',
            'loaded': False
        }
        self._save_config()
    
    def load_plugin(self, plugin_id: str) -> Optional[Any]:
        """
        Load a plugin module.
        
        Args:
            plugin_id: Plugin identifier
        
        Returns:
            Plugin instance or None
        """
        if plugin_id not in self.registered_plugins:
            return None
        
        plugin_info = self.registered_plugins[plugin_id]
        
        try:
            module = importlib.import_module(plugin_info['module'])
            plugin_class = getattr(module, plugin_info['class'])
            plugin_instance = plugin_class()
            
            plugin_info['loaded'] = True
            plugin_info['instance'] = plugin_instance
            self._save_config()
            
            return plugin_instance
        except Exception as e:
            plugin_info['error'] = str(e)
            plugin_info['loaded'] = False
            self._save_config()
            return None
    
    def execute_plugin(self, plugin_id: str, method: str, *args, **kwargs) -> Any:
        """
        Execute a plugin method.
        
        Args:
            plugin_id: Plugin identifier
            method: Method name to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Method result
        """
        if plugin_id not in self.registered_plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        plugin_info = self.registered_plugins[plugin_id]
        
        # Load plugin if not loaded
        if not plugin_info.get('loaded', False) or 'instance' not in plugin_info:
            instance = self.load_plugin(plugin_id)
            if not instance:
                raise RuntimeError(f"Failed to load plugin {plugin_id}")
        else:
            instance = plugin_info['instance']
        
        # Call method
        if hasattr(instance, method):
            method_func = getattr(instance, method)
            return method_func(*args, **kwargs)
        else:
            raise AttributeError(f"Plugin {plugin_id} has no method {method}")
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins."""
        return self.registered_plugins.copy()
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin."""
        return self.registered_plugins.get(plugin_id)

