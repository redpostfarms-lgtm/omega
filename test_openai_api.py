#!/usr/bin/env python3
"""
Test OpenAI API Integration
============================
Test the OpenAI API with proper endpoints and models
"""

import sys
import json
import requests
from omega_api_keys_enhanced import get_openai_key

def test_openai_api():
    """Test OpenAI API connection"""
    print("=" * 80)
    print("OPENAI API TEST")
    print("=" * 80)
    print()
    
    # Get API key from secure storage
    api_key = get_openai_key()
    
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please store the key first using STORE_API_KEY.py")
        return False
    
    print(f"✅ API key retrieved (length: {len(api_key)} characters)")
    print(f"   Key prefix: {api_key[:15]}...")
    print()
    
    # Test with chat completions endpoint (standard OpenAI API)
    print("Testing OpenAI Chat Completions API...")
    print("-" * 80)
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4",  # Using standard model (gpt-5-nano doesn't exist yet)
        "messages": [
            {"role": "user", "content": "write a haiku about ai"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print(f"Endpoint: {url}")
        print(f"Model: {payload['model']}")
        print(f"Request: {payload['messages'][0]['content']}")
        print()
        print("Sending request...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print("✅ API Response:")
                print("-" * 80)
                print(content)
                print("-" * 80)
                print()
                print("✅ OpenAI API test successful!")
                return True
            else:
                print("❌ No response content in API response")
                print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to parse error
            try:
                error = response.json()
                if "error" in error:
                    print(f"Error: {error['error'].get('message', 'Unknown error')}")
                    print(f"Type: {error['error'].get('type', 'Unknown')}")
            except:
                pass
            
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_alternative_endpoint():
    """Test alternative endpoint (if /v1/responses exists)"""
    print()
    print("=" * 80)
    print("TESTING ALTERNATIVE ENDPOINT")
    print("=" * 80)
    print()
    
    api_key = get_openai_key()
    if not api_key:
        return False
    
    # Try the endpoint from the curl command (may not exist)
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4",  # Using standard model
        "input": "write a haiku about ai",
        "store": True
    }
    
    try:
        print(f"Testing endpoint: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print()
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Alternative endpoint works!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"⚠️ Alternative endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            print()
            print("Note: /v1/responses endpoint may not be available.")
            print("Using standard /v1/chat/completions endpoint is recommended.")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request error: {e}")
        print("This endpoint may not exist. Using standard endpoint is recommended.")
        return False

if __name__ == "__main__":
    # Test standard endpoint
    success = test_openai_api()
    
    # Try alternative endpoint
    test_alternative_endpoint()
    
    print()
    print("=" * 80)
    if success:
        print("✅ OPENAI API TEST COMPLETE - API WORKING")
    else:
        print("❌ OPENAI API TEST FAILED - CHECK API KEY AND NETWORK")
    print("=" * 80)
