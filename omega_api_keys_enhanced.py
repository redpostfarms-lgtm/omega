"""
Omega API Keys Manager - Enhanced Secure API Key Storage
=========================================================
Enhanced with best practices, key derivation, key rotation, and multiple encryption methods
"""

import os
import json
import base64
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EnhancedAPIKeyManager:
    """Enhanced secure API key management with best practices"""
    
    def __init__(self, master_password: Optional[str] = None):
        self.keys_file = Path("api_keys.encrypted")
        self.config_file = Path("api_keys_config.json")
        self.master_key_file = Path(".master_key")
        self.backup_dir = Path("api_keys_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.primary_method = "fernet"  # Primary: Fernet (authenticated encryption)
        self.backup_method = "aesgcm"  # Backup: AES-GCM
        
        self.key_rotation_days = 90  # Rotate keys every 90 days
        self.max_key_versions = 3  # Keep 3 versions of keys
        
        self._init_encryption(master_password)
    
    def _init_encryption(self, master_password: Optional[str] = None):
        """Initialize encryption with key derivation"""
        if self.master_key_file.exists():
            with open(self.master_key_file, 'rb') as f:
                encrypted_master_key = f.read()
            
            if master_password:
                master_key = self._derive_key_from_password(master_password)
                try:
                    cipher = Fernet(master_key)
                    self.master_key = cipher.decrypt(encrypted_master_key)
                except:
                    raise ValueError("Invalid master password")
            else:
                self.master_key = encrypted_master_key
        else:
            if master_password:
                master_key = self._derive_key_from_password(master_password)
                self.master_key = Fernet.generate_key()
                
                cipher = Fernet(master_key)
                encrypted_master_key = cipher.encrypt(self.master_key)
            else:
                self.master_key = Fernet.generate_key()
                encrypted_master_key = self.master_key
            
            with open(self.master_key_file, 'wb') as f:
                f.write(encrypted_master_key)
            
            try:
                os.chmod(self.master_key_file, 0o600)
            except:
                pass
        
        self.fernet_cipher = Fernet(self.master_key)
        
        aes_key_material = hashlib.sha256(self.master_key).digest()
        self.aesgcm = AESGCM(aes_key_material[:32])  # 32 bytes for AES-256
    
    def _derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # 100k iterations (NIST recommendation)
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _generate_nonce(self) -> bytes:
        """Generate secure random nonce for AES-GCM"""
        return secrets.token_bytes(12)  # 12 bytes for AES-GCM
    
    def _hash_key(self, key: str) -> str:
        """Create a hash of the key for verification (not storage)"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _encrypt_key(self, key: str, method: str = "fernet") -> Dict[str, Any]:
        """Encrypt API key using specified method"""
        if method == "fernet":
            encrypted = self.fernet_cipher.encrypt(key.encode())
            return {
                "method": "fernet",
                "data": base64.b64encode(encrypted).decode(),
                "encrypted": True
            }
        elif method == "aesgcm":
            nonce = self._generate_nonce()
            encrypted = self.aesgcm.encrypt(nonce, key.encode(), None)
            return {
                "method": "aesgcm",
                "data": base64.b64encode(encrypted).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "encrypted": True
            }
        else:
            raise ValueError(f"Unknown encryption method: {method}")
    
    def _decrypt_key(self, encrypted_data: Dict[str, Any]) -> str:
        """Decrypt API key using stored method"""
        method = encrypted_data.get("method", "fernet")
        
        if method == "fernet":
            encrypted = base64.b64decode(encrypted_data["data"].encode())
            decrypted = self.fernet_cipher.decrypt(encrypted)
            return decrypted.decode()
        elif method == "aesgcm":
            encrypted = base64.b64decode(encrypted_data["data"].encode())
            nonce = base64.b64decode(encrypted_data["nonce"].encode())
            decrypted = self.aesgcm.decrypt(nonce, encrypted, None)
            return decrypted.decode()
        else:
            raise ValueError(f"Unknown decryption method: {method}")
    
    def store_key(self, service: str, api_key: str, description: str = "", 
                  rotation_enabled: bool = True) -> bool:
        """Store an API key securely with versioning"""
        try:
            keys_data = self._load_keys()
            
            encrypted_data = self._encrypt_key(api_key, self.primary_method)
            
            if service.upper() not in keys_data:
                keys_data[service.upper()] = {
                    "versions": [],
                    "current_version": 0,
                    "description": description,
                    "rotation_enabled": rotation_enabled,
                    "created": datetime.now().isoformat()
                }
            
            service_data = keys_data[service.upper()]
            
            version_data = {
                "version": len(service_data["versions"]) + 1,
                "encrypted_key": encrypted_data,
                "created": datetime.now().isoformat(),
                "hash": self._hash_key(api_key)
            }
            
            service_data["versions"].append(version_data)
            service_data["current_version"] = len(service_data["versions"])
            service_data["updated"] = datetime.now().isoformat()
            
            if len(service_data["versions"]) > self.max_key_versions:
                service_data["versions"] = service_data["versions"][-self.max_key_versions:]
            
            self._save_keys(keys_data)
            
            self._create_backup()
            
            os.environ[f"{service.upper()}_API_KEY"] = api_key
            
            return True
        except Exception as e:
            print(f"Error storing API key: {e}")
            return False
    
    def get_key(self, service: str, version: Optional[int] = None) -> Optional[str]:
        """Retrieve an API key (latest version by default)"""
        try:
            env_key = os.getenv(f"{service.upper()}_API_KEY")
            if env_key and not version:
                return env_key
            
            keys_data = self._load_keys()
            service_upper = service.upper()
            
            if service_upper in keys_data:
                service_data = keys_data[service_upper]
                versions = service_data.get("versions", [])
                
                if not versions:
                    return None
                
                if version:
                    version_data = next((v for v in versions if v["version"] == version), None)
                else:
                    version_data = versions[-1]  # Latest version
                
                if version_data:
                    encrypted_data = version_data["encrypted_key"]
                    decrypted_key = self._decrypt_key(encrypted_data)
                    return decrypted_key
            
            return None
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None
    
    def rotate_key(self, service: str, new_api_key: str) -> bool:
        """Rotate API key (add new version)"""
        return self.store_key(service, new_api_key)
    
    def check_key_rotation(self, service: str) -> bool:
        """Check if key needs rotation"""
        keys_data = self._load_keys()
        service_upper = service.upper()
        
        if service_upper not in keys_data:
            return False
        
        service_data = keys_data[service_upper]
        if not service_data.get("rotation_enabled", True):
            return False
        
        versions = service_data.get("versions", [])
        if not versions:
            return False
        
        latest_version = versions[-1]
        created = datetime.fromisoformat(latest_version["created"])
        age = datetime.now() - created
        
        return age.days >= self.key_rotation_days
    
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
    
    def _create_backup(self):
        """Create backup of keys file"""
        if self.keys_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"api_keys_backup_{timestamp}.json"
            
            try:
                import shutil
                shutil.copy2(self.keys_file, backup_file)
                
                backups = sorted(self.backup_dir.glob("api_keys_backup_*.json"))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_backup.unlink()
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
    
    def list_services(self) -> Dict[str, bool]:
        """List all stored services"""
        keys_data = self._load_keys()
        return {service: len(keys_data[service].get("versions", [])) > 0 
                for service in keys_data.keys()}
    
    def verify_key(self, service: str) -> bool:
        """Verify if a key exists and is valid"""
        key = self.get_key(service)
        return key is not None and len(key) > 0
    
    def get_key_info(self, service: str) -> Optional[Dict[str, Any]]:
        """Get information about stored key"""
        keys_data = self._load_keys()
        service_upper = service.upper()
        
        if service_upper in keys_data:
            service_data = keys_data[service_upper]
            versions = service_data.get("versions", [])
            
            if versions:
                latest = versions[-1]
                created = datetime.fromisoformat(latest["created"])
                age = datetime.now() - created
                
                return {
                    "service": service_upper,
                    "description": service_data.get("description", ""),
                    "version_count": len(versions),
                    "current_version": service_data.get("current_version", 0),
                    "created": latest["created"],
                    "age_days": age.days,
                    "rotation_enabled": service_data.get("rotation_enabled", True),
                    "needs_rotation": age.days >= self.key_rotation_days
                }
        
        return None

_enhanced_api_key_manager = None

def get_enhanced_api_key_manager(master_password: Optional[str] = None) -> EnhancedAPIKeyManager:
    """Get singleton enhanced API key manager instance"""
    global _enhanced_api_key_manager
    if _enhanced_api_key_manager is None:
        _enhanced_api_key_manager = EnhancedAPIKeyManager(master_password)
    return _enhanced_api_key_manager

def get_api_key_manager() -> EnhancedAPIKeyManager:
    """Get API key manager (enhanced version)"""
    return get_enhanced_api_key_manager()

def store_openai_key(api_key: str, master_password: Optional[str] = None) -> bool:
    """Store OpenAI API key"""
    manager = get_enhanced_api_key_manager(master_password)
    return manager.store_key("OPENAI", api_key, "OpenAI API Key for Omega System")
    
def get_openai_key(master_password: Optional[str] = None) -> Optional[str]:
    """Get OpenAI API key"""
    manager = get_enhanced_api_key_manager(master_password)
    return manager.get_key("OPENAI")

if __name__ == "__main__":
    manager = get_enhanced_api_key_manager()
    
    test_key = "sk-test-key-12345"
    if manager.store_key("OPENAI", test_key, "Test OpenAI Key"):
        print("✅ API key stored successfully")
    
    retrieved = manager.get_key("OPENAI")
    if retrieved == test_key:
        print("✅ API key retrieved successfully")
    else:
        print("❌ API key retrieval failed")
    
    info = manager.get_key_info("OPENAI")
    if info:
        print(f"✅ Key info: {info}")
