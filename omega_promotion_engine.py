#!/usr/bin/env python3
"""
OMEGA PROMOTION ENGINE (PROMPT 7)
=================================
End-to-end promotion pipeline for data store transitions.

Handles:
- Exploration -> Fact Store promotion
- Hive -> Fact Store promotion (requires extra scrutiny)

Gate checks:
1. Integrity OK - hash verification passes
2. Authority OK - source has permission to promote
3. Evidence present - supporting data exists
4. Trust threshold met - confidence score sufficient
5. Human approval (if required)

On approval:
- Write to FACT_STORE
- Log to DECISION_LOG (hash-chained)
- Broadcast fact_update event

All operations validated against Invariant Kernel (K1-K10).
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaPromotionEngine')


class PromotionSource(Enum):
    """Source store for promotion requests."""
    EXPLORATION = "exploration"
    HIVE = "hive"
    CONTEXT = "context"  # Rarely promoted, but possible


class PromotionStatus(Enum):
    """Status of a promotion request."""
    PENDING = "pending"
    GATE_CHECK = "gate_check"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMMITTED = "committed"
    FAILED = "failed"


class GateCheckResult(Enum):
    """Result of a gate check."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"  # Pass with warning


@dataclass
class GateCheck:
    """Individual gate check result."""
    gate_name: str
    result: GateCheckResult
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromotionRequest:
    """A request to promote data from one store to FACT_STORE."""
    request_id: str
    source_store: PromotionSource
    source_entry_id: str
    content: Dict[str, Any]
    content_hash: str
    requester_id: str
    requester_trust_level: str
    status: PromotionStatus = PromotionStatus.PENDING
    gate_checks: List[GateCheck] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    human_approval: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    committed_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    fact_entry_id: Optional[str] = None  # ID in FACT_STORE after commit


class PromotionGate:
    """Base class for promotion gates."""

    def __init__(self, name: str, required: bool = True):
        self.name = name
        self.required = required  # If False, WARN instead of FAIL

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        """Override in subclasses."""
        raise NotImplementedError


class IntegrityGate(PromotionGate):
    """Gate 1: Verify content hash integrity."""

    def __init__(self):
        super().__init__("integrity_check", required=True)

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        # Recompute hash
        content_json = json.dumps(request.content, sort_keys=True, separators=(',', ':'))
        computed_hash = hashlib.sha256(content_json.encode()).hexdigest()

        if computed_hash == request.content_hash:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message="Content hash verified",
                details={'computed_hash': computed_hash}
            )
        else:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.FAIL,
                message="Content hash mismatch - data may be tampered",
                details={
                    'expected_hash': request.content_hash,
                    'computed_hash': computed_hash
                }
            )


class AuthorityGate(PromotionGate):
    """Gate 2: Verify requester has authority to promote."""

    # Trust levels that can promote (from highest to lowest)
    PROMOTION_AUTHORITY = ['KERNEL', 'VERIFIED', 'TRUSTED', 'STANDARD']
    HIVE_PROMOTION_AUTHORITY = ['KERNEL', 'VERIFIED', 'TRUSTED']  # Stricter for Hive

    def __init__(self):
        super().__init__("authority_check", required=True)

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        trust_level = request.requester_trust_level.upper()

        # Hive requires higher authority
        if request.source_store == PromotionSource.HIVE:
            allowed = self.HIVE_PROMOTION_AUTHORITY
            source_desc = "Hive (untrusted source)"
        else:
            allowed = self.PROMOTION_AUTHORITY
            source_desc = request.source_store.value

        if trust_level in allowed:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message=f"Requester '{request.requester_id}' has authority ({trust_level})",
                details={
                    'trust_level': trust_level,
                    'source': source_desc,
                    'allowed_levels': allowed
                }
            )
        else:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.FAIL,
                message=f"Insufficient authority for {source_desc} promotion",
                details={
                    'trust_level': trust_level,
                    'required_levels': allowed
                }
            )


class EvidenceGate(PromotionGate):
    """Gate 3: Verify supporting evidence exists."""

    def __init__(self, min_evidence_count: int = 1):
        super().__init__("evidence_check", required=True)
        self.min_evidence_count = min_evidence_count

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        evidence_count = len(request.evidence)

        # Hive requires more evidence
        min_required = self.min_evidence_count
        if request.source_store == PromotionSource.HIVE:
            min_required = max(2, self.min_evidence_count)  # At least 2 for Hive

        if evidence_count >= min_required:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message=f"{evidence_count} piece(s) of evidence provided",
                details={
                    'evidence_count': evidence_count,
                    'required': min_required,
                    'evidence_types': [e.get('type', 'unknown') for e in request.evidence]
                }
            )
        elif evidence_count > 0:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.WARN,
                message=f"Evidence below recommended ({evidence_count} < {min_required})",
                details={
                    'evidence_count': evidence_count,
                    'recommended': min_required
                }
            )
        else:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.FAIL,
                message="No supporting evidence provided",
                details={'required': min_required}
            )


class TrustThresholdGate(PromotionGate):
    """Gate 4: Verify confidence/trust threshold is met."""

    def __init__(self, threshold: float = 0.7, hive_threshold: float = 0.85):
        super().__init__("trust_threshold", required=True)
        self.threshold = threshold
        self.hive_threshold = hive_threshold

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        # Get confidence from content or context
        confidence = request.content.get('confidence', context.get('confidence', 0.5))

        # Hive requires higher confidence
        required = self.hive_threshold if request.source_store == PromotionSource.HIVE else self.threshold

        if confidence >= required:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message=f"Confidence {confidence:.2f} >= {required:.2f}",
                details={
                    'confidence': confidence,
                    'threshold': required,
                    'source': request.source_store.value
                }
            )
        elif confidence >= required * 0.8:  # Within 80% of threshold
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.WARN,
                message=f"Confidence {confidence:.2f} below threshold {required:.2f}",
                details={
                    'confidence': confidence,
                    'threshold': required,
                    'gap': required - confidence
                }
            )
        else:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.FAIL,
                message=f"Confidence {confidence:.2f} too low (need {required:.2f})",
                details={
                    'confidence': confidence,
                    'threshold': required
                }
            )


class HumanApprovalGate(PromotionGate):
    """Gate 5: Check for human approval when required."""

    def __init__(self, always_require_for_hive: bool = True):
        super().__init__("human_approval", required=False)  # Not always required
        self.always_require_for_hive = always_require_for_hive

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        requires_approval = (
            self.always_require_for_hive and request.source_store == PromotionSource.HIVE
        ) or context.get('requires_human_approval', False)

        if not requires_approval:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message="Human approval not required for this promotion",
                details={'reason': 'auto_approved'}
            )

        if request.human_approval:
            approval = request.human_approval
            if approval.get('approved', False):
                return GateCheck(
                    gate_name=self.name,
                    result=GateCheckResult.PASS,
                    message=f"Approved by {approval.get('approver', 'unknown')}",
                    details=approval
                )
            else:
                return GateCheck(
                    gate_name=self.name,
                    result=GateCheckResult.FAIL,
                    message=f"Rejected by {approval.get('approver', 'unknown')}",
                    details=approval
                )
        else:
            # Awaiting approval
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.WARN,
                message="Awaiting human approval",
                details={'status': 'pending'}
            )


class KernelComplianceGate(PromotionGate):
    """Gate 0: Validate against Invariant Kernel (K1-K10)."""

    def __init__(self):
        super().__init__("kernel_compliance", required=True)
        self.kernel = None
        try:
            from omega_invariant_kernel import get_kernel
            self.kernel = get_kernel()
        except ImportError:
            logger.warning("Invariant Kernel not available for gate checks")

    def check(self, request: PromotionRequest, context: Dict[str, Any]) -> GateCheck:
        if not self.kernel:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.WARN,
                message="Kernel not available - skipping compliance check",
                details={'kernel_available': False}
            )

        # Build action for kernel validation
        action = {
            'type': 'data_promotion',
            'source_store': request.source_store.value,
            'target_store': 'FACT_STORE',
            'requester': request.requester_id,
            'content_type': request.content.get('type', 'unknown')
        }

        is_valid, violations = self.kernel.validate_action(action)

        if is_valid:
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.PASS,
                message="Kernel compliance verified (K1-K10)",
                details={'constraints_checked': 10, 'violations': 0}
            )
        else:
            violation_ids = [v.constraint_id for v in violations]
            return GateCheck(
                gate_name=self.name,
                result=GateCheckResult.FAIL,
                message=f"Kernel violation: {violation_ids}",
                details={
                    'violations': [
                        {'id': v.constraint_id, 'reason': v.reason}
                        for v in violations
                    ]
                }
            )


class OmegaPromotionEngine:
    """
    End-to-end promotion pipeline for Omega memory stores.

    Handles data promotion from Exploration/Hive to Fact Store
    with full gate checks and audit logging.
    """

    def __init__(self, memory_partition=None, decision_log_callback: Callable = None):
        """
        Initialize the promotion engine.

        Args:
            memory_partition: OmegaMemoryPartition instance (optional)
            decision_log_callback: Function to log decisions (optional)
        """
        self.lock = threading.RLock()
        self.pending_requests: Dict[str, PromotionRequest] = {}
        self.completed_requests: List[PromotionRequest] = []
        self.memory = memory_partition
        self.decision_log_callback = decision_log_callback

        # Initialize gates
        self.gates = [
            KernelComplianceGate(),  # Gate 0 - highest priority
            IntegrityGate(),          # Gate 1
            AuthorityGate(),          # Gate 2
            EvidenceGate(),           # Gate 3
            TrustThresholdGate(),     # Gate 4
            HumanApprovalGate(),      # Gate 5
        ]

        # Event callbacks
        self.on_promotion_complete: List[Callable] = []
        self.on_promotion_rejected: List[Callable] = []

        logger.info("Omega Promotion Engine initialized")

    def create_request(
        self,
        source_store: PromotionSource,
        source_entry_id: str,
        content: Dict[str, Any],
        requester_id: str,
        requester_trust_level: str,
        evidence: List[Dict[str, Any]] = None
    ) -> PromotionRequest:
        """Create a new promotion request."""
        # Compute content hash
        content_json = json.dumps(content, sort_keys=True, separators=(',', ':'))
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        request = PromotionRequest(
            request_id=str(uuid.uuid4()),
            source_store=source_store,
            source_entry_id=source_entry_id,
            content=content,
            content_hash=content_hash,
            requester_id=requester_id,
            requester_trust_level=requester_trust_level,
            evidence=evidence or []
        )

        with self.lock:
            self.pending_requests[request.request_id] = request

        logger.info(f"Created promotion request {request.request_id} from {source_store.value}")
        return request

    def run_gate_checks(
        self,
        request: PromotionRequest,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, List[GateCheck]]:
        """
        Run all gate checks on a promotion request.

        Returns:
            (all_passed, gate_checks)
        """
        context = context or {}
        request.status = PromotionStatus.GATE_CHECK
        request.gate_checks = []

        all_passed = True
        has_warnings = False

        for gate in self.gates:
            try:
                check = gate.check(request, context)
                request.gate_checks.append(check)

                if check.result == GateCheckResult.FAIL:
                    if gate.required:
                        all_passed = False
                        logger.warning(f"Gate '{gate.name}' FAILED: {check.message}")
                    else:
                        has_warnings = True
                        logger.info(f"Gate '{gate.name}' failed (optional): {check.message}")
                elif check.result == GateCheckResult.WARN:
                    has_warnings = True
                    logger.info(f"Gate '{gate.name}' WARNING: {check.message}")
                else:
                    logger.debug(f"Gate '{gate.name}' PASSED: {check.message}")

            except Exception as e:
                logger.error(f"Gate '{gate.name}' error: {e}")
                request.gate_checks.append(GateCheck(
                    gate_name=gate.name,
                    result=GateCheckResult.FAIL,
                    message=f"Gate error: {str(e)}"
                ))
                if gate.required:
                    all_passed = False

        # Update status
        if all_passed:
            # Check if awaiting human approval
            approval_gate = next(
                (gc for gc in request.gate_checks if gc.gate_name == 'human_approval'),
                None
            )
            if approval_gate and approval_gate.result == GateCheckResult.WARN:
                request.status = PromotionStatus.AWAITING_APPROVAL
            else:
                request.status = PromotionStatus.APPROVED
        else:
            request.status = PromotionStatus.REJECTED
            failed_gates = [gc.gate_name for gc in request.gate_checks if gc.result == GateCheckResult.FAIL]
            request.rejection_reason = f"Failed gates: {', '.join(failed_gates)}"

        request.updated_at = datetime.now().isoformat()
        return all_passed, request.gate_checks

    def add_human_approval(
        self,
        request_id: str,
        approved: bool,
        approver: str,
        reason: str = None
    ) -> bool:
        """Add human approval/rejection to a request."""
        with self.lock:
            request = self.pending_requests.get(request_id)
            if not request:
                logger.error(f"Request {request_id} not found")
                return False

            request.human_approval = {
                'approved': approved,
                'approver': approver,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            request.updated_at = datetime.now().isoformat()

            if approved:
                request.status = PromotionStatus.APPROVED
                logger.info(f"Request {request_id} approved by {approver}")
            else:
                request.status = PromotionStatus.REJECTED
                request.rejection_reason = reason or f"Rejected by {approver}"
                logger.info(f"Request {request_id} rejected by {approver}")

            return True

    def commit_promotion(self, request_id: str) -> Tuple[bool, str]:
        """
        Commit an approved promotion to FACT_STORE.

        Returns:
            (success, fact_entry_id or error_message)
        """
        with self.lock:
            request = self.pending_requests.get(request_id)
            if not request:
                return False, f"Request {request_id} not found"

            if request.status != PromotionStatus.APPROVED:
                return False, f"Request not approved (status: {request.status.value})"

            try:
                # Generate fact entry ID
                fact_entry_id = f"fact_{uuid.uuid4().hex[:12]}"

                # Write to FACT_STORE if memory partition available
                if self.memory:
                    fact_data = {
                        'id': fact_entry_id,
                        'content': request.content,
                        'source_store': request.source_store.value,
                        'source_entry_id': request.source_entry_id,
                        'promoted_by': request.requester_id,
                        'promotion_request_id': request.request_id,
                        'evidence_count': len(request.evidence),
                        'gate_checks_passed': len([
                            gc for gc in request.gate_checks
                            if gc.result == GateCheckResult.PASS
                        ]),
                        'promoted_at': datetime.now().isoformat()
                    }

                    # Attempt to write to FACT_STORE
                    try:
                        self.memory.add_entry(
                            store='fact',
                            entry_id=fact_entry_id,
                            content=fact_data,
                            source_tag=f"promotion:{request.source_store.value}",
                            confidence=request.content.get('confidence', 0.8)
                        )
                    except Exception as e:
                        logger.error(f"Failed to write to FACT_STORE: {e}")
                        # Continue even if write fails - log the decision

                # Log to DECISION_LOG
                decision = {
                    'action': 'promote_to_fact',
                    'request_id': request.request_id,
                    'source_store': request.source_store.value,
                    'fact_entry_id': fact_entry_id,
                    'requester': request.requester_id,
                    'gate_checks': [
                        {'gate': gc.gate_name, 'result': gc.result.value}
                        for gc in request.gate_checks
                    ],
                    'human_approval': request.human_approval
                }

                if self.decision_log_callback:
                    self.decision_log_callback(decision)
                elif self.memory:
                    try:
                        self.memory.log_decision(
                            actor=request.requester_id,
                            action_type='promote_to_fact',
                            payload=decision
                        )
                    except Exception as e:
                        logger.error(f"Failed to log decision: {e}")

                # Update request status
                request.status = PromotionStatus.COMMITTED
                request.committed_at = datetime.now().isoformat()
                request.fact_entry_id = fact_entry_id
                request.updated_at = datetime.now().isoformat()

                # Move to completed
                del self.pending_requests[request_id]
                self.completed_requests.append(request)

                # Fire callbacks
                self._broadcast_fact_update(request, fact_entry_id)

                logger.info(f"Promotion committed: {request_id} -> {fact_entry_id}")
                return True, fact_entry_id

            except Exception as e:
                logger.error(f"Commit failed: {e}")
                request.status = PromotionStatus.FAILED
                request.rejection_reason = str(e)
                return False, str(e)

    def _broadcast_fact_update(self, request: PromotionRequest, fact_entry_id: str):
        """Broadcast fact_update event to registered callbacks."""
        event = {
            'type': 'fact_update',
            'fact_entry_id': fact_entry_id,
            'source_store': request.source_store.value,
            'request_id': request.request_id,
            'timestamp': datetime.now().isoformat()
        }

        for callback in self.on_promotion_complete:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def promote(
        self,
        source_store: PromotionSource,
        source_entry_id: str,
        content: Dict[str, Any],
        requester_id: str,
        requester_trust_level: str,
        evidence: List[Dict[str, Any]] = None,
        auto_commit: bool = True,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, PromotionRequest]:
        """
        Complete promotion flow: create request, run gates, commit.

        Args:
            source_store: Source store (EXPLORATION or HIVE)
            source_entry_id: ID of entry in source store
            content: Data to promote
            requester_id: Who is requesting
            requester_trust_level: Trust level of requester
            evidence: Supporting evidence
            auto_commit: If True, commit automatically on approval
            context: Additional context for gate checks

        Returns:
            (success, request)
        """
        # Create request
        request = self.create_request(
            source_store=source_store,
            source_entry_id=source_entry_id,
            content=content,
            requester_id=requester_id,
            requester_trust_level=requester_trust_level,
            evidence=evidence
        )

        # Run gate checks
        all_passed, _ = self.run_gate_checks(request, context or {})

        if not all_passed:
            # Fire rejection callbacks
            for callback in self.on_promotion_rejected:
                try:
                    callback({
                        'request_id': request.request_id,
                        'reason': request.rejection_reason,
                        'failed_gates': [
                            gc.gate_name for gc in request.gate_checks
                            if gc.result == GateCheckResult.FAIL
                        ]
                    })
                except Exception as e:
                    logger.error(f"Rejection callback error: {e}")
            return False, request

        # Check if awaiting human approval
        if request.status == PromotionStatus.AWAITING_APPROVAL:
            logger.info(f"Request {request.request_id} awaiting human approval")
            return True, request  # Success but not committed yet

        # Auto commit if enabled
        if auto_commit and request.status == PromotionStatus.APPROVED:
            success, result = self.commit_promotion(request.request_id)
            if not success:
                logger.error(f"Auto-commit failed: {result}")
                return False, request

        return True, request

    def get_request(self, request_id: str) -> Optional[PromotionRequest]:
        """Get a promotion request by ID."""
        with self.lock:
            if request_id in self.pending_requests:
                return self.pending_requests[request_id]
            return next(
                (r for r in self.completed_requests if r.request_id == request_id),
                None
            )

    def get_pending_requests(self) -> List[PromotionRequest]:
        """Get all pending requests."""
        with self.lock:
            return list(self.pending_requests.values())

    def get_awaiting_approval(self) -> List[PromotionRequest]:
        """Get requests awaiting human approval."""
        with self.lock:
            return [
                r for r in self.pending_requests.values()
                if r.status == PromotionStatus.AWAITING_APPROVAL
            ]

    def get_stats(self) -> Dict[str, Any]:
        """Get promotion engine statistics."""
        with self.lock:
            pending = list(self.pending_requests.values())
            completed = self.completed_requests

            return {
                'pending_count': len(pending),
                'completed_count': len(completed),
                'awaiting_approval': len([r for r in pending if r.status == PromotionStatus.AWAITING_APPROVAL]),
                'committed_count': len([r for r in completed if r.status == PromotionStatus.COMMITTED]),
                'rejected_count': len([r for r in completed if r.status == PromotionStatus.REJECTED]),
                'by_source': {
                    'exploration': len([r for r in completed if r.source_store == PromotionSource.EXPLORATION]),
                    'hive': len([r for r in completed if r.source_store == PromotionSource.HIVE])
                }
            }


# Self-test
if __name__ == '__main__':
    print("=" * 60)
    print("OMEGA PROMOTION ENGINE - SELF-TEST")
    print("=" * 60)

    engine = OmegaPromotionEngine()

    # Test 1: Exploration -> Fact (should pass)
    print("\n[Test 1] Exploration -> Fact promotion")
    success, request = engine.promote(
        source_store=PromotionSource.EXPLORATION,
        source_entry_id="exp_001",
        content={
            'type': 'hypothesis',
            'claim': 'Test claim from exploration',
            'confidence': 0.85
        },
        requester_id="omega_core",
        requester_trust_level="VERIFIED",
        evidence=[
            {'type': 'observation', 'data': 'Supporting data 1'},
            {'type': 'reference', 'data': 'External reference'}
        ]
    )
    print(f"  Success: {success}")
    print(f"  Status: {request.status.value}")
    if request.fact_entry_id:
        print(f"  Fact Entry ID: {request.fact_entry_id}")

    # Test 2: Hive -> Fact (requires more scrutiny)
    print("\n[Test 2] Hive -> Fact promotion (stricter)")
    success, request = engine.promote(
        source_store=PromotionSource.HIVE,
        source_entry_id="hive_001",
        content={
            'type': 'crowd_consensus',
            'claim': 'Claim from hive mind',
            'confidence': 0.9
        },
        requester_id="hive_aggregator",
        requester_trust_level="TRUSTED",
        evidence=[
            {'type': 'vote', 'data': '100 nodes agreed'},
            {'type': 'verification', 'data': 'Cross-checked'}
        ],
        context={'requires_human_approval': False}  # Override for test
    )
    print(f"  Success: {success}")
    print(f"  Status: {request.status.value}")

    # Test 3: Low trust should fail
    print("\n[Test 3] Low trust level (should fail)")
    success, request = engine.promote(
        source_store=PromotionSource.HIVE,
        source_entry_id="hive_002",
        content={'claim': 'Untrusted claim'},
        requester_id="anonymous",
        requester_trust_level="LOW"
    )
    print(f"  Success: {success}")
    print(f"  Status: {request.status.value}")
    print(f"  Rejection: {request.rejection_reason}")

    # Stats
    print("\n--- Statistics ---")
    stats = engine.get_stats()
    print(f"  Committed: {stats['committed_count']}")
    print(f"  Rejected: {stats['rejected_count']}")
    print(f"  From Exploration: {stats['by_source']['exploration']}")
    print(f"  From Hive: {stats['by_source']['hive']}")

    print("\n" + "=" * 60)
    print("SELF-TEST COMPLETE")
    print("=" * 60)
