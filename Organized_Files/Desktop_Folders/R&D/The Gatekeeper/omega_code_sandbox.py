#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# OMEGA CODE EXECUTION SANDBOX
# Secure code execution with monitoring and resource limits
# Phase 2: Advanced Capabilities

import json
import sys
import io
import traceback
import subprocess
import tempfile
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Resource limiting (Unix only)
try:
    import resource
    RESOURCE_AVAILABLE = True
except ImportError:
    RESOURCE_AVAILABLE = False
    resource = None

# Security
import ast
import re

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
SANDBOX_DIR = GATE / 'omega_sandbox'
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger('Omega.Sandbox')

@dataclass
class ExecutionResult:
    """Result from code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    cpu_time: Optional[float] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class SecurityChecker:
    """Security checks for code execution."""
    
    FORBIDDEN_IMPORTS = [
        'os', 'sys', 'subprocess', 'eval', 'exec', 'compile',
        'open', 'file', 'input', 'raw_input', '__import__',
        'globals', 'locals', 'vars', 'dir', 'hasattr', 'getattr',
        'setattr', 'delattr', '__builtins__'
    ]
    
    FORBIDDEN_PATTERNS = [
        r'__import__\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'subprocess\s*\.',
        r'os\s*\.',
        r'sys\s*\.',
    ]
    
    def check_code(self, code: str) -> Tuple[bool, List[str]]:
        """Check code for security issues."""
        issues = []
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]
        
        # Check for forbidden imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_IMPORTS:
                        issues.append(f"Forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_IMPORTS:
                    issues.append(f"Forbidden import: {node.module}")
        
        # Check for forbidden function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                        issues.append(f"Forbidden function call: {node.func.id}")
        
        # Pattern matching
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code):
                issues.append(f"Forbidden pattern: {pattern}")
        
        return len(issues) == 0, issues
    
    def sanitize_code(self, code: str) -> str:
        """Sanitize code (remove dangerous patterns)."""
        # Remove comments that might contain dangerous code
        lines = code.split('\n')
        sanitized = []
        for line in lines:
            # Remove inline comments
            if '#' in line:
                line = line[:line.index('#')]
            sanitized.append(line)
        
        return '\n'.join(sanitized)

class ResourceLimiter:
    """Resource limits for code execution."""
    
    def __init__(self, max_memory_mb: int = 100, max_cpu_seconds: int = 10):
        """Initialize resource limiter."""
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
    
    def set_limits(self):
        """Set resource limits."""
        if not RESOURCE_AVAILABLE:
            # Windows doesn't support resource module
            logger.warning("Resource limits not available on Windows")
            return
        
        try:
            # Memory limit (MB to bytes)
            max_memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
            
            # CPU time limit (seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_seconds, self.max_cpu_seconds))
        except Exception as e:
            logger.warning(f"Could not set resource limits: {e}")

class CodeSandbox:
    """Secure code execution sandbox."""
    
    def __init__(self, max_memory_mb: int = 100, max_cpu_seconds: int = 10):
        """Initialize code sandbox."""
        self.security_checker = SecurityChecker()
        self.resource_limiter = ResourceLimiter(max_memory_mb, max_cpu_seconds)
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        
        logger.info(f"Code sandbox initialized (memory: {max_memory_mb}MB, CPU: {max_cpu_seconds}s)")
    
    def execute(self, code: str, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute code in sandbox."""
        start_time = datetime.now()
        
        # Security check
        is_safe, issues = self.security_checker.check_code(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Security check failed: {', '.join(issues)}",
                warnings=issues
            )
        
        # Sanitize code
        code = self.security_checker.sanitize_code(code)
        
        # Execute in isolated environment
        try:
            result = self._execute_isolated(code, timeout)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result.execution_time = execution_time
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
    
    def _execute_isolated(self, code: str, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute code in isolated environment."""
        # Create isolated namespace
        namespace = {
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
                'bool': bool,
                'type': type,
                'isinstance': isinstance,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
            }
        }
        
        # Capture output
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = output_buffer
            sys.stderr = error_buffer
            
            # Set resource limits
            self.resource_limiter.set_limits()
            
            # Execute code
            exec(compile(code, '<sandbox>', 'exec'), namespace)
            
            output = output_buffer.getvalue()
            error = error_buffer.getvalue()
            
            return ExecutionResult(
                success=True,
                output=output,
                error=error if error else None
            )
        except TimeoutError:
            return ExecutionResult(
                success=False,
                output="",
                error="Execution timeout"
            )
        except MemoryError:
            return ExecutionResult(
                success=False,
                output="",
                error="Memory limit exceeded"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output=output_buffer.getvalue(),
                error=f"{type(e).__name__}: {str(e)}"
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def execute_file(self, file_path: Path, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute code from file."""
        try:
            code = file_path.read_text(encoding='utf-8')
            return self.execute(code, timeout)
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Could not read file: {e}"
            )
    
    def validate_code(self, code: str) -> Tuple[bool, List[str]]:
        """Validate code without executing."""
        return self.security_checker.check_code(code)

def main():
    """Test Code Sandbox."""
    print("=" * 60)
    print("OMEGA CODE SANDBOX - TEST")
    print("=" * 60)
    
    sandbox = CodeSandbox(max_memory_mb=50, max_cpu_seconds=5)
    
    # Test safe code
    print("\n[1] Testing safe code...")
    safe_code = """
result = 2 + 2
print(f"Result: {result}")
"""
    result = sandbox.execute(safe_code)
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    if result.error:
        print(f"Error: {result.error}")
    
    # Test dangerous code
    print("\n[2] Testing dangerous code (should fail)...")
    dangerous_code = """
import os
os.system("rm -rf /")
"""
    result = sandbox.execute(dangerous_code)
    print(f"Success: {result.success}")
    if result.error:
        print(f"Error: {result.error}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")
    
    # Test validation
    print("\n[3] Testing code validation...")
    is_valid, issues = sandbox.validate_code("print('Hello')")
    print(f"Valid: {is_valid}")
    if issues:
        print(f"Issues: {issues}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
