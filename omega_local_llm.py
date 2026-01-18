#!/usr/bin/env python3
"""
Omega Local LLM Integration
===========================
Run Llama 3.2 locally via Ollama or LM Studio
Integrates with omega_full_brain.py for offline AI capabilities
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Generator
from pathlib import Path
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM configuration"""
    backend: str = "ollama"  # "ollama" or "lmstudio"
    model: str = "llama3.2"  # Default model
    host: str = "http://localhost:11434"  # Ollama default
    temperature: float = 0.7
    max_tokens: int = 512
    timeout: int = 30


class LocalLLM:
    """Local LLM interface with Ollama/LM Studio support"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize local LLM

        Args:
            config: LLM configuration (uses defaults if None)
        """
        self.config = config or LLMConfig()
        self.available = False
        self.client = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize LLM backend"""
        if self.config.backend == "ollama":
            self._initialize_ollama()
        elif self.config.backend == "lmstudio":
            self._initialize_lmstudio()
        else:
            print(f"[LLM] Unknown backend: {self.config.backend}")

    def _initialize_ollama(self) -> None:
        """Initialize Ollama client"""
        try:
            import ollama
            self.client = ollama
            self.available = True
            print(f"[LLM] Ollama initialized - {self.config.model}")
        except ImportError:
            print("[LLM] Ollama not installed. Install: py -3.11 -m pip install ollama")
            print("[LLM] Also install Ollama: https://ollama.ai/download")
            self.available = False
        except Exception as e:
            print(f"[LLM] Error initializing Ollama: {e}")
            self.available = False

    def _initialize_lmstudio(self) -> None:
        """Initialize LM Studio client"""
        try:
            import openai
            # LM Studio uses OpenAI-compatible API
            self.client = openai.OpenAI(base_url=self.config.host)
            self.available = True
            print(f"[LLM] LM Studio initialized - {self.config.model}")
        except ImportError:
            print("[LLM] OpenAI library not installed. Install: py -3.11 -m pip install openai")
            self.available = False
        except Exception as e:
            print(f"[LLM] Error initializing LM Studio: {e}")
            self.available = False

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                stream: bool = False) -> str:
        """
        Generate text from prompt

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            stream: Stream response (not implemented yet)

        Returns:
            Generated text
        """
        if not self.available:
            return "[LLM unavailable - install Ollama or LM Studio]"

        try:
            if self.config.backend == "ollama":
                return self._generate_ollama(prompt, system_prompt)
            elif self.config.backend == "lmstudio":
                return self._generate_lmstudio(prompt, system_prompt)
        except Exception as e:
            print(f"[LLM] Generation error: {e}")
            return f"[Error: {e}]"

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using Ollama"""
        messages = []

        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })

        messages.append({
            'role': 'user',
            'content': prompt
        })

        response = self.client.chat(
            model=self.config.model,
            messages=messages,
            options={
                'temperature': self.config.temperature,
                'num_predict': self.config.max_tokens
            }
        )

        return response['message']['content']

    def _generate_lmstudio(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using LM Studio"""
        messages = []

        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })

        messages.append({
            'role': 'user',
            'content': prompt
        })

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        return response.choices[0].message.content

    async def generate_async(self, prompt: str,
                            system_prompt: Optional[str] = None) -> str:
        """
        Async generation (runs in executor)

        Args:
            prompt: User prompt
            system_prompt: System prompt

        Returns:
            Generated text
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate,
            prompt,
            system_prompt
        )

    def check_model_installed(self) -> bool:
        """Check if model is installed"""
        if not self.available:
            return False

        try:
            if self.config.backend == "ollama":
                models = self.client.list()
                model_names = [m['name'] for m in models['models']]
                return any(self.config.model in name for name in model_names)
        except Exception as e:
            print(f"[LLM] Error checking model: {e}")
            return False

        return True

    def pull_model(self) -> bool:
        """Download model if not installed"""
        if not self.available:
            return False

        try:
            if self.config.backend == "ollama":
                print(f"[LLM] Downloading {self.config.model}...")
                self.client.pull(self.config.model)
                print(f"[LLM] ✓ Model downloaded")
                return True
        except Exception as e:
            print(f"[LLM] Error downloading model: {e}")
            return False

        return False


class OmegaBrainLLM:
    """Integration bridge between Omega and Local LLM"""

    def __init__(self):
        """Initialize Omega Brain LLM"""
        self.llm = LocalLLM()
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10

    def process_voice_input(self, user_text: str, emotion: str = "neutral") -> str:
        """
        Process voice input and generate response

        Args:
            user_text: User's spoken text
            emotion: Detected emotion

        Returns:
            AI response
        """
        if not self.llm.available:
            return "Local AI unavailable. Using fallback response."

        # Build context-aware prompt
        system_prompt = self._build_system_prompt(emotion)
        prompt = self._build_prompt(user_text)

        # Generate response
        response = self.llm.generate(prompt, system_prompt)

        # Update conversation history
        self.conversation_history.append({
            'user': user_text,
            'assistant': response,
            'emotion': emotion
        })

        # Trim history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        return response

    def _build_system_prompt(self, emotion: str) -> str:
        """Build system prompt with emotion awareness"""
        base_prompt = (
            "You are Omega, a helpful voice assistant. "
            "Keep responses brief (1-2 sentences) for text-to-speech. "
            "Be conversational and natural. "
        )

        emotion_prompts = {
            'happy': "The user sounds happy - respond positively and enthusiastically.",
            'sad': "The user sounds sad - respond with empathy and support.",
            'angry': "The user sounds frustrated - respond calmly and helpfully.",
            'neutral': "Respond naturally and helpfully."
        }

        return base_prompt + emotion_prompts.get(emotion, emotion_prompts['neutral'])

    def _build_prompt(self, user_text: str) -> str:
        """Build prompt with conversation history"""
        if not self.conversation_history:
            return user_text

        # Include last 3 exchanges for context
        context = "\n".join([
            f"User: {exchange['user']}\nAssistant: {exchange['assistant']}"
            for exchange in self.conversation_history[-3:]
        ])

        return f"{context}\n\nUser: {user_text}\nAssistant:"

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []


# Global LLM instance
_brain_llm = None


def get_brain_llm() -> OmegaBrainLLM:
    """Get global Omega Brain LLM instance"""
    global _brain_llm
    if _brain_llm is None:
        _brain_llm = OmegaBrainLLM()
    return _brain_llm


async def omega_llm_response(user_text: str, emotion: str = "neutral") -> str:
    """
    Get LLM response for Omega (async)

    Args:
        user_text: User's text
        emotion: Detected emotion

    Returns:
        AI response
    """
    brain = get_brain_llm()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        brain.process_voice_input,
        user_text,
        emotion
    )


def setup_ollama() -> bool:
    """
    Setup guide for Ollama

    Returns:
        True if Ollama is ready
    """
    print("=" * 70)
    print("  OLLAMA SETUP GUIDE")
    print("=" * 70)
    print()
    print("1. Download Ollama:")
    print("   https://ollama.ai/download")
    print()
    print("2. Install Ollama (run the installer)")
    print()
    print("3. Open terminal and pull Llama 3.2:")
    print("   ollama pull llama3.2")
    print()
    print("4. Test Ollama:")
    print("   ollama run llama3.2 \"Hello!\"")
    print()
    print("5. Install Python client:")
    print("   py -3.11 -m pip install ollama")
    print()
    print("=" * 70)

    # Check if already set up
    try:
        import ollama
        models = ollama.list()
        model_names = [m['name'] for m in models['models']]

        if any('llama3.2' in name for name in model_names):
            print()
            print("✓ Ollama is ready!")
            print(f"  Models available: {', '.join(model_names)}")
            return True
        else:
            print()
            print("✗ Ollama installed but llama3.2 not found")
            print("  Run: ollama pull llama3.2")
            return False
    except ImportError:
        print()
        print("✗ Ollama Python client not installed")
        print("  Run: py -3.11 -m pip install ollama")
        return False
    except Exception as e:
        print()
        print(f"✗ Ollama not running: {e}")
        print("  Make sure Ollama is installed and running")
        return False


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("  OMEGA LOCAL LLM - TEST")
    print("=" * 70)
    print()

    # Check setup
    if not setup_ollama():
        print()
        print("Please complete setup and run again")
        sys.exit(1)

    # Test generation
    print()
    print("Testing LLM generation...")
    print()

    brain = OmegaBrainLLM()

    if brain.llm.available:
        test_prompts = [
            ("Hello! How are you?", "happy"),
            ("What can you help me with?", "neutral"),
            ("Tell me a joke", "happy")
        ]

        for prompt, emotion in test_prompts:
            print(f"\nUser ({emotion}): {prompt}")
            response = brain.process_voice_input(prompt, emotion)
            print(f"Omega: {response}")

        print()
        print("=" * 70)
        print("✓ Local LLM is working!")
        print()
        print("Next steps:")
        print("  1. Integrate with omega_full_brain.py")
        print("  2. Use omega_llm_response() instead of hardcoded replies")
        print("=" * 70)
    else:
        print("✗ LLM not available")
        print("  Complete the setup steps above")
