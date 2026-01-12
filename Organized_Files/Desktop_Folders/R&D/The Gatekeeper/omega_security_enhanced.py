# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Security Enhanced Module

"""
Security enhancements for Omega system:
- Input sanitization
- Entropy killswitch
- Security audit logging
- Path validation
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger('OmegaSecurity')

class InputSanitizer:
    """Sanitizes and validates user input."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """Sanitize a string input."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_path(path: str, base_dir: Path) -> Path:
        """Validate and sanitize a file path."""
        # Convert to Path
        if isinstance(path, Path):
            path_obj = path
        else:
            path_obj = Path(path)
        
        # Resolve to absolute path
        try:
            resolved = path_obj.resolve()
        except (OSError, ValueError):
            raise ValueError(f"Invalid path: {path}")
        
        # Ensure it's within base directory
        try:
            resolved.relative_to(base_dir.resolve())
        except ValueError:
            raise ValueError(f"Path outside allowed directory: {path}")
        
        return resolved

class EntropyKillswitch:
    """Monitors entropy and can trigger emergency shutdown."""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.entropy_history: List[float] = []
        self.activated = False
    
    def check_entropy(self) -> float:
        """Check current entropy level."""
        try:
            # Simple entropy check using random data
            import random
            sample = bytes([random.randint(0, 255) for _ in range(100)])
            entropy = self._calculate_entropy(sample)
            self.entropy_history.append(entropy)
            
            # Keep last 100 readings
            if len(self.entropy_history) > 100:
                self.entropy_history = self.entropy_history[-100:]
            
            return entropy
        except Exception as e:
            logger.warning(f"Entropy check failed: {e}")
            return 0.5  # Default safe value
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate entropy of data."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        for count in frequencies.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy / 8.0  # Normalize to 0-1
    
    def should_kill(self) -> bool:
        """Check if killswitch should activate."""
        if self.activated:
            return True
        
        entropy = self.check_entropy()
        if entropy < self.threshold:
            logger.critical(f"Entropy below threshold: {entropy:.3f} < {self.threshold}")
            return True
        
        return False
    
    def activate(self):
        """Activate killswitch."""
        self.activated = True
        logger.critical("ENTROPY KILLSWITCH ACTIVATED")
        # In a real system, this would trigger shutdown procedures

class SecurityAuditLogger:
    """Logs security events."""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path("omega_security_audit.log")
        self.events: List[Dict[str, Any]] = []
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        
        self.events.append(event)
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write security log: {e}")
        
        logger.info(f"Security event: {event_type}")

# Global instances
SANITIZER = InputSanitizer()
KILLSWITCH = EntropyKillswitch()
AUDIT_LOGGER = SecurityAuditLogger()
