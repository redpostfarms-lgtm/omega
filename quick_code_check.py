#!/usr/bin/env python3
"""
Quick Code Check - Find and Fix Flaws
=====================================
Simple, direct check for code issues
"""

import os
import re
from pathlib import Path

def check_file(file_path):
    """Check a single file for issues"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (IOError, OSError, PermissionError, UnicodeDecodeError):
        return issues
    
    for i, line in enumerate(lines, 1):
        # Incomplete functions
        if re.search(r'def\s+\w+.*:\s*$', line) and i < len(lines):
            next_line = lines[i].strip() if i < len(lines) else ""
            if next_line in ['pass', '...']:
                issues.append(f"Line {i}: Incomplete function - only 'pass'")
            elif 'NotImplementedError' in next_line:
                issues.append(f"Line {i}: Function raises NotImplementedError")
        
        # Empty API keys
        if re.search(r'api_key\s*=\s*["\']\s*["\']', line, re.IGNORECASE):
            issues.append(f"Line {i}: Empty API key")
        
        # Critical TODOs
        if re.search(r'TODO.*critical|FIXME.*critical|BUG.*critical', line, re.IGNORECASE):
            issues.append(f"Line {i}: Critical TODO/FIXME/BUG")
    
    return issues

def main():
    """Main check"""
    print("=" * 80)
    print("QUICK CODE CHECK - Finding Flaws")
    print("=" * 80)
    print()
    
    root = Path.cwd()
    exclude_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv', 
                    'Organized_Files', '.cache', '.matplotlib', '.ollama'}
    
    issues_found = {}
    files_checked = 0
    
    # Check main Python files (not in Organized_Files)
    for file_path in root.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        
        # Skip if too deep in subdirectories
        if len(file_path.parts) > 3:
            continue
        
        files_checked += 1
        issues = check_file(file_path)
        if issues:
            issues_found[str(file_path)] = issues
    
    print(f"Files checked: {files_checked}")
    print(f"Files with issues: {len(issues_found)}")
    print()
    
    if issues_found:
        print("ISSUES FOUND:")
        print("-" * 80)
        for file_path, issues in list(issues_found.items())[:20]:  # Show first 20
            print(f"\n{file_path}:")
            for issue in issues:
                print(f"  ⚠️  {issue}")
    else:
        print("✅ No critical issues found in main code files!")
    
    print()
    print("=" * 80)
    print("Check complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
