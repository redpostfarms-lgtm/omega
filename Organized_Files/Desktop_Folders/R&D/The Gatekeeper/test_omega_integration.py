# -*- coding: utf-8 -*-
# Quick test script for Omega integration

import sys
from pathlib import Path

# Add paths
GATE = Path(__file__).parent
if str(GATE) not in sys.path:
    sys.path.insert(0, str(GATE))

print("=" * 80)
print("Ω OMEGA INTEGRATION TEST")
print("=" * 80)
print()

# Test imports
print("Testing imports...")
try:
    from omega_security_enhanced import SANITIZER, KILLSWITCH, AUDIT_LOGGER
    print("✓ Security enhanced module")
except ImportError as e:
    print(f"✗ Security enhanced module: {e}")

try:
    from omega_speed_enhanced import lru_cache, CONNECTION_POOL, PARALLEL_EXECUTOR
    print("✓ Speed enhanced module")
except ImportError as e:
    print(f"✗ Speed enhanced module: {e}")

try:
    from omega_scalability_enhanced import RATE_LIMITER, RESOURCE_MONITOR
    print("✓ Scalability enhanced module")
except ImportError as e:
    print(f"✗ Scalability enhanced module: {e}")

try:
    from omega_quantum_enhanced import HARDWARE_ENTROPY, CRYPTO_RNG
    print("✓ Quantum enhanced module")
except ImportError as e:
    print(f"✗ Quantum enhanced module: {e}")

try:
    from deep_system_test import OmegaSystemTester
    print("✓ Omega system tester")
except ImportError as e:
    print(f"✗ Omega system tester: {e}")

try:
    sys.path.insert(0, str(GATE.parent))
    from quantum_worldwide_scrub import QuantumWorldwideScrub
    print("✓ Quantum Worldwide Scrub")
except ImportError as e:
    print(f"✗ Quantum Worldwide Scrub: {e}")

try:
    from omega_master_integration import OmegaMasterIntegration
    print("✓ Omega Master Integration")
except ImportError as e:
    print(f"✗ Omega Master Integration: {e}")

print()
print("=" * 80)
print("Test complete!")
print("=" * 80)
