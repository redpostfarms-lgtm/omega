# -*- coding: utf-8 -*-
# Script to add copyright headers to all Python files

import sys
from pathlib import Path

GATE = Path(__file__).parent

COPYRIGHT_HEADER = """# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
"""

def add_copyright_to_file(file_path):
    """Add copyright header to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has copyright
        if 'PROPRIETARY SOFTWARE' in content or 'Copyright (c) 2025-2026' in content:
            return False, "Already has copyright"
        
        # Skip test files and utility scripts
        if file_path.name in ['test_suite.py', 'add_copyright.py', 'improve_all_quality.py']:
            return False, "Skipped (utility file)"
        
        # Find where to insert (after encoding line if present)
        if content.startswith('# -*- coding: utf-8 -*-'):
            lines = content.split('\n')
            # Insert after encoding line
            new_content = COPYRIGHT_HEADER + '\n'.join(lines[1:])
        else:
            new_content = COPYRIGHT_HEADER + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Copyright added"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Add copyright to all Python files."""
    print("=" * 60)
    print("ADDING COPYRIGHT HEADERS")
    print("=" * 60)
    
    python_files = list(GATE.glob('*.py'))
    added = 0
    skipped = 0
    
    for py_file in python_files:
        success, message = add_copyright_to_file(py_file)
        if success:
            print(f"[OK] {py_file.name}: {message}")
            added += 1
        else:
            print(f"[SKIP] {py_file.name}: {message}")
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"[OK] Added copyright to: {added} files")
    print(f"[SKIP] Skipped: {skipped} files")
    print("=" * 60)

if __name__ == '__main__':
    main()

