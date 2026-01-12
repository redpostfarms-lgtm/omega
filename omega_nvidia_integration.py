#!/usr/bin/env python3
"""
Omega NVIDIA API Integration
============================
Integration with NVIDIA Developer Playground API
"""

import requests
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class NVIDIAIntegration:
    """NVIDIA API integration for Omega"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.invoke_url = f"{self.base_url}/chat/completions"
        
    def chat_completion(self, 
                       messages: List[Dict[str, str]],
                       model: str = "meta/llama-4-maverick-17b-128e-instruct",
                       max_tokens: int = 512,
                       temperature: float = 1.0,
                       top_p: float = 1.0,
                       frequency_penalty: float = 0.0,
                       presence_penalty: float = 0.0,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Generate chat completion using NVIDIA API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: llama-4-maverick-17b-128e-instruct)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stream: Whether to stream responses
            
        Returns:
            Response dict or stream iterator
        """
        if not self.api_key:
            raise ValueError("NVIDIA API key not set. Set NVIDIA_API_KEY environment variable or pass api_key parameter.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": stream
        }
        
        try:
            response = requests.post(self.invoke_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"NVIDIA API request failed: {e}")
    
    def _handle_stream_response(self, response):
        """Handle streaming responses"""
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    data = decoded[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a simple text response from a prompt
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for chat_completion
            
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        
        result = self.chat_completion(messages, stream=False, **kwargs)
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Unexpected response format: {result}")
    
    def conversation(self, conversation_history: List[Dict[str, str]], **kwargs) -> str:
        """
        Continue a conversation with history
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for chat_completion
            
        Returns:
            Generated response
        """
        result = self.chat_completion(conversation_history, stream=False, **kwargs)
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Unexpected response format: {result}")

# Global instance
_nvidia_integration = None

def get_nvidia_integration(api_key: Optional[str] = None) -> NVIDIAIntegration:
    """Get singleton NVIDIA integration instance"""
    global _nvidia_integration
    if _nvidia_integration is None:
        _nvidia_integration = NVIDIAIntegration(api_key)
    elif api_key:
        # Update API key if provided
        _nvidia_integration.api_key = api_key
    return _nvidia_integration

def set_nvidia_api_key(api_key: str):
    """Set NVIDIA API key globally"""
    global _nvidia_integration
    if _nvidia_integration is None:
        _nvidia_integration = NVIDIAIntegration(api_key)
    else:
        _nvidia_integration.api_key = api_key
    os.environ["NVIDIA_API_KEY"] = api_key

# Example usage
if __name__ == "__main__":
    # Load API key from environment or config
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("NVIDIA_API_KEY environment variable not set.")
        print("Set it with: export NVIDIA_API_KEY=your_key")
        print("Or pass it when creating NVIDIAIntegration instance")
    else:
        nvidia = get_nvidia_integration()
        
        # Simple prompt
        prompt = "Hello! How are you?"
        print(f"Prompt: {prompt}")
        
        try:
            response = nvidia.generate_response(prompt)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
