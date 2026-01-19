
"""
Ω Omega Security Enhanced

Security improvements:
- Comprehensive input sanitization
- Entropy killswitch
- Enhanced sandbox isolation
- Security audit logging
"""

import os
import sys
import re
import hashlib
import secrets
import logging
import json
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime

logger = logging.getLogger('OmegaSecurity')


class InputSanitizer:
    """Comprehensive input sanitization."""
    
    DANGEROUS_PATTERNS = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'compile\s*\(',
        r'open\s*\([^)]*[\'"]w[\'"]',  # Write operations
        r'subprocess\s*\.',
        r'os\.system\s*\(',
        r'shell\s*=\s*True',
    ]
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize user input."""
        if not isinstance(user_input, str):
            return str(user_input)
        
        sanitized = user_input.replace('\\x00', '')
        
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                raise ValueError(f"Potentially dangerous input detected: {pattern}")
        
        if len(sanitized) > 10000:
            raise ValueError("Input too long")
        
        return sanitized
    
    @staticmethod
    def validate_path(path: str, allowed_base: Path) -> Path:
        """Validate and sanitize file paths."""
        try:
            resolved = Path(path).resolve()
            base = allowed_base.resolve()
            
            if not str(resolved).startswith(str(base)):
                raise ValueError(f"Path outside allowed base: {path}")
            
            return resolved
        except Exception as e:
            logger.error(f"Path validation failed: {e}")
            raise ValueError(f"Invalid path: {path}")


class EntropyKillswitch:
    """Entropy-based killswitch for emergency shutdown."""
    
    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.enabled = True
        self.entropy_history = []
    
    def check_entropy(self) -> float:
        """Check current system entropy."""
        try:
            sample = os.urandom(32)
            entropy = len(set(sample)) / len(sample)
            self.entropy_history.append(entropy)
            
            if len(self.entropy_history) > 100:
                self.entropy_history.pop(0)
            
            return entropy
        except Exception:
            return 0.5  # Default if measurement fails
    
    def should_kill(self) -> bool:
        """Determine if killswitch should activate."""
        if not self.enabled:
            return False
        
        entropy = self.check_entropy()
        
        if entropy < (1.0 - self.threshold):
            logger.critical(f"Entropy killswitch activated: entropy={entropy:.3f}")
            return True
        
        return False
    
    def activate(self):
        """Activate killswitch."""
        logger.critical("ENTROPY KILLSWITCH ACTIVATED - System shutdown")
        sys.exit(1)


class SandboxIsolation:
    """Enhanced sandbox isolation."""
    
    def __init__(self, sandbox_dir: Path):
        self.sandbox_dir = Path(sandbox_dir)
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_operations = set()
        self.blocked_operations = set()
    
    def isolate_execution(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute code in isolated sandbox."""
        InputSanitizer.sanitize_input(code)
        
        isolated_namespace = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
            },
            '__name__': '__sandbox__',
            '__file__': None,
        }
        
        blocked = ['import', 'open', 'eval', 'exec', '__import__']
        for block in blocked:
            if block in code:
                raise ValueError(f"Blocked operation: {block}")
        
        try:
            compiled = compile(code, '<sandbox>', 'exec')
            exec(compiled, isolated_namespace)
            
            return {
                "success": True,
                "result": isolated_namespace.get('result', None),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }


class SecurityAuditLogger:
    """Security audit logging."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\\n')
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")


from pathlib import Path
_GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not _GATE.exists():
    _GATE = Path.cwd() / 'The Gatekeeper'
if not _GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    _GATE = Path.cwd()

SANITIZER = InputSanitizer()
KILLSWITCH = EntropyKillswitch()
AUDIT_LOGGER = SecurityAuditLogger(_GATE / 'omega_security_audit.log')

SANDBOX = SandboxIsolation(_GATE / 'omega_sandbox')
