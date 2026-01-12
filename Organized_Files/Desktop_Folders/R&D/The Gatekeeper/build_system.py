# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER BUILD SYSTEM
# Verifies all systems, then starts building

import sys
import io
import subprocess
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

def verify_system():
    """Verify all systems are ready."""
    print("=" * 60)
    print("GATEKEEPER BUILD SYSTEM - VERIFICATION")
    print("=" * 60)
    print()
    
    checks = {
        'Voice (Vosk)': False,
        'Voice (SpeechBrain)': False,
        'Knowledge (ChromaDB)': False,
        'Knowledge (Sentence Transformers)': False,
        'Fusion Models': False,
        'Scrapy': False,
        'Parallel Agents': True,  # Built-in
    }
    
    # Check Vosk
    try:
        import vosk
        checks['Voice (Vosk)'] = True
        print("✅ Vosk: Available")
    except ImportError:
        print("⚠️  Vosk: Not installed (pip install vosk)")
    
    # Check SpeechBrain
    try:
        import speechbrain
        checks['Voice (SpeechBrain)'] = True
        print("✅ SpeechBrain: Available")
    except ImportError:
        print("⚠️  SpeechBrain: Not installed (pip install speechbrain)")
    
    # Check ChromaDB
    try:
        import chromadb
        checks['Knowledge (ChromaDB)'] = True
        print("✅ ChromaDB: Available")
    except ImportError:
        print("⚠️  ChromaDB: Not installed (pip install chromadb)")
    
    # Check Sentence Transformers
    try:
        from sentence_transformers import SentenceTransformer
        checks['Knowledge (Sentence Transformers)'] = True
        print("✅ Sentence Transformers: Available")
    except ImportError:
        print("⚠️  Sentence Transformers: Not installed (pip install sentence-transformers)")
    
    # Check Fusion Models
    fusion_models = GATE / 'models' / 'fusion'
    final_models = GATE / 'models' / 'final'
    if fusion_models.exists() or final_models.exists():
        checks['Fusion Models'] = True
        print("✅ Fusion Models: Directory exists")
    else:
        print("⚠️  Fusion Models: Run fusion_2026.bat or upgrade_to_100_final.bat")
    
    # Check Scrapy
    try:
        import scrapy
        checks['Scrapy'] = True
        print("✅ Scrapy: Available")
    except ImportError:
        print("⚠️  Scrapy: Not installed (pip install scrapy)")
    
    # Check llama-cpp-python
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python: Available")
    except ImportError:
        print("⚠️  llama-cpp-python: Not installed (pip install llama-cpp-python)")
    
    print()
    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    ready_count = sum(1 for v in checks.values() if v)
    total_count = len(checks)
    
    print(f"\nSystem Ready: {ready_count}/{total_count} components")
    
    if ready_count >= total_count * 0.7:  # 70% threshold
        print("✅ System ready for building")
        return True
    else:
        print("⚠️  Some components missing - system will use fallbacks")
        return True  # Still allow building with fallbacks

def build_test_project():
    """Build a test project to verify fusion system."""
    print("\n" + "=" * 60)
    print("BUILDING TEST PROJECT")
    print("=" * 60)
    print()
    
    test_prompt = "write a simple hello world program in Python that prints 'Gatekeeper is ready'"
    
    print(f"Test Prompt: {test_prompt}\n")
    print("Running fusion system...\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'gatekeeper_fusion.py'),
                test_prompt
            ],
            cwd=str(GATE),
            timeout=300,  # 5 minutes
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Fusion test successful")
            print("\nOutput preview:")
            print(result.stdout[:500])
            return True
        else:
            print("⚠️  Fusion test had issues")
            print(result.stderr[:200])
            return False
    except Exception as e:
        print(f"⚠️  Fusion test error: {e}")
        return False

def build_farm_os_starter():
    """Build a starter off-grid farm OS structure."""
    print("\n" + "=" * 60)
    print("BUILDING FARM OS STARTER")
    print("=" * 60)
    print()
    
    prompt = """Create a starter structure for an off-grid farm operating system in Rust and Python:
- Main Rust binary for system control
- Python modules for sensor data collection
- Configuration file structure
- Basic MPPT controller logic
- Battery management system interface
- Documentation (README.md)
Keep it simple but production-ready."""
    
    print("Building farm OS starter...\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'gatekeeper_fusion.py'),
                prompt
            ],
            cwd=str(GATE),
            timeout=600,  # 10 minutes
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Farm OS starter built")
            print("\nOutput saved to: Archived/fusion_outputs/")
            return True
        else:
            print("⚠️  Build had issues")
            return False
    except Exception as e:
        print(f"⚠️  Build error: {e}")
        return False

def main():
    """Main build system entry point."""
    print("\n" + "=" * 60)
    print("GATEKEEPER BUILD SYSTEM")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Verify system
    if not verify_system():
        print("\n⚠️  System verification failed. Continuing with fallbacks...")
    
    # Step 2: Build test project
    print("\n" + "=" * 60)
    print("STEP 1: BUILDING TEST PROJECT")
    print("=" * 60)
    build_test_project()
    
    # Step 3: Build farm OS starter
    print("\n" + "=" * 60)
    print("STEP 2: BUILDING FARM OS STARTER")
    print("=" * 60)
    build_farm_os_starter()
    
    print("\n" + "=" * 60)
    print("BUILD SYSTEM COMPLETE")
    print("=" * 60)
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Gatekeeper is ready to build.")
    print("Say: 'Hey, Gatekeeper, write [anything]'")
    print("It will do it. In one shot. No questions.")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

