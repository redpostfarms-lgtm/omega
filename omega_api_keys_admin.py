"""
Omega API Keys - Admin Key Management
======================================
Helper functions for managing admin API keys
"""

from omega_api_keys_enhanced import get_enhanced_api_key_manager, get_api_key_manager

def get_admin_key() -> str:
    """Get OpenAI admin API key"""
    manager = get_enhanced_api_key_manager()
    return manager.get_key("OPENAI_ADMIN")

def get_openai_key() -> str:
    """Get OpenAI API key (regular or admin)"""
    manager = get_enhanced_api_key_manager()
    
    admin_key = manager.get_key("OPENAI_ADMIN")
    if admin_key:
        return admin_key
    
    return manager.get_key("OPENAI")

def store_admin_key(api_key: str) -> bool:
    """Store OpenAI admin API key"""
    manager = get_enhanced_api_key_manager()
    return manager.store_key("OPENAI_ADMIN", api_key, "OpenAI Admin API Key")

def get_api_key(prefer_admin: bool = True) -> str:
    """
    Get API key (admin or regular)
    
    Args:
        prefer_admin: If True, prefer admin key; if False, prefer regular key
    
    Returns:
        API key string or None
    """
    manager = get_enhanced_api_key_manager()
    
    if prefer_admin:
        admin_key = manager.get_key("OPENAI_ADMIN")
        if admin_key:
            return admin_key
        
        return manager.get_key("OPENAI")
    else:
        regular_key = manager.get_key("OPENAI")
        if regular_key:
            return regular_key
        
        return manager.get_key("OPENAI_ADMIN")

if __name__ == "__main__":
    manager = get_enhanced_api_key_manager()
    
    print("API Key Status:")
    print("=" * 80)
    
    admin_key = get_admin_key()
    regular_key = manager.get_key("OPENAI")
    
    print(f"Admin Key: {'✅ STORED' if admin_key else '❌ NOT FOUND'}")
    if admin_key:
        print(f"  Length: {len(admin_key)} characters")
        print(f"  Prefix: {admin_key[:15]}...")
    
    print(f"Regular Key: {'✅ STORED' if regular_key else '❌ NOT FOUND'}")
    if regular_key:
        print(f"  Length: {len(regular_key)} characters")
        print(f"  Prefix: {regular_key[:15]}...")
    
    preferred_key = get_api_key(prefer_admin=True)
    print(f"\nPreferred Key (Admin): {'✅ AVAILABLE' if preferred_key else '❌ NOT AVAILABLE'}")
    
    print("=" * 80)
