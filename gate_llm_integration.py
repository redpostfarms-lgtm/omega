#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE LLM Integration System
Integrates with all major LLM providers for problem solving and code generation
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class GateLLMIntegration:
    """
    LLM Integration for GATE Administrator
    Supports: OpenAI, Anthropic, Google, Local models, Hugging Face
    """

    def __init__(self):
        self.root = Path(__file__).parent
        self.config_file = self.root / "config" / "llm_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.root / "data" / "gate_memory.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.memory = self.load_memory()

    def load_config(self) -> Dict:
        """Load LLM configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)

        # Default configuration
        return {
            "providers": {
                "openai": {
                    "enabled": False,
                    "api_key_env": "OPENAI_API_KEY",
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "default_model": "gpt-4"
                },
                "anthropic": {
                    "enabled": False,
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                    "default_model": "claude-3-sonnet-20240229"
                },
                "google": {
                    "enabled": False,
                    "api_key_env": "GOOGLE_API_KEY",
                    "models": ["gemini-pro"],
                    "default_model": "gemini-pro"
                },
                "local": {
                    "enabled": True,
                    "endpoint": "http://localhost:11434",  # Ollama default
                    "models": ["codellama", "mistral", "llama2"],
                    "default_model": "codellama"
                },
                "huggingface": {
                    "enabled": False,
                    "api_key_env": "HUGGINGFACE_API_KEY",
                    "models": ["codellama/CodeLlama-7b-hf"],
                    "default_model": "codellama/CodeLlama-7b-hf"
                }
            },
            "default_provider": "local",
            "temperature": 0.7,
            "max_tokens": 2000
        }

    def save_config(self):
        """Save LLM configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, indent=2)

    def load_memory(self) -> Dict:
        """Load GATE's memory"""
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)

        return {
            "problems_solved": [],
            "code_patterns": [],
            "solutions_cache": {},
            "learning_history": []
        }

    def save_memory(self):
        """Save GATE's memory"""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2, default=str)

    async def query_llm(self, prompt: str, provider: Optional[str] = None) -> str:
        """Query LLM for solution"""
        provider = provider or self.config["default_provider"]

        if provider == "openai":
            return await self.query_openai(prompt)
        elif provider == "anthropic":
            return await self.query_anthropic(prompt)
        elif provider == "google":
            return await self.query_google(prompt)
        elif provider == "local":
            return await self.query_local(prompt)
        elif provider == "huggingface":
            return await self.query_huggingface(prompt)
        else:
            return "Provider not supported"

    async def query_openai(self, prompt: str) -> str:
        """Query OpenAI API"""
        try:
            import openai

            api_key = os.getenv(self.config["providers"]["openai"]["api_key_env"])
            if not api_key:
                return "OpenAI API key not set"

            openai.api_key = api_key
            model = self.config["providers"]["openai"]["default_model"]

            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )

            return response.choices[0].message.content

        except ImportError:
            return "OpenAI library not installed. Run: pip install openai"
        except Exception as e:
            return f"OpenAI error: {str(e)}"

    async def query_anthropic(self, prompt: str) -> str:
        """Query Anthropic API"""
        try:
            import anthropic

            api_key = os.getenv(self.config["providers"]["anthropic"]["api_key_env"])
            if not api_key:
                return "Anthropic API key not set"

            client = anthropic.Anthropic(api_key=api_key)
            model = self.config["providers"]["anthropic"]["default_model"]

            response = await client.messages.create(
                model=model,
                max_tokens=self.config["max_tokens"],
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except ImportError:
            return "Anthropic library not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Anthropic error: {str(e)}"

    async def query_local(self, prompt: str) -> str:
        """Query local LLM (Ollama)"""
        try:
            import aiohttp

            endpoint = self.config["providers"]["local"]["endpoint"]
            model = self.config["providers"]["local"]["default_model"]

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "No response")
                    else:
                        return f"Local LLM error: {response.status}"

        except ImportError:
            return "aiohttp not installed. Run: pip install aiohttp"
        except Exception as e:
            return f"Local LLM error: {str(e)}"

    async def solve_problem_with_llm(self, problem: Dict) -> Dict:
        """Use LLM to solve a problem"""
        # Generate prompt
        prompt = self.generate_problem_prompt(problem)

        # Check memory first
        if prompt in self.memory["solutions_cache"]:
            return {
                "solution": self.memory["solutions_cache"][prompt],
                "source": "memory"
            }

        # Query LLM
        response = await self.query_llm(prompt)

        # Cache solution
        self.memory["solutions_cache"][prompt] = response
        self.memory["problems_solved"].append({
            "problem": problem,
            "solution": response,
            "timestamp": str(asyncio.get_event_loop().time())
        })

        self.save_memory()

        return {
            "solution": response,
            "source": "llm"
        }

    def generate_problem_prompt(self, problem: Dict) -> str:
        """Generate prompt for LLM"""
        prompt = f"""As GATE Administrator, solve this problem:

Problem Type: {problem.get('category', 'unknown')}
Severity: {problem.get('severity', 'unknown')}
Description: {problem.get('description', '')}

"""

        if 'file' in problem:
            prompt += f"File: {problem['file']}\n"

        if 'error' in problem:
            prompt += f"Error: {problem['error']}\n"

        prompt += "\nProvide a solution that can be automatically applied."

        return prompt

    def commit_to_memory(self, key: str, value: any):
        """Commit information to GATE's memory"""
        if key not in self.memory:
            self.memory[key] = []

        if isinstance(self.memory[key], list):
            self.memory[key].append(value)
        else:
            self.memory[key] = value

        self.save_memory()


# Initialize global instance
llm_integration = GateLLMIntegration()


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  GATE LLM INTEGRATION")
    print("=" * 70 + "\n")

    integration = GateLLMIntegration()

    print("Configured Providers:")
    for provider, config in integration.config["providers"].items():
        status = "✓" if config["enabled"] else "✗"
        print(f"  {status} {provider}: {config.get('default_model', 'N/A')}")

    print("\nMemory Stats:")
    print(f"  Problems solved: {len(integration.memory['problems_solved'])}")
    print(f"  Solutions cached: {len(integration.memory['solutions_cache'])}")

    # Test query
    print("\nTest Query:")
    test_prompt = "How do I fix a Python syntax error?"
    response = await integration.query_llm(test_prompt)
    print(f"Response: {response[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
