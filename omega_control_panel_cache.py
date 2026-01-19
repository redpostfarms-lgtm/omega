"""
Omega Control Panel Cache
==========================
Caches control panel data for faster loading.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class CachedPanelData:
    """Cached control panel data"""
    timestamp: str
    cpu_usage: float
    cpu_temperature: float
    memory_usage: float
    disk_usage: float
    fan_speed: int
    rgb_enabled: bool
    rgb_color: str
    notifications: list
    integrated_systems: list
    process_improvements: list
    optional_processes: list

class ControlPanelCache:
    """Manages control panel cache for fast loading"""
    
    def __init__(self, cache_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.cache_file = cache_file or (self.base_dir / ".omega_panel_cache.json")
        self.cache_data: Optional[Dict[str, Any]] = None
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached data from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                return self.cache_data
        except Exception as e:
            print(f"[Cache] Failed to load cache: {e}")
        return None
    
    def save_cache(self, data: Dict[str, Any]) -> bool:
        """Save data to cache file"""
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[Cache] Failed to save cache: {e}")
            return False
    
    def get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get cached data (loads if not already loaded)"""
        if self.cache_data is None:
            self.load_cache()
        return self.cache_data
    
    def clear_cache(self) -> bool:
        """Clear cache file"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self.cache_data = None
            return True
        except Exception as e:
            print(f"[Cache] Failed to clear cache: {e}")
            return False
