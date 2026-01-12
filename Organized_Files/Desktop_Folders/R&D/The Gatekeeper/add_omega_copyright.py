# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Script to add copyright headers to files missing them

"""
Add copyright headers to Python files that are missing them.
Specifically ensures Omega trademark protection.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(__file__).parent

COPYRIGHT_HEADER = """# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
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
    """Add copyright to files missing it."""
    print("=" * 80)
    print("ADDING OMEGA COPYRIGHT PROTECTION")
    print("=" * 80)
    
    # Files that were identified as missing copyright
    files_to_check = [
        'improve_all_quality.py',
        'play_chess_ai_vs_ai.py',
        'test_chess_ai.py',
        'test_suite.py',
        'voice_intent.py',
        'voice_multilang.py',
        'voice_noise_cancel.py',
        'voice_skills.py',
        'voice_stt_offline.py',
        'voice_tts_offline.py',
    ]
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filename in files_to_check:
        file_path = GATE / filename
        if not file_path.exists():
            print(f"⚠️  {filename}: File not found")
            continue
        
        success, message = add_copyright_to_file(file_path)
        if success:
            print(f"[OK] {filename}: {message}")
            updated += 1
        elif "Already has copyright" in message:
            print(f"[SKIP] {filename}: {message}")
            skipped += 1
        else:
            print(f"[ERROR] {filename}: {message}")
            errors += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Updated: {updated}")
    print(f"Skipped (already protected): {skipped}")
    print(f"Errors: {errors}")
    print("\n[OK] Omega copyright protection updated")

if __name__ == '__main__':
    main()

