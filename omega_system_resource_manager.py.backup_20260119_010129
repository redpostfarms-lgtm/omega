#!/usr/bin/env python3
"""
Omega System Resource Manager
==============================
Global resource manager for Omega system-wide optimization.
Manages CPU, GPU, and RAM resources across all Omega components.
"""

import sys
from pathlib import Path

# Import the resource manager
try:
    from omega_resource_manager import ResourceManager, GradualLoader, get_resource_manager
    RESOURCE_MANAGER_AVAILABLE = True
except ImportError:
    RESOURCE_MANAGER_AVAILABLE = False
    print("[Warning] Resource manager not available")

# Global resource manager instance
_system_resource_manager = None
_system_gradual_loader = None

def get_system_resource_manager() -> ResourceManager:
    """Get global system resource manager instance"""
    global _system_resource_manager
    if _system_resource_manager is None:
        if RESOURCE_MANAGER_AVAILABLE:
            _system_resource_manager = get_resource_manager()
        else:
            # Return None if not available
            return None
    return _system_resource_manager

def get_system_gradual_loader() -> GradualLoader:
    """Get global system gradual loader instance"""
    global _system_gradual_loader
    if _system_gradual_loader is None:
        resource_manager = get_system_resource_manager()
        if resource_manager and RESOURCE_MANAGER_AVAILABLE:
            from omega_resource_manager import GradualLoader
            _system_gradual_loader = GradualLoader(resource_manager)
        else:
            return None
    return _system_gradual_loader

def initialize_system_resources():
    """Initialize system resource management"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        print("[Omega System] Resource manager initialized")
        status = resource_manager.get_resource_status()
        print(f"[Omega System] Performance profile: {status['performance_profile']}")
        if status['gpu']:
            print(f"[Omega System] GPU available: {status['gpu']['device_name']}")
        return True
    return False

def load_component_gradually(component_name: str, load_func, *args, **kwargs):
    """Load a component gradually using the system gradual loader"""
    gradual_loader = get_system_gradual_loader()
    if gradual_loader:
        return gradual_loader.load_component(component_name, load_func, *args, **kwargs)
    else:
        # Fallback to immediate load
        return load_func(*args, **kwargs)

def get_optimal_workers(task_complexity: str = "medium") -> int:
    """Get optimal number of workers for parallel processing"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        return resource_manager.get_optimal_workers(task_complexity)
    return 1

def should_use_multiprocessing(task_complexity: str = "medium") -> bool:
    """Determine if multiprocessing should be used"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        return resource_manager.should_use_multiprocessing(task_complexity)
    return False

def get_resource_status():
    """Get current resource status"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        return resource_manager.get_resource_status()
    return None

def save_system_patterns():
    """Save system loading patterns"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        base_dir = Path(__file__).parent.absolute()
        patterns_file = base_dir / ".omega_system_loading_patterns.json"
        resource_manager.save_loading_patterns(patterns_file)

def load_system_patterns():
    """Load system loading patterns"""
    resource_manager = get_system_resource_manager()
    if resource_manager:
        base_dir = Path(__file__).parent.absolute()
        patterns_file = base_dir / ".omega_system_loading_patterns.json"
        resource_manager.load_loading_patterns(patterns_file)

def main():
    """Test system resource manager"""
    print("=" * 80)
    print(" " * 20 + "OMEGA SYSTEM RESOURCE MANAGER")
    print("=" * 80)
    print()
    
    if initialize_system_resources():
        status = get_resource_status()
        if status:
            print("System Resource Status:")
            print(f"  CPU: {status['cpu']['count']} cores, {status['cpu']['usage_percent']:.1f}% usage")
            print(f"  RAM: {status['ram']['used_gb']:.1f}/{status['ram']['total_gb']:.1f} GB ({status['ram']['percent']:.1f}%)")
            if status['gpu']:
                print(f"  GPU: {status['gpu']['device_name']}")
            print(f"  Profile: {status['performance_profile']}")
            print()
            print("System resource manager ready!")
        else:
            print("Resource status unavailable")
    else:
        print("Resource manager not available")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
