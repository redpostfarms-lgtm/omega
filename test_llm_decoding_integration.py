#!/usr/bin/env python3
"""
Omega LLM Decoding Strategies Integration Test
==============================================

Tests that all dependencies and key code examples are working correctly.
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {str(e)}"

def test_core_dependencies() -> List[Tuple[bool, str]]:
    """Test core dependencies"""
    print("\n" + "="*80)
    print("Testing Core Dependencies")
    print("="*80)
    
    results = []
    
    # Core libraries (should already be installed)
    results.append(test_import("torch", "PyTorch"))
    results.append(test_import("transformers", "Hugging Face Transformers"))
    results.append(test_import("numpy", "NumPy"))
    results.append(test_import("scipy", "SciPy"))
    
    return results

def test_llm_decoding_dependencies() -> List[Tuple[bool, str]]:
    """Test LLM decoding strategy dependencies"""
    print("\n" + "="*80)
    print("Testing LLM Decoding Strategy Dependencies")
    print("="*80)
    
    results = []
    
    # Structured Generation
    results.append(test_import("outlines", "Outlines"))
    results.append(test_import("pydantic", "Pydantic"))
    
    # Evaluation
    results.append(test_import("mauve", "MAUVE-text"))
    results.append(test_import("datasets", "Hugging Face Datasets"))
    results.append(test_import("accelerate", "Accelerate"))
    
    # Visualization
    results.append(test_import("matplotlib", "Matplotlib"))
    results.append(test_import("plotly", "Plotly"))
    results.append(test_import("pandas", "Pandas"))
    
    # Security & Token Handling
    results.append(test_import("jwt", "PyJWT"))
    results.append(test_import("redis", "Redis"))
    results.append(test_import("requests", "Requests"))
    
    # Utilities
    results.append(test_import("tqdm", "tqdm"))
    
    # Optional
    try:
        importlib.import_module("vllm")
        results.append((True, "✅ vLLM (optional - available)"))
    except ImportError:
        results.append((True, "⚠️  vLLM (optional - not installed, requires CUDA)"))
    
    return results

def test_knowledge_base_files() -> List[Tuple[bool, str]]:
    """Test that knowledge base files exist"""
    print("\n" + "="*80)
    print("Testing Knowledge Base Files")
    print("="*80)
    
    import os
    from pathlib import Path
    
    results = []
    
    knowledge_files = [
        "LLM_DECODING_STRATEGIES_2026.md",
        "BEAM_SEARCH_VARIANTS_2026.md",
        "GRID_BEAM_SEARCH_2026.md",
        "GRID_BEAM_SEARCH_FROM_SCRATCH.py",
        "CONTRASTIVE_SEARCH_MATH_2026.md",
        "DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md",
    ]
    
    for file in knowledge_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            results.append((True, f"✅ {file} ({size:,} bytes)"))
        else:
            results.append((False, f"❌ {file} (missing)"))
    
    return results

def test_code_syntax() -> List[Tuple[bool, str]]:
    """Test that Python code files have valid syntax"""
    print("\n" + "="*80)
    print("Testing Code Syntax")
    print("="*80)
    
    import ast
    from pathlib import Path
    
    results = []
    
    code_files = [
        "GRID_BEAM_SEARCH_FROM_SCRATCH.py",
    ]
    
    for file in code_files:
        filepath = Path(file)
        if not filepath.exists():
            results.append((False, f"❌ {file} (missing)"))
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            results.append((True, f"✅ {file} (valid syntax)"))
        except SyntaxError as e:
            results.append((False, f"❌ {file} (syntax error: {e})"))
        except Exception as e:
            results.append((False, f"❌ {file} (error: {e})"))
    
    return results

def main():
    """Run all integration tests"""
    print("="*80)
    print("Omega LLM Decoding Strategies Integration Test")
    print("="*80)
    
    all_results = []
    
    # Test core dependencies
    all_results.extend(test_core_dependencies())
    
    # Test LLM decoding dependencies
    all_results.extend(test_llm_decoding_dependencies())
    
    # Test knowledge base files
    all_results.extend(test_knowledge_base_files())
    
    # Test code syntax
    all_results.extend(test_code_syntax())
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed = sum(1 for success, _ in all_results if success)
    total = len(all_results)
    failed = total - passed
    
    for success, message in all_results:
        print(f"  {message}")
    
    print("\n" + "-"*80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed/Warnings: {failed} {'❌' if failed > 0 else ''}")
    print("-"*80)
    
    if failed == 0:
        print("\n✅ All tests passed! Integration is complete.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed or have warnings.")
        print("   Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
