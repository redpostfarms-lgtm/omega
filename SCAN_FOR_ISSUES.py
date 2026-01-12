#!/usr/bin/env python3
"""
Scan for Issues in Omega Control Panel
======================================
Systematic scan for potential issues, bugs, and improvements.
"""

import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Any

def scan_file(file_path: Path) -> Dict[str, Any]:
    """Scan a Python file for potential issues"""
    issues = {
        'file': str(file_path),
        'syntax_errors': [],
        'import_errors': [],
        'exceptions': [],
        'todo_comments': [],
        'potential_issues': []
    }
    
    if not file_path.exists():
        issues['errors'] = ['File not found']
        return issues
    
    # Check syntax
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            ast.parse(code)
    except SyntaxError as e:
        issues['syntax_errors'].append({
            'line': e.lineno,
            'message': str(e)
        })
    except Exception as e:
        issues['errors'] = [str(e)]
        return issues
    
    # Scan for TODO/FIXME comments
    todo_pattern = re.compile(r'#\s*(TODO|FIXME|BUG|HACK|XXX):\s*(.+)', re.IGNORECASE)
    for i, line in enumerate(code.split('\n'), 1):
        match = todo_pattern.search(line)
        if match:
            issues['todo_comments'].append({
                'line': i,
                'type': match.group(1),
                'message': match.group(2)
            })
    
    # Scan for bare except clauses
    bare_except_pattern = re.compile(r'except\s*:', re.MULTILINE)
    for match in bare_except_pattern.finditer(code):
        # Find line number
        line_num = code[:match.start()].count('\n') + 1
        issues['exceptions'].append({
            'line': line_num,
            'type': 'bare_except',
            'message': 'Bare except clause - catches all exceptions including SystemExit and KeyboardInterrupt'
        })
    
    # Scan for except Exception: pass (silent failures)
    except_pass_pattern = re.compile(r'except\s+Exception[^:]*:\s*pass', re.MULTILINE)
    for match in except_pass_pattern.finditer(code):
        line_num = code[:match.start()].count('\n') + 1
        issues['potential_issues'].append({
            'line': line_num,
            'type': 'silent_exception',
            'message': 'Exception caught and silently ignored'
        })
    
    # Check for missing return statements in functions that should return
    # This is a simplified check - would need AST analysis for better results
    
    return issues

def scan_control_panel_files():
    """Scan control panel related files"""
    base_dir = Path(__file__).parent.absolute()
    
    files_to_scan = [
        base_dir / "omega_control_panel.py",
        base_dir / "OMEGA_UI_LAUNCHER.py",
        base_dir / "omega_control_panel_web.py"
    ]
    
    print("=" * 80)
    print(" " * 20 + "SCANNING FOR ISSUES")
    print("=" * 80)
    print()
    
    all_issues = []
    
    for file_path in files_to_scan:
        if not file_path.exists():
            print(f"⚠ File not found: {file_path.name}")
            continue
        
        print(f"Scanning: {file_path.name}")
        issues = scan_file(file_path)
        all_issues.append(issues)
        
        # Report issues
        if issues['syntax_errors']:
            print(f"  ✗ Syntax errors: {len(issues['syntax_errors'])}")
            for err in issues['syntax_errors']:
                print(f"    Line {err['line']}: {err['message']}")
        
        if issues['todo_comments']:
            print(f"  ⚠ TODO/FIXME comments: {len(issues['todo_comments'])}")
            for todo in issues['todo_comments'][:5]:  # Show first 5
                print(f"    Line {todo['line']} ({todo['type']}): {todo['message']}")
        
        if issues['exceptions']:
            print(f"  ⚠ Exception handling issues: {len(issues['exceptions'])}")
            for exc in issues['exceptions'][:5]:
                print(f"    Line {exc['line']}: {exc['message']}")
        
        if issues['potential_issues']:
            print(f"  ⚠ Potential issues: {len(issues['potential_issues'])}")
            for issue in issues['potential_issues'][:5]:
                print(f"    Line {issue['line']}: {issue['message']}")
        
        if not any([issues['syntax_errors'], issues['todo_comments'], 
                   issues['exceptions'], issues['potential_issues']]):
            print(f"  ✓ No obvious issues found")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_syntax = sum(len(i['syntax_errors']) for i in all_issues)
    total_todos = sum(len(i['todo_comments']) for i in all_issues)
    total_exceptions = sum(len(i['exceptions']) for i in all_issues)
    total_issues = sum(len(i['potential_issues']) for i in all_issues)
    
    print(f"Syntax Errors: {total_syntax}")
    print(f"TODO/FIXME Comments: {total_todos}")
    print(f"Exception Handling Issues: {total_exceptions}")
    print(f"Potential Issues: {total_issues}")
    print()
    
    if total_syntax > 0:
        print("⚠ CRITICAL: Syntax errors found - code will not run!")
    elif total_exceptions > 0 or total_issues > 0:
        print("⚠ WARNING: Some issues found - review recommended")
    else:
        print("✓ No critical issues found")
    
    return all_issues

if __name__ == "__main__":
    try:
        issues = scan_control_panel_files()
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
