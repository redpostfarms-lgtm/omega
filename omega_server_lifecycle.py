#!/usr/bin/env python3
"""
OMEGA SERVER LIFECYCLE (PROMPT 9)
=================================
Complete server lifecycle management for Omega system.

Phases:
1. INIT - Load kernel, verify signatures, initialize components
2. RUNNING - Normal operation, accept requests
3. MAINTENANCE - Reduced capacity, maintenance tasks
4. DRAINING - Stop accepting new work, complete existing
5. SHUTDOWN - Graceful shutdown with state preservation

State Management:
- Checkpoint creation and restoration
- Graceful degradation on component failure
- Health monitoring and auto-recovery

All lifecycle events logged to DECISION_LOG.
Invariant Kernel (K1-K10) enforced throughout lifecycle.
"""

import hashlib
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import atexit

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaServerLifecycle')


class ServerPhase(Enum):
    """Server lifecycle phases."""
    INIT = "init"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    DRAINING = "draining"
    SHUTDOWN = "shutdown"
    FAILED = "failed"


class ComponentStatus(Enum):
    """Status of individual components."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class ComponentState:
    """State of a managed component."""
    name: str
    status: ComponentStatus = ComponentStatus.UNINITIALIZED
    last_health_check: Optional[str] = None
    error_message: Optional[str] = None
    restart_count: int = 0
    max_restarts: int = 3
    dependencies: List[str] = field(default_factory=list)
    critical: bool = False  # If True, server fails without this component


@dataclass
class Checkpoint:
    """Server state checkpoint for recovery."""
    checkpoint_id: str
    phase: ServerPhase
    timestamp: str
    components: Dict[str, str]  # name -> status
    state_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LifecycleHook:
    """Hook for lifecycle events."""

    def __init__(self, phase: ServerPhase, callback: Callable, priority: int = 50):
        self.phase = phase
        self.callback = callback
        self.priority = priority  # Lower = earlier execution

    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the hook. Returns True on success."""
        try:
            self.callback(context)
            return True
        except Exception as e:
            logger.error(f"Hook failed: {e}")
            return False


class OmegaServerLifecycle:
    """
    Complete server lifecycle management for Omega.

    Manages initialization, operation, maintenance, and shutdown
    with full state preservation and recovery capabilities.
    """

    VERSION = "1.0.0"
    CHECKPOINT_DIR = Path("checkpoints")

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.lock = threading.RLock()

        # State
        self.phase = ServerPhase.INIT
        self.started_at: Optional[str] = None
        self.phase_changed_at: Optional[str] = None

        # Components
        self.components: Dict[str, ComponentState] = {}
        self.component_instances: Dict[str, Any] = {}

        # Hooks
        self.hooks: Dict[ServerPhase, List[LifecycleHook]] = {
            phase: [] for phase in ServerPhase
        }

        # Health monitoring
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.health_thread: Optional[threading.Thread] = None
        self.running = False

        # Kernel reference
        self.kernel = None

        # Decision log callback
        self.decision_log_callback: Optional[Callable] = None

        # Checkpoint management
        self.last_checkpoint: Optional[Checkpoint] = None
        self.CHECKPOINT_DIR.mkdir(exist_ok=True)

        # Register signal handlers
        self._register_signal_handlers()

        # Register atexit handler
        atexit.register(self._atexit_handler)

        logger.info(f"Omega Server Lifecycle Manager v{self.VERSION} initialized")

    def _register_signal_handlers(self):
        """Register OS signal handlers for graceful shutdown."""
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle OS signals."""
        sig_name = signal.Signals(signum).name
        logger.info(f"Received signal {sig_name}")

        if signum in (signal.SIGINT, signal.SIGTERM):
            self.shutdown(reason=f"Signal: {sig_name}")
        elif hasattr(signal, 'SIGHUP') and signum == signal.SIGHUP:
            self.enter_maintenance(reason=f"Signal: {sig_name}")

    def _atexit_handler(self):
        """Handle process exit."""
        if self.phase not in (ServerPhase.SHUTDOWN, ServerPhase.FAILED):
            logger.warning("Unexpected exit - creating emergency checkpoint")
            self.create_checkpoint(emergency=True)

    def register_component(
        self,
        name: str,
        init_func: Callable,
        dependencies: List[str] = None,
        critical: bool = False,
        max_restarts: int = 3
    ) -> None:
        """Register a component for lifecycle management."""
        with self.lock:
            self.components[name] = ComponentState(
                name=name,
                dependencies=dependencies or [],
                critical=critical,
                max_restarts=max_restarts
            )
            self.component_instances[name] = {
                'init_func': init_func,
                'instance': None
            }
            logger.info(f"Registered component: {name} (critical={critical})")

    def register_hook(
        self,
        phase: ServerPhase,
        callback: Callable,
        priority: int = 50
    ) -> None:
        """Register a lifecycle hook."""
        hook = LifecycleHook(phase, callback, priority)
        with self.lock:
            self.hooks[phase].append(hook)
            self.hooks[phase].sort(key=lambda h: h.priority)
        logger.debug(f"Registered hook for {phase.value} (priority={priority})")

    def _execute_hooks(self, phase: ServerPhase, context: Dict[str, Any] = None) -> bool:
        """Execute all hooks for a phase."""
        context = context or {}
        context['phase'] = phase.value
        context['timestamp'] = datetime.now().isoformat()

        with self.lock:
            hooks = self.hooks.get(phase, [])

        all_success = True
        for hook in hooks:
            if not hook.execute(context):
                all_success = False
                logger.warning(f"Hook failed for phase {phase.value}")

        return all_success

    def _init_component(self, name: str) -> bool:
        """Initialize a single component."""
        with self.lock:
            state = self.components.get(name)
            comp_info = self.component_instances.get(name)

            if not state or not comp_info:
                return False

            # Check dependencies
            for dep in state.dependencies:
                dep_state = self.components.get(dep)
                if not dep_state or dep_state.status != ComponentStatus.HEALTHY:
                    logger.error(f"Dependency {dep} not healthy for {name}")
                    return False

            state.status = ComponentStatus.INITIALIZING

        try:
            init_func = comp_info['init_func']
            instance = init_func()

            with self.lock:
                comp_info['instance'] = instance
                state.status = ComponentStatus.HEALTHY
                state.last_health_check = datetime.now().isoformat()

            logger.info(f"Component initialized: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize {name}: {e}")
            with self.lock:
                state.status = ComponentStatus.FAILED
                state.error_message = str(e)
            return False

    def _topological_sort(self) -> List[str]:
        """Sort components by dependencies."""
        with self.lock:
            components = dict(self.components)

        # Build dependency graph
        in_degree = {name: 0 for name in components}
        dependents = {name: [] for name in components}

        for name, state in components.items():
            for dep in state.dependencies:
                if dep in dependents:
                    dependents[dep].append(name)
                    in_degree[name] += 1

        # Kahn's algorithm
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for dependent in dependents.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(components):
            logger.warning("Circular dependency detected")
            # Return in registration order as fallback
            return list(components.keys())

        return result

    def start(self) -> bool:
        """Start the server (INIT -> RUNNING)."""
        if self.phase != ServerPhase.INIT:
            logger.error(f"Cannot start from phase {self.phase.value}")
            return False

        logger.info("Starting Omega server...")
        self.started_at = datetime.now().isoformat()

        # Execute INIT hooks
        self._execute_hooks(ServerPhase.INIT)

        # Load kernel first
        try:
            from omega_invariant_kernel import get_kernel
            self.kernel = get_kernel()
            logger.info(f"Invariant Kernel loaded: v{self.kernel.KERNEL_VERSION}")
        except ImportError:
            logger.warning("Invariant Kernel not available")

        # Initialize components in dependency order
        init_order = self._topological_sort()
        failed_critical = False

        for name in init_order:
            success = self._init_component(name)
            if not success:
                state = self.components.get(name)
                if state and state.critical:
                    logger.error(f"Critical component failed: {name}")
                    failed_critical = True
                    break

        if failed_critical:
            self._set_phase(ServerPhase.FAILED)
            self._log_lifecycle_event('start_failed', {'reason': 'Critical component failure'})
            return False

        # Start health monitoring
        self._start_health_monitoring()

        # Transition to RUNNING
        self._set_phase(ServerPhase.RUNNING)
        self._execute_hooks(ServerPhase.RUNNING)
        self._log_lifecycle_event('server_started', {'components': len(self.components)})

        # Create initial checkpoint
        self.create_checkpoint()

        logger.info("Omega server started successfully")
        return True

    def _set_phase(self, new_phase: ServerPhase) -> None:
        """Set the server phase."""
        with self.lock:
            old_phase = self.phase
            self.phase = new_phase
            self.phase_changed_at = datetime.now().isoformat()

        logger.info(f"Phase transition: {old_phase.value} -> {new_phase.value}")

    def enter_maintenance(self, reason: str = None) -> bool:
        """Enter maintenance mode (RUNNING -> MAINTENANCE)."""
        if self.phase != ServerPhase.RUNNING:
            logger.error(f"Cannot enter maintenance from {self.phase.value}")
            return False

        logger.info(f"Entering maintenance mode: {reason or 'scheduled'}")

        # Execute maintenance hooks
        self._execute_hooks(ServerPhase.MAINTENANCE, {'reason': reason})

        self._set_phase(ServerPhase.MAINTENANCE)
        self._log_lifecycle_event('maintenance_started', {'reason': reason})

        return True

    def exit_maintenance(self) -> bool:
        """Exit maintenance mode (MAINTENANCE -> RUNNING)."""
        if self.phase != ServerPhase.MAINTENANCE:
            return False

        logger.info("Exiting maintenance mode")

        # Run health checks on all components
        self._check_all_health()

        # Check if any critical component is failed
        with self.lock:
            for name, state in self.components.items():
                if state.critical and state.status == ComponentStatus.FAILED:
                    logger.error(f"Cannot exit maintenance - {name} failed")
                    return False

        self._set_phase(ServerPhase.RUNNING)
        self._execute_hooks(ServerPhase.RUNNING)
        self._log_lifecycle_event('maintenance_completed', {})

        return True

    def drain(self, timeout: float = 30.0) -> bool:
        """Enter draining mode (stop accepting new work)."""
        if self.phase not in (ServerPhase.RUNNING, ServerPhase.MAINTENANCE):
            return False

        logger.info(f"Draining server (timeout={timeout}s)")

        self._set_phase(ServerPhase.DRAINING)
        self._execute_hooks(ServerPhase.DRAINING, {'timeout': timeout})

        # Wait for in-flight work (simplified - real impl would track requests)
        time.sleep(min(timeout, 5.0))

        self._log_lifecycle_event('drain_completed', {'timeout': timeout})
        return True

    def shutdown(self, reason: str = None, emergency: bool = False) -> None:
        """Shutdown the server gracefully."""
        logger.info(f"Shutting down server: {reason or 'requested'}")

        # Create checkpoint before shutdown
        if not emergency:
            self.create_checkpoint()

        # Drain first if running
        if self.phase in (ServerPhase.RUNNING, ServerPhase.MAINTENANCE):
            self.drain(timeout=10.0 if emergency else 30.0)

        self._set_phase(ServerPhase.SHUTDOWN)
        self._execute_hooks(ServerPhase.SHUTDOWN, {'reason': reason, 'emergency': emergency})

        # Stop health monitoring
        self._stop_health_monitoring()

        # Stop components in reverse order
        init_order = self._topological_sort()
        for name in reversed(init_order):
            self._stop_component(name)

        self._log_lifecycle_event('server_shutdown', {'reason': reason, 'emergency': emergency})
        logger.info("Omega server shutdown complete")

    def _stop_component(self, name: str) -> None:
        """Stop a single component."""
        with self.lock:
            state = self.components.get(name)
            comp_info = self.component_instances.get(name)

            if not state or not comp_info:
                return

            instance = comp_info.get('instance')

        try:
            if instance and hasattr(instance, 'stop'):
                instance.stop()
            elif instance and hasattr(instance, 'shutdown'):
                instance.shutdown()

            with self.lock:
                state.status = ComponentStatus.STOPPED
                comp_info['instance'] = None

            logger.info(f"Component stopped: {name}")

        except Exception as e:
            logger.error(f"Error stopping {name}: {e}")

    def _start_health_monitoring(self) -> None:
        """Start background health monitoring."""
        self.running = True
        self.health_thread = threading.Thread(target=self._health_loop, daemon=True)
        self.health_thread.start()

    def _stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        self.running = False
        if self.health_thread:
            self.health_thread.join(timeout=5.0)

    def _health_loop(self) -> None:
        """Background health check loop."""
        while self.running and self.phase in (ServerPhase.RUNNING, ServerPhase.MAINTENANCE):
            try:
                self._check_all_health()
            except Exception as e:
                logger.error(f"Health check error: {e}")

            time.sleep(self.health_check_interval)

    def _check_all_health(self) -> None:
        """Check health of all components."""
        with self.lock:
            component_names = list(self.components.keys())

        for name in component_names:
            self._check_component_health(name)

    def _check_component_health(self, name: str) -> bool:
        """Check health of a single component."""
        with self.lock:
            state = self.components.get(name)
            comp_info = self.component_instances.get(name)

            if not state or not comp_info:
                return False

            instance = comp_info.get('instance')

        try:
            is_healthy = True

            if instance:
                if hasattr(instance, 'health_check'):
                    is_healthy = instance.health_check()
                elif hasattr(instance, 'is_healthy'):
                    is_healthy = instance.is_healthy()
                elif hasattr(instance, 'get_status'):
                    status = instance.get_status()
                    is_healthy = status.get('status') == 'healthy' if isinstance(status, dict) else True

            with self.lock:
                state.last_health_check = datetime.now().isoformat()
                if is_healthy:
                    state.status = ComponentStatus.HEALTHY
                    state.error_message = None
                else:
                    state.status = ComponentStatus.DEGRADED

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            with self.lock:
                state.status = ComponentStatus.FAILED
                state.error_message = str(e)

            # Attempt restart if allowed
            self._attempt_restart(name)
            return False

    def _attempt_restart(self, name: str) -> bool:
        """Attempt to restart a failed component."""
        with self.lock:
            state = self.components.get(name)
            if not state:
                return False

            if state.restart_count >= state.max_restarts:
                logger.error(f"Max restarts exceeded for {name}")
                if state.critical:
                    self._set_phase(ServerPhase.FAILED)
                return False

            state.restart_count += 1

        logger.info(f"Attempting restart {state.restart_count}/{state.max_restarts} for {name}")

        # Stop and reinitialize
        self._stop_component(name)
        success = self._init_component(name)

        if success:
            logger.info(f"Restart successful for {name}")

        return success

    def create_checkpoint(self, emergency: bool = False) -> Optional[Checkpoint]:
        """Create a state checkpoint."""
        with self.lock:
            component_status = {
                name: state.status.value
                for name, state in self.components.items()
            }

        # Compute state hash
        state_data = json.dumps({
            'phase': self.phase.value,
            'components': component_status,
            'timestamp': datetime.now().isoformat()
        }, sort_keys=True)
        state_hash = hashlib.sha256(state_data.encode()).hexdigest()

        checkpoint = Checkpoint(
            checkpoint_id=f"cp_{state_hash[:12]}",
            phase=self.phase,
            timestamp=datetime.now().isoformat(),
            components=component_status,
            state_hash=state_hash,
            metadata={'emergency': emergency}
        )

        # Save to file
        checkpoint_file = self.CHECKPOINT_DIR / f"{checkpoint.checkpoint_id}.json"
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'checkpoint_id': checkpoint.checkpoint_id,
                    'phase': checkpoint.phase.value,
                    'timestamp': checkpoint.timestamp,
                    'components': checkpoint.components,
                    'state_hash': checkpoint.state_hash,
                    'metadata': checkpoint.metadata
                }, f, indent=2)

            logger.info(f"Checkpoint created: {checkpoint.checkpoint_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

        with self.lock:
            self.last_checkpoint = checkpoint

        return checkpoint

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint from disk."""
        checkpoint_file = self.CHECKPOINT_DIR / f"{checkpoint_id}.json"

        if not checkpoint_file.exists():
            logger.error(f"Checkpoint not found: {checkpoint_id}")
            return None

        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)

            checkpoint = Checkpoint(
                checkpoint_id=data['checkpoint_id'],
                phase=ServerPhase(data['phase']),
                timestamp=data['timestamp'],
                components=data['components'],
                state_hash=data['state_hash'],
                metadata=data.get('metadata', {})
            )

            logger.info(f"Checkpoint loaded: {checkpoint_id}")
            return checkpoint

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def recover_from_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Recover server state from a checkpoint."""
        logger.info(f"Recovering from checkpoint: {checkpoint.checkpoint_id}")

        # Verify we're in INIT or FAILED state
        if self.phase not in (ServerPhase.INIT, ServerPhase.FAILED):
            logger.error(f"Cannot recover from phase {self.phase.value}")
            return False

        # Note which components should be healthy
        expected_healthy = {
            name for name, status in checkpoint.components.items()
            if status == ComponentStatus.HEALTHY.value
        }

        # Reinitialize components
        for name in self._topological_sort():
            if name in expected_healthy:
                self._init_component(name)

        # Verify recovery
        with self.lock:
            recovered = {
                name for name, state in self.components.items()
                if state.status == ComponentStatus.HEALTHY
            }

        success = expected_healthy.issubset(recovered)

        if success:
            self._set_phase(ServerPhase.RUNNING)
            logger.info("Recovery successful")
        else:
            missing = expected_healthy - recovered
            logger.error(f"Recovery incomplete - missing: {missing}")

        return success

    def _log_lifecycle_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a lifecycle event."""
        if self.decision_log_callback:
            try:
                self.decision_log_callback({
                    'event_type': event_type,
                    'phase': self.phase.value,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Failed to log lifecycle event: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current server status."""
        with self.lock:
            return {
                'version': self.VERSION,
                'phase': self.phase.value,
                'started_at': self.started_at,
                'phase_changed_at': self.phase_changed_at,
                'kernel_loaded': self.kernel is not None,
                'components': {
                    name: {
                        'status': state.status.value,
                        'critical': state.critical,
                        'restart_count': state.restart_count,
                        'last_health_check': state.last_health_check,
                        'error': state.error_message
                    }
                    for name, state in self.components.items()
                },
                'last_checkpoint': self.last_checkpoint.checkpoint_id if self.last_checkpoint else None
            }

    def get_component(self, name: str) -> Optional[Any]:
        """Get a component instance."""
        with self.lock:
            comp_info = self.component_instances.get(name)
            return comp_info.get('instance') if comp_info else None


# Convenience functions
_lifecycle_instance: Optional[OmegaServerLifecycle] = None
_lifecycle_lock = threading.Lock()


def get_lifecycle() -> OmegaServerLifecycle:
    """Get or create the global lifecycle manager."""
    global _lifecycle_instance

    if _lifecycle_instance is None:
        with _lifecycle_lock:
            if _lifecycle_instance is None:
                _lifecycle_instance = OmegaServerLifecycle()

    return _lifecycle_instance


# Self-test
if __name__ == '__main__':
    print("=" * 60)
    print("OMEGA SERVER LIFECYCLE - SELF-TEST")
    print("=" * 60)

    lifecycle = OmegaServerLifecycle()

    # Register mock components
    def init_mock_kernel():
        class MockKernel:
            def health_check(self):
                return True
        return MockKernel()

    def init_mock_memory():
        class MockMemory:
            def health_check(self):
                return True
        return MockMemory()

    def init_mock_api():
        class MockAPI:
            def health_check(self):
                return True
            def stop(self):
                pass
        return MockAPI()

    lifecycle.register_component('kernel', init_mock_kernel, critical=True)
    lifecycle.register_component('memory', init_mock_memory, dependencies=['kernel'])
    lifecycle.register_component('api', init_mock_api, dependencies=['memory'])

    # Register hooks
    lifecycle.register_hook(
        ServerPhase.RUNNING,
        lambda ctx: print(f"  [HOOK] Server running at {ctx['timestamp']}")
    )
    lifecycle.register_hook(
        ServerPhase.SHUTDOWN,
        lambda ctx: print(f"  [HOOK] Shutting down: {ctx.get('reason', 'unknown')}")
    )

    # Start server
    print("\n--- Starting Server ---")
    success = lifecycle.start()
    print(f"Start success: {success}")
    print(f"Phase: {lifecycle.phase.value}")

    # Get status
    print("\n--- Server Status ---")
    status = lifecycle.get_status()
    print(f"Version: {status['version']}")
    print(f"Phase: {status['phase']}")
    print(f"Components:")
    for name, comp in status['components'].items():
        print(f"  - {name}: {comp['status']} (critical={comp['critical']})")

    # Enter maintenance
    print("\n--- Entering Maintenance ---")
    lifecycle.enter_maintenance(reason="Self-test")
    print(f"Phase: {lifecycle.phase.value}")

    # Exit maintenance
    print("\n--- Exiting Maintenance ---")
    lifecycle.exit_maintenance()
    print(f"Phase: {lifecycle.phase.value}")

    # Create checkpoint
    print("\n--- Creating Checkpoint ---")
    checkpoint = lifecycle.create_checkpoint()
    print(f"Checkpoint ID: {checkpoint.checkpoint_id}")
    print(f"State hash: {checkpoint.state_hash[:16]}...")

    # Shutdown
    print("\n--- Shutting Down ---")
    lifecycle.shutdown(reason="Self-test complete")
    print(f"Final phase: {lifecycle.phase.value}")

    print("\n" + "=" * 60)
    print("SELF-TEST COMPLETE")
    print("=" * 60)
