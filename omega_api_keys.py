"""
Omega API Keys Manager - Secure API Key Storage
===============================================
Secure storage and management of API keys
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import hashlib

class APIKeyManager:
    """Secure API key management"""
    
    def __init__(self):
        self.keys_file = Path("api_keys.encrypted")
        self.config_file = Path("api_keys_config.json")
        self.master_key_file = Path(".master_key")
        
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption key"""
        if self.master_key_file.exists():
            with open(self.master_key_file, 'rb') as f:
                self.master_key = f.read()
        else:
            self.master_key = Fernet.generate_key()
            with open(self.master_key_file, 'wb') as f:
                f.write(self.master_key)
            try:
                os.chmod(self.master_key_file, 0o600)
            except:
                pass  # Windows doesn't support chmod
        
        self.cipher = Fernet(self.master_key)
    
    def _hash_key(self, key: str) -> str:
        """Create a hash of the key for verification (not storage)"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def store_key(self, service: str, api_key: str, description: str = "") -> bool:
        """Store an API key securely"""
        try:
            keys_data = self._load_keys()
            
            encrypted_key = self.cipher.encrypt(api_key.encode())
            
            keys_data[service.upper()] = {
                "encrypted_key": base64.b64encode(encrypted_key).decode(),
                "description": description,
                "hash": self._hash_key(api_key),  # For verification only
                "stored": True
            }
            
            self._save_keys(keys_data)
            
            os.environ[f"{service.upper()}_API_KEY"] = api_key
            
            return True
        except Exception as e:
            print(f"Error storing API key: {e}")
            return False
    
    def get_key(self, service: str) -> Optional[str]:
        """Retrieve an API key"""
        try:
            env_key = os.getenv(f"{service.upper()}_API_KEY")
            if env_key:
                return env_key
            
            keys_data = self._load_keys()
            service_upper = service.upper()
            
            if service_upper in keys_data:
                encrypted_key_b64 = keys_data[service_upper]["encrypted_key"]
                encrypted_key = base64.b64decode(encrypted_key_b64.encode())
                decrypted_key = self.cipher.decrypt(encrypted_key)
                return decrypted_key.decode()
            
            return None
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None
    
    def _load_keys(self) -> Dict[str, Any]:
        """Load encrypted keys"""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_keys(self, keys_data: Dict[str, Any]):
        """Save encrypted keys"""
        with open(self.keys_file, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        try:
            os.chmod(self.keys_file, 0o600)
        except:
            pass
    
    def list_services(self) -> Dict[str, bool]:
        """List all stored services"""
        keys_data = self._load_keys()
        return {service: keys_data[service].get("stored", False) 
                for service in keys_data.keys()}
    
    def verify_key(self, service: str) -> bool:
        """Verify if a key exists and is valid"""
        key = self.get_key(service)
        return key is not None and len(key) > 0

_api_key_manager = None

def get_api_key_manager() -> APIKeyManager:
    """Get singleton API key manager"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

def store_openai_key(api_key: str) -> bool:
    """Store OpenAI API key"""
    manager = get_api_key_manager()
    return manager.store_key("OPENAI", api_key, "OpenAI API Key")
    
def get_openai_key() -> Optional[str]:
    """Get OpenAI API key"""
    manager = get_api_key_manager()
    return manager.get_key("OPENAI")

if __name__ == "__main__":
    manager = get_api_key_manager()
    
    test_key = "sk-test-key-12345"
    if manager.store_key("OPENAI", test_key, "Test OpenAI Key"):
        print("✅ API key stored successfully")
    
    retrieved = manager.get_key("OPENAI")
    if retrieved == test_key:
        print("✅ API key retrieved successfully")
    else:
        print("❌ API key retrieval failed")
