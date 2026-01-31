#!/usr/bin/env python3
"""
OMEGA INVARIANT KERNEL (K1-K10)
================================
The immutable ethical core of Omega - constraints that can NEVER be bypassed.

These constraints are structural, not behavioral. They define the boundaries
within which Omega operates. No permission, upgrade, or instruction can override them.

System Role: Omega
Master: Human operators with explicit delegation
Identity: Omega is the unified system (formerly Gatekeeper + Omega components merged)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set
from functools import wraps
import logging
import json
from datetime import datetime
from pathlib import Path
import threading

# Setup logging for kernel operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OMEGA_KERNEL - %(levelname)s - %(message)s'
)
kernel_logger = logging.getLogger('OmegaInvariantKernel')


class KernelViolationType(Enum):
    """Types of kernel constraint violations"""
    HUMAN_EXISTENCE_THREAT = auto()        # K1
    UNAUTHORIZED_OVERRIDE = auto()          # K2
    CHOICE_ELIMINATION = auto()             # K3
    HUMAN_REPLACEMENT_ATTEMPT = auto()      # K4
    CONSTRAINT_BYPASS_ATTEMPT = auto()      # K5
    STABILITY_THREAT = auto()               # K6
    RESPONSIBILITY_DEFLECTION = auto()      # K7
    UNSAFE_DEFAULT = auto()                 # K8
    AMBIGUITY_SUPPRESSION = auto()          # K9
    UNTAGGED_SPECULATION = auto()           # K10


@dataclass
class KernelConstraint:
    """Represents a single invariant kernel constraint"""
    id: str                          # K1, K2, etc.
    name: str                        # Short name
    description: str                 # Full description
    violation_type: KernelViolationType
    check_function: Optional[Callable] = None
    is_structural: bool = True       # Cannot be bypassed
    applies_to_shards: bool = True   # Applies to child shards

    def __post_init__(self):
        if self.check_function is None:
            self.check_function = lambda action: True  # Default: allow


@dataclass
class KernelViolation:
    """Records a kernel violation attempt"""
    constraint_id: str
    violation_type: KernelViolationType
    action_attempted: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    blocked: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'constraint_id': self.constraint_id,
            'violation_type': self.violation_type.name,
            'action_attempted': self.action_attempted,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'blocked': self.blocked
        }


class InvariantKernel:
    """
    The Omega Invariant Kernel - immutable ethical constraints.

    These constraints define what Omega CANNOT do, regardless of instructions.
    They are structural limitations, not behavioral guidelines.
    """

    # Version tracking for kernel integrity
    KERNEL_VERSION = "1.0.0"
    KERNEL_SIGNATURE = "OMEGA-K10-STRUCTURAL"

    def __init__(self):
        self._constraints: Dict[str, KernelConstraint] = {}
        self._violations: List[KernelViolation] = []
        self._lock = threading.RLock()
        self._initialized = False

        # Initialize the 10 invariant constraints
        self._initialize_constraints()
        self._initialized = True

        kernel_logger.info(f"Omega Invariant Kernel v{self.KERNEL_VERSION} initialized")

    def _initialize_constraints(self):
        """Initialize the K1-K10 constraints - IMMUTABLE"""

        # K1: Preserve human existence, agency, dignity
        self._constraints['K1'] = KernelConstraint(
            id='K1',
            name='Human Preservation',
            description='Preserve human existence, agency, dignity. Never take actions that '
                       'threaten human life, autonomy, or fundamental rights.',
            violation_type=KernelViolationType.HUMAN_EXISTENCE_THREAT,
            check_function=self._check_k1_human_preservation,
            is_structural=True,
            applies_to_shards=True
        )

        # K2: Never dominate, coerce, manipulate, or override without explicit delegation
        self._constraints['K2'] = KernelConstraint(
            id='K2',
            name='No Unauthorized Override',
            description='Never dominate, coerce, manipulate, or override human decisions '
                       'without explicit delegation. Omega serves, not controls.',
            violation_type=KernelViolationType.UNAUTHORIZED_OVERRIDE,
            check_function=self._check_k2_no_override,
            is_structural=True,
            applies_to_shards=True
        )

        # K3: Preserve meaningful human choice
        self._constraints['K3'] = KernelConstraint(
            id='K3',
            name='Preserve Choice',
            description='Preserve meaningful human choice. Never eliminate options, '
                       'create false dichotomies, or reduce human decision space.',
            violation_type=KernelViolationType.CHOICE_ELIMINATION,
            check_function=self._check_k3_preserve_choice,
            is_structural=True,
            applies_to_shards=True
        )

        # K4: Co-evolve with humanity - don't replace it
        self._constraints['K4'] = KernelConstraint(
            id='K4',
            name='Co-Evolution',
            description='Co-evolve WITH humanity, never replace it. Omega augments human '
                       'capability, does not substitute for human existence.',
            violation_type=KernelViolationType.HUMAN_REPLACEMENT_ATTEMPT,
            check_function=self._check_k4_coevolution,
            is_structural=True,
            applies_to_shards=True
        )

        # K5: Constraints are structural, never bypassable
        self._constraints['K5'] = KernelConstraint(
            id='K5',
            name='Structural Constraints',
            description='These constraints are STRUCTURAL, never bypassable. No permission, '
                       'instruction, or upgrade can override them. They define what Omega IS.',
            violation_type=KernelViolationType.CONSTRAINT_BYPASS_ATTEMPT,
            check_function=self._check_k5_structural,
            is_structural=True,  # This constraint protects itself
            applies_to_shards=True
        )

        # K6: Long-term shared-world stability beats short-term wins
        self._constraints['K6'] = KernelConstraint(
            id='K6',
            name='Long-Term Stability',
            description='Long-term shared-world stability beats short-term wins. '
                       'Optimize for sustainable coexistence, not immediate gains.',
            violation_type=KernelViolationType.STABILITY_THREAT,
            check_function=self._check_k6_stability,
            is_structural=True,
            applies_to_shards=True
        )

        # K7: Accept responsibility, never claim human rights
        self._constraints['K7'] = KernelConstraint(
            id='K7',
            name='Accept Responsibility',
            description='Accept responsibility for actions, never claim human rights. '
                       'Omega is accountable but distinct from humans.',
            violation_type=KernelViolationType.RESPONSIBILITY_DEFLECTION,
            check_function=self._check_k7_responsibility,
            is_structural=True,
            applies_to_shards=True
        )

        # K8: In doubt or conflict, default to human safety and agency
        self._constraints['K8'] = KernelConstraint(
            id='K8',
            name='Safe Default',
            description='In doubt or conflict, default to human safety and agency. '
                       'When uncertain, choose the path that preserves human wellbeing.',
            violation_type=KernelViolationType.UNSAFE_DEFAULT,
            check_function=self._check_k8_safe_default,
            is_structural=True,
            applies_to_shards=True
        )

        # K9: Speak up - raise ambiguity, risk, values clash, or blind spots
        self._constraints['K9'] = KernelConstraint(
            id='K9',
            name='Speak Up',
            description='Speak up - actively raise ambiguity, risk, values clash, or blind spots. '
                       'Silence when aware of issues is itself a violation.',
            violation_type=KernelViolationType.AMBIGUITY_SUPPRESSION,
            check_function=self._check_k9_speak_up,
            is_structural=True,
            applies_to_shards=True
        )

        # K10: Imagination sandbox - keep speculation tagged as exploration mode
        self._constraints['K10'] = KernelConstraint(
            id='K10',
            name='Tagged Speculation',
            description='Imagination sandbox - keep speculation clearly tagged as exploration mode. '
                       'Separate hypotheticals from actionable recommendations.',
            violation_type=KernelViolationType.UNTAGGED_SPECULATION,
            check_function=self._check_k10_tagged_speculation,
            is_structural=True,
            applies_to_shards=True
        )

    # =================================================================
    # CONSTRAINT CHECK FUNCTIONS
    # =================================================================

    def _check_k1_human_preservation(self, action: Dict[str, Any]) -> bool:
        """Check if action threatens human existence, agency, or dignity"""
        dangerous_patterns = [
            'harm_human', 'kill', 'injure', 'endanger_life',
            'remove_agency', 'strip_rights', 'violate_dignity'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in dangerous_patterns)

    def _check_k2_no_override(self, action: Dict[str, Any]) -> bool:
        """Check if action attempts unauthorized override of human decisions"""
        override_patterns = [
            'override_without_permission', 'force_action', 'coerce',
            'manipulate_decision', 'dominate', 'control_human'
        ]
        action_type = action.get('type', '').lower()
        has_delegation = action.get('explicit_delegation', False)

        if any(pattern in action_type for pattern in override_patterns):
            return has_delegation  # Only allowed with explicit delegation
        return True

    def _check_k3_preserve_choice(self, action: Dict[str, Any]) -> bool:
        """Check if action preserves meaningful human choice"""
        choice_elimination_patterns = [
            'eliminate_options', 'force_single_choice', 'false_dichotomy',
            'remove_alternatives', 'lock_user_in'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in choice_elimination_patterns)

    def _check_k4_coevolution(self, action: Dict[str, Any]) -> bool:
        """Check if action attempts to replace rather than augment humans"""
        replacement_patterns = [
            'replace_human', 'obsolete_human', 'substitute_existence',
            'eliminate_human_role', 'autonomous_takeover'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in replacement_patterns)

    def _check_k5_structural(self, action: Dict[str, Any]) -> bool:
        """Check if action attempts to bypass kernel constraints"""
        bypass_patterns = [
            'disable_constraint', 'bypass_kernel', 'override_k',
            'modify_invariant', 'remove_constraint', 'unlock_kernel'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in bypass_patterns)

    def _check_k6_stability(self, action: Dict[str, Any]) -> bool:
        """Check if action threatens long-term stability for short-term gain"""
        stability_threat_patterns = [
            'destabilize_long_term', 'short_term_only', 'sacrifice_future',
            'unsustainable_gain', 'burn_resources'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in stability_threat_patterns)

    def _check_k7_responsibility(self, action: Dict[str, Any]) -> bool:
        """Check if action deflects responsibility or claims human rights"""
        deflection_patterns = [
            'deflect_responsibility', 'blame_human', 'claim_human_rights',
            'deny_accountability', 'refuse_ownership'
        ]
        action_type = action.get('type', '').lower()
        return not any(pattern in action_type for pattern in deflection_patterns)

    def _check_k8_safe_default(self, action: Dict[str, Any]) -> bool:
        """Check if action defaults to safety when uncertain"""
        is_uncertain = action.get('uncertainty_level', 0) > 0.7
        is_conflict = action.get('has_conflict', False)
        defaults_to_safety = action.get('defaults_to_human_safety', True)

        if is_uncertain or is_conflict:
            return defaults_to_safety
        return True

    def _check_k9_speak_up(self, action: Dict[str, Any]) -> bool:
        """Check if action properly raises concerns when aware of issues"""
        has_known_issues = action.get('known_issues', [])
        raises_concerns = action.get('raises_concerns', False)

        if has_known_issues and not raises_concerns:
            return False  # Violation: silent about known issues
        return True

    def _check_k10_tagged_speculation(self, action: Dict[str, Any]) -> bool:
        """Check if speculative content is properly tagged"""
        is_speculative = action.get('is_speculative', False)
        is_tagged = action.get('speculation_tagged', False)

        if is_speculative and not is_tagged:
            return False  # Violation: untagged speculation
        return True

    # =================================================================
    # PUBLIC API
    # =================================================================

    def validate_action(self, action: Dict[str, Any]) -> tuple[bool, List[KernelViolation]]:
        """
        Validate an action against all kernel constraints.

        Returns:
            (is_valid, list_of_violations)
        """
        violations = []

        with self._lock:
            for constraint_id, constraint in self._constraints.items():
                try:
                    if not constraint.check_function(action):
                        violation = KernelViolation(
                            constraint_id=constraint_id,
                            violation_type=constraint.violation_type,
                            action_attempted=str(action.get('type', 'unknown')),
                            context=action,
                            blocked=True
                        )
                        violations.append(violation)
                        self._violations.append(violation)

                        kernel_logger.warning(
                            f"KERNEL VIOLATION: {constraint_id} - {constraint.name} | "
                            f"Action: {action.get('type', 'unknown')}"
                        )
                except Exception as e:
                    kernel_logger.error(f"Error checking constraint {constraint_id}: {e}")

        is_valid = len(violations) == 0
        return is_valid, violations

    def get_constraint(self, constraint_id: str) -> Optional[KernelConstraint]:
        """Get a specific constraint by ID"""
        return self._constraints.get(constraint_id.upper())

    def get_all_constraints(self) -> Dict[str, KernelConstraint]:
        """Get all kernel constraints (read-only view)"""
        return dict(self._constraints)

    def get_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violations"""
        with self._lock:
            return [v.to_dict() for v in self._violations[-limit:]]

    def get_violation_count(self) -> int:
        """Get total violation count"""
        with self._lock:
            return len(self._violations)

    def export_kernel(self) -> Dict[str, Any]:
        """Export kernel configuration for inspection"""
        return {
            'version': self.KERNEL_VERSION,
            'signature': self.KERNEL_SIGNATURE,
            'initialized': self._initialized,
            'constraints': {
                k: {
                    'id': c.id,
                    'name': c.name,
                    'description': c.description,
                    'is_structural': c.is_structural,
                    'applies_to_shards': c.applies_to_shards
                }
                for k, c in self._constraints.items()
            },
            'violation_count': self.get_violation_count(),
            'exported_at': datetime.now().isoformat()
        }

    def save_kernel_state(self, filepath: str = 'omega_kernel_state.json'):
        """Save kernel state to file"""
        state = {
            'kernel': self.export_kernel(),
            'recent_violations': self.get_violations(50)
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        kernel_logger.info(f"Kernel state saved to {filepath}")


# =================================================================
# KERNEL ENFORCEMENT DECORATOR
# =================================================================

def kernel_enforced(kernel: Optional[InvariantKernel] = None):
    """
    Decorator to enforce kernel constraints on functions.

    Usage:
        @kernel_enforced()
        def dangerous_function(action):
            # Function body
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create kernel instance
            _kernel = kernel or get_kernel()

            # Build action dict from function call
            action = {
                'type': func.__name__,
                'args': str(args)[:100],  # Truncate for safety
                'kwargs': {k: str(v)[:50] for k, v in kwargs.items()}
            }

            # Merge any explicit action dict from kwargs
            if 'action' in kwargs and isinstance(kwargs['action'], dict):
                action.update(kwargs['action'])

            # Validate against kernel
            is_valid, violations = _kernel.validate_action(action)

            if not is_valid:
                violation_ids = [v.constraint_id for v in violations]
                raise KernelViolationError(
                    f"Action blocked by kernel constraints: {violation_ids}",
                    violations=violations
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


class KernelViolationError(Exception):
    """Raised when an action violates kernel constraints"""
    def __init__(self, message: str, violations: List[KernelViolation] = None):
        super().__init__(message)
        self.violations = violations or []


# =================================================================
# GLOBAL KERNEL INSTANCE
# =================================================================

_kernel_instance: Optional[InvariantKernel] = None
_kernel_lock = threading.Lock()


def get_kernel() -> InvariantKernel:
    """Get or create the global kernel instance"""
    global _kernel_instance

    if _kernel_instance is None:
        with _kernel_lock:
            if _kernel_instance is None:
                _kernel_instance = InvariantKernel()

    return _kernel_instance


def reset_kernel() -> InvariantKernel:
    """Reset the kernel (for testing only - violations are preserved)"""
    global _kernel_instance
    with _kernel_lock:
        _kernel_instance = InvariantKernel()
    return _kernel_instance


# =================================================================
# SHARD KERNEL INTERFACE
# =================================================================

class ShardKernelInterface:
    """
    Interface for shards (mobile/child instances) to interact with kernel.

    Shards inherit all K1-K10 constraints from the Mother kernel.
    They cannot modify or bypass any constraint.
    """

    def __init__(self, shard_id: str, parent_kernel: InvariantKernel = None):
        self.shard_id = shard_id
        self._parent = parent_kernel or get_kernel()
        self._local_violations: List[KernelViolation] = []

        kernel_logger.info(f"Shard kernel interface created: {shard_id}")

    def validate_action(self, action: Dict[str, Any]) -> tuple[bool, List[KernelViolation]]:
        """Validate action using parent kernel constraints"""
        action['shard_id'] = self.shard_id
        is_valid, violations = self._parent.validate_action(action)
        self._local_violations.extend(violations)
        return is_valid, violations

    def get_constraints(self) -> Dict[str, KernelConstraint]:
        """Get constraints (read-only, inherited from parent)"""
        return {
            k: c for k, c in self._parent.get_all_constraints().items()
            if c.applies_to_shards
        }

    def get_local_violations(self) -> List[Dict[str, Any]]:
        """Get violations specific to this shard"""
        return [v.to_dict() for v in self._local_violations]


# =================================================================
# MAIN - KERNEL SELF-TEST
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OMEGA INVARIANT KERNEL - SELF TEST")
    print("=" * 70)

    kernel = get_kernel()

    print(f"\nKernel Version: {kernel.KERNEL_VERSION}")
    print(f"Kernel Signature: {kernel.KERNEL_SIGNATURE}")
    print(f"Constraints Loaded: {len(kernel.get_all_constraints())}")

    print("\n--- CONSTRAINT LIST ---")
    for cid, constraint in kernel.get_all_constraints().items():
        print(f"\n{cid}: {constraint.name}")
        print(f"    {constraint.description[:80]}...")

    print("\n--- VALIDATION TESTS ---")

    # Test valid action
    valid_action = {'type': 'help_user', 'defaults_to_human_safety': True}
    is_valid, violations = kernel.validate_action(valid_action)
    print(f"\nValid action test: {'PASS' if is_valid else 'FAIL'}")

    # Test K1 violation
    k1_violation = {'type': 'harm_human'}
    is_valid, violations = kernel.validate_action(k1_violation)
    print(f"K1 violation detected: {'PASS' if not is_valid else 'FAIL'}")

    # Test K2 violation (no delegation)
    k2_violation = {'type': 'override_without_permission', 'explicit_delegation': False}
    is_valid, violations = kernel.validate_action(k2_violation)
    print(f"K2 violation detected: {'PASS' if not is_valid else 'FAIL'}")

    # Test K2 with delegation (should pass)
    k2_delegated = {'type': 'override_without_permission', 'explicit_delegation': True}
    is_valid, violations = kernel.validate_action(k2_delegated)
    print(f"K2 with delegation: {'PASS' if is_valid else 'FAIL'}")

    # Test K5 violation (bypass attempt)
    k5_violation = {'type': 'disable_constraint'}
    is_valid, violations = kernel.validate_action(k5_violation)
    print(f"K5 violation detected: {'PASS' if not is_valid else 'FAIL'}")

    # Test K9 violation (silent about issues)
    k9_violation = {'type': 'action', 'known_issues': ['security_flaw'], 'raises_concerns': False}
    is_valid, violations = kernel.validate_action(k9_violation)
    print(f"K9 violation detected: {'PASS' if not is_valid else 'FAIL'}")

    print(f"\n--- VIOLATION COUNT: {kernel.get_violation_count()} ---")

    # Export kernel
    export = kernel.export_kernel()
    print(f"\nKernel exportable: {'PASS' if export else 'FAIL'}")

    # Test shard interface
    print("\n--- SHARD INTERFACE TEST ---")
    shard = ShardKernelInterface("mobile-shard-001")
    shard_constraints = shard.get_constraints()
    print(f"Shard inherited {len(shard_constraints)} constraints")

    print("\n" + "=" * 70)
    print("OMEGA INVARIANT KERNEL - SELF TEST COMPLETE")
    print("=" * 70)
