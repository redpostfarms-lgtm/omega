# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
VOICE CORE V2.0 - LLM INTEGRATION
Integrate compiled voice with LLM for real-time generation
"""

import sys
import io
import argparse
from pathlib import Path
from typing import Optional

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

try:
    from omega_llm_core import get_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("[WARNING] omega_llm_core not available")

try:
    from voice_core_v2_compile import VoiceCoreV2Compiler
    COMPILER_AVAILABLE = True
except ImportError:
    COMPILER_AVAILABLE = False
    print("[WARNING] voice_core_v2_compile not available")

try:
    from omega_voice import OmegaVoice
    OMEGA_VOICE_AVAILABLE = True
except ImportError:
    OMEGA_VOICE_AVAILABLE = False
    print("[WARNING] omega_voice not available")


class VoiceCoreV2LLM:
    """Voice Core V2.0 with LLM integration."""
    
    def __init__(self, model_name: str = 'llama', voice_file: Optional[Path] = None):
        self.llm = None
        if LLM_AVAILABLE:
            try:
                self.llm = get_llm(model_name)
            except Exception as e:
                print(f"[WARNING] LLM initialization failed: {e}")
        
        self.voice = None
        if OMEGA_VOICE_AVAILABLE:
            try:
                self.voice = OmegaVoice()
            except Exception as e:
                print(f"[WARNING] Voice initialization failed: {e}")
        
        self.compiler = None
        if COMPILER_AVAILABLE:
            try:
                self.compiler = VoiceCoreV2Compiler(sample_rate=44100)
            except Exception as e:
                print(f"[WARNING] Compiler initialization failed: {e}")
        
        self.voice_file = voice_file
    
    def generate_and_speak(self, prompt: str, 
                          temperature: float = 0.7,
                          compile_voice: bool = True) -> str:
        """
        Generate response with LLM and speak with Voice Core V2.0
        
        Args:
            prompt: User prompt
            temperature: LLM temperature
            compile_voice: Whether to compile voice with V2 effects
        
        Returns:
            Generated response text
        """
        # Generate with LLM
        if not self.llm or not self.llm.is_available():
            print("[ERROR] LLM not available")
            return "[LLM not available]"
        
        print(f"[LLM] Generating response...")
        response = self.llm.generate(
            prompt=prompt,
            system_prompt="You are Omega. Be genuine, real, conversational. Not robotic.",
            max_tokens=512,
            temperature=temperature
        )
        
        if not response:
            return "[No response generated]"
        
        print(f"[LLM] Generated: {response[:100]}...")
        
        # Speak with Voice Core V2.0
        if compile_voice and self.compiler:
            # Compile voice with V2 effects
            print(f"[Voice Core V2] Compiling voice for response...")
            # Note: This would need TTS audio generation first
            # For now, use Omega Voice TTS
            if self.voice:
                self.voice.speak(response, natural=True)
        elif self.voice:
            # Use standard Omega Voice
            self.voice.speak(response, natural=True)
        else:
            # Fallback: print
            print(f"[Omega] {response}")
        
        return response
    
    def listen_and_respond(self, listen_timeout: float = 5.0):
        """Listen for input and respond (interactive mode)."""
        print("=" * 80)
        print("VOICE CORE V2.0 - LLM INTEGRATION")
        print("Interactive mode - type 'quit' to exit")
        print("=" * 80)
        
        while True:
            try:
                user_input = input("\n[You] ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("[Omega] Goodbye.")
                    break
                
                # Generate and speak response
                response = self.generate_and_speak(user_input)
                
            except KeyboardInterrupt:
                print("\n[Omega] Interrupted. Goodbye.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(description='Voice Core V2.0 LLM Integration')
    parser.add_argument('--model', type=str, default='llama', help='LLM model name')
    parser.add_argument('--voice', type=str, help='Path to compiled voice file')
    parser.add_argument('--temp', type=float, default=0.7, help='LLM temperature')
    parser.add_argument('--listen', action='store_true', help='Interactive listen mode')
    parser.add_argument('--speak', action='store_true', help='Enable voice output')
    
    args = parser.parse_args()
    
    voice_file = None
    if args.voice:
        voice_file = Path(args.voice)
        if not voice_file.exists():
            print(f"[WARNING] Voice file not found: {voice_file}")
            voice_file = None
    
    v2_llm = VoiceCoreV2LLM(model_name=args.model, voice_file=voice_file)
    
    if args.listen:
        # Interactive mode
        v2_llm.listen_and_respond()
    else:
        # Single prompt mode
        prompt = input("[You] ").strip()
        if prompt:
            response = v2_llm.generate_and_speak(prompt, temperature=args.temp)
            print(f"\n[Omega] {response}")


if __name__ == '__main__':
    main()

