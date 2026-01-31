#!/usr/bin/env python3
"""
OMEGA UNIFIED SYSTEM BRIDGE
===========================
The central integration layer for the Omega system.

Omega is the unified AI system (formerly Gatekeeper + Omega merged).
All components operate under Omega's Invariant Kernel (K1-K10).

Components integrated:
- Security & threat detection (formerly Gatekeeper)
- Omega AI voice system
- Control panel web interface
- System automation & scheduling
- Invariant Kernel enforcement

This bridge ensures all components work cohesively while
respecting the immutable constraints of the Invariant Kernel.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import threading
from functools import wraps

# Import the Invariant Kernel
try:
    from omega_invariant_kernel import (
        get_kernel, InvariantKernel, kernel_enforced,
        KernelViolationError, ShardKernelInterface
    )
    KERNEL_AVAILABLE = True
except ImportError:
    KERNEL_AVAILABLE = False
    get_kernel = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaSystemBridge')


class SystemStatus(Enum):
    """System health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class OmegaSystemBridge:
    """
    Main integration bridge connecting all Omega system components.
    Provides unified API for security, voice, UI, and automation.

    All actions are validated against the Invariant Kernel (K1-K10).
    """

    # System identity
    SYSTEM_NAME = "Omega"
    SYSTEM_VERSION = "2.0.0"  # Version 2 = unified system with kernel

    def __init__(self):
        """Initialize the bridge and all subsystems including the kernel."""
        self.status = SystemStatus.OFFLINE
        self.components = {}
        self.errors = []
        self.lock = threading.RLock()
        self.initialized_at = datetime.now()

        # Initialize Invariant Kernel first (highest priority)
        self.kernel = None
        if KERNEL_AVAILABLE:
            try:
                self.kernel = get_kernel()
                logger.info(f"Invariant Kernel v{self.kernel.KERNEL_VERSION} loaded")
            except Exception as e:
                logger.error(f"Failed to load Invariant Kernel: {e}")
        else:
            logger.warning("Invariant Kernel not available - operating without constraints")

        logger.info(f"Initializing {self.SYSTEM_NAME} System Bridge v{self.SYSTEM_VERSION}...")
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components with error handling."""
        components_to_init = [
            ('invariant_kernel', self._init_kernel),
            ('security_module', self._init_security),  # Renamed from gatekeeper
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
        # Kernel is CRITICAL - without it, system operates in degraded mode
        kernel_loaded = 'invariant_kernel' in self.components and self.components['invariant_kernel']

        if successful >= 2 and kernel_loaded:
            self.status = SystemStatus.HEALTHY
            logger.info(f"{self.SYSTEM_NAME} Bridge initialization SUCCESSFUL")
        elif successful >= 2:
            self.status = SystemStatus.WARNING
            logger.warning(f"{self.SYSTEM_NAME} Bridge initialization PARTIAL - kernel not loaded")
        elif successful >= 1:
            self.status = SystemStatus.WARNING
            logger.warning(f"{self.SYSTEM_NAME} Bridge initialization PARTIAL - some components failed")
        else:
            self.status = SystemStatus.CRITICAL
            logger.critical(f"{self.SYSTEM_NAME} Bridge initialization FAILED - no components available")
    
    def _init_kernel(self) -> Optional[Any]:
        """Initialize the Invariant Kernel - highest priority component."""
        if self.kernel:
            return self.kernel
        if KERNEL_AVAILABLE:
            try:
                self.kernel = get_kernel()
                return self.kernel
            except Exception as e:
                logger.error(f"Kernel initialization error: {e}")
                raise
        return None

    def _init_security(self) -> Optional[Any]:
        """Initialize security module (formerly Gatekeeper)."""
        try:
            from gatekeeper_integration_module import GatekeeperIntegration
            security = GatekeeperIntegration()
            return security
        except ImportError:
            logger.warning("Security integration module not available")
            return None
        except Exception as e:
            logger.error(f"Security module initialization error: {e}")
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
            # Include kernel status
            kernel_status = None
            if self.kernel:
                kernel_status = {
                    'version': self.kernel.KERNEL_VERSION,
                    'signature': self.kernel.KERNEL_SIGNATURE,
                    'constraints_loaded': len(self.kernel.get_all_constraints()),
                    'violation_count': self.kernel.get_violation_count()
                }

            return {
                'system_name': self.SYSTEM_NAME,
                'system_version': self.SYSTEM_VERSION,
                'timestamp': datetime.now().isoformat(),
                'status': self.status.value,
                'uptime_seconds': (datetime.now() - self.initialized_at).total_seconds(),
                'kernel': kernel_status,
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
        """Get security status from security module."""
        security = self.get_component('security_module')
        if not security:
            return {'error': 'Security module not available', 'status': 'unknown'}

        try:
            # Get threats from integrated security systems
            status = security.get_status()
            metrics = security.get_system_metrics()

            return {
                'security_status': status,
                'system_metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            return {'error': str(e), 'status': 'error'}

    def validate_action(self, action: Dict[str, Any]) -> tuple[bool, List[Any]]:
        """Validate an action against the Invariant Kernel (K1-K10)."""
        if not self.kernel:
            logger.warning("Kernel not available - action not validated")
            return True, []  # Allow but warn

        return self.kernel.validate_action(action)

    def create_shard_interface(self, shard_id: str) -> Optional['ShardKernelInterface']:
        """Create a kernel interface for a child shard."""
        if not self.kernel:
            logger.warning("Cannot create shard interface - kernel not available")
            return None

        return ShardKernelInterface(shard_id, self.kernel)
    
    def execute_voice_command(self, command: str) -> Dict[str, Any]:
        """Execute a voice command through integrated systems.

        All commands are validated against the Invariant Kernel before execution.
        """
        try:
            # Log the command
            logger.info(f"Executing voice command: {command}")

            # Validate against kernel first
            action = {'type': 'voice_command', 'command': command}
            is_valid, violations = self.validate_action(action)

            if not is_valid:
                violation_ids = [v.constraint_id for v in violations]
                logger.warning(f"Voice command blocked by kernel: {violation_ids}")
                return {
                    'command': command,
                    'status': 'blocked',
                    'reason': f'Kernel violation: {violation_ids}'
                }

            # Route to appropriate subsystem
            if 'security' in command.lower() or 'threat' in command.lower():
                security = self.get_component('security_module')
                if security:
                    return {
                        'command': command,
                        'system': 'security',
                        'status': 'routed'
                    }

            # Default: execute in Omega voice system
            omega = self.get_component('omega_voice')
            if omega:
                return {
                    'command': command,
                    'system': 'omega_voice',
                    'status': 'routed'
                }

            return {'command': command, 'status': 'no_handler'}

        except Exception as e:
            logger.error(f"Error executing voice command: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        logger.info(f"Running {self.SYSTEM_NAME} system diagnostics...")

        diagnostics = {
            'system_name': self.SYSTEM_NAME,
            'system_version': self.SYSTEM_VERSION,
            'timestamp': datetime.now().isoformat(),
            'system_health': self.get_system_health(),
            'security_status': self.get_security_status(),
            'kernel_export': self.kernel.export_kernel() if self.kernel else None,
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


def get_bridge() -> OmegaSystemBridge:
    """Get or create the global Omega bridge instance."""
    global _bridge_instance

    if _bridge_instance is None:
        with _bridge_lock:
            if _bridge_instance is None:
                _bridge_instance = OmegaSystemBridge()

    return _bridge_instance


# Alias for backward compatibility
def get_omega() -> OmegaSystemBridge:
    """Get the Omega system bridge (preferred method)."""
    return get_bridge()


# Legacy alias - deprecated
GatekeeperOmegaBridge = OmegaSystemBridge


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


def kernel_validated(func):
    """Decorator to validate function calls against the Invariant Kernel."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        bridge = get_bridge()

        # Build action from function call
        action = {
            'type': f'function:{func.__name__}',
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        }

        is_valid, violations = bridge.validate_action(action)
        if not is_valid:
            violation_ids = [v.constraint_id for v in violations]
            raise RuntimeError(f"Action blocked by Invariant Kernel: {violation_ids}")

        return func(*args, **kwargs)
    return wrapper


# Main execution example
if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("OMEGA UNIFIED SYSTEM - BRIDGE CHECK")
    print("=" * 70)

    # Initialize bridge
    bridge = get_omega()

    # Print system info
    print(f"\nSystem: {bridge.SYSTEM_NAME} v{bridge.SYSTEM_VERSION}")

    # Print health status
    health = bridge.get_system_health()
    print(f"Status: {health['status']}")
    print(f"Components: {len(health['components'])} loaded")
    print(f"Errors: {health['error_count']}")

    # Kernel status
    if health.get('kernel'):
        kernel = health['kernel']
        print(f"\n--- INVARIANT KERNEL ---")
        print(f"Version: {kernel['version']}")
        print(f"Signature: {kernel['signature']}")
        print(f"Constraints: {kernel['constraints_loaded']} loaded (K1-K10)")
        print(f"Violations: {kernel['violation_count']}")
    else:
        print("\n[WARN] Invariant Kernel not loaded!")

    # Run diagnostics
    print("\nRunning full diagnostics...")
    diagnostics = bridge.run_diagnostics()

    print(f"\nHealth Check: {diagnostics['system_health']['status']}")
    print(f"Security Status: {'OK' if 'security_status' in diagnostics['security_status'] else 'PENDING'}")

    # Save report
    report_file = bridge.save_diagnostics()
    if report_file:
        print(f"\nReport saved to: {report_file}")

    print("\n" + "=" * 70)

    # Exit with appropriate code
    sys.exit(0 if bridge.status == SystemStatus.HEALTHY else 1)
