"""
Omega Configuration System - Optimized
========================================
Consolidated configuration system to avoid redundancy.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

class OmegaConfig:
    """Optimized consolidated configuration system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.config_file = self.base_dir / "omega_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load consolidated configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        config = {}
        
        search_config_file = self.base_dir / "omega_search_config.json"
        if search_config_file.exists():
            try:
                with open(search_config_file, 'r', encoding='utf-8') as f:
                    config['search'] = json.load(f)
            except:
                pass
        
        autonomy_config_file = self.base_dir / "omega_autonomous_config.json"
        if autonomy_config_file.exists():
            try:
                with open(autonomy_config_file, 'r', encoding='utf-8') as f:
                    config['autonomy'] = json.load(f)
            except:
                pass
        
        if not config:
            config = {
                "version": "2.0",
                "timestamp": datetime.now().isoformat(),
                "search": {
                    "automatic_deep_search": True,
                    "search_depth": "deepest",
                    "search_breadth": "widest",
                    "use_all_resources": True,
                    "resources": {
                        "web_search": True,
                        "codebase_search": True,
                        "quantum_scrub": True,
                        "software_repositories": True,
                        "documentation": True,
                        "stack_overflow": True,
                        "github": True,
                        "research_papers": True,
                        "official_docs": True
                    }
                },
                "autonomy": {
                    "enabled": True,
                    "auto_implement": True,
                    "auto_create_files": True,
                    "auto_edit_files": True,
                    "require_confirmation": False
                }
            }
        
        self.save_config(config)
        return config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save consolidated configuration"""
        if config is None:
            config = self.config
        
        config['version'] = config.get('version', '2.0')
        config['timestamp'] = datetime.now().isoformat()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration"""
        return self.config.get('search', {})
    
    def get_autonomy_config(self) -> Dict[str, Any]:
        """Get autonomy configuration"""
        return self.config.get('autonomy', {})

def get_config() -> OmegaConfig:
    """Get global config instance"""
    if not hasattr(get_config, '_instance'):
        get_config._instance = OmegaConfig()
    return get_config._instance

if __name__ == "__main__":
    config = OmegaConfig()
    print("Omega Configuration System - Optimized")
    print("=" * 50)
    print(f"Config file: {config.config_file}")
    print(f"Version: {config.config.get('version', 'unknown')}")
    print(f"Search config loaded: {'search' in config.config}")
    print(f"Autonomy config loaded: {'autonomy' in config.config}")
