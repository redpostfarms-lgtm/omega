#!/usr/bin/env python3
"""
Omega User Storage - Persistent User Authentication Storage
===========================================================
Persistent storage for user authentication data with role-based access control.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from werkzeug.security import generate_password_hash, check_password_hash

class UserStorage:
    """Persistent user storage for authentication"""
    
    def __init__(self, storage_file: str = "omega_users.json"):
        self.storage_file = Path(storage_file)
        self.users: Dict[str, Dict[str, Any]] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from storage file"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    self.users = json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                self.users = {}
        else:
            # Initialize with default admin user if file doesn't exist
            self._initialize_default_users()
    
    def _save_users(self):
        """Save users to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            # Set restrictive permissions (Unix-like systems)
            try:
                os.chmod(self.storage_file, 0o600)
            except:
                pass  # Windows doesn't support chmod
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def _initialize_default_users(self):
        """Initialize with default users including admin"""
        self.users = {
            'admin': {
                'password': generate_password_hash('admin2026'),
                'role': 'admin',
                'created': '2026-01-01',
                'active': True
            },
            'operator': {
                'password': generate_password_hash('op2026'),
                'role': 'operator',
                'created': '2026-01-01',
                'active': True
            },
            'viewer': {
                'password': generate_password_hash('view2026'),
                'role': 'viewer',
                'created': '2026-01-01',
                'active': True
            }
        }
        self._save_users()
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username"""
        return self.users.get(username)
    
    def add_user(self, username: str, password: str, role: str = 'viewer', active: bool = True) -> bool:
        """Add a new user"""
        if username in self.users:
            return False  # User already exists
        
        self.users[username] = {
            'password': generate_password_hash(password),
            'role': role,
            'created': str(Path(__file__).stat().st_mtime),  # Simple timestamp
            'active': active
        }
        return self._save_users()
    
    def update_user(self, username: str, password: Optional[str] = None, 
                   role: Optional[str] = None, active: Optional[bool] = None) -> bool:
        """Update user data"""
        if username not in self.users:
            return False
        
        if password:
            self.users[username]['password'] = generate_password_hash(password)
        if role:
            self.users[username]['role'] = role
        if active is not None:
            self.users[username]['active'] = active
        
        return self._save_users()
    
    def delete_user(self, username: str) -> bool:
        """Delete a user (cannot delete admin)"""
        if username == 'admin':
            return False  # Cannot delete admin user
        if username in self.users:
            del self.users[username]
            return self._save_users()
        return False
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password"""
        user = self.get_user(username)
        if not user or not user.get('active', True):
            return False
        return check_password_hash(user['password'], password)
    
    def list_users(self) -> Dict[str, Dict[str, Any]]:
        """List all users (without passwords)"""
        return {
            username: {
                'role': data.get('role', 'viewer'),
                'active': data.get('active', True),
                'created': data.get('created', 'unknown')
            }
            for username, data in self.users.items()
        }
    
    def ensure_admin_exists(self) -> bool:
        """Ensure admin user exists and is properly configured"""
        if 'admin' not in self.users:
            # Create admin user
            self.users['admin'] = {
                'password': generate_password_hash('admin2026'),
                'role': 'admin',
                'created': '2026-01-01',
                'active': True
            }
            return self._save_users()
        else:
            # Ensure admin has correct role and valid password hash
            needs_save = False
            if self.users['admin'].get('role') != 'admin':
                self.users['admin']['role'] = 'admin'
                needs_save = True
            if not self.users['admin'].get('active', True):
                self.users['admin']['active'] = True
                needs_save = True
            # Update password if it's a placeholder
            if 'placeholder' in str(self.users['admin'].get('password', '')):
                self.users['admin']['password'] = generate_password_hash('admin2026')
                needs_save = True
            if needs_save:
                return self._save_users()
        return True

# Global instance
_user_storage = None

def get_user_storage() -> UserStorage:
    """Get global user storage instance"""
    global _user_storage
    if _user_storage is None:
        _user_storage = UserStorage()
        _user_storage.ensure_admin_exists()  # Ensure admin exists
    return _user_storage

if __name__ == "__main__":
    # Test and initialize user storage
    print("=" * 80)
    print("OMEGA USER STORAGE - ADMIN SETUP")
    print("=" * 80)
    print()
    
    storage = get_user_storage()
    
    # Ensure admin exists
    print("Ensuring admin user exists...")
    storage.ensure_admin_exists()
    print("✅ Admin user configured")
    print()
    
    # List users
    print("Stored users:")
    users = storage.list_users()
    for username, data in users.items():
        role_icon = "👑" if data['role'] == 'admin' else "🔧" if data['role'] == 'operator' else "👁️"
        status = "✅ Active" if data['active'] else "❌ Inactive"
        print(f"  {role_icon} {username}: {data['role']} - {status}")
    
    print()
    print("=" * 80)
    print("✅ User storage initialized and admin user configured")
    print("=" * 80)
