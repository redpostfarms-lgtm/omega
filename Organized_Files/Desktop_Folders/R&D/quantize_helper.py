#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script for model quantization
Provides alternative quantization methods if llama.cpp tools aren't available
"""
import sys
import os
from pathlib import Path

def check_llama_cpp_python():
    """Check if llama-cpp-python is available (can be used for some quantization tasks)"""
    try:
        import llama_cpp
        return True
    except ImportError:
        return False

def find_quantize_tool():
    """Find llama.cpp quantize tool in common locations"""
    possible_paths = [
        Path("./llama.cpp/build/bin/Release/quantize.exe"),
        Path("./llama.cpp/build/Release/quantize.exe"),
        Path("./llama.cpp/quantize.exe"),
        Path("./llama.cpp/quantize"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.absolute())
    
    # Check PATH
    import shutil
    quantize_exe = shutil.which("quantize.exe") or shutil.which("quantize")
    if quantize_exe:
        return quantize_exe
    
    return None

def main():
    print("=" * 60)
    print("Model Quantization Helper")
    print("=" * 60)
    print()
    
    # Check for quantize tool
    quantize_tool = find_quantize_tool()
    if quantize_tool:
        print(f"[OK] Found llama.cpp quantize tool: {quantize_tool}")
        print()
        print("You can use the batch script or run quantize directly:")
        print(f'  "{quantize_tool}" input.gguf output.gguf Q3_K_S')
    else:
        print("[X] llama.cpp quantize tool not found")
        print()
        print("Options:")
        print("  1. Build llama.cpp:")
        print("     git clone https://github.com/ggerganov/llama.cpp")
        print("     cd llama.cpp")
        print("     mkdir build && cd build")
        print("     cmake .. -DCMAKE_BUILD_TYPE=Release")
        print("     cmake --build . --config Release")
        print()
        print("  2. Download pre-built binaries from:")
        print("     https://github.com/ggerganov/llama.cpp/releases")
        print()
    
    # Check for llama-cpp-python
    if check_llama_cpp_python():
        print("[OK] llama-cpp-python is installed")
        print("  Note: llama-cpp-python can load models but doesn't include quantization")
        print("  You'll still need the llama.cpp quantize tool for conversion")
    else:
        print("[X] llama-cpp-python not installed")
        print("  Install with: pip install llama-cpp-python")
    
    print()
    print("=" * 60)
    
    # Check model files
    models_dir = Path("./models")
    if models_dir.exists():
        print("\nModels directory found. Files:")
        for model_file in models_dir.glob("*.gguf"):
            size_gb = model_file.stat().st_size / (1024**3)
            print(f"  {model_file.name} ({size_gb:.2f} GB)")
    else:
        print("\n[X] Models directory not found: ./models")

if __name__ == "__main__":
    main()
