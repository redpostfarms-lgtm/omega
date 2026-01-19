"""
Omega OpenAI Integration
========================
OpenAI API integration for Omega system
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from omega_api_keys_enhanced import get_openai_key

class OpenAIIntegration:
    """OpenAI API integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_openai_key() or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY or use store_openai_key()")
        
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4"  # Default model
        self.conversation_history: List[Dict[str, str]] = []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Create a chat completion"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stream:
            payload["stream"] = True
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                stream=stream,
                timeout=30
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def _handle_stream_response(self, response) -> Dict[str, Any]:
        """Handle streaming response"""
        full_content = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    data_str = decoded[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_content += delta['content']
                    except json.JSONDecodeError:
                        pass
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": full_content
                }
            }],
            "success": True
        }
    
    def generate_response(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Generate a response to a user message"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        result = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if "choices" in result and len(result["choices"]) > 0:
            assistant_message = result["choices"][0]["message"]["content"]
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        
        return "No response generated"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()

_openai_integration = None

def get_openai_integration(api_key: Optional[str] = None) -> OpenAIIntegration:
    """Get singleton OpenAI integration instance"""
    global _openai_integration
    if _openai_integration is None:
        _openai_integration = OpenAIIntegration(api_key)
    return _openai_integration

if __name__ == "__main__":
    try:
        openai = get_openai_integration()
        
        print("OpenAI Integration Test")
        print("=" * 80)
        print()
        
        response = openai.generate_response(
            "Hello! Can you tell me a short joke?",
            system_message="You are a helpful assistant."
        )
        
        print("Response:")
        print(response)
        print()
        
        print("✅ OpenAI integration working!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please store your API key first using STORE_API_KEY.py")
    except Exception as e:
        print(f"❌ Error: {e}")
