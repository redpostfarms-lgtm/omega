#!/usr/bin/env python3
"""
Gatekeeper-Omega Integration Bridge
===================================
Unified integration layer connecting:
- Gatekeeper security & threat detection
- Omega AI voice system
- Control panel web interface
- System automation & scheduling

This bridge ensures all components work cohesively.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import threading
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GatekeeperOmegaBridge')


class SystemStatus(Enum):
    """System health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class GatekeeperOmegaBridge:
    """
    Main integration bridge connecting all system components.
    Provides unified API for security, voice, UI, and automation.
    """
    
    def __init__(self):
        """Initialize the bridge and all subsystems."""
        self.status = SystemStatus.OFFLINE
        self.components = {}
        self.errors = []
        self.lock = threading.RLock()
        self.initialized_at = datetime.now()
        
        logger.info("Initializing Gatekeeper-Omega Bridge...")
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components with error handling."""
        components_to_init = [
            ('gatekeeper_integration', self._init_gatekeeper),
            ('omega_voice', self._init_omega_voice),
            ('control_panel', self._init_control_panel),
            ('wazuh_siem', self._init_wazuh),
        ]
        
        successful = 0
        for name, init_func in components_to_init:
            try:
                logger.info(f"Initializing {name}...")
                component = init_func()
                if component:
                    self.components[name] = component
                    logger.info(f"Successfully initialized {name}")
                    successful += 1
                else:
                    logger.warning(f"{name} initialization returned None")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}", exc_info=True)
                self.errors.append({
                    'component': name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Determine overall status
        if successful >= 2:  # At least 2 components must work
            self.status = SystemStatus.HEALTHY
            logger.info("Bridge initialization SUCCESSFUL")
        elif successful >= 1:
            self.status = SystemStatus.WARNING
            logger.warning("Bridge initialization PARTIAL - some components failed")
        else:
            self.status = SystemStatus.CRITICAL
            logger.critical("Bridge initialization FAILED - no components available")
    
    def _init_gatekeeper(self) -> Optional[Any]:
        """Initialize Gatekeeper security module."""
        try:
            from gatekeeper_integration_module import GatekeeperIntegration
            gk = GatekeeperIntegration()
            return gk
        except ImportError:
            logger.warning("gatekeeper_integration_module not available")
            return None
        except Exception as e:
            logger.error(f"Gatekeeper initialization error: {e}")
            raise
    
    def _init_omega_voice(self) -> Optional[Any]:
        """Initialize Omega voice system."""
        try:
            # Try full brain (most features)
            try:
                import omega_full_brain
                return omega_full_brain
            except ImportError:
                # Fallback to simple final
                import omega_simple_final
                return omega_simple_final
        except ImportError:
            logger.warning("Omega voice modules not available")
            return None
        except Exception as e:
            logger.error(f"Omega voice initialization error: {e}")
            raise
    
    def _init_control_panel(self) -> Optional[Any]:
        """Initialize Control Panel web interface."""
        try:
            from omega_control_panel_web import Flask
            # We don't need to initialize the full Flask app here, just check availability
            return True
        except ImportError:
            logger.warning("Control Panel (Flask) not available")
            return None
        except Exception as e:
            logger.error(f"Control Panel initialization error: {e}")
            raise
    
    def _init_wazuh(self) -> Optional[Any]:
        """Initialize Wazuh SIEM integration."""
        try:
            from gatekeeper_wazuh_integration import WazuhIntegration
            # Don't instantiate yet as it requires server config
            return WazuhIntegration
        except ImportError:
            logger.warning("Wazuh integration not available")
            return None
        except Exception as e:
            logger.error(f"Wazuh initialization error: {e}")
            raise
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        with self.lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'status': self.status.value,
                'uptime_seconds': (datetime.now() - self.initialized_at).total_seconds(),
                'components': {
                    name: {
                        'available': component is not None,
                        'type': type(component).__name__ if component else 'None'
                    }
                    for name, component in self.components.items()
                },
                'errors': self.errors[-10:],  # Last 10 errors
                'error_count': len(self.errors)
            }
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a specific component by name."""
        with self.lock:
            return self.components.get(name)
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status from Gatekeeper."""
        gk = self.get_component('gatekeeper_integration')
        if not gk:
            return {'error': 'Gatekeeper not available', 'status': 'unknown'}
        
        try:
            # Get threats from integrated security systems
            status = gk.get_status()
            metrics = gk.get_system_metrics()
            
            return {
                'gatekeeper_status': status,
                'system_metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def execute_voice_command(self, command: str) -> Dict[str, Any]:
        """Execute a voice command through integrated systems."""
        try:
            # Log the command
            logger.info(f"Executing voice command: {command}")
            
            # Route to appropriate subsystem
            if 'security' in command.lower() or 'threat' in command.lower():
                gk = self.get_component('gatekeeper_integration')
                if gk:
                    return {
                        'command': command,
                        'system': 'gatekeeper',
                        'status': 'routed'
                    }
            
            # Default: execute in Omega voice system
            omega = self.get_component('omega_voice')
            if omega:
                return {
                    'command': command,
                    'system': 'omega',
                    'status': 'routed'
                }
            
            return {'command': command, 'status': 'no_handler'}
        
        except Exception as e:
            logger.error(f"Error executing voice command: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        logger.info("Running system diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_health': self.get_system_health(),
            'security_status': self.get_security_status(),
            'component_details': {}
        }
        
        # Component-specific diagnostics
        for name, component in self.components.items():
            try:
                if hasattr(component, 'get_status'):
                    diagnostics['component_details'][name] = component.get_status()
                else:
                    diagnostics['component_details'][name] = {
                        'type': type(component).__name__,
                        'available': True
                    }
            except Exception as e:
                diagnostics['component_details'][name] = {
                    'error': str(e),
                    'type': type(component).__name__
                }
        
        logger.info(f"Diagnostics complete. Status: {diagnostics['system_health']['status']}")
        return diagnostics
    
    def save_diagnostics(self, filename: str = 'system_diagnostics.json'):
        """Save diagnostics report to file."""
        try:
            diagnostics = self.run_diagnostics()
            with open(filename, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            logger.info(f"Diagnostics saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving diagnostics: {e}")
            return None


# Global bridge instance
_bridge_instance = None
_bridge_lock = threading.Lock()


def get_bridge() -> GatekeeperOmegaBridge:
    """Get or create the global bridge instance."""
    global _bridge_instance
    
    if _bridge_instance is None:
        with _bridge_lock:
            if _bridge_instance is None:
                _bridge_instance = GatekeeperOmegaBridge()
    
    return _bridge_instance


def bridge_component(component_name: str):
    """Decorator to automatically use bridge component in functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bridge = get_bridge()
            component = bridge.get_component(component_name)
            if not component:
                raise RuntimeError(f"Component '{component_name}' not available")
            # Pass component as first argument
            return func(component, *args, **kwargs)
        return wrapper
    return decorator


# Main execution example
if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("GATEKEEPER-OMEGA BRIDGE - SYSTEM CHECK")
    print("=" * 60)
    
    # Initialize bridge
    bridge = get_bridge()
    
    # Print health status
    health = bridge.get_system_health()
    print(f"\nStatus: {health['status']}")
    print(f"Components: {len(health['components'])} loaded")
    print(f"Errors: {health['error_count']}")
    
    # Run diagnostics
    print("\nRunning full diagnostics...")
    diagnostics = bridge.run_diagnostics()
    
    print(f"\nHealth Check: {diagnostics['system_health']['status']}")
    print(f"Security Status: OK" if 'gatekeeper_status' in diagnostics['security_status'] else "Security: PENDING")
    
    # Save report
    report_file = bridge.save_diagnostics()
    if report_file:
        print(f"\nReport saved to: {report_file}")
    
    print("\n" + "=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if bridge.status == SystemStatus.HEALTHY else 1)
