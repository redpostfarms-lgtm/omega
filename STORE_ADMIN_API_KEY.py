#!/usr/bin/env python3
"""
Store Admin API Key - Secure API Key Storage
=============================================
Securely store OpenAI admin API key for Omega system
"""

import sys
from omega_api_keys_enhanced import get_enhanced_api_key_manager, store_openai_key, get_api_key_manager

def main():
    print("=" * 80)
    print("OMEGA API KEY STORAGE - ADMIN KEY")
    print("=" * 80)
    print()
    
    # The admin API key provided
    admin_api_key = "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"
    
    print("Storing OpenAI Admin API key...")
    print("Key prefix: sk-admin-...")
    print()
    
    # Store the key
    manager = get_enhanced_api_key_manager()
    
    # Store as ADMIN key (separate from regular key)
    success = manager.store_key("OPENAI_ADMIN", admin_api_key, "OpenAI Admin API Key for Omega System")
    
    if success:
        print("✅ Admin API key stored securely")
        print("✅ Key encrypted and saved")
        print("✅ Environment variable set (OPENAI_ADMIN_API_KEY)")
        print()
        
        # Verify it was stored
        retrieved = manager.get_key("OPENAI_ADMIN")
        if retrieved:
            print("✅ Key verification: SUCCESS")
            print(f"   Key length: {len(retrieved)} characters")
            print(f"   Key prefix: {retrieved[:15]}...")
            print(f"   Key type: Admin")
        else:
            print("❌ Key verification: FAILED")
        
        # Also store as regular key if needed (for backward compatibility)
        # Uncomment if you want to replace the regular key with admin key
        # success2 = manager.store_key("OPENAI", admin_api_key, "OpenAI API Key (Admin)")
        # if success2:
        #     print("✅ Also stored as regular OPENAI key")
    else:
        print("❌ Failed to store API key")
        print("   Please check permissions and try again")
    
    print()
    print("=" * 80)
    print("API KEY STORAGE COMPLETE")
    print("=" * 80)
    print()
    print("The admin API key is now:")
    print("  ✅ Encrypted and stored securely")
    print("  ✅ Available as environment variable (OPENAI_ADMIN_API_KEY)")
    print("  ✅ Ready for use in Omega system")
    print()
    print("Note: Admin keys typically have additional permissions.")
    print("      Use this key for administrative operations.")

if __name__ == "__main__":
    main()
