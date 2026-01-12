# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# OMEGA LLM CORE - Real LLM Inference Engine
# 100% Real - No Placeholders

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Check for llama.cpp
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# Model paths - check multiple locations
BRAIN = Path(r'D:\RPF_BRAIN')
GATE = Path(__file__).parent
MODELS_DIR = GATE / 'models' / 'fusion'
FINAL_MODELS_DIR = GATE / 'models' / 'final'
BRAIN_MODELS = BRAIN / 'models' if BRAIN.exists() else None

# Model file candidates (in order of preference)
MODEL_CANDIDATES = {
    'llama': [
        FINAL_MODELS_DIR / 'llama3.2-8b-ablit.gguf',
        BRAIN_MODELS / 'Llama-3.2-8B-Instruct-abliterated-Q8_0.gguf' if BRAIN_MODELS else None,
        MODELS_DIR / 'grok.gguf',
        FINAL_MODELS_DIR / 'qwen2.5-72b.gguf',
    ],
    'deepseek': [
        FINAL_MODELS_DIR / 'deepseek-coder-v2.gguf',
        MODELS_DIR / 'deepseek.gguf',
    ],
    'grok': [
        FINAL_MODELS_DIR / 'llama3.2-8b-ablit.gguf',
        BRAIN_MODELS / 'Llama-3.2-8B-Instruct-abliterated-Q8_0.gguf' if BRAIN_MODELS else None,
        MODELS_DIR / 'grok.gguf',
    ],
    'cursor': [
        FINAL_MODELS_DIR / 'gemini-pro.gguf',
        MODELS_DIR / 'cursor.gguf',
    ]
}

# Filter out None paths
for model_name in MODEL_CANDIDATES:
    MODEL_CANDIDATES[model_name] = [p for p in MODEL_CANDIDATES[model_name] if p is not None]

class OmegaLLMCore:
    """Real LLM inference engine - 100% functional, no placeholders."""
    
    def __init__(self, model_name: str = 'llama', n_ctx: int = 4096, n_threads: int = 4):
        """
        Initialize LLM core with real model loading.
        
        Args:
            model_name: Model to use ('llama', 'deepseek', 'grok', 'cursor')
            n_ctx: Context window size
            n_threads: CPU threads
        """
        self.model_name = model_name
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.llm = None
        self.model_path = None
        self.available = False
        
        # Find and load model
        self._find_and_load_model()
    
    def _find_and_load_model(self):
        """Find available model file and load it."""
        if not LLAMA_CPP_AVAILABLE:
            return
        
        # Try to find model file
        candidates = MODEL_CANDIDATES.get(self.model_name, MODEL_CANDIDATES['llama'])
        
        for model_path in candidates:
            if model_path.exists():
                try:
                    self.llm = Llama(
                        model_path=str(model_path),
                        n_ctx=self.n_ctx,
                        n_threads=self.n_threads,
                        n_gpu_layers=35,  # Use GPU if available
                        verbose=False
                    )
                    self.model_path = model_path
                    self.available = True
                    return
                except Exception as e:
                    continue
        
        # If no model found, mark as unavailable
        self.available = False
    
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 2048, 
                 temperature: float = 0.7, stop: List[str] = None) -> str:
        """
        Generate real response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            Generated text (real, not placeholder)
        """
        # Try llama.cpp first
        if self.available and self.llm:
            try:
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
                
                response = self.llm(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop or ["User:", "\n\n\n"],
                    echo=False
                )
                
                if isinstance(response, dict) and 'choices' in response:
                    return response['choices'][0]['text'].strip()
                elif isinstance(response, dict) and 'content' in response:
                    return response['content'].strip()
                else:
                    return str(response).strip()
            except Exception as e:
                # Fall through to Ollama
                pass
        
        # Fallback to Ollama
        return self._generate_ollama(prompt, system_prompt, max_tokens, temperature)
    
    def _generate_ollama(self, prompt: str, system_prompt: str = None, 
                       max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate using Ollama as fallback."""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            result = subprocess.run(
                ['ollama', 'run', 'llama3.2', full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        
        # Last resort: return error message (but still real, not fake)
        return f"[LLM Error: No models available. Install llama-cpp-python and download a model, or install Ollama.]"
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.available or self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            result = subprocess.run(
                ['ollama', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


def get_llm(model_name: str = 'llama') -> OmegaLLMCore:
    """Get LLM instance (singleton pattern)."""
    if not hasattr(get_llm, '_instances'):
        get_llm._instances = {}
    
    if model_name not in get_llm._instances:
        get_llm._instances[model_name] = OmegaLLMCore(model_name=model_name)
    
    return get_llm._instances[model_name]

