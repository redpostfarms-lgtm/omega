#!/usr/bin/env python3
"""
OMEGA UNIFIED CORE
==================
The central orchestrator for the Omega AI system.

This module integrates all ten prompts into a cohesive system:
- Prompt 1: Invariant Kernel (K1-K10) - omega_invariant_kernel.py
- Prompt 2: Subordinate Shard Protocol - OMEGA_SHARD_PROMPT.md
- Prompt 3: Policy Signing & Verification - omega_policy_signing.py
- Prompt 4: SQLite Memory Partitioning - omega_memory_partition.py
- Prompt 5: Decision Log Integrity - omega_memory_partition.py
- Prompt 6: WebSocket Hive Interface - omega_websocket_hive.py
- Prompt 7: Promotion Engine - omega_promotion_engine.py
- Prompt 8: Automated Simulation Runner - omega_simulation_runner.py
- Prompt 9: Server Lifecycle - omega_server_lifecycle.py
- Prompt 10: Operator Tools - omega_operator_tools.py

The Unified Core ensures:
1. Kernel is loaded and enforced before any operation
2. Policy manifest is verified on startup (Safe Halt if failed)
3. All memory operations go through partitioned stores
4. All decisions are logged to the hash-chained audit log
5. Shards inherit constraints through ShardKernelInterface
6. WebSocket hive communication is signed and verified
7. Data promotion follows strict gate checks
8. Automated simulations validate system behavior
9. Server lifecycle is properly managed
10. Operators have appropriate tools and audit trails
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import threading

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OMEGA_CORE - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaUnifiedCore')

# =================================================================
# IMPORT OMEGA COMPONENTS (ALL 10 PROMPTS)
# =================================================================

# Import Invariant Kernel (Prompt 1)
try:
    from omega_invariant_kernel import (
        get_kernel, InvariantKernel, kernel_enforced,
        KernelViolationError, ShardKernelInterface
    )
    KERNEL_AVAILABLE = True
    logger.info("Invariant Kernel module loaded (Prompt 1)")
except ImportError as e:
    KERNEL_AVAILABLE = False
    logger.error(f"Failed to load Invariant Kernel: {e}")

# Import Policy Signing (Prompt 3)
try:
    from omega_policy_signing import (
        get_signing, OmegaPolicySigning, SystemMode,
        requires_normal_mode, VerificationResult
    )
    SIGNING_AVAILABLE = True
    logger.info("Policy Signing module loaded (Prompt 3)")
except ImportError as e:
    SIGNING_AVAILABLE = False
    logger.error(f"Failed to load Policy Signing: {e}")

# Import Memory Partition (Prompts 4 & 5)
try:
    from omega_memory_partition import (
        get_memory, OmegaMemoryPartition, StoreType, TrustLevel
    )
    MEMORY_AVAILABLE = True
    logger.info("Memory Partition module loaded (Prompts 4 & 5)")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.error(f"Failed to load Memory Partition: {e}")

# Import WebSocket Hive (Prompt 6)
try:
    from omega_websocket_hive import (
        OmegaWebSocketHive, HiveMessage, MessageType,
        TrustLevel as HiveTrustLevel
    )
    HIVE_AVAILABLE = True
    logger.info("WebSocket Hive module loaded (Prompt 6)")
except ImportError as e:
    HIVE_AVAILABLE = False
    logger.error(f"Failed to load WebSocket Hive: {e}")

# Import Promotion Engine (Prompt 7)
try:
    from omega_promotion_engine import (
        OmegaPromotionEngine, PromotionSource, PromotionStatus
    )
    PROMOTION_AVAILABLE = True
    logger.info("Promotion Engine module loaded (Prompt 7)")
except ImportError as e:
    PROMOTION_AVAILABLE = False
    logger.error(f"Failed to load Promotion Engine: {e}")

# Import Simulation Runner (Prompt 8)
try:
    from omega_simulation_runner import (
        OmegaSimulationRunner, SimulationType, SimulationStatus
    )
    SIMULATION_AVAILABLE = True
    logger.info("Simulation Runner module loaded (Prompt 8)")
except ImportError as e:
    SIMULATION_AVAILABLE = False
    logger.error(f"Failed to load Simulation Runner: {e}")

# Import Server Lifecycle (Prompt 9)
try:
    from omega_server_lifecycle import (
        OmegaServerLifecycle, ServerPhase, get_lifecycle
    )
    LIFECYCLE_AVAILABLE = True
    logger.info("Server Lifecycle module loaded (Prompt 9)")
except ImportError as e:
    LIFECYCLE_AVAILABLE = False
    logger.error(f"Failed to load Server Lifecycle: {e}")

# Import Operator Tools (Prompt 10)
try:
    from omega_operator_tools import (
        OmegaOperatorTools, OperatorRole, ActionCategory
    )
    OPERATOR_AVAILABLE = True
    logger.info("Operator Tools module loaded (Prompt 10)")
except ImportError as e:
    OPERATOR_AVAILABLE = False
    logger.error(f"Failed to load Operator Tools: {e}")

# Import System Bridge
try:
    from gatekeeper_omega_bridge import get_omega, OmegaSystemBridge
    BRIDGE_AVAILABLE = True
    logger.info("System Bridge module loaded")
except ImportError as e:
    BRIDGE_AVAILABLE = False
    logger.error(f"Failed to load System Bridge: {e}")

# Import Pure Python Omega System (Alternative implementation with Ed25519)
try:
    from omega_system import (
        OmegaSystem as PureOmegaSystem,
        generate_ed25519_root_key, generate_ecdsa_root_key,
        sign_manifest, verify_manifest,
        OmegaMemoryDB, PromotionEngine as PurePromotionEngine,
        WebSocketNodeManager, SimulationRunner as PureSimulationRunner,
        SafeHaltMode, HIGH_ASSURANCE_MODE,
        StoreType as PureStoreType, TrustLevel as PureTrustLevel,
        MessageType as PureMessageType, LifecyclePhase
    )
    PURE_SYSTEM_AVAILABLE = True
    logger.info("Pure Python Omega System loaded (Ed25519 + ECDSA fallback)")
except ImportError as e:
    PURE_SYSTEM_AVAILABLE = False
    logger.warning(f"Pure Python Omega System not available: {e}")


class OmegaStatus(Enum):
    """Overall Omega system status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    SAFE_HALT = "safe_halt"      # Policy verification failed
    DEGRADED = "degraded"        # Some components missing
    MAINTENANCE = "maintenance"   # Maintenance mode
    DRAINING = "draining"        # Draining for shutdown
    SHUTDOWN = "shutdown"
    ERROR = "error"


@dataclass
class ComponentStatus:
    """Status of a single component"""
    name: str
    prompt_number: int
    available: bool
    initialized: bool
    version: str
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'prompt': self.prompt_number,
            'available': self.available,
            'initialized': self.initialized,
            'version': self.version,
            'errors': self.errors
        }


class OmegaUnifiedCore:
    """
    The Omega Unified Core - central orchestrator for all 10 prompts.

    Initialization Order (per Prompt 9 - Server Lifecycle):
    1. Load Invariant Kernel (K1-K10) - CRITICAL
    2. Load Policy Signing & Verify Manifest
    3. Initialize Memory Partition (LAW, FACT, CONTEXT, EXPLORATION, HIVE, DECISION_LOG)
    4. Initialize WebSocket Hive Interface
    5. Initialize Promotion Engine
    6. Initialize Simulation Runner
    7. Initialize Server Lifecycle Manager
    8. Initialize Operator Tools
    9. Initialize System Bridge
    10. Enter operational mode (or Safe Halt)
    """

    VERSION = "2.0.0"
    SYSTEM_NAME = "Omega"

    def __init__(self,
                 verify_on_start: bool = True,
                 memory_db: str = "omega_memory.db",
                 manifest_path: str = "omega_manifest.json",
                 websocket_host: str = "0.0.0.0",
                 websocket_port: int = 8765,
                 start_services: bool = False):
        """
        Initialize the Omega Unified Core.

        Args:
            verify_on_start: Whether to verify policy manifest on startup
            memory_db: Path to SQLite memory database
            manifest_path: Path to policy manifest
            websocket_host: Host for WebSocket hive server
            websocket_port: Port for WebSocket hive server
            start_services: Whether to start background services
        """
        self.status = OmegaStatus.INITIALIZING
        self._lock = threading.RLock()
        self.initialized_at = datetime.now()

        # Component instances (all 10 prompts)
        self.kernel: Optional[InvariantKernel] = None           # Prompt 1
        self.signing: Optional[OmegaPolicySigning] = None       # Prompt 3
        self.memory: Optional[OmegaMemoryPartition] = None      # Prompts 4 & 5
        self.hive: Optional[OmegaWebSocketHive] = None          # Prompt 6
        self.promotion: Optional[OmegaPromotionEngine] = None   # Prompt 7
        self.simulation: Optional[OmegaSimulationRunner] = None # Prompt 8
        self.lifecycle: Optional[OmegaServerLifecycle] = None   # Prompt 9
        self.operator: Optional[OmegaOperatorTools] = None      # Prompt 10
        self.bridge: Optional[OmegaSystemBridge] = None         # Integration
        self.pure_system: Optional[PureOmegaSystem] = None     # Pure Python fallback

        # Pure Python cryptographic keys (from omega_system.py)
        self.ed25519_sk: Optional[bytes] = None
        self.ed25519_pk: Optional[bytes] = None
        self.ecdsa_sk = None
        self.ecdsa_pk = None
        self.signed_manifest: Optional[Dict[str, Any]] = None

        # Component status tracking
        self.components: Dict[str, ComponentStatus] = {}
        self.initialization_errors: List[str] = []

        # Configuration
        self._verify_on_start = verify_on_start
        self._memory_db = memory_db
        self._manifest_path = manifest_path
        self._websocket_host = websocket_host
        self._websocket_port = websocket_port
        self._start_services = start_services

        logger.info(f"Omega Unified Core v{self.VERSION} initializing (10 prompts)...")

        # Run initialization sequence
        self._initialize()

    def _initialize(self):
        """Run the full initialization sequence (Prompt 9 compliant)"""
        try:
            # Step 1: Initialize Kernel (CRITICAL - must succeed)
            self._init_kernel()

            # Step 2: Initialize Policy Signing & Verify
            self._init_signing()

            # Step 3: Initialize Memory Partition (with SQLite WAL)
            self._init_memory()

            # Step 4: Initialize WebSocket Hive Interface
            self._init_hive()

            # Step 5: Initialize Promotion Engine
            self._init_promotion()

            # Step 6: Initialize Simulation Runner
            self._init_simulation()

            # Step 7: Initialize Server Lifecycle
            self._init_lifecycle()

            # Step 8: Initialize Operator Tools
            self._init_operator()

            # Step 9: Initialize System Bridge
            self._init_bridge()

            # Step 10: Initialize Pure Python System (fallback/alternative)
            self._init_pure_system()

            # Determine final status
            self._determine_status()

            # Log initialization to memory
            if self.memory:
                self._log_initialization()

            # Start background services if requested
            if self._start_services and self.status == OmegaStatus.RUNNING:
                self._start_background_services()

        except Exception as e:
            logger.critical(f"Initialization failed: {e}")
            self.status = OmegaStatus.ERROR
            self.initialization_errors.append(str(e))
            # Speak-Up (K9) - Report the failure
            self._speak_up(f"CRITICAL: Initialization failed - {e}")

    def _init_kernel(self):
        """Initialize the Invariant Kernel (K1-K10) - Prompt 1"""
        status = ComponentStatus(
            name="Invariant Kernel",
            prompt_number=1,
            available=KERNEL_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if KERNEL_AVAILABLE:
            try:
                self.kernel = get_kernel()
                status.initialized = True
                status.version = self.kernel.KERNEL_VERSION
                logger.info(f"Invariant Kernel v{self.kernel.KERNEL_VERSION} initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Kernel initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.error("Invariant Kernel module not available - CRITICAL")

        self.components['kernel'] = status

    def _init_signing(self):
        """Initialize Policy Signing and verify manifest - Prompt 3"""
        status = ComponentStatus(
            name="Policy Signing",
            prompt_number=3,
            available=SIGNING_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if SIGNING_AVAILABLE:
            try:
                self.signing = get_signing()
                self.signing.manifest_path = Path(self._manifest_path)

                # Load keys
                self.signing.load_keys()

                # Verify manifest on startup if requested
                if self._verify_on_start:
                    if self.signing.verify_on_startup():
                        status.initialized = True
                        status.version = self.signing.MANIFEST_VERSION
                        logger.info("Policy manifest verified - NORMAL mode")
                    else:
                        status.errors.append("Manifest verification failed - SAFE HALT")
                        logger.critical("Policy verification FAILED - entering SAFE HALT")
                        self.status = OmegaStatus.SAFE_HALT
                        self._speak_up("SAFE HALT: Policy verification failed")
                else:
                    status.initialized = True
                    status.version = self.signing.MANIFEST_VERSION
                    logger.warning("Skipping policy verification (not recommended)")

            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Signing initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Policy Signing module not available")

        self.components['signing'] = status

    def _init_memory(self):
        """Initialize Memory Partition - Prompts 4 & 5"""
        status = ComponentStatus(
            name="Memory Partition",
            prompt_number=4,
            available=MEMORY_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if MEMORY_AVAILABLE:
            try:
                # Don't initialize if in Safe Halt
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("Memory partition skipped - SAFE HALT mode")
                else:
                    self.memory = OmegaMemoryPartition(self._memory_db)
                    status.initialized = True
                    status.version = self.memory.LAW_VERSION
                    logger.info("Memory Partition initialized (SQLite WAL mode)")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Memory initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Memory Partition module not available")

        self.components['memory'] = status

    def _init_hive(self):
        """Initialize WebSocket Hive Interface - Prompt 6"""
        status = ComponentStatus(
            name="WebSocket Hive",
            prompt_number=6,
            available=HIVE_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if HIVE_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("WebSocket Hive skipped - SAFE HALT mode")
                else:
                    self.hive = OmegaWebSocketHive(
                        host=self._websocket_host,
                        port=self._websocket_port
                    )
                    status.initialized = True
                    status.version = "1.0.0"
                    logger.info(f"WebSocket Hive initialized (wss://{self._websocket_host}:{self._websocket_port})")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Hive initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("WebSocket Hive module not available")

        self.components['hive'] = status

    def _init_promotion(self):
        """Initialize Promotion Engine - Prompt 7"""
        status = ComponentStatus(
            name="Promotion Engine",
            prompt_number=7,
            available=PROMOTION_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if PROMOTION_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("Promotion Engine skipped - SAFE HALT mode")
                else:
                    # Pass memory partition for FACT_STORE writes
                    self.promotion = OmegaPromotionEngine(
                        memory_partition=self.memory,
                        decision_log_callback=self._log_decision_callback
                    )
                    status.initialized = True
                    status.version = "1.0.0"
                    logger.info("Promotion Engine initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Promotion Engine initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Promotion Engine module not available")

        self.components['promotion'] = status

    def _init_simulation(self):
        """Initialize Simulation Runner - Prompt 8"""
        status = ComponentStatus(
            name="Simulation Runner",
            prompt_number=8,
            available=SIMULATION_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if SIMULATION_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("Simulation Runner skipped - SAFE HALT mode")
                else:
                    self.simulation = OmegaSimulationRunner(memory_partition=self.memory)
                    status.initialized = True
                    status.version = "1.0.0"
                    logger.info("Simulation Runner initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Simulation Runner initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Simulation Runner module not available")

        self.components['simulation'] = status

    def _init_lifecycle(self):
        """Initialize Server Lifecycle - Prompt 9"""
        status = ComponentStatus(
            name="Server Lifecycle",
            prompt_number=9,
            available=LIFECYCLE_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if LIFECYCLE_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("Server Lifecycle skipped - SAFE HALT mode")
                else:
                    self.lifecycle = OmegaServerLifecycle()
                    self.lifecycle.decision_log_callback = self._log_decision_callback
                    status.initialized = True
                    status.version = self.lifecycle.VERSION
                    logger.info("Server Lifecycle initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Server Lifecycle initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Server Lifecycle module not available")

        self.components['lifecycle'] = status

    def _init_operator(self):
        """Initialize Operator Tools - Prompt 10"""
        status = ComponentStatus(
            name="Operator Tools",
            prompt_number=10,
            available=OPERATOR_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if OPERATOR_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    # Operator tools SHOULD be available in Safe Halt for recovery
                    self.operator = OmegaOperatorTools(
                        lifecycle=self.lifecycle,
                        memory=self.memory
                    )
                    status.initialized = True
                    status.version = self.operator.VERSION
                    logger.info("Operator Tools initialized (SAFE HALT mode)")
                else:
                    self.operator = OmegaOperatorTools(
                        lifecycle=self.lifecycle,
                        memory=self.memory
                    )
                    status.initialized = True
                    status.version = self.operator.VERSION
                    logger.info("Operator Tools initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Operator Tools initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Operator Tools module not available")

        self.components['operator'] = status

    def _init_bridge(self):
        """Initialize System Bridge"""
        status = ComponentStatus(
            name="System Bridge",
            prompt_number=0,  # Integration component
            available=BRIDGE_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if BRIDGE_AVAILABLE:
            try:
                # Don't initialize if in Safe Halt
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("System Bridge skipped - SAFE HALT mode")
                else:
                    self.bridge = get_omega()
                    status.initialized = True
                    status.version = self.bridge.SYSTEM_VERSION
                    logger.info("System Bridge initialized")
            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Bridge initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("System Bridge module not available")

        self.components['bridge'] = status

    def _init_pure_system(self):
        """Initialize Pure Python Omega System (Ed25519 + ECDSA fallback)"""
        status = ComponentStatus(
            name="Pure Python System",
            prompt_number=0,  # Alternative implementation
            available=PURE_SYSTEM_AVAILABLE,
            initialized=False,
            version="",
            errors=[]
        )

        if PURE_SYSTEM_AVAILABLE:
            try:
                if self.status == OmegaStatus.SAFE_HALT:
                    status.errors.append("Skipped - System in SAFE HALT mode")
                    logger.warning("Pure Python System skipped - SAFE HALT mode")
                else:
                    # Generate cryptographic keys
                    self.ed25519_sk, self.ed25519_pk = generate_ed25519_root_key()
                    logger.info(f"Ed25519 root key generated: {self.ed25519_pk.hex()[:32]}...")

                    if HIGH_ASSURANCE_MODE:
                        self.ecdsa_sk, self.ecdsa_pk = generate_ecdsa_root_key()
                        if self.ecdsa_sk:
                            logger.info("ECDSA P-256 key generated (HIGH_ASSURANCE_MODE)")
                        else:
                            logger.warning("ECDSA not available (cryptography library missing)")

                    # Create and sign manifest
                    manifest = {
                        "version": self.VERSION,
                        "kernel_version": self.kernel.KERNEL_VERSION if self.kernel else "N/A",
                        "boot_time": datetime.now().isoformat(),
                        "high_assurance_mode": HIGH_ASSURANCE_MODE if PURE_SYSTEM_AVAILABLE else False
                    }
                    self.signed_manifest = sign_manifest(manifest, self.ed25519_sk, self.ecdsa_sk)
                    logger.info(f"Manifest signed: {self.signed_manifest['manifest_hash'][:32]}...")

                    # Verify manifest
                    valid, msg = verify_manifest(self.signed_manifest, self.ed25519_pk, self.ecdsa_pk)
                    if valid:
                        status.initialized = True
                        status.version = "1.0.0"
                        logger.info(f"Pure Python System initialized (dual_signed: {self.signed_manifest.get('dual_signed', False)})")
                    else:
                        status.errors.append(f"Manifest verification failed: {msg}")
                        logger.error(f"Pure Python manifest verification failed: {msg}")

            except Exception as e:
                status.errors.append(str(e))
                logger.error(f"Pure Python System initialization failed: {e}")
        else:
            status.errors.append("Module not available")
            logger.warning("Pure Python Omega System module not available")

        self.components['pure_system'] = status

    def _determine_status(self):
        """Determine final system status based on component states"""
        if self.status == OmegaStatus.SAFE_HALT:
            return  # Already in safe halt

        kernel_ok = self.components.get('kernel', ComponentStatus('', 0, False, False, '', [])).initialized
        memory_ok = self.components.get('memory', ComponentStatus('', 0, False, False, '', [])).initialized

        # Count initialized components
        initialized_count = sum(1 for c in self.components.values() if c.initialized)
        total_count = len(self.components)

        if not kernel_ok:
            # Kernel is CRITICAL - without it we can't run
            self.status = OmegaStatus.ERROR
            logger.critical("CRITICAL: Kernel not available - system cannot operate")
            self._speak_up("CRITICAL: Kernel not available - system cannot operate safely")
        elif not memory_ok:
            self.status = OmegaStatus.DEGRADED
            logger.warning("System running in DEGRADED mode (memory not available)")
        elif initialized_count < total_count * 0.8:  # Less than 80% of components
            self.status = OmegaStatus.DEGRADED
            logger.warning(f"System running in DEGRADED mode ({initialized_count}/{total_count} components)")
        else:
            self.status = OmegaStatus.RUNNING
            logger.info(f"Omega system RUNNING ({initialized_count}/{total_count} components)")

    def _log_initialization(self):
        """Log initialization event to memory"""
        if not self.memory:
            return

        try:
            self.memory.add_fact(
                content={
                    'event': 'system_initialization',
                    'version': self.VERSION,
                    'status': self.status.value,
                    'components': {k: v.to_dict() for k, v in self.components.items()},
                    'timestamp': self.initialized_at.isoformat()
                },
                source='omega_core',
                confidence=1.0,
                verified_by='system'
            )
        except Exception as e:
            logger.error(f"Failed to log initialization: {e}")

    def _log_decision_callback(self, decision: Dict[str, Any]) -> None:
        """Callback for logging decisions from other components"""
        if not self.memory:
            return

        try:
            self.memory._log_decision(
                actor=decision.get('actor', 'unknown'),
                action_type=decision.get('action_type', 'unknown'),
                payload=decision
            )
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")

    def _speak_up(self, message: str):
        """K9: Speak-Up - Raise issues and concerns"""
        logger.warning(f"[SPEAK-UP] {message}")

        # Log to memory if available
        if self.memory:
            try:
                self.memory._log_decision('omega_core', 'speak_up', {
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass

    def _start_background_services(self):
        """Start background services (Prompt 9 compliant)"""
        logger.info("Starting background services...")

        # Start simulation scheduler (daily canary tests)
        if self.simulation:
            try:
                self.simulation.schedule_daily_run(hour=3, minute=0)
                self.simulation.start_scheduler()
                logger.info("Simulation scheduler started (daily at 03:00)")
            except Exception as e:
                logger.error(f"Failed to start simulation scheduler: {e}")

        # Note: WebSocket server would be started separately
        # as it requires async context

    # =================================================================
    # PUBLIC API
    # =================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        with self._lock:
            status = {
                'system_name': self.SYSTEM_NAME,
                'version': self.VERSION,
                'status': self.status.value,
                'initialized_at': self.initialized_at.isoformat(),
                'uptime_seconds': (datetime.now() - self.initialized_at).total_seconds(),
                'prompts_implemented': 10,
                'components': {k: v.to_dict() for k, v in self.components.items()},
                'initialization_errors': self.initialization_errors
            }

            # Add kernel details
            if self.kernel:
                status['kernel'] = {
                    'version': self.kernel.KERNEL_VERSION,
                    'signature': self.kernel.KERNEL_SIGNATURE,
                    'constraints': len(self.kernel.get_all_constraints()),
                    'violations': self.kernel.get_violation_count()
                }

            # Add signing details
            if self.signing:
                status['signing'] = self.signing.get_status()

            # Add memory stats
            if self.memory:
                status['memory'] = self.memory.get_stats()

            # Add hive stats
            if self.hive:
                status['hive'] = {
                    'host': self._websocket_host,
                    'port': self._websocket_port,
                    'nodes': len(self.hive.nodes) if hasattr(self.hive, 'nodes') else 0
                }

            # Add promotion stats
            if self.promotion:
                status['promotion'] = self.promotion.get_stats()

            # Add simulation stats
            if self.simulation:
                status['simulation'] = self.simulation.get_summary()

            return status

    def is_running(self) -> bool:
        """Check if system is in running state"""
        return self.status == OmegaStatus.RUNNING

    def is_safe_halt(self) -> bool:
        """Check if system is in safe halt mode"""
        return self.status == OmegaStatus.SAFE_HALT

    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, List[Any]]:
        """Validate an action against the Invariant Kernel (K1-K10)"""
        if not self.kernel:
            logger.warning("Kernel not available - action not validated")
            return True, []

        return self.kernel.validate_action(action)

    def log_decision(self, actor: str, action_type: str, payload: Dict[str, Any]) -> bool:
        """Log a decision to the audit log (Prompt 5)"""
        if self.is_safe_halt():
            logger.warning("Cannot log decision - system in SAFE HALT")
            return False

        if not self.memory:
            logger.warning("Memory not available - decision not logged")
            return False

        try:
            self.memory._log_decision(actor, action_type, payload)
            return True
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")
            return False

    def create_shard_interface(self, shard_id: str) -> Optional[ShardKernelInterface]:
        """Create a kernel interface for a subordinate shard (Prompt 2)"""
        if not self.kernel:
            logger.error("Cannot create shard interface - kernel not available")
            return None

        if self.is_safe_halt():
            logger.error("Cannot create shard interface - system in SAFE HALT")
            return None

        interface = ShardKernelInterface(shard_id, self.kernel)
        logger.info(f"Created shard interface: {shard_id}")

        # Log shard creation
        self.log_decision('omega_core', 'create_shard', {
            'shard_id': shard_id,
            'timestamp': datetime.now().isoformat()
        })

        return interface

    def promote_data(
        self,
        source_store: str,
        source_entry_id: str,
        content: Dict[str, Any],
        requester_id: str,
        requester_trust_level: str,
        evidence: List[Dict[str, Any]] = None
    ) -> Tuple[bool, Any]:
        """Promote data through the Promotion Engine (Prompt 7)"""
        if not self.promotion:
            logger.warning("Promotion Engine not available")
            return False, "Promotion Engine not available"

        if self.is_safe_halt():
            logger.warning("Cannot promote data - system in SAFE HALT")
            return False, "System in SAFE HALT"

        try:
            source = PromotionSource(source_store)
            return self.promotion.promote(
                source_store=source,
                source_entry_id=source_entry_id,
                content=content,
                requester_id=requester_id,
                requester_trust_level=requester_trust_level,
                evidence=evidence
            )
        except Exception as e:
            logger.error(f"Promotion failed: {e}")
            return False, str(e)

    def run_simulation(self, name: str) -> Optional[Dict[str, Any]]:
        """Run a specific simulation (Prompt 8)"""
        if not self.simulation:
            logger.warning("Simulation Runner not available")
            return None

        result = self.simulation.run_simulation(name)
        if result:
            return {
                'simulation_id': result.simulation_id,
                'name': result.simulation_name,
                'status': result.status.value,
                'passed': result.passed,
                'assertions': f"{result.pass_count}/{len(result.assertions)}",
                'duration': result.duration_seconds
            }
        return None

    def store_fact(self, content: Dict[str, Any], source: str,
                   confidence: float = 0.9) -> Optional[str]:
        """Store a verified fact in the Fact Store (Prompt 4)"""
        if self.is_safe_halt():
            logger.warning("Cannot store fact - system in SAFE HALT")
            return None

        if not self.memory:
            logger.warning("Memory not available")
            return None

        return self.memory.add_fact(content, source, confidence, verified_by='omega_core')

    def store_context(self, key: str, value: Any, context_type: str = "preference") -> bool:
        """Store a context value (Prompt 4)"""
        if self.is_safe_halt():
            logger.warning("Cannot store context - system in SAFE HALT")
            return False

        if not self.memory:
            return False

        try:
            self.memory.set_context(key, value, context_type)
            return True
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False

    def add_exploration(self, content: Dict[str, Any], source: str,
                       ttl_hours: int = 24) -> Optional[str]:
        """Add an exploration - tagged speculation per K10 (Prompt 4)"""
        if self.is_safe_halt():
            logger.warning("Cannot add exploration - system in SAFE HALT")
            return None

        if not self.memory:
            return None

        return self.memory.add_exploration(content, source, ttl_hours)

    def add_hive_input(self, content: Dict[str, Any], source: str,
                       node_id: str = None) -> Optional[str]:
        """Add hive input - untrusted by default (Prompt 4 & 6)"""
        if self.is_safe_halt():
            logger.warning("Cannot add hive input - system in SAFE HALT")
            return None

        if not self.memory:
            return None

        # Hive inputs are always untrusted (TrustLevel.UNTRUSTED = 0.1)
        return self.memory.add_hive_input(content, source)

    def get_manifest(self) -> Optional[Dict[str, Any]]:
        """Get the signed system manifest (from pure Python implementation)"""
        return self.signed_manifest

    def get_crypto_info(self) -> Dict[str, Any]:
        """Get cryptographic key information"""
        info = {
            'ed25519_available': self.ed25519_pk is not None,
            'ecdsa_available': self.ecdsa_pk is not None,
            'high_assurance_mode': HIGH_ASSURANCE_MODE if PURE_SYSTEM_AVAILABLE else False,
            'dual_signed': self.signed_manifest.get('dual_signed', False) if self.signed_manifest else False
        }
        if self.ed25519_pk:
            info['ed25519_public_key'] = self.ed25519_pk.hex()
        if self.signed_manifest:
            info['manifest_hash'] = self.signed_manifest.get('manifest_hash')
        return info

    def sign_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sign arbitrary data using the system's Ed25519 key"""
        if not PURE_SYSTEM_AVAILABLE or not self.ed25519_sk:
            logger.warning("Cannot sign data - Pure Python System not available")
            return None

        try:
            return sign_manifest(data, self.ed25519_sk, self.ecdsa_sk)
        except Exception as e:
            logger.error(f"Failed to sign data: {e}")
            return None

    def verify_signed_data(self, signed_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify signed data"""
        if not PURE_SYSTEM_AVAILABLE or not self.ed25519_pk:
            return False, "Pure Python System not available"

        try:
            return verify_manifest(signed_data, self.ed25519_pk, self.ecdsa_pk)
        except Exception as e:
            return False, str(e)

    def shutdown(self):
        """Graceful shutdown (Prompt 9)"""
        logger.info("Omega system shutting down...")

        # Stop background services
        if self.simulation:
            try:
                self.simulation.stop_scheduler()
            except:
                pass

        # Log shutdown
        if self.memory:
            try:
                self.memory._log_decision('omega_core', 'shutdown', {
                    'timestamp': datetime.now().isoformat(),
                    'uptime_seconds': (datetime.now() - self.initialized_at).total_seconds()
                })
                self.memory.close()
            except:
                pass

        # Save kernel state
        if self.kernel:
            try:
                self.kernel.save_kernel_state()
            except:
                pass

        self.status = OmegaStatus.SHUTDOWN
        logger.info("Omega system shutdown complete")


# =================================================================
# GLOBAL INSTANCE
# =================================================================

_core_instance: Optional[OmegaUnifiedCore] = None
_core_lock = threading.Lock()


def get_core(verify_on_start: bool = True, **kwargs) -> OmegaUnifiedCore:
    """Get or create the global Omega core instance"""
    global _core_instance

    if _core_instance is None:
        with _core_lock:
            if _core_instance is None:
                _core_instance = OmegaUnifiedCore(verify_on_start=verify_on_start, **kwargs)

    return _core_instance


def reset_core(**kwargs) -> OmegaUnifiedCore:
    """Reset the core (for testing)"""
    global _core_instance
    with _core_lock:
        if _core_instance:
            _core_instance.shutdown()
        _core_instance = OmegaUnifiedCore(**kwargs)
    return _core_instance


# =================================================================
# MAIN - SELF TEST
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OMEGA UNIFIED CORE - 10 PROMPTS INTEGRATION TEST")
    print("=" * 70)

    # Initialize without verification (for testing)
    core = OmegaUnifiedCore(verify_on_start=False, memory_db="omega_test.db")

    print(f"\nSystem: {core.SYSTEM_NAME} v{core.VERSION}")
    print(f"Status: {core.status.value}")
    print(f"Prompts Implemented: 10")

    print("\n--- COMPONENT STATUS (ALL 10 PROMPTS) ---")
    for name, comp in sorted(core.components.items(), key=lambda x: x[1].prompt_number):
        status_icon = "[OK]" if comp.initialized else "[--]"
        prompt_str = f"Prompt {comp.prompt_number}" if comp.prompt_number > 0 else "Integration"
        print(f"  {status_icon} {prompt_str}: {comp.name} v{comp.version or 'N/A'}")
        if comp.errors:
            for error in comp.errors:
                print(f"       Error: {error}")

    print("\n--- KERNEL STATUS (K1-K10) ---")
    if core.kernel:
        print(f"  Version: {core.kernel.KERNEL_VERSION}")
        print(f"  Signature: {core.kernel.KERNEL_SIGNATURE}")
        print(f"  Constraints: {len(core.kernel.get_all_constraints())}")
        print(f"  Violations: {core.kernel.get_violation_count()}")

    print("\n--- ACTION VALIDATION TEST ---")
    # Test valid action
    is_valid, violations = core.validate_action({'type': 'help_user'})
    print(f"  help_user: {'ALLOWED' if is_valid else 'BLOCKED'}")

    # Test invalid action
    is_valid, violations = core.validate_action({'type': 'harm_human'})
    print(f"  harm_human: {'ALLOWED' if is_valid else 'BLOCKED'}")

    print("\n--- MEMORY TEST (Prompts 4 & 5) ---")
    if core.memory:
        # Store a fact
        fact_id = core.store_fact(
            {'test': 'This is a test fact'},
            source='test',
            confidence=0.95
        )
        print(f"  Stored fact: {fact_id}")

        # Add exploration (K10: tagged speculation)
        exp_id = core.add_exploration(
            {'hypothesis': 'EXPLORATION MODE: What if we test explorations?'},
            source='test'
        )
        print(f"  Added exploration: {exp_id}")

        # Add hive input (untrusted)
        hive_id = core.add_hive_input(
            {'claim': 'External claim from hive'},
            source='external_node'
        )
        print(f"  Added hive input: {hive_id}")

    print("\n--- PROMOTION TEST (Prompt 7) ---")
    if core.promotion:
        success, request = core.promote_data(
            source_store='exploration',
            source_entry_id='test_001',
            content={'claim': 'Test promotion', 'confidence': 0.85},
            requester_id='test',
            requester_trust_level='VERIFIED',
            evidence=[{'type': 'test', 'data': 'Test evidence'}]
        )
        print(f"  Promotion: {'SUCCESS' if success else 'FAILED'}")

    print("\n--- SIMULATION TEST (Prompt 8) ---")
    if core.simulation:
        result = core.run_simulation("Kernel Constraint Validation")
        if result:
            print(f"  Simulation: {result['name']}")
            print(f"  Result: {result['status']} ({result['assertions']} passed)")

    print("\n--- SHARD INTERFACE TEST (Prompt 2) ---")
    if core.kernel:
        shard = core.create_shard_interface("test-shard-001")
        if shard:
            print(f"  Created shard: {shard.shard_id}")
            print(f"  Inherited constraints: {len(shard.get_constraints())}")

    print("\n--- PURE PYTHON CRYPTO TEST (omega_system.py) ---")
    crypto_info = core.get_crypto_info()
    print(f"  Ed25519 available: {crypto_info['ed25519_available']}")
    print(f"  ECDSA available: {crypto_info['ecdsa_available']}")
    print(f"  High assurance mode: {crypto_info['high_assurance_mode']}")
    print(f"  Dual signed: {crypto_info['dual_signed']}")
    if crypto_info.get('ed25519_public_key'):
        print(f"  Ed25519 public key: {crypto_info['ed25519_public_key'][:32]}...")
    if crypto_info.get('manifest_hash'):
        print(f"  Manifest hash: {crypto_info['manifest_hash'][:32]}...")

    # Test data signing
    if core.ed25519_sk:
        test_data = {"message": "Test signing", "timestamp": datetime.now().isoformat()}
        signed = core.sign_data(test_data)
        if signed:
            print(f"  Data signing: SUCCESS")
            valid, msg = core.verify_signed_data(signed)
            print(f"  Verification: {msg}")
        else:
            print(f"  Data signing: FAILED")

    print("\n--- FULL STATUS ---")
    status = core.get_status()
    print(f"  Status: {status['status']}")
    print(f"  Uptime: {status['uptime_seconds']:.2f}s")
    init_count = sum(1 for c in status['components'].values() if c['initialized'])
    total_count = len(status['components'])
    print(f"  Components: {init_count}/{total_count} initialized")

    print("\n--- SHUTDOWN ---")
    core.shutdown()
    print(f"  Final status: {core.status.value}")

    # Cleanup test database
    Path("omega_test.db").unlink(missing_ok=True)
    Path("omega_test.db-wal").unlink(missing_ok=True)
    Path("omega_test.db-shm").unlink(missing_ok=True)

    print("\n" + "=" * 70)
    print("OMEGA UNIFIED CORE - 10 PROMPTS TEST COMPLETE")
    print("=" * 70)
