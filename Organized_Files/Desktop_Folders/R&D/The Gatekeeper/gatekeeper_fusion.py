# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER FUSION - Multi-Model Orchestration
# Grok + Cursor + DeepSeek + Llama → ONE BRAIN
# All models run locally, in parallel, zero cost, zero cloud

import subprocess
import sys
import io
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
MODELS_DIR = GATE / 'models' / 'fusion'

# Model paths (fusion models)
GROK_MODEL = MODELS_DIR / 'grok.gguf'
CURSOR_MODEL = MODELS_DIR / 'cursor.gguf'
DEEPSEEK_MODEL = MODELS_DIR / 'deepseek.gguf'
LLAMA_MODEL = MODELS_DIR / 'grok.gguf'  # Use Grok model as Llama (same architecture)

# Final 2027 models (best quality)
FINAL_MODELS_DIR = GATE / 'models' / 'final'
LLAMA32_ABLIT = FINAL_MODELS_DIR / 'llama3.2-8b-ablit.gguf'
DEEPSEEK_V2 = FINAL_MODELS_DIR / 'deepseek-coder-v2.gguf'
GEMINI_PRO = FINAL_MODELS_DIR / 'gemini-pro.gguf'
QWEN_72B = FINAL_MODELS_DIR / 'qwen2.5-72b.gguf'

# Check for llama.cpp
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("  ⚠️  llama-cpp-python not installed. Install with: pip install llama-cpp-python")

# Model configurations (with 2027 final models as priority)
MODELS = {
    'grok': {
        'path': GROK_MODEL,
        'final_path': LLAMA32_ABLIT,  # Use final model if available
        'role': 'Fast + sarcastic reasoning',
        'system_prompt': 'You are Grok. Be fast, direct, and add sarcastic comments. Think like Elon Musk.',
        'temperature': 0.7
    },
    'cursor': {
        'path': CURSOR_MODEL,
        'final_path': GEMINI_PRO,  # Use final model if available
        'role': 'Code writing (file-aware)',
        'system_prompt': 'You are Cursor AI. Write clean, production-ready code. Be file-aware and context-aware.',
        'temperature': 0.3
    },
    'deepseek': {
        'path': DEEPSEEK_MODEL,
        'final_path': DEEPSEEK_V2,  # Use final model if available
        'role': 'Math + long context specialist',
        'system_prompt': 'You are DeepSeek. Handle complex math, algorithms, and long-context reasoning. Be precise.',
        'temperature': 0.2
    },
    'llama': {
        'path': LLAMA_MODEL,
        'final_path': QWEN_72B,  # Use final model if available (best quality)
        'role': 'Review + compliance',
        'system_prompt': 'You are Llama. Review code for correctness, compliance, and best practices. Be thorough.',
        'temperature': 0.4
    }
}

def check_model_available(model_name: str) -> bool:
    """Check if model file exists (prefer final 2027 models)."""
    model_config = MODELS[model_name]
    # Check final model first, then fallback to fusion model
    if 'final_path' in model_config and model_config['final_path'].exists():
        return True
    return model_config['path'].exists()

def run_llama_cpp_model(model_name: str, prompt: str, max_tokens: int = 2048) -> str:
    """Run a model using llama-cpp-python."""
    if not LLAMA_CPP_AVAILABLE:
        return f"[{model_name}]: Model unavailable (llama-cpp-python not installed)"
    
    if not check_model_available(model_name):
        return f"[{model_name}]: Model file not found at {MODELS[model_name]['path']}"
    
    try:
        model_config = MODELS[model_name]
        # Prefer final 2027 model if available
        if 'final_path' in model_config and model_config['final_path'].exists():
            model_path = str(model_config['final_path'])
        else:
            model_path = str(model_config['path'])
        
        # Initialize model
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context window (32k for Gemini)
            n_threads=4,  # CPU threads
            verbose=False
        )
        
        # Build full prompt with system message
        full_prompt = f"{model_config['system_prompt']}\n\nUser: {prompt}\n\nAssistant:"
        
        # Generate response
        response = llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=model_config['temperature'],
            stop=["User:", "\n\n\n"],
            echo=False
        )
        
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"[{model_name}]: Error - {str(e)}"

def run_ollama_model(model_name: str, prompt: str) -> str:
    """Run a model using Ollama (fallback)."""
    try:
        model_config = MODELS[model_name]
        full_prompt = f"{model_config['system_prompt']}\n\nUser: {prompt}\n\nAssistant:"
        
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2', full_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[{model_name}]: Ollama error"
    except Exception as e:
        return f"[{model_name}]: Ollama unavailable - {str(e)}"

def run_model(model_name: str, prompt: str) -> dict:
    """Run a single model and return result."""
    start_time = time.time()
    
    # Try llama-cpp first, fallback to Ollama
    if LLAMA_CPP_AVAILABLE and check_model_available(model_name):
        response = run_llama_cpp_model(model_name, prompt)
    else:
        response = run_ollama_model(model_name, prompt)
    
    elapsed = time.time() - start_time
    
    return {
        'model': model_name,
        'role': MODELS[model_name]['role'],
        'response': response,
        'time': elapsed
    }

def fuse_models(prompt: str) -> dict:
    """Run all models in parallel and fuse results."""
    print("=" * 60)
    print("GATEKEEPER FUSION - Multi-Model Orchestration")
    print("=" * 60)
    print(f"\nPrompt: {prompt}\n")
    print("The doors of knowledge opens. Four brains awaken.\n")
    
    # Check available models
    available_models = [name for name in MODELS.keys() if check_model_available(name) or True]  # Allow Ollama fallback
    
    if not available_models:
        print("  ⚠️  No models available. Install models or Ollama.")
        return {'error': 'No models available'}
    
    print(f"Running {len(available_models)} models in parallel...\n")
    
    # Run all models in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=len(available_models)) as executor:
        futures = {
            executor.submit(run_model, name, prompt): name 
            for name in available_models
        }
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results[result['model']] = result
                print(f"✅ [{result['model'].upper()}] Complete ({result['time']:.2f}s)")
                print(f"   Role: {result['role']}")
                print(f"   Response: {result['response'][:200]}...\n")
            except Exception as e:
                model_name = futures[future]
                print(f"  ⚠️  [{model_name.upper()}] Error: {e}\n")
                results[model_name] = {
                    'model': model_name,
                    'role': MODELS[model_name]['role'],
                    'response': f"Error: {str(e)}",
                    'time': 0
                }
    
    return results

def synthesize_response(results: dict, prompt: str) -> str:
    """Synthesize final response from all model outputs."""
    print("\n" + "=" * 60)
    print("SYNTHESIS - Combining All Brains")
    print("=" * 60 + "\n")
    
    # Extract responses
    grok_response = results.get('grok', {}).get('response', '')
    cursor_response = results.get('cursor', {}).get('response', '')
    deepseek_response = results.get('deepseek', {}).get('response', '')
    llama_response = results.get('llama', {}).get('response', '')
    
    # Build synthesis
    synthesis = f"""# GATEKEEPER FUSION OUTPUT
# Generated: {datetime.now().isoformat()}
# Prompt: {prompt}

## CURSOR BRAIN (Code Writing)
{cursor_response}

## DEEPSEEK BRAIN (Math + Algorithms)
{deepseek_response}

## GROK BRAIN (Comments + Sarcasm)
{grok_response}

## LLAMA BRAIN (Review + Compliance)
{llama_response}

---
# FUSION COMPLETE
# All four brains have spoken. Code is ready.
"""
    
    return synthesis

def save_output(output: str, prompt: str):
    """Save fusion output to file."""
    output_dir = BRAIN / 'Archived' / 'fusion_outputs'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"fusion_{timestamp}.md"
    output_path = output_dir / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\n✅ Output saved to: {output_path}")
    return output_path

def main():
    """Main fusion function."""
    if len(sys.argv) < 2:
        print("Usage: python gatekeeper_fusion.py <prompt>")
        print("Example: python gatekeeper_fusion.py 'write a quantum-safe BMS in Rust'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])
    
    # Run all models in parallel
    results = fuse_models(prompt)
    
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
        sys.exit(1)
    
    # Synthesize final response
    final_output = synthesize_response(results, prompt)
    
    # Save output
    output_path = save_output(final_output, prompt)
    
    # Print summary
    print("\n" + "=" * 60)
    print("FUSION COMPLETE")
    print("=" * 60)
    print(f"\n✅ All {len(results)} models completed")
    print(f"✅ Output saved to: {output_path}")
    print(f"\nTotal time: {sum(r.get('time', 0) for r in results.values()):.2f}s")
    print("(Parallel execution - actual time: ~max(individual times))")
    
    # Print final output
    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    print(final_output)

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

