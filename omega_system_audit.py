#!/usr/bin/env python3
# Comprehensive System Audit and Issue Detection Agent
"""
Deep scan agent to identify potential issues, breakage flags, and integration problems.
"""
import ast
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback

class SystemAuditAgent:
    """Agent to audit Omega system for potential issues."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.missing_imports = []
        self.compatibility_issues = []
        
    def audit_imports(self, file_path: Path) -> List[Dict]:
        """Check for missing or problematic imports."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name)
                        except ImportError:
                            issues.append({
                                'type': 'missing_import',
                                'module': alias.name,
                                'file': str(file_path),
                                'line': node.lineno,
                                'severity': 'error'
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            mod = __import__(node.module, fromlist=[n.name for n in node.names])
                            for alias in node.names:
                                if not hasattr(mod, alias.name):
                                    issues.append({
                                        'type': 'missing_attribute',
                                        'module': node.module,
                                        'attribute': alias.name,
                                        'file': str(file_path),
                                        'line': node.lineno,
                                        'severity': 'error'
                                    })
                        except ImportError:
                            issues.append({
                                'type': 'missing_import',
                                'module': node.module,
                                'file': str(file_path),
                                'line': node.lineno,
                                'severity': 'error'
                            })
        except Exception as e:
            issues.append({
                'type': 'parse_error',
                'file': str(file_path),
                'error': str(e),
                'severity': 'warning'
            })
        return issues
    
    def audit_error_handling(self, file_path: Path) -> List[Dict]:
        """Check for missing error handling."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            functions_with_io = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_try = False
                    has_io = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Try):
                            has_try = True
                        if isinstance(child, (ast.Call)) and isinstance(child.func, ast.Attribute):
                            if child.func.attr in ['read', 'write', 'open', 'load', 'save', 'transcribe', 'recognize']:
                                has_io = True
                    if has_io and not has_try and len([n for n in ast.walk(node) if isinstance(n, ast.Raise)]) == 0:
                        issues.append({
                            'type': 'missing_error_handling',
                            'file': str(file_path),
                            'function': node.name,
                            'line': node.lineno,
                            'severity': 'warning'
                        })
        except Exception as e:
            pass  # Skip parse errors here
        return issues
    
    def audit_async_usage(self, file_path: Path) -> List[Dict]:
        """Check for async/await issues."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    is_async = isinstance(node, ast.AsyncFunctionDef)
                    for child in ast.walk(node):
                        if isinstance(child, ast.Await):
                            if not is_async:
                                issues.append({
                                    'type': 'await_in_sync_function',
                                    'file': str(file_path),
                                    'function': node.name,
                                    'line': child.lineno,
                                    'severity': 'error'
                                })
                        elif isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                            # Check for blocking calls in async functions
                            if is_async and child.func.attr in ['read', 'write', 'sleep']:
                                if not any(isinstance(parent, (ast.Call, ast.Await)) for parent in ast.walk(node)):
                                    issues.append({
                                        'type': 'blocking_call_in_async',
                                        'file': str(file_path),
                                        'function': node.name,
                                        'line': child.lineno,
                                        'severity': 'warning'
                                    })
        except Exception as e:
            pass
        return issues
    
    def audit_file_paths(self, file_path: Path) -> List[Dict]:
        """Check for potential file path issues."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Check for hardcoded paths
                if any(keyword in line for keyword in ['/home/', '/tmp/', 'C:\\', 'D:\\']):
                    if '#' not in line or line.index('#') > line.index(keyword):
                        issues.append({
                            'type': 'hardcoded_path',
                            'file': str(file_path),
                            'line': i,
                            'severity': 'warning',
                            'content': line.strip()
                        })
                # Check for path.join issues
                if 'path.join' in line.lower() or 'pathlib' in line.lower():
                    # This is usually fine, but flag for review
                    pass
        except Exception as e:
            pass
        return issues
    
    def audit_compatibility(self) -> List[Dict]:
        """Check for compatibility issues."""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 9):
            issues.append({
                'type': 'python_version',
                'severity': 'error',
                'message': f'Python {sys.version_info.major}.{sys.version_info.minor} detected. Requires 3.9+'
            })
        
        # Check for known problematic patterns
        core_files = [
            'omega_optimized_speech.py',
            'hands_free_omega_optimized.py',
            'omega_adaptive_improvements.py'
        ]
        
        for file_name in core_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for potential issues
                    if 'large-v2' in content and 'int8' in content:
                        # Large-v2 with int8 may have compatibility issues
                        if 'fallback' not in content.lower():
                            issues.append({
                                'type': 'compatibility_risk',
                                'file': file_name,
                                'severity': 'warning',
                                'message': 'Large-v2 with int8 quantization - ensure fallback is tested'
                            })
                    
                    # Check for WebRTC VAD frame size issues
                    if 'webrtcvad' in content:
                        if '480' in content or '30' in content:  # 30ms = 480 samples at 16kHz
                            # This should be fine, but verify
                            pass
                    
                    # Check for missing error handling around critical operations
                    if 'whisper_model.transcribe' in content:
                        if content.count('try:') < content.count('transcribe'):
                            issues.append({
                                'type': 'missing_error_handling',
                                'file': file_name,
                                'severity': 'warning',
                                'message': 'Potential missing error handling around transcribe calls'
                            })
                            
                except Exception as e:
                    issues.append({
                        'type': 'audit_error',
                        'file': file_name,
                        'severity': 'error',
                        'message': f'Could not audit file: {e}'
                    })
        
        return issues
    
    def audit_integration(self) -> List[Dict]:
        """Check for integration issues between components."""
        issues = []
        
        # Check if all required modules are importable
        required_modules = [
            'omega_optimized_speech',
            'omega_optimized_tts',
            'omega_full_brain',
            'hands_free_omega_optimized',
            'omega_adaptive_improvements'
        ]
        
        for module_name in required_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    issues.append({
                        'type': 'missing_module',
                        'module': module_name,
                        'severity': 'error',
                        'message': f'Module {module_name} not found'
                    })
            except Exception as e:
                issues.append({
                    'type': 'import_error',
                    'module': module_name,
                    'severity': 'error',
                    'message': f'Error importing {module_name}: {e}'
                })
        
        # Check for circular imports
        # This is simplified - full analysis would require dependency graph
        try:
            import omega_optimized_speech
            import hands_free_omega_optimized
            # If we get here, no immediate circular import
        except RecursionError:
            issues.append({
                'type': 'circular_import',
                'severity': 'error',
                'message': 'Circular import detected'
            })
        except Exception as e:
            pass  # Other import errors handled above
        
        return issues
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit of Omega system."""
        print("=" * 70)
        print("  OMEGA SYSTEM AUDIT - DEEP SCAN")
        print("=" * 70)
        print()
        
        all_issues = []
        all_warnings = []
        
        # Audit core files
        core_files = [
            'omega_optimized_speech.py',
            'hands_free_omega_optimized.py',
            'omega_adaptive_improvements.py',
            'omega_optimized_tts.py',
            'omega_full_brain.py'
        ]
        
        print("[AUDIT] Checking imports...")
        for file_name in core_files:
            file_path = Path(file_name)
            if file_path.exists():
                import_issues = self.audit_imports(file_path)
                all_issues.extend([i for i in import_issues if i['severity'] == 'error'])
                all_warnings.extend([i for i in import_issues if i['severity'] == 'warning'])
        
        print("[AUDIT] Checking error handling...")
        for file_name in core_files:
            file_path = Path(file_name)
            if file_path.exists():
                error_issues = self.audit_error_handling(file_path)
                all_warnings.extend(error_issues)
        
        print("[AUDIT] Checking async usage...")
        for file_name in core_files:
            file_path = Path(file_name)
            if file_path.exists():
                async_issues = self.audit_async_usage(file_path)
                all_issues.extend([i for i in async_issues if i['severity'] == 'error'])
                all_warnings.extend([i for i in async_issues if i['severity'] == 'warning'])
        
        print("[AUDIT] Checking compatibility...")
        compatibility_issues = self.audit_compatibility()
        all_issues.extend([i for i in compatibility_issues if i['severity'] == 'error'])
        all_warnings.extend([i for i in compatibility_issues if i['severity'] == 'warning'])
        
        print("[AUDIT] Checking integration...")
        integration_issues = self.audit_integration()
        all_issues.extend([i for i in integration_issues if i['severity'] == 'error'])
        all_warnings.extend([i for i in integration_issues if i['severity'] == 'warning'])
        
        return {
            'errors': all_issues,
            'warnings': all_warnings,
            'total_issues': len(all_issues) + len(all_warnings)
        }

def main():
    """Run system audit."""
    auditor = SystemAuditAgent()
    results = auditor.run_full_audit()
    
    print("\n" + "=" * 70)
    print("  AUDIT RESULTS")
    print("=" * 70)
    print(f"\nErrors Found: {len(results['errors'])}")
    print(f"Warnings Found: {len(results['warnings'])}")
    print(f"Total Issues: {results['total_issues']}")
    
    if results['errors']:
        print("\n" + "=" * 70)
        print("  ERRORS (Must Fix)")
        print("=" * 70)
        for error in results['errors']:
            print(f"\n[{error.get('type', 'unknown')}] {error.get('file', 'system')}")
            print(f"  Line {error.get('line', 'N/A')}: {error.get('message', error)}")
    
    if results['warnings']:
        print("\n" + "=" * 70)
        print("  WARNINGS (Should Review)")
        print("=" * 70)
        for warning in results['warnings'][:20]:  # Limit output
            print(f"\n[{warning.get('type', 'unknown')}] {warning.get('file', 'system')}")
            if 'line' in warning:
                print(f"  Line {warning['line']}: {warning.get('message', warning)}")
            else:
                print(f"  {warning.get('message', warning)}")
        
        if len(results['warnings']) > 20:
            print(f"\n... and {len(results['warnings']) - 20} more warnings")
    
    print("\n" + "=" * 70)
    print()
    
    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if len(results['errors']) == 0 else 1)
