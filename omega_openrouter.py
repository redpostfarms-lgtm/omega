"""
Omega OpenRouter Integration
Loads OpenRouter API key from environment and provides client
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OpenRouter API key not found. Please add OPENROUTER_API_KEY to your .env file"
    )


def get_openrouter_client():
    """
    Get configured OpenRouter client
    """
    import requests

    class OpenRouterClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://openrouter.ai/api/v1"
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

        def chat_completion(self, model, messages, **kwargs):
            """
            Send chat completion request
            """
            url = f"{self.base_url}/chat/completions"
            data = {"model": model, "messages": messages, **kwargs}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

    return OpenRouterClient(OPENROUTER_API_KEY)


if __name__ == "__main__":
    print("🔑 OpenRouter API Key Configuration")
    print("=" * 50)
    print(f"✓ API Key loaded: {OPENROUTER_API_KEY[:20]}...")
    print(f"✓ Config file: {env_path}")
    print("\nUsage:")
    print("  from omega_openrouter import get_openrouter_client")
    print("  client = get_openrouter_client()")
    print("  response = client.chat_completion('openai/gpt-4', messages)")
