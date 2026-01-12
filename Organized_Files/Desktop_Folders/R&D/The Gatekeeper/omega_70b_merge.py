# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Merge LoRA and Convert to GGUF
# Merges trained LoRA weights and converts to GGUF for llama.cpp

"""
Ω Omega 70B Merge Script

Merges LoRA weights into base model and converts to GGUF format
for use with llama.cpp inference.
"""

import sys
import io
import subprocess
from pathlib import Path

# Set UTF-8 encoding
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

OMEGA_HOME = Path.home() / 'omega_70b'
OUTPUT_DIR = OMEGA_HOME / 'omega-70b-wiley'
MERGED_DIR = OMEGA_HOME / 'omega-70b-wiley-merged'
MODELS_DIR = OMEGA_HOME / 'models'
LLAMA_CPP_DIR = OMEGA_HOME / 'llama.cpp'
FINAL_MODEL = MODELS_DIR / 'omega-70b-wiley.gguf'


def merge_lora():
    """Merge LoRA weights into base model."""
    print("=" * 80)
    print("MERGING LORA WEIGHTS")
    print("=" * 80)
    
    if not OUTPUT_DIR.exists():
        print(f"✗ Trained model not found: {OUTPUT_DIR}")
        print("Please run omega_70b_train.py first.")
        return False
    
    print(f"✓ Found trained model: {OUTPUT_DIR}")
    print(f"  Merging to: {MERGED_DIR}")
    
    try:
        # Use unsloth merge
        cmd = [
            sys.executable, "-m", "unsloth.merge",
            "--model", str(OUTPUT_DIR),
            "--output", str(MERGED_DIR)
        ]
        
        print("\nRunning merge...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("✓ Merge complete")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Merge failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def convert_to_gguf():
    """Convert merged model to GGUF format."""
    print("\n" + "=" * 80)
    print("CONVERTING TO GGUF")
    print("=" * 80)
    
    if not MERGED_DIR.exists():
        print(f"✗ Merged model not found: {MERGED_DIR}")
        return False
    
    convert_script = LLAMA_CPP_DIR / 'convert-hf-to-gguf.py'
    if not convert_script.exists():
        print(f"✗ Convert script not found: {convert_script}")
        print("Please ensure llama.cpp is cloned and the script exists.")
        return False
    
    print(f"✓ Found convert script: {convert_script.name}")
    print(f"  Converting to: {FINAL_MODEL}")
    
    try:
        cmd = [
            sys.executable,
            str(convert_script),
            str(MERGED_DIR),
            "--outfile", str(FINAL_MODEL),
            "--outtype", "q4_k_m"
        ]
        
        print("\nRunning conversion...")
        print("This may take 30-60 minutes...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        if FINAL_MODEL.exists():
            size_gb = FINAL_MODEL.stat().st_size / 1024 / 1024 / 1024
            print(f"\n✓ Conversion complete")
            print(f"  Model: {FINAL_MODEL.name}")
            print(f"  Size: {size_gb:.2f} GB")
            return True
        else:
            print("✗ Conversion completed but model file not found")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Conversion failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main merge and convert workflow."""
    print("=" * 80)
    print("Ω OMEGA 70B - MERGE & CONVERT")
    print("=" * 80)
    print()
    
    # Merge LoRA
    if not merge_lora():
        return
    
    # Convert to GGUF
    if not convert_to_gguf():
        return
    
    print("\n" + "=" * 80)
    print("✓ COMPLETE")
    print("=" * 80)
    print(f"\nModel ready: {FINAL_MODEL}")
    print("\nNext: Run omega_70b_server.py to start the server")


if __name__ == '__main__':
    main()

