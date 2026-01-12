# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Ownership Verification Script
# Finds hidden Easter egg signatures

import sys
import io
from pathlib import Path
import hashlib

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

# Expected signatures
EXPECTED_SIGNATURES = {
    'RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E': '.signature_rpf_2026',
    'RPF-GK-OWNER-2026-7A3F9B2C': '.ownership_proof',
}

def find_signatures():
    """Find all hidden signature files."""
    signatures_found = []
    
    # Check Gatekeeper directory
    sig_file = GATE / '.signature_rpf_2026'
    if sig_file.exists():
        with open(sig_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RPF-GK-2026-7A3F9B2C' in content:
                signatures_found.append(('Gatekeeper/.signature_rpf_2026', content[:100]))
    
    # Check Archived directory
    archived_sig = BRAIN / 'Archived' / '.ownership_proof'
    if archived_sig.exists():
        with open(archived_sig, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RPF-GK-OWNER-2026' in content:
                signatures_found.append(('Archived/.ownership_proof', content[:100]))
    
    # Check voiceprint watermark
    voiceprint_watermark = BRAIN / 'Archived' / 'voiceprint' / '.rpf_watermark'
    if voiceprint_watermark.exists():
        with open(voiceprint_watermark, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RPF-GK-VOICE-2026' in content:
                signatures_found.append(('Archived/voiceprint/.rpf_watermark', content[:80]))
    
    # Check learning marker
    learning_marker = BRAIN / 'Archived' / 'learning' / '.rpf_marker'
    if learning_marker.exists():
        with open(learning_marker, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RPF-GK-LEARN-2026' in content:
                signatures_found.append(('Archived/learning/.rpf_marker', content[:80]))
    
    # Check for embedded signatures in Python files
    for py_file in GATE.glob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'RPF-GK-2026-7A3F9B2C' in content or 'RPF-GK-OWNER-2026' in content:
                    signatures_found.append((f'{py_file.name} (embedded)', 'Found in code'))
        except:
            pass
    
    return signatures_found

def verify_ownership():
    """Verify ownership by finding signatures."""
    print("=" * 60)
    print("GATEKEEPER OWNERSHIP VERIFICATION")
    print("=" * 60)
    print("\nSearching for hidden signatures...\n")
    
    signatures = find_signatures()
    
    if signatures:
        print(f"✅ Found {len(signatures)} signature(s):\n")
        for location, preview in signatures:
            print(f"  📍 {location}")
            print(f"     {preview}...\n")
        
        print("=" * 60)
        print("✅ OWNERSHIP VERIFIED")
        print("=" * 60)
        print("\nThis system belongs to Red Post Farms, LLC")
        print("Copyright (c) 2025-2026 - All Rights Reserved")
        return True
    else:
        print("❌ No signatures found")
        print("⚠️  Ownership cannot be verified")
        return False

if __name__ == '__main__':
    verify_ownership()

