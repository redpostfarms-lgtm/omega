# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Master Integration - Complete System Integration
# Integrates Omega + Quantum World Web Spray + All Enhancements

"""
Ω Omega Master Integration System

This is the master entry point that:
1. Fixes all import issues
2. Integrates Quantum World Web Spray
3. Provides unified command prompt interface
4. Ensures all systems work together
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Set up paths
GATE = Path(__file__).parent
REPO_ROOT = GATE.parent
BRAIN_DIR = Path(r"D:\RPF_BRAIN")
if not BRAIN_DIR.exists():
    BRAIN_DIR = REPO_ROOT / "Analysis"
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

# Add paths to sys.path
if str(GATE) not in sys.path:
    sys.path.insert(0, str(GATE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import core systems
try:
    from deep_system_test import OmegaSystemTester
    OMEGA_AVAILABLE = True
except ImportError as e:
    OMEGA_AVAILABLE = False
    print(f"Warning: Omega system not available: {e}")

try:
    # Import Quantum World Web Spray
    sys.path.insert(0, str(REPO_ROOT))
    from quantum_worldwide_scrub import QuantumWorldwideScrub
    QUANTUM_SCRUB_AVAILABLE = True
except ImportError as e:
    QUANTUM_SCRUB_AVAILABLE = False
    print(f"Warning: Quantum Worldwide Scrub not available: {e}")

class OmegaMasterIntegration:
    """Master integration system for Omega + Quantum World Web Spray."""
    
    def __init__(self):
        self.omega_tester = None
        self.quantum_scrubber = None
        self.integration_status = {
            "omega": False,
            "quantum_scrub": False,
            "enhanced_modules": {},
            "errors": []
        }
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all systems."""
        # Initialize Omega
        if OMEGA_AVAILABLE:
            try:
                self.omega_tester = OmegaSystemTester(autonomous=True)
                self.integration_status["omega"] = True
            except Exception as e:
                self.integration_status["errors"].append(f"Omega initialization: {e}")
        
        # Initialize Quantum Worldwide Scrub
        if QUANTUM_SCRUB_AVAILABLE:
            try:
                self.quantum_scrubber = QuantumWorldwideScrub()
                self.integration_status["quantum_scrub"] = True
            except Exception as e:
                self.integration_status["errors"].append(f"Quantum Scrub initialization: {e}")
        
        # Check enhanced modules
        self._check_enhanced_modules()
    
    def _check_enhanced_modules(self):
        """Check which enhanced modules are available."""
        enhanced = {
            "security": False,
            "speed": False,
            "scalability": False,
            "quantum": False
        }
        
        try:
            from omega_security_enhanced import SANITIZER, KILLSWITCH, AUDIT_LOGGER
            enhanced["security"] = True
        except ImportError:
            pass
        
        try:
            from omega_speed_enhanced import lru_cache, CONNECTION_POOL, PARALLEL_EXECUTOR
            enhanced["speed"] = True
        except ImportError:
            pass
        
        try:
            from omega_scalability_enhanced import RATE_LIMITER, RESOURCE_MONITOR
            enhanced["scalability"] = True
        except ImportError:
            pass
        
        try:
            from omega_quantum_enhanced import HARDWARE_ENTROPY, CRYPTO_RNG
            enhanced["quantum"] = True
        except ImportError:
            pass
        
        self.integration_status["enhanced_modules"] = enhanced
    
    def run_omega_tests(self, parallel: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Run Omega system tests."""
        if not self.omega_tester:
            return {"error": "Omega system not available"}
        
        print("=" * 80)
        print("Ω OMEGA SYSTEM TEST")
        print("=" * 80)
        
        results = self.omega_tester.run_all_tests(parallel=parallel)
        return results
    
    def run_quantum_scrub(self) -> Dict[str, Any]:
        """Run Quantum Worldwide Scrub analysis."""
        if not self.quantum_scrubber:
            return {"error": "Quantum Worldwide Scrub not available"}
        
        print("=" * 80)
        print("QUANTUM WORLDWIDE SCRUB")
        print("=" * 80)
        
        system_scan, comparison, improvements = self.quantum_scrubber.run()
        
        return {
            "system_scan": system_scan,
            "comparison": comparison,
            "improvements": improvements
        }
    
    def run_full_analysis(self, parallel: bool = False) -> Dict[str, Any]:
        """Run complete analysis: Omega tests + Quantum Scrub."""
        print("=" * 80)
        print("Ω OMEGA MASTER INTEGRATION - FULL ANALYSIS")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "integration_status": self.integration_status,
            "omega_results": None,
            "quantum_scrub_results": None
        }
        
        # Run Omega tests
        if self.omega_tester:
            print("\n[1/2] Running Omega System Tests...")
            results["omega_results"] = self.run_omega_tests(parallel=parallel)
        
        # Run Quantum Scrub
        if self.quantum_scrubber:
            print("\n[2/2] Running Quantum Worldwide Scrub...")
            results["quantum_scrub_results"] = self.run_quantum_scrub()
        
        # Save results
        report_file = BRAIN_DIR / f"omega_master_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nReport saved to: {report_file}")
        
        return results
    
    def show_status(self):
        """Show integration status."""
        print("=" * 80)
        print("Ω OMEGA MASTER INTEGRATION STATUS")
        print("=" * 80)
        print(f"\nOmega System: {'✓ Available' if self.integration_status['omega'] else '✗ Not Available'}")
        print(f"Quantum Scrub: {'✓ Available' if self.integration_status['quantum_scrub'] else '✗ Not Available'}")
        print("\nEnhanced Modules:")
        for module, available in self.integration_status["enhanced_modules"].items():
            status = "✓" if available else "✗"
            print(f"  {status} {module.capitalize()}")
        
        if self.integration_status["errors"]:
            print("\nErrors:")
            for error in self.integration_status["errors"]:
                print(f"  - {error}")
        
        print()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ω Omega Master Integration - Complete System Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python omega_master_integration.py --omega              # Run Omega tests only
  python omega_master_integration.py --quantum-scrub      # Run Quantum Scrub only
  python omega_master_integration.py --full                # Run full analysis
  python omega_master_integration.py --status              # Show status
        """
    )
    
    parser.add_argument('--omega', action='store_true', help='Run Omega system tests')
    parser.add_argument('--quantum-scrub', action='store_true', help='Run Quantum Worldwide Scrub')
    parser.add_argument('--full', action='store_true', help='Run full analysis (Omega + Quantum Scrub)')
    parser.add_argument('--status', action='store_true', help='Show integration status')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel (Omega only)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create integration system
    integration = OmegaMasterIntegration()
    
    # Execute requested actions
    if args.status:
        integration.show_status()
    elif args.omega:
        integration.run_omega_tests(parallel=args.parallel, verbose=args.verbose)
    elif args.quantum_scrub:
        integration.run_quantum_scrub()
    elif args.full:
        integration.run_full_analysis(parallel=args.parallel)
    else:
        # Default: show status and run full analysis
        integration.show_status()
        print("\nRunning full analysis...\n")
        integration.run_full_analysis(parallel=args.parallel)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
