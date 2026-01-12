#!/usr/bin/env python3
"""
Omega API Wrapper for Visual Studio Application
================================================
Python API wrapper that exposes Omega Control Panel functionality
for use in Visual Studio C# WPF application.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from omega_control_panel import ControlPanel
    CONTROL_PANEL_AVAILABLE = True
except ImportError:
    CONTROL_PANEL_AVAILABLE = False

class OmegaAPI:
    """API wrapper for Omega Control Panel"""
    
    def __init__(self):
        if not CONTROL_PANEL_AVAILABLE:
            raise ImportError("omega_control_panel not available")
        
        self.panel = ControlPanel()
    
    def get_status(self) -> Dict[str, Any]:
        """Get control panel status"""
        return {
            "running": self.panel.running,
            "update_interval": self.panel.update_interval,
            "hardware_available": self.panel.hw_controller is not None,
            "integration_available": self.panel.integration_manager is not None
        }
    
    def get_file_list(self) -> List[str]:
        """Get list of important files"""
        return self.panel.important_files
    
    def get_integrated_systems(self) -> List[Dict[str, Any]]:
        """Get integrated systems information"""
        return [
            {
                "name": s.name,
                "status": s.status,
                "cpu_usage": s.cpu_usage,
                "temperature": s.temperature,
                "processing_power": s.processing_power
            }
            for s in self.panel.integrated_systems
        ]
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        notifications = list(self.panel.notifications)[-10:]
        return [
            {
                "message": n.message,
                "level": n.level,
                "timestamp": n.timestamp.isoformat()
            }
            for n in notifications
        ]
    
    def get_process_improvements(self) -> List[Dict[str, Any]]:
        """Get process improvements"""
        return [
            {
                "name": p.name,
                "current_percentage": p.current_percentage,
                "target_percentage": p.target_percentage,
                "priority": p.priority,
                "description": p.description
            }
            for p in self.panel.process_improvements[:10]
        ]
    
    def get_optional_processes(self) -> List[Dict[str, Any]]:
        """Get optional processes"""
        return [
            {
                "name": o.name,
                "description": o.description,
                "usefulness_score": o.usefulness_score,
                "category": o.category
            }
            for o in self.panel.optional_processes[:10]
        ]
    
    def update_data(self):
        """Update control panel data"""
        self.panel._update_integrated_systems()
        self.panel._scan_process_improvements()

# Create global instance for easy access
_omega_api_instance = None

def get_omega_api() -> OmegaAPI:
    """Get or create OmegaAPI instance"""
    global _omega_api_instance
    if _omega_api_instance is None:
        _omega_api_instance = OmegaAPI()
    return _omega_api_instance

if __name__ == "__main__":
    # Test the API
    try:
        api = OmegaAPI()
        print("Omega API initialized successfully!")
        print()
        print("Status:", api.get_status())
        print("File list:", len(api.get_file_list()), "files")
        print("Integrated systems:", len(api.get_integrated_systems()))
        print("Notifications:", len(api.get_notifications()))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
