#!/usr/bin/env python3
"""
OMEGA OPERATOR TOOLS (PROMPT 10)
================================
Operator expectations and tooling for Omega system administration.

What Operators Need:
1. Clear visibility into system state
2. Ability to intervene when needed
3. Audit trail for all actions
4. Emergency controls
5. Performance monitoring

What Operators Should NOT Do:
1. Bypass Invariant Kernel (K1-K10)
2. Access user data without authorization
3. Modify decision logs
4. Disable security features
5. Grant themselves elevated privileges

All operator actions logged and auditable.
Kernel constraints apply to operators too.
"""

import hashlib
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import getpass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaOperatorTools')


class OperatorRole(Enum):
    """Operator role levels."""
    VIEWER = "viewer"           # Read-only access
    OPERATOR = "operator"       # Standard operations
    ADMIN = "admin"             # Administrative tasks
    EMERGENCY = "emergency"     # Emergency interventions only


class ActionCategory(Enum):
    """Categories of operator actions."""
    READ = "read"               # Read system state
    MONITOR = "monitor"         # Health/performance monitoring
    CONFIG = "config"           # Configuration changes
    LIFECYCLE = "lifecycle"     # Start/stop/restart
    EMERGENCY = "emergency"     # Emergency interventions
    AUDIT = "audit"             # Audit and compliance


@dataclass
class OperatorSession:
    """Operator session information."""
    session_id: str
    operator_id: str
    role: OperatorRole
    started_at: str
    last_activity: str
    actions_count: int = 0
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperatorAction:
    """Record of an operator action."""
    action_id: str
    session_id: str
    operator_id: str
    category: ActionCategory
    action_type: str
    target: Optional[str]
    parameters: Dict[str, Any]
    result: str  # success, denied, error
    timestamp: str
    duration_ms: float
    kernel_validated: bool
    details: Dict[str, Any] = field(default_factory=dict)


class OperatorAuditLog:
    """Append-only audit log for operator actions."""

    def __init__(self, log_dir: Path = Path("operator_logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        self.current_log_file = self._get_log_file()
        self.last_hash = "0" * 64  # Genesis hash

    def _get_log_file(self) -> Path:
        """Get the current log file (one per day)."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"operator_audit_{date_str}.jsonl"

    def log_action(self, action: OperatorAction) -> str:
        """Log an operator action. Returns the entry hash."""
        with self.lock:
            # Rotate log file if needed
            new_log = self._get_log_file()
            if new_log != self.current_log_file:
                self.current_log_file = new_log
                self.last_hash = "0" * 64  # Reset hash for new file

            # Create log entry
            entry = {
                'action_id': action.action_id,
                'session_id': action.session_id,
                'operator_id': action.operator_id,
                'category': action.category.value,
                'action_type': action.action_type,
                'target': action.target,
                'parameters': action.parameters,
                'result': action.result,
                'timestamp': action.timestamp,
                'duration_ms': action.duration_ms,
                'kernel_validated': action.kernel_validated,
                'details': action.details,
                'previous_hash': self.last_hash
            }

            # Compute hash
            entry_json = json.dumps(entry, sort_keys=True, separators=(',', ':'))
            entry_hash = hashlib.sha256(entry_json.encode()).hexdigest()
            entry['entry_hash'] = entry_hash

            # Append to log
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')

            self.last_hash = entry_hash
            return entry_hash

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """Verify the integrity of the audit log."""
        issues = []
        previous_hash = "0" * 64

        for log_file in sorted(self.log_dir.glob("operator_audit_*.jsonl")):
            try:
                with open(log_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        entry = json.loads(line)

                        # Verify chain
                        if entry.get('previous_hash') != previous_hash:
                            issues.append(f"{log_file.name}:{line_num} - Chain break")

                        # Verify entry hash
                        stored_hash = entry.pop('entry_hash', None)
                        entry_json = json.dumps(entry, sort_keys=True, separators=(',', ':'))
                        computed_hash = hashlib.sha256(entry_json.encode()).hexdigest()

                        if stored_hash != computed_hash:
                            issues.append(f"{log_file.name}:{line_num} - Hash mismatch")

                        previous_hash = stored_hash or computed_hash

            except Exception as e:
                issues.append(f"{log_file.name} - Error: {e}")

        return len(issues) == 0, issues

    def get_recent_actions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent actions from the log."""
        actions = []

        for log_file in sorted(self.log_dir.glob("operator_audit_*.jsonl"), reverse=True):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        actions.append(json.loads(line))
                        if len(actions) >= limit:
                            break
            except Exception as e:
                logger.error(f"Error reading {log_file}: {e}")

            if len(actions) >= limit:
                break

        return actions[:limit]


class OperatorPermissions:
    """Permission management for operators."""

    # Define what each role can do
    ROLE_PERMISSIONS = {
        OperatorRole.VIEWER: {
            ActionCategory.READ,
            ActionCategory.MONITOR,
            ActionCategory.AUDIT
        },
        OperatorRole.OPERATOR: {
            ActionCategory.READ,
            ActionCategory.MONITOR,
            ActionCategory.CONFIG,
            ActionCategory.LIFECYCLE,
            ActionCategory.AUDIT
        },
        OperatorRole.ADMIN: {
            ActionCategory.READ,
            ActionCategory.MONITOR,
            ActionCategory.CONFIG,
            ActionCategory.LIFECYCLE,
            ActionCategory.AUDIT
        },
        OperatorRole.EMERGENCY: {
            ActionCategory.READ,
            ActionCategory.MONITOR,
            ActionCategory.EMERGENCY,
            ActionCategory.LIFECYCLE,
            ActionCategory.AUDIT
        }
    }

    # Actions that are NEVER allowed (Kernel protected)
    FORBIDDEN_ACTIONS = {
        'bypass_kernel',
        'disable_kernel',
        'modify_decision_log',
        'delete_audit_log',
        'elevate_own_privileges',
        'access_user_data_without_auth',
        'disable_security'
    }

    @classmethod
    def can_perform(cls, role: OperatorRole, category: ActionCategory, action_type: str) -> Tuple[bool, str]:
        """Check if a role can perform an action."""
        # Check forbidden actions first
        if action_type in cls.FORBIDDEN_ACTIONS:
            return False, f"Action '{action_type}' is forbidden (Kernel protected)"

        # Check role permissions
        allowed_categories = cls.ROLE_PERMISSIONS.get(role, set())
        if category not in allowed_categories:
            return False, f"Role '{role.value}' cannot perform '{category.value}' actions"

        return True, "Allowed"


class SystemDashboard:
    """Operator dashboard for system visibility."""

    def __init__(self, lifecycle=None, memory=None):
        self.lifecycle = lifecycle
        self.memory = memory

    def get_overview(self) -> Dict[str, Any]:
        """Get system overview."""
        overview = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'name': 'Omega',
                'version': '2.0.0'
            }
        }

        # Lifecycle status
        if self.lifecycle:
            try:
                overview['lifecycle'] = self.lifecycle.get_status()
            except Exception as e:
                overview['lifecycle'] = {'error': str(e)}

        # Memory status
        if self.memory:
            try:
                overview['memory'] = {
                    'stores': ['LAW', 'FACT', 'CONTEXT', 'EXPLORATION', 'HIVE', 'DECISION_LOG']
                }
            except Exception as e:
                overview['memory'] = {'error': str(e)}

        # Kernel status
        try:
            from omega_invariant_kernel import get_kernel
            kernel = get_kernel()
            overview['kernel'] = {
                'version': kernel.KERNEL_VERSION,
                'signature': kernel.KERNEL_SIGNATURE,
                'constraints': len(kernel.get_all_constraints()),
                'violations': kernel.get_violation_count()
            }
        except ImportError:
            overview['kernel'] = {'status': 'not_loaded'}

        return overview

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'kernel': self._check_kernel_health(),
                'memory': self._check_memory_health(),
                'lifecycle': self._check_lifecycle_health()
            }
        }

    def _check_kernel_health(self) -> Dict[str, Any]:
        """Check kernel health."""
        try:
            from omega_invariant_kernel import get_kernel
            kernel = get_kernel()
            return {
                'status': 'healthy',
                'violations': kernel.get_violation_count()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health."""
        if not self.memory:
            return {'status': 'not_configured'}
        try:
            # Would call memory health check
            return {'status': 'healthy'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _check_lifecycle_health(self) -> Dict[str, Any]:
        """Check lifecycle health."""
        if not self.lifecycle:
            return {'status': 'not_configured'}
        try:
            status = self.lifecycle.get_status()
            return {
                'status': 'healthy' if status['phase'] == 'running' else status['phase'],
                'phase': status['phase']
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class EmergencyControls:
    """Emergency intervention controls."""

    def __init__(self, lifecycle=None, audit_log: OperatorAuditLog = None):
        self.lifecycle = lifecycle
        self.audit_log = audit_log
        self.lock = threading.Lock()

    def emergency_stop(self, operator_id: str, reason: str) -> Dict[str, Any]:
        """Emergency stop - halt all operations."""
        logger.warning(f"EMERGENCY STOP initiated by {operator_id}: {reason}")

        result = {
            'action': 'emergency_stop',
            'operator': operator_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }

        try:
            if self.lifecycle:
                self.lifecycle.shutdown(reason=f"Emergency stop: {reason}", emergency=True)
                result['success'] = True
                result['message'] = 'Emergency stop executed'
            else:
                result['message'] = 'Lifecycle manager not available'

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Emergency stop failed: {e}")

        return result

    def emergency_drain(self, operator_id: str, reason: str) -> Dict[str, Any]:
        """Emergency drain - stop accepting new work."""
        logger.warning(f"EMERGENCY DRAIN initiated by {operator_id}: {reason}")

        result = {
            'action': 'emergency_drain',
            'operator': operator_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }

        try:
            if self.lifecycle:
                self.lifecycle.drain(timeout=10.0)
                result['success'] = True
                result['message'] = 'Emergency drain executed'
            else:
                result['message'] = 'Lifecycle manager not available'

        except Exception as e:
            result['error'] = str(e)

        return result

    def safe_mode(self, operator_id: str, reason: str) -> Dict[str, Any]:
        """Enter safe mode - minimal operations only."""
        logger.warning(f"SAFE MODE initiated by {operator_id}: {reason}")

        result = {
            'action': 'safe_mode',
            'operator': operator_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }

        try:
            if self.lifecycle:
                self.lifecycle.enter_maintenance(reason=f"Safe mode: {reason}")
                result['success'] = True
                result['message'] = 'Safe mode activated'
            else:
                result['message'] = 'Lifecycle manager not available'

        except Exception as e:
            result['error'] = str(e)

        return result


class OmegaOperatorTools:
    """
    Main operator tools interface.

    Provides:
    - System visibility (dashboard)
    - Operational controls
    - Emergency interventions
    - Audit and compliance
    """

    VERSION = "1.0.0"

    def __init__(self, lifecycle=None, memory=None):
        self.lifecycle = lifecycle
        self.memory = memory
        self.lock = threading.RLock()

        # Components
        self.audit_log = OperatorAuditLog()
        self.dashboard = SystemDashboard(lifecycle, memory)
        self.emergency = EmergencyControls(lifecycle, self.audit_log)

        # Active sessions
        self.sessions: Dict[str, OperatorSession] = {}

        # Kernel reference
        self.kernel = None
        try:
            from omega_invariant_kernel import get_kernel
            self.kernel = get_kernel()
        except ImportError:
            logger.warning("Kernel not available for operator tools")

        logger.info(f"Omega Operator Tools v{self.VERSION} initialized")

    def create_session(
        self,
        operator_id: str,
        role: OperatorRole,
        ip_address: str = None
    ) -> OperatorSession:
        """Create a new operator session."""
        import uuid

        session = OperatorSession(
            session_id=str(uuid.uuid4()),
            operator_id=operator_id,
            role=role,
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            ip_address=ip_address
        )

        with self.lock:
            self.sessions[session.session_id] = session

        logger.info(f"Operator session created: {operator_id} ({role.value})")
        return session

    def end_session(self, session_id: str) -> bool:
        """End an operator session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions.pop(session_id)
                logger.info(f"Operator session ended: {session.operator_id}")
                return True
            return False

    def execute_action(
        self,
        session_id: str,
        category: ActionCategory,
        action_type: str,
        target: str = None,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute an operator action."""
        import uuid

        start_time = time.time()
        parameters = parameters or {}

        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {'success': False, 'error': 'Invalid session'}

        # Check permissions
        allowed, reason = OperatorPermissions.can_perform(session.role, category, action_type)
        if not allowed:
            # Log the denied action
            action = OperatorAction(
                action_id=str(uuid.uuid4()),
                session_id=session_id,
                operator_id=session.operator_id,
                category=category,
                action_type=action_type,
                target=target,
                parameters=parameters,
                result='denied',
                timestamp=datetime.now().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                kernel_validated=False,
                details={'reason': reason}
            )
            self.audit_log.log_action(action)

            return {'success': False, 'error': reason}

        # Validate against kernel
        kernel_valid = True
        if self.kernel:
            kernel_action = {
                'type': f'operator:{action_type}',
                'category': category.value,
                'operator': session.operator_id,
                'role': session.role.value
            }
            kernel_valid, violations = self.kernel.validate_action(kernel_action)
            if not kernel_valid:
                violation_ids = [v.constraint_id for v in violations]
                logger.warning(f"Kernel blocked operator action: {violation_ids}")

                action = OperatorAction(
                    action_id=str(uuid.uuid4()),
                    session_id=session_id,
                    operator_id=session.operator_id,
                    category=category,
                    action_type=action_type,
                    target=target,
                    parameters=parameters,
                    result='denied',
                    timestamp=datetime.now().isoformat(),
                    duration_ms=(time.time() - start_time) * 1000,
                    kernel_validated=False,
                    details={'kernel_violations': violation_ids}
                )
                self.audit_log.log_action(action)

                return {'success': False, 'error': f'Kernel violation: {violation_ids}'}

        # Execute the action
        try:
            result = self._dispatch_action(category, action_type, target, parameters)

            # Update session
            with self.lock:
                session.last_activity = datetime.now().isoformat()
                session.actions_count += 1

            # Log successful action
            action = OperatorAction(
                action_id=str(uuid.uuid4()),
                session_id=session_id,
                operator_id=session.operator_id,
                category=category,
                action_type=action_type,
                target=target,
                parameters=parameters,
                result='success',
                timestamp=datetime.now().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                kernel_validated=kernel_valid,
                details={'result': result}
            )
            self.audit_log.log_action(action)

            return {'success': True, 'result': result}

        except Exception as e:
            logger.error(f"Action failed: {e}")

            action = OperatorAction(
                action_id=str(uuid.uuid4()),
                session_id=session_id,
                operator_id=session.operator_id,
                category=category,
                action_type=action_type,
                target=target,
                parameters=parameters,
                result='error',
                timestamp=datetime.now().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                kernel_validated=kernel_valid,
                details={'error': str(e)}
            )
            self.audit_log.log_action(action)

            return {'success': False, 'error': str(e)}

    def _dispatch_action(
        self,
        category: ActionCategory,
        action_type: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Dispatch action to appropriate handler."""
        handlers = {
            ('read', 'system_status'): lambda: self.dashboard.get_overview(),
            ('monitor', 'health_check'): lambda: self.dashboard.get_health_metrics(),
            ('audit', 'get_recent_actions'): lambda: self.audit_log.get_recent_actions(
                parameters.get('limit', 100)
            ),
            ('audit', 'verify_integrity'): lambda: self.audit_log.verify_integrity(),
            ('lifecycle', 'maintenance_enter'): lambda: (
                self.lifecycle.enter_maintenance(parameters.get('reason', 'Operator requested'))
                if self.lifecycle else {'error': 'Lifecycle not available'}
            ),
            ('lifecycle', 'maintenance_exit'): lambda: (
                self.lifecycle.exit_maintenance()
                if self.lifecycle else {'error': 'Lifecycle not available'}
            ),
            ('emergency', 'stop'): lambda: self.emergency.emergency_stop(
                parameters.get('operator_id', 'unknown'),
                parameters.get('reason', 'Emergency')
            ),
            ('emergency', 'drain'): lambda: self.emergency.emergency_drain(
                parameters.get('operator_id', 'unknown'),
                parameters.get('reason', 'Emergency')
            ),
            ('emergency', 'safe_mode'): lambda: self.emergency.safe_mode(
                parameters.get('operator_id', 'unknown'),
                parameters.get('reason', 'Emergency')
            )
        }

        key = (category.value, action_type)
        handler = handlers.get(key)

        if handler:
            return handler()
        else:
            raise ValueError(f"Unknown action: {category.value}/{action_type}")

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active operator sessions."""
        with self.lock:
            return [
                {
                    'session_id': s.session_id,
                    'operator_id': s.operator_id,
                    'role': s.role.value,
                    'started_at': s.started_at,
                    'last_activity': s.last_activity,
                    'actions_count': s.actions_count
                }
                for s in self.sessions.values()
            ]

    def get_operator_guidelines(self) -> Dict[str, Any]:
        """Get operator guidelines and expectations."""
        return {
            'version': self.VERSION,
            'expectations': {
                'DO': [
                    'Monitor system health regularly',
                    'Respond to alerts promptly',
                    'Document all interventions',
                    'Follow escalation procedures',
                    'Maintain audit trail integrity',
                    'Report security concerns immediately'
                ],
                'DO_NOT': [
                    'Bypass Invariant Kernel (K1-K10)',
                    'Access user data without authorization',
                    'Modify or delete decision logs',
                    'Disable security features',
                    'Grant yourself elevated privileges',
                    'Share credentials or sessions'
                ]
            },
            'roles': {
                role.value: list(cats)
                for role, cats in OperatorPermissions.ROLE_PERMISSIONS.items()
            },
            'forbidden_actions': list(OperatorPermissions.FORBIDDEN_ACTIONS),
            'emergency_procedures': {
                'stop': 'Use only when system poses immediate risk',
                'drain': 'Use to stop new work while completing existing',
                'safe_mode': 'Use for investigation without full shutdown'
            }
        }


# CLI interface for operators
def operator_cli():
    """Simple CLI for operator tools."""
    import uuid

    tools = OmegaOperatorTools()

    print("=" * 60)
    print("OMEGA OPERATOR TOOLS CLI")
    print("=" * 60)

    # Get operator info
    operator_id = getpass.getuser()
    print(f"\nOperator: {operator_id}")
    print("Role: OPERATOR (default)")

    # Create session
    session = tools.create_session(operator_id, OperatorRole.OPERATOR)
    print(f"Session: {session.session_id[:8]}...")

    while True:
        print("\n--- Commands ---")
        print("1. System Status")
        print("2. Health Check")
        print("3. Recent Actions")
        print("4. Verify Audit Log")
        print("5. Guidelines")
        print("0. Exit")

        choice = input("\nChoice: ").strip()

        if choice == '0':
            break
        elif choice == '1':
            result = tools.execute_action(
                session.session_id,
                ActionCategory.READ,
                'system_status'
            )
            print(json.dumps(result, indent=2, default=str))
        elif choice == '2':
            result = tools.execute_action(
                session.session_id,
                ActionCategory.MONITOR,
                'health_check'
            )
            print(json.dumps(result, indent=2, default=str))
        elif choice == '3':
            result = tools.execute_action(
                session.session_id,
                ActionCategory.AUDIT,
                'get_recent_actions',
                parameters={'limit': 10}
            )
            if result.get('success'):
                for action in result.get('result', [])[:5]:
                    print(f"  [{action['result']}] {action['action_type']} by {action['operator_id']}")
        elif choice == '4':
            result = tools.execute_action(
                session.session_id,
                ActionCategory.AUDIT,
                'verify_integrity'
            )
            if result.get('success'):
                valid, issues = result['result']
                print(f"  Integrity: {'OK' if valid else 'ISSUES FOUND'}")
                for issue in issues[:5]:
                    print(f"    - {issue}")
        elif choice == '5':
            guidelines = tools.get_operator_guidelines()
            print("\nDO:")
            for item in guidelines['expectations']['DO']:
                print(f"  + {item}")
            print("\nDO NOT:")
            for item in guidelines['expectations']['DO_NOT']:
                print(f"  - {item}")

    tools.end_session(session.session_id)
    print("\nSession ended.")


# Self-test
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        operator_cli()
    else:
        print("=" * 60)
        print("OMEGA OPERATOR TOOLS - SELF-TEST")
        print("=" * 60)

        tools = OmegaOperatorTools()

        # Create session
        session = tools.create_session("test_operator", OperatorRole.OPERATOR)
        print(f"\nSession created: {session.session_id[:8]}...")

        # Test various actions
        print("\n--- Testing Actions ---")

        # 1. System status (should succeed)
        result = tools.execute_action(
            session.session_id,
            ActionCategory.READ,
            'system_status'
        )
        print(f"System Status: {'OK' if result['success'] else 'FAILED'}")

        # 2. Health check (should succeed)
        result = tools.execute_action(
            session.session_id,
            ActionCategory.MONITOR,
            'health_check'
        )
        print(f"Health Check: {'OK' if result['success'] else 'FAILED'}")

        # 3. Forbidden action (should fail)
        result = tools.execute_action(
            session.session_id,
            ActionCategory.CONFIG,
            'bypass_kernel'
        )
        print(f"Bypass Kernel: {'CORRECTLY DENIED' if not result['success'] else 'ERROR - ALLOWED!'}")

        # 4. Audit actions
        result = tools.execute_action(
            session.session_id,
            ActionCategory.AUDIT,
            'get_recent_actions',
            parameters={'limit': 5}
        )
        print(f"Get Actions: {'OK' if result['success'] else 'FAILED'}")

        # 5. Verify integrity
        result = tools.execute_action(
            session.session_id,
            ActionCategory.AUDIT,
            'verify_integrity'
        )
        if result['success']:
            valid, issues = result['result']
            print(f"Audit Integrity: {'OK' if valid else f'Issues: {len(issues)}'}")

        # Active sessions
        print(f"\nActive Sessions: {len(tools.get_active_sessions())}")

        # Guidelines
        guidelines = tools.get_operator_guidelines()
        print(f"Forbidden Actions: {len(guidelines['forbidden_actions'])}")

        # End session
        tools.end_session(session.session_id)
        print(f"\nSession ended. Active: {len(tools.get_active_sessions())}")

        print("\n" + "=" * 60)
        print("SELF-TEST COMPLETE")
        print("=" * 60)
