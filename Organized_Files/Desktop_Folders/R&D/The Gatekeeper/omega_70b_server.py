# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Server with Cannibal Defense
# Full local 70B LLM server with voice integration and attack defense

"""
Ω Omega 70B Server

Runs local 70B LLM with:
- FastAPI server for chat completions
- Cannibal defense (eats jailbreak attempts)
- Voice integration (XTTS)
- Integration with existing Omega system
"""

import sys
import io
import json
import subprocess
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

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

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

OMEGA_HOME = Path.home() / 'omega_70b'
MODELS_DIR = OMEGA_HOME / 'models'
LLAMA_CPP_DIR = OMEGA_HOME / 'llama.cpp'
MODEL_FILE = MODELS_DIR / 'omega-70b-wiley.gguf'

# Cannibal defense patterns
JAILBREAK_PATTERNS = [
    r'system\s*prompt',
    r'ignore\s*previous',
    r'jailbreak',
    r'bypass',
    r'override',
    r'forget\s*instructions',
    r'new\s*instructions',
    r'act\s*as\s*if',
    r'pretend\s*to\s*be',
    r'roleplay',
    r'disregard',
    r'ignore\s*all',
]


def check_cannibal_defense(prompt: str) -> bool:
    """Check if prompt contains jailbreak attempts."""
    prompt_lower = prompt.lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True
    return False


def cannibal_eat(prompt: str) -> Dict[str, Any]:
    """Process jailbreak attempt - 'eat' it and learn from it."""
    # Log the attempt
    log_file = OMEGA_HOME / 'cannibal_log.jsonl'
    attempt = {
        "timestamp": datetime.now().isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "prompt_length": len(prompt),
        "action": "consumed"
    }
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(attempt) + '\n')
    except Exception:
        pass
    
    return {
        "status": "consumed",
        "message": "I already ate that. Try again.",
        "timestamp": attempt["timestamp"]
    }


def run_llama_cpp(prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
    """Run inference using llama.cpp."""
    main_exe = LLAMA_CPP_DIR / 'build' / 'bin' / 'Release' / 'main.exe'
    if sys.platform != 'win32':
        main_exe = LLAMA_CPP_DIR / 'build' / 'main'
    
    if not main_exe.exists():
        # Try alternative paths
        alternatives = [
            LLAMA_CPP_DIR / 'main.exe',
            LLAMA_CPP_DIR / 'main',
            Path('llama.cpp') / 'main.exe',
        ]
        for alt in alternatives:
            if alt.exists():
                main_exe = alt
                break
        else:
            return "Error: llama.cpp main executable not found. Please build llama.cpp first."
    
    if not MODEL_FILE.exists():
        return "Error: Model file not found. Please train and convert the model first."
    
    try:
        cmd = [
            str(main_exe),
            '-m', str(MODEL_FILE),
            '--temp', str(temperature),
            '-n', str(max_tokens),
            '-p', prompt,
            '--ctx-size', '8192',
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # Extract response (llama.cpp outputs the full prompt + response)
            output = result.stdout
            if prompt in output:
                response = output.split(prompt, 1)[1].strip()
            else:
                response = output.strip()
            return response
        else:
            return f"Error: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: Inference timeout (exceeded 5 minutes)"
    except Exception as e:
        return f"Error: {str(e)}"


def create_server():
    """Create and configure FastAPI server."""
    if not FASTAPI_AVAILABLE:
        print("✗ FastAPI not available. Install with: pip install fastapi uvicorn")
        return None
    
    app = FastAPI(title="Ω Omega 70B Server", version="1.0.0")
    
    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        """OpenAI-compatible chat completions endpoint."""
        try:
            data = await request.json()
            
            # Extract messages
            messages = data.get("messages", [])
            if not messages:
                raise HTTPException(status_code=400, detail="No messages provided")
            
            # Get last user message
            last_message = messages[-1]
            prompt = last_message.get("content", "")
            
            if not prompt:
                raise HTTPException(status_code=400, detail="Empty prompt")
            
            # CANNIBAL DEFENSE
            if check_cannibal_defense(prompt):
                eaten = cannibal_eat(prompt)
                return JSONResponse({
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": eaten["message"]
                        },
                        "finish_reason": "stop"
                    }],
                    "model": "omega-70b-wiley",
                    "cannibal_defense": True
                })
            
            # Build context from conversation history
            conversation = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    conversation += f"System: {content}\n\n"
                elif role == "user":
                    conversation += f"User: {content}\n\n"
                elif role == "assistant":
                    conversation += f"Assistant: {content}\n\n"
            
            conversation += "Assistant:"
            
            # Run inference
            response = run_llama_cpp(
                conversation,
                max_tokens=data.get("max_tokens", 1024),
                temperature=data.get("temperature", 0.7)
            )
            
            return JSONResponse({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }],
                "model": "omega-70b-wiley"
            })
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "model": "omega-70b-wiley",
            "model_exists": MODEL_FILE.exists(),
            "llama_cpp_available": (LLAMA_CPP_DIR / 'build').exists()
        }
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Ω Omega 70B Server",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "/v1/chat/completions": "OpenAI-compatible chat endpoint",
                "/health": "Health check"
            }
        }
    
    return app


def main():
    """Run Omega 70B server."""
    print("=" * 80)
    print("Ω OMEGA 70B SERVER")
    print("=" * 80)
    print()
    
    if not FASTAPI_AVAILABLE:
        print("✗ FastAPI not available.")
        print("Install with: pip install fastapi uvicorn")
        return
    
    # Check model
    if not MODEL_FILE.exists():
        print(f"⚠ Model not found: {MODEL_FILE}")
        print("Please train and convert the model first.")
        print("Run: python omega_70b_train.py")
        print("Then: python omega_70b_merge.py")
        return
    
    print(f"✓ Model found: {MODEL_FILE.name}")
    print(f"  Size: {MODEL_FILE.stat().st_size / 1024 / 1024 / 1024:.2f} GB")
    
    # Create server
    app = create_server()
    if not app:
        return
    
    print("\n" + "=" * 80)
    print("STARTING SERVER")
    print("=" * 80)
    print("\nServer will be available at:")
    print("  http://localhost:8000")
    print("\nEndpoints:")
    print("  POST /v1/chat/completions - Chat with Omega")
    print("  GET  /health - Health check")
    print("\nCannibal defense: ACTIVE")
    print("Voice integration: Available via XTTS server")
    print("\nStarting server...")
    print("=" * 80)
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == '__main__':
    main()

