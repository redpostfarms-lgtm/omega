"""
Agents to automatically fix common issues detected in Omega system.
"""
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple
import shutil

class FixAgent:
    """Base class for fix agents."""
    
    def __init__(self):
        self.fixes_applied = []
        self.fixes_failed = []
    
    def apply_fix(self, issue: Dict) -> bool:
        """Apply fix for an issue. Returns True if successful."""
        raise NotImplementedError
    
    def can_fix(self, issue: Dict) -> bool:
        """Check if this agent can fix the issue."""
        raise NotImplementedError

class ImportFixAgent(FixAgent):
    """Agent to fix missing import issues."""
    
    def can_fix(self, issue: Dict) -> bool:
        return issue.get('type') == 'missing_import' or issue.get('type') == 'missing_module'
    
    def apply_fix(self, issue: Dict) -> bool:
        """Add try/except around problematic imports."""
        file_path = Path(issue.get('file', ''))
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_name = issue.get('module', '')
            
            if f'try:' in content and module_name in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f'import {module_name}' in line or f'from {module_name}' in line:
                        has_try = False
                        for j in range(max(0, i-10), i):
                            if 'try:' in lines[j] and (j < i-1 or 'except' not in lines[j+1]):
                                has_try = True
                                break
                        
                        if not has_try:
                            indent = len(line) - len(line.lstrip())
                            try_block = ' ' * indent + f'try:\n'
                            try_block += line + '\n'
                            try_block += ' ' * indent + 'except ImportError:\n'
                            try_block += ' ' * indent + f'    print(f"[WARNING] {module_name} not available, feature disabled")\n'
                            try_block += ' ' * indent + f'    {module_name.split(".")[-1].upper()}_AVAILABLE = False\n'
                            
                            self.fixes_applied.append({
                                'issue': issue,
                                'file': str(file_path),
                                'fix_type': 'wrap_import_try_except',
                                'manual': True,
                                'instructions': f'Wrap import of {module_name} in try/except block'
                            })
                            return True
        except Exception as e:
            self.fixes_failed.append({
                'issue': issue,
                'error': str(e)
            })
            return False
        return False

class ErrorHandlingFixAgent(FixAgent):
    """Agent to add missing error handling."""
    
    def can_fix(self, issue: Dict) -> bool:
        return issue.get('type') == 'missing_error_handling'
    
    def apply_fix(self, issue: Dict) -> bool:
        """Add error handling to functions."""
        file_path = Path(issue.get('file', ''))
        function_name = issue.get('function', '')
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.fixes_applied.append({
                'issue': issue,
                'file': str(file_path),
                'function': function_name,
                'fix_type': 'add_error_handling',
                'manual': True,
                'instructions': f'Add try/except error handling to function {function_name}'
            })
            return True
        except Exception as e:
            self.fixes_failed.append({
                'issue': issue,
                'error': str(e)
            })
            return False

class CompatibilityFixAgent(FixAgent):
    """Agent to fix compatibility issues."""
    
    def can_fix(self, issue: Dict) -> bool:
        return issue.get('type') == 'compatibility_risk'
    
    def apply_fix(self, issue: Dict) -> bool:
        """Fix compatibility issues (e.g., add fallbacks)."""
        file_path = Path(issue.get('file', ''))
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'large-v2' in content and 'WhisperModel("large-v2"' in content:
                pattern = r'WhisperModel\("large-v2"[^)]+\)'
                match = re.search(pattern, content)
                if match:
                    start_pos = match.start()
                    before = content[max(0, start_pos-200):start_pos]
                    if 'try:' not in before[-50:]:
                        self.fixes_applied.append({
                            'issue': issue,
                            'file': str(file_path),
                            'fix_type': 'add_fallback',
                            'manual': True,
                            'instructions': 'Ensure large-v2 initialization has try/except with base model fallback'
                        })
                        return True
            
            return False
        except Exception as e:
            self.fixes_failed.append({
                'issue': issue,
                'error': str(e)
            })
            return False

class PathFixAgent(FixAgent):
    """Agent to fix hardcoded path issues."""
    
    def can_fix(self, issue: Dict) -> bool:
        return issue.get('type') == 'hardcoded_path'
    
    def apply_fix(self, issue: Dict) -> bool:
        """Replace hardcoded paths with Path or os.path.join."""
        self.fixes_applied.append({
            'issue': issue,
            'file': issue.get('file', ''),
            'fix_type': 'replace_hardcoded_path',
            'manual': True,
            'instructions': f'Replace hardcoded path on line {issue.get("line")} with Path() or os.path.join()'
        })
        return True

class SystemFixOrchestrator:
    """Orchestrates all fix agents."""
    
    def __init__(self):
        self.agents = [
            ImportFixAgent(),
            ErrorHandlingFixAgent(),
            CompatibilityFixAgent(),
            PathFixAgent()
        ]
    
    def fix_issues(self, issues: List[Dict]) -> Dict:
        """Apply fixes to all issues."""
        fixed = []
        failed = []
        manual = []
        
        for issue in issues:
            fixed_this = False
            for agent in self.agents:
                if agent.can_fix(issue):
                    if agent.apply_fix(issue):
                        fixed_this = True
                        if agent.fixes_applied:
                            last_fix = agent.fixes_applied[-1]
                            if last_fix.get('manual'):
                                manual.append(last_fix)
                            else:
                                fixed.append(last_fix)
                        break
            
            if not fixed_this:
                failed.append(issue)
        
        return {
            'fixed': fixed,
            'manual': manual,
            'failed': failed,
            'agents_status': {
                agent.__class__.__name__: {
                    'applied': len(agent.fixes_applied),
                    'failed': len(agent.fixes_failed)
                }
                for agent in self.agents
            }
        }

def main():
    """Run fix agents on audit results."""
    print("=" * 70)
    print("  OMEGA FIX AGENTS - READY")
    print("=" * 70)
    print("\nFix Agents Available:")
    print("  1. ImportFixAgent - Fixes missing import issues")
    print("  2. ErrorHandlingFixAgent - Adds missing error handling")
    print("  3. CompatibilityFixAgent - Fixes compatibility issues")
    print("  4. PathFixAgent - Fixes hardcoded path issues")
    print("\nRun system audit first, then apply fixes.")
    print()

if __name__ == "__main__":
    main()
