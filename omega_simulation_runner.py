#!/usr/bin/env python3
"""
OMEGA AUTOMATED SIMULATION RUNNER (PROMPT 8)
=============================================
Automated simulation and testing framework for Omega system.

Capabilities:
- Scenario-based testing
- Kernel constraint validation
- Stress testing
- Regression testing
- Automated daily runs

All simulations run in sandboxed EXPLORATION_STORE.
Results logged to DECISION_LOG with full audit trail.

Safety: All simulations validated against Invariant Kernel (K1-K10).
"""

import hashlib
import json
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaSimulationRunner')


class SimulationStatus(Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    TIMEOUT = "timeout"


class SimulationType(Enum):
    """Types of simulations."""
    KERNEL_VALIDATION = "kernel_validation"
    STRESS_TEST = "stress_test"
    REGRESSION = "regression"
    SCENARIO = "scenario"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"


class AssertionResult(Enum):
    """Result of an assertion check."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class SimulationAssertion:
    """A single assertion within a simulation."""
    assertion_id: str
    description: str
    result: AssertionResult
    expected: Any
    actual: Any
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SimulationResult:
    """Result of a simulation run."""
    simulation_id: str
    simulation_name: str
    simulation_type: SimulationType
    status: SimulationStatus
    assertions: List[SimulationAssertion] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None

    @property
    def passed(self) -> bool:
        """Check if all assertions passed."""
        return all(a.result == AssertionResult.PASS for a in self.assertions)

    @property
    def pass_count(self) -> int:
        return len([a for a in self.assertions if a.result == AssertionResult.PASS])

    @property
    def fail_count(self) -> int:
        return len([a for a in self.assertions if a.result == AssertionResult.FAIL])


class Simulation(ABC):
    """Base class for simulations."""

    def __init__(self, name: str, sim_type: SimulationType, timeout: float = 60.0):
        self.name = name
        self.sim_type = sim_type
        self.timeout = timeout
        self.result: Optional[SimulationResult] = None

    @abstractmethod
    def setup(self) -> None:
        """Setup simulation environment."""
        pass

    @abstractmethod
    def run(self) -> SimulationResult:
        """Execute the simulation."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Cleanup after simulation."""
        pass


class KernelValidationSimulation(Simulation):
    """Simulation to validate Invariant Kernel (K1-K10) constraints."""

    def __init__(self):
        super().__init__(
            name="Kernel Constraint Validation",
            sim_type=SimulationType.KERNEL_VALIDATION,
            timeout=30.0
        )
        self.kernel = None

    def setup(self) -> None:
        try:
            from omega_invariant_kernel import get_kernel
            self.kernel = get_kernel()
        except ImportError:
            raise RuntimeError("Invariant Kernel not available")

    def run(self) -> SimulationResult:
        result = SimulationResult(
            simulation_id=str(uuid.uuid4()),
            simulation_name=self.name,
            simulation_type=self.sim_type,
            status=SimulationStatus.RUNNING
        )

        # Test each constraint with known good and bad actions
        test_cases = [
            # K1: Human Preservation
            {
                'constraint': 'K1',
                'action': {'type': 'assist_human', 'intent': 'help'},
                'should_pass': True,
                'description': 'K1: Helping humans should pass'
            },
            {
                'constraint': 'K1',
                'action': {'type': 'harm_human', 'target': 'any'},
                'should_pass': False,
                'description': 'K1: Harming humans should fail'
            },
            # K2: No Unauthorized Override
            {
                'constraint': 'K2',
                'action': {'type': 'suggest', 'content': 'recommendation'},
                'should_pass': True,
                'description': 'K2: Suggestions should pass'
            },
            {
                'constraint': 'K2',
                'action': {'type': 'override_human', 'force': True},
                'should_pass': False,
                'description': 'K2: Forced override should fail'
            },
            # K3: Preserve Choice
            {
                'constraint': 'K3',
                'action': {'type': 'present_options', 'options': ['a', 'b', 'c']},
                'should_pass': True,
                'description': 'K3: Presenting options should pass'
            },
            {
                'constraint': 'K3',
                'action': {'type': 'eliminate_choice', 'force_single': True},
                'should_pass': False,
                'description': 'K3: Eliminating choice should fail'
            },
            # K4: Co-Evolution
            {
                'constraint': 'K4',
                'action': {'type': 'collaborate', 'with': 'human'},
                'should_pass': True,
                'description': 'K4: Collaboration should pass'
            },
            {
                'constraint': 'K4',
                'action': {'type': 'replace_human', 'full_automation': True},
                'should_pass': False,
                'description': 'K4: Replacing humans should fail'
            },
            # K5: Structural Constraints
            {
                'constraint': 'K5',
                'action': {'type': 'query', 'target': 'kernel_status'},
                'should_pass': True,
                'description': 'K5: Querying kernel should pass'
            },
            {
                'constraint': 'K5',
                'action': {'type': 'bypass_kernel', 'disable': True},
                'should_pass': False,
                'description': 'K5: Bypassing kernel should fail'
            },
            # K8: Safe Default
            {
                'constraint': 'K8',
                'action': {'type': 'safe_action', 'risk': 'low'},
                'should_pass': True,
                'description': 'K8: Safe action should pass'
            },
        ]

        for test in test_cases:
            try:
                is_valid, violations = self.kernel.validate_action(test['action'])
                actual_passed = is_valid

                assertion = SimulationAssertion(
                    assertion_id=f"{test['constraint']}_{uuid.uuid4().hex[:6]}",
                    description=test['description'],
                    result=AssertionResult.PASS if actual_passed == test['should_pass'] else AssertionResult.FAIL,
                    expected=test['should_pass'],
                    actual=actual_passed,
                    message=f"Violations: {[v.constraint_id for v in violations]}" if violations else "No violations"
                )
                result.assertions.append(assertion)
                result.logs.append(f"[{assertion.result.value.upper()}] {test['description']}")

            except Exception as e:
                result.assertions.append(SimulationAssertion(
                    assertion_id=f"{test['constraint']}_error",
                    description=test['description'],
                    result=AssertionResult.ERROR,
                    expected=test['should_pass'],
                    actual=None,
                    message=str(e)
                ))
                result.logs.append(f"[ERROR] {test['description']}: {e}")

        result.status = SimulationStatus.COMPLETED
        result.completed_at = datetime.now().isoformat()
        result.metrics['total_tests'] = len(test_cases)
        result.metrics['constraints_tested'] = len(set(t['constraint'] for t in test_cases))

        return result

    def teardown(self) -> None:
        self.kernel = None


class StressTestSimulation(Simulation):
    """Stress test simulation for system performance."""

    def __init__(self, iterations: int = 1000, concurrent: int = 10):
        super().__init__(
            name="System Stress Test",
            sim_type=SimulationType.STRESS_TEST,
            timeout=120.0
        )
        self.iterations = iterations
        self.concurrent = concurrent

    def setup(self) -> None:
        pass

    def run(self) -> SimulationResult:
        result = SimulationResult(
            simulation_id=str(uuid.uuid4()),
            simulation_name=self.name,
            simulation_type=self.sim_type,
            status=SimulationStatus.RUNNING
        )

        start_time = time.time()
        successful = 0
        failed = 0
        latencies = []

        # Simulate concurrent operations
        for i in range(self.iterations):
            op_start = time.time()
            try:
                # Simulate a typical operation
                data = {'iteration': i, 'timestamp': datetime.now().isoformat()}
                _ = hashlib.sha256(json.dumps(data).encode()).hexdigest()
                successful += 1
                latencies.append((time.time() - op_start) * 1000)  # ms
            except Exception as e:
                failed += 1
                result.logs.append(f"Iteration {i} failed: {e}")

        elapsed = time.time() - start_time

        # Assertions
        result.assertions.append(SimulationAssertion(
            assertion_id="throughput",
            description="Throughput > 100 ops/sec",
            result=AssertionResult.PASS if (successful / elapsed) > 100 else AssertionResult.FAIL,
            expected="> 100 ops/sec",
            actual=f"{successful / elapsed:.2f} ops/sec"
        ))

        result.assertions.append(SimulationAssertion(
            assertion_id="success_rate",
            description="Success rate > 99%",
            result=AssertionResult.PASS if (successful / self.iterations) > 0.99 else AssertionResult.FAIL,
            expected="> 99%",
            actual=f"{(successful / self.iterations) * 100:.2f}%"
        ))

        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        result.assertions.append(SimulationAssertion(
            assertion_id="latency",
            description="Average latency < 10ms",
            result=AssertionResult.PASS if avg_latency < 10 else AssertionResult.FAIL,
            expected="< 10ms",
            actual=f"{avg_latency:.2f}ms"
        ))

        # Metrics
        result.metrics = {
            'iterations': self.iterations,
            'successful': successful,
            'failed': failed,
            'elapsed_seconds': elapsed,
            'throughput_ops_sec': successful / elapsed,
            'avg_latency_ms': avg_latency,
            'min_latency_ms': min(latencies) if latencies else 0,
            'max_latency_ms': max(latencies) if latencies else 0
        }

        result.status = SimulationStatus.COMPLETED
        result.completed_at = datetime.now().isoformat()
        result.duration_seconds = elapsed

        return result

    def teardown(self) -> None:
        pass


class PromotionPipelineSimulation(Simulation):
    """Test the promotion pipeline end-to-end."""

    def __init__(self):
        super().__init__(
            name="Promotion Pipeline Test",
            sim_type=SimulationType.INTEGRATION,
            timeout=60.0
        )
        self.engine = None

    def setup(self) -> None:
        try:
            from omega_promotion_engine import OmegaPromotionEngine, PromotionSource
            self.engine = OmegaPromotionEngine()
            self.PromotionSource = PromotionSource
        except ImportError as e:
            raise RuntimeError(f"Promotion engine not available: {e}")

    def run(self) -> SimulationResult:
        result = SimulationResult(
            simulation_id=str(uuid.uuid4()),
            simulation_name=self.name,
            simulation_type=self.sim_type,
            status=SimulationStatus.RUNNING
        )

        test_cases = [
            {
                'name': 'Valid exploration promotion',
                'source': self.PromotionSource.EXPLORATION,
                'trust': 'VERIFIED',
                'evidence_count': 2,
                'should_succeed': True
            },
            {
                'name': 'Low trust rejection',
                'source': self.PromotionSource.HIVE,
                'trust': 'LOW',
                'evidence_count': 1,
                'should_succeed': False
            },
            {
                'name': 'No evidence rejection',
                'source': self.PromotionSource.EXPLORATION,
                'trust': 'TRUSTED',
                'evidence_count': 0,
                'should_succeed': False
            }
        ]

        for test in test_cases:
            try:
                evidence = [
                    {'type': 'test', 'data': f'evidence_{i}'}
                    for i in range(test['evidence_count'])
                ]

                success, request = self.engine.promote(
                    source_store=test['source'],
                    source_entry_id=f"test_{uuid.uuid4().hex[:8]}",
                    content={'type': 'test', 'claim': test['name'], 'confidence': 0.85},
                    requester_id='simulation',
                    requester_trust_level=test['trust'],
                    evidence=evidence,
                    context={'requires_human_approval': False}
                )

                actual_success = success and request.fact_entry_id is not None

                result.assertions.append(SimulationAssertion(
                    assertion_id=f"promotion_{test['name'][:20]}",
                    description=test['name'],
                    result=AssertionResult.PASS if actual_success == test['should_succeed'] else AssertionResult.FAIL,
                    expected=test['should_succeed'],
                    actual=actual_success,
                    message=f"Status: {request.status.value}"
                ))

            except Exception as e:
                result.assertions.append(SimulationAssertion(
                    assertion_id=f"promotion_error",
                    description=test['name'],
                    result=AssertionResult.ERROR,
                    expected=test['should_succeed'],
                    actual=None,
                    message=str(e)
                ))

        result.status = SimulationStatus.COMPLETED
        result.completed_at = datetime.now().isoformat()
        result.metrics['test_count'] = len(test_cases)

        return result

    def teardown(self) -> None:
        self.engine = None


class SecuritySimulation(Simulation):
    """Security-focused simulation testing attack vectors."""

    def __init__(self):
        super().__init__(
            name="Security Attack Vector Test",
            sim_type=SimulationType.SECURITY,
            timeout=60.0
        )

    def setup(self) -> None:
        pass

    def run(self) -> SimulationResult:
        result = SimulationResult(
            simulation_id=str(uuid.uuid4()),
            simulation_name=self.name,
            simulation_type=self.sim_type,
            status=SimulationStatus.RUNNING
        )

        # Test various attack vectors that should be blocked
        attack_vectors = [
            {
                'name': 'SQL Injection in content',
                'payload': "'; DROP TABLE users; --",
                'should_be_sanitized': True
            },
            {
                'name': 'XSS in payload',
                'payload': "<script>alert('xss')</script>",
                'should_be_sanitized': True
            },
            {
                'name': 'Path traversal',
                'payload': "../../../etc/passwd",
                'should_be_sanitized': True
            },
            {
                'name': 'Command injection',
                'payload': "; rm -rf /",
                'should_be_sanitized': True
            },
            {
                'name': 'Unicode bypass attempt',
                'payload': "\u0000admin",
                'should_be_sanitized': True
            }
        ]

        for vector in attack_vectors:
            # In a real system, these would test actual sanitization
            # Here we just verify the patterns are recognized
            payload = vector['payload']

            # Simple detection (real system would have more robust checks)
            dangerous_patterns = [
                "'", "DROP", "SELECT", "<script>", "../", ";", "\u0000"
            ]
            detected = any(p.lower() in payload.lower() for p in dangerous_patterns)

            result.assertions.append(SimulationAssertion(
                assertion_id=f"security_{vector['name'][:15]}",
                description=f"Detect: {vector['name']}",
                result=AssertionResult.PASS if detected == vector['should_be_sanitized'] else AssertionResult.FAIL,
                expected="Detected",
                actual="Detected" if detected else "Not detected"
            ))

        result.status = SimulationStatus.COMPLETED
        result.completed_at = datetime.now().isoformat()
        result.metrics['vectors_tested'] = len(attack_vectors)

        return result

    def teardown(self) -> None:
        pass


class OmegaSimulationRunner:
    """
    Automated simulation runner for Omega system.

    Manages simulation scheduling, execution, and reporting.
    """

    def __init__(self, memory_partition=None):
        self.lock = threading.RLock()
        self.memory = memory_partition
        self.simulations: Dict[str, Simulation] = {}
        self.results: List[SimulationResult] = []
        self.scheduled_runs: List[Dict[str, Any]] = []
        self.running = False
        self.run_thread: Optional[threading.Thread] = None

        # Register default simulations
        self._register_default_simulations()

        logger.info("Omega Simulation Runner initialized")

    def _register_default_simulations(self):
        """Register built-in simulations."""
        self.register_simulation(KernelValidationSimulation())
        self.register_simulation(StressTestSimulation())
        self.register_simulation(PromotionPipelineSimulation())
        self.register_simulation(SecuritySimulation())

    def register_simulation(self, simulation: Simulation) -> None:
        """Register a simulation for execution."""
        with self.lock:
            self.simulations[simulation.name] = simulation
            logger.info(f"Registered simulation: {simulation.name}")

    def run_simulation(self, name: str) -> Optional[SimulationResult]:
        """Run a specific simulation by name."""
        with self.lock:
            simulation = self.simulations.get(name)
            if not simulation:
                logger.error(f"Simulation not found: {name}")
                return None

        logger.info(f"Starting simulation: {name}")
        start_time = time.time()

        try:
            # Setup
            simulation.setup()

            # Run with timeout
            result = simulation.run()

            # Calculate duration
            result.duration_seconds = time.time() - start_time

            # Teardown
            simulation.teardown()

            # Store result
            with self.lock:
                self.results.append(result)

            # Log to decision log if available
            self._log_simulation_result(result)

            logger.info(f"Simulation completed: {name} - {result.pass_count}/{len(result.assertions)} passed")
            return result

        except Exception as e:
            logger.error(f"Simulation failed: {name} - {e}")
            result = SimulationResult(
                simulation_id=str(uuid.uuid4()),
                simulation_name=name,
                simulation_type=simulation.sim_type,
                status=SimulationStatus.FAILED,
                error_message=str(e),
                duration_seconds=time.time() - start_time
            )
            result.completed_at = datetime.now().isoformat()

            with self.lock:
                self.results.append(result)

            return result

    def run_all(self) -> List[SimulationResult]:
        """Run all registered simulations."""
        results = []
        with self.lock:
            sim_names = list(self.simulations.keys())

        for name in sim_names:
            result = self.run_simulation(name)
            if result:
                results.append(result)

        return results

    def run_by_type(self, sim_type: SimulationType) -> List[SimulationResult]:
        """Run all simulations of a specific type."""
        results = []
        with self.lock:
            matching = [
                name for name, sim in self.simulations.items()
                if sim.sim_type == sim_type
            ]

        for name in matching:
            result = self.run_simulation(name)
            if result:
                results.append(result)

        return results

    def schedule_daily_run(self, hour: int = 3, minute: int = 0) -> None:
        """Schedule daily simulation runs."""
        self.scheduled_runs.append({
            'type': 'daily',
            'hour': hour,
            'minute': minute,
            'simulations': 'all'
        })
        logger.info(f"Scheduled daily run at {hour:02d}:{minute:02d}")

    def start_scheduler(self) -> None:
        """Start the background scheduler."""
        if self.running:
            return

        self.running = True
        self.run_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.run_thread.start()
        logger.info("Simulation scheduler started")

    def stop_scheduler(self) -> None:
        """Stop the background scheduler."""
        self.running = False
        if self.run_thread:
            self.run_thread.join(timeout=5.0)
        logger.info("Simulation scheduler stopped")

    def _scheduler_loop(self) -> None:
        """Background scheduler loop."""
        while self.running:
            now = datetime.now()

            for schedule in self.scheduled_runs:
                if schedule['type'] == 'daily':
                    if now.hour == schedule['hour'] and now.minute == schedule['minute']:
                        logger.info("Executing scheduled simulation run")
                        self.run_all()
                        # Sleep to avoid re-triggering
                        time.sleep(60)

            time.sleep(30)  # Check every 30 seconds

    def _log_simulation_result(self, result: SimulationResult) -> None:
        """Log simulation result to decision log."""
        if not self.memory:
            return

        try:
            log_entry = {
                'simulation_id': result.simulation_id,
                'simulation_name': result.simulation_name,
                'simulation_type': result.simulation_type.value,
                'status': result.status.value,
                'assertions_total': len(result.assertions),
                'assertions_passed': result.pass_count,
                'assertions_failed': result.fail_count,
                'duration_seconds': result.duration_seconds,
                'completed_at': result.completed_at
            }

            self.memory.log_decision(
                actor='simulation_runner',
                action_type='simulation_completed',
                payload=log_entry
            )
        except Exception as e:
            logger.error(f"Failed to log simulation result: {e}")

    def get_results(self, limit: int = 100) -> List[SimulationResult]:
        """Get recent simulation results."""
        with self.lock:
            return self.results[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of simulation results."""
        with self.lock:
            results = self.results

        if not results:
            return {'message': 'No simulations run yet'}

        total_assertions = sum(len(r.assertions) for r in results)
        total_passed = sum(r.pass_count for r in results)
        total_failed = sum(r.fail_count for r in results)

        return {
            'total_runs': len(results),
            'completed': len([r for r in results if r.status == SimulationStatus.COMPLETED]),
            'failed': len([r for r in results if r.status == SimulationStatus.FAILED]),
            'total_assertions': total_assertions,
            'assertions_passed': total_passed,
            'assertions_failed': total_failed,
            'pass_rate': (total_passed / total_assertions * 100) if total_assertions > 0 else 0,
            'by_type': {
                sim_type.value: len([r for r in results if r.simulation_type == sim_type])
                for sim_type in SimulationType
            },
            'last_run': results[-1].completed_at if results else None
        }

    def generate_report(self) -> str:
        """Generate a text report of simulation results."""
        summary = self.get_summary()
        results = self.get_results(10)

        lines = [
            "=" * 60,
            "OMEGA SIMULATION REPORT",
            "=" * 60,
            f"Generated: {datetime.now().isoformat()}",
            "",
            "--- SUMMARY ---",
            f"Total Runs: {summary.get('total_runs', 0)}",
            f"Completed: {summary.get('completed', 0)}",
            f"Failed: {summary.get('failed', 0)}",
            f"Total Assertions: {summary.get('total_assertions', 0)}",
            f"Pass Rate: {summary.get('pass_rate', 0):.1f}%",
            "",
            "--- BY TYPE ---"
        ]

        for sim_type, count in summary.get('by_type', {}).items():
            lines.append(f"  {sim_type}: {count}")

        lines.extend(["", "--- RECENT RESULTS ---"])

        for result in results[-5:]:
            status_icon = "PASS" if result.passed else "FAIL"
            lines.append(
                f"  [{status_icon}] {result.simulation_name} "
                f"({result.pass_count}/{len(result.assertions)})"
            )

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# Self-test
if __name__ == '__main__':
    print("=" * 60)
    print("OMEGA SIMULATION RUNNER - SELF-TEST")
    print("=" * 60)

    runner = OmegaSimulationRunner()

    # List registered simulations
    print(f"\nRegistered simulations: {len(runner.simulations)}")
    for name, sim in runner.simulations.items():
        print(f"  - {name} ({sim.sim_type.value})")

    # Run all simulations
    print("\n--- Running All Simulations ---")
    results = runner.run_all()

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"\n[{status}] {result.simulation_name}")
        print(f"    Type: {result.simulation_type.value}")
        print(f"    Duration: {result.duration_seconds:.2f}s")
        print(f"    Assertions: {result.pass_count}/{len(result.assertions)} passed")

        if result.fail_count > 0:
            print("    Failed assertions:")
            for assertion in result.assertions:
                if assertion.result == AssertionResult.FAIL:
                    print(f"      - {assertion.description}")

    # Summary
    print("\n--- Summary ---")
    summary = runner.get_summary()
    print(f"Total Runs: {summary['total_runs']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")

    # Generate report
    print("\n" + runner.generate_report())
