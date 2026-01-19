"""
Omega Automatic Deep Search Configuration
==========================================
Configures automatic deep, wide, broad searches using all available resources.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

try:
    from OMEGA_CONFIG_OPTIMIZED import OmegaConfig, get_config
    CONFIG_SYSTEM_AVAILABLE = True
except ImportError:
    CONFIG_SYSTEM_AVAILABLE = False

class AutomaticDeepSearch:
    """Automatic deep search configuration and handler"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        if CONFIG_SYSTEM_AVAILABLE:
            self.config_manager = get_config()
            self.config = self.config_manager.get_search_config()
        else:
            self.config_file = self.base_dir / "omega_search_config.json"
            self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load search configuration (legacy fallback)"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
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
            },
            "efficiency_optimization": True,
            "multi_source_validation": True,
            "cross_reference": True
        }
    
    def save_config(self):
        """Save search configuration"""
        if CONFIG_SYSTEM_AVAILABLE and hasattr(self, 'config_manager'):
            search_config = self.config_manager.get_search_config()
            search_config.update(self.config)
            self.config_manager.config['search'] = search_config
            self.config_manager.save_config()
        else:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
    
    def get_search_parameters(self) -> Dict[str, Any]:
        """Get current search parameters"""
        config = self.config_manager.get_search_config() if CONFIG_SYSTEM_AVAILABLE and hasattr(self, 'config_manager') else self.config
        return {
            "mode": "automatic_deep_search",
            "depth": config.get("search_depth", "deepest"),
            "breadth": config.get("search_breadth", "widest"),
            "use_all_resources": config.get("use_all_resources", True),
            "resources": config.get("resources", {}),
            "efficiency": config.get("efficiency_optimization", True),
            "multi_source": config.get("multi_source_validation", True),
            "cross_reference": config.get("cross_reference", True)
        }

def configure_automatic_deep_search():
    """Configure automatic deep search parameters"""
    
    config = {
        "automatic_deep_search": True,
        "search_depth": "deepest",  # deepest, deep, medium, shallow
        "search_breadth": "widest",  # widest, wide, medium, narrow
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
            "official_docs": True,
            "reddit": True,
            "discord_communities": False,
            "twitter": False
        },
        "efficiency_optimization": True,
        "multi_source_validation": True,
        "cross_reference": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    config_file = Path(__file__).parent / "omega_search_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("[OK] Automatic deep search configuration saved")
    return config

if __name__ == "__main__":
    config = configure_automatic_deep_search()
    print("\nConfiguration:")
    print(json.dumps(config, indent=2))
