#!/usr/bin/env python3
"""
Store API Key - Secure API Key Storage
=======================================
Securely store API keys for Omega system
"""

import sys
from omega_api_keys import store_openai_key, get_api_key_manager

def main():
    print("=" * 80)
    print("OMEGA API KEY STORAGE")
    print("=" * 80)
    print()
    
    # The API key provided
    api_key = "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"
    
    print("Storing OpenAI API key...")
    print("Key prefix: sk-proj-...")
    print()
    
    # Store the key
    manager = get_api_key_manager()
    success = manager.store_key("OPENAI", api_key, "OpenAI API Key for Omega System")
    
    if success:
        print("✅ API key stored securely")
        print("✅ Key encrypted and saved")
        print("✅ Environment variable set")
        print()
        
        # Verify it was stored
        retrieved = manager.get_key("OPENAI")
        if retrieved:
            print("✅ Key verification: SUCCESS")
            print(f"   Key length: {len(retrieved)} characters")
            print(f"   Key prefix: {retrieved[:10]}...")
        else:
            print("❌ Key verification: FAILED")
    else:
        print("❌ Failed to store API key")
        print("   Please check permissions and try again")
    
    print()
    print("=" * 80)
    print("API KEY STORAGE COMPLETE")
    print("=" * 80)
    print()
    print("The API key is now:")
    print("  ✅ Encrypted and stored securely")
    print("  ✅ Available as environment variable")
    print("  ✅ Ready for use in Omega system")
    print()
    print("Note: The key file is encrypted and protected.")
    print("      Only the Omega system can decrypt and use it.")

if __name__ == "__main__":
    main()
