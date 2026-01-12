# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Integration - Integrate All Enhancements

"""
Ω Omega Integration

Integrates all enhanced modules into Omega's core systems.
"""

import sys
from pathlib import Path

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

# Add both locations to path
import sys
if str(GATE) not in sys.path:
    sys.path.insert(0, str(GATE))
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

# Import all enhanced modules
try:
    from omega_security_enhanced import (
        InputSanitizer, EntropyKillswitch, SandboxIsolation, SecurityAuditLogger,
        SANITIZER, KILLSWITCH, AUDIT_LOGGER, SANDBOX
    )
    SECURITY_ENHANCED = True
except ImportError as e:
    SECURITY_ENHANCED = False
    print(f"Warning: Security enhancements not available: {e}")

try:
    from omega_speed_enhanced import (
        lru_cache, ConnectionPool, ParallelExecutor,
        CONNECTION_POOL, PARALLEL_EXECUTOR
    )
    SPEED_ENHANCED = True
except ImportError:
    SPEED_ENHANCED = False
    print("Warning: Speed enhancements not available")

try:
    from omega_scalability_enhanced import (
        RateLimiter, ResourceMonitor, OfflineMode,
        RATE_LIMITER, RESOURCE_MONITOR, OFFLINE_MODE
    )
    SCALABILITY_ENHANCED = True
except ImportError:
    SCALABILITY_ENHANCED = False
    print("Warning: Scalability enhancements not available")

try:
    from omega_quantum_enhanced import (
        HardwareEntropy, QuantumCircuit, CryptographicRNG, RNGQualityTester,
        HARDWARE_ENTROPY, CRYPTO_RNG, RNG_TESTER
    )
    QUANTUM_ENHANCED = True
except ImportError:
    QUANTUM_ENHANCED = False
    print("Warning: Quantum enhancements not available")

print("=" * 80)
print("OMEGA INTEGRATION STATUS")
print("=" * 80)
print(f"Security Enhanced: {'YES' if SECURITY_ENHANCED else 'NO'}")
print(f"Speed Enhanced: {'YES' if SPEED_ENHANCED else 'NO'}")
print(f"Scalability Enhanced: {'YES' if SCALABILITY_ENHANCED else 'NO'}")
print(f"Quantum Enhanced: {'YES' if QUANTUM_ENHANCED else 'NO'}")
print("=" * 80)

