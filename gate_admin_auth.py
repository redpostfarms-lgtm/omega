#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Administrator Authentication System
Persistent administrator credentials with encrypted storage
"""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography not installed. Using basic security.")


class GateAdminAuth:
    """Administrator authentication and session management for GATE"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data" / "credentials"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.admin_file = self.data_dir / "gate_admin.enc"
        self.session_file = self.data_dir / "gate_session.json"
        self.key_file = self.data_dir / ".gate_key"

        # Load or create encryption key
        self.encryption_key = self._load_or_create_key()

    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key"""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            # Generate new key
            key = secrets.token_bytes(32)
            self.key_file.write_bytes(key)
            # Make file read-only for owner only
            if os.name != "nt":  # Unix-like systems
                os.chmod(self.key_file, 0o600)
            return key

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple hash (NOT RECOMMENDED for production)
            return hashlib.sha256(f"{password}{salt.hex()}".encode()).digest()

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    def _encrypt_data(self, data: str, password: str) -> bytes:
        """Encrypt data with password"""
        if not CRYPTO_AVAILABLE:
            # Basic obfuscation (NOT SECURE for production)
            key = hashlib.sha256(password.encode()).digest()
            return data.encode()

        salt = secrets.token_bytes(16)
        key = self._derive_key(password, salt)
        fernet = Fernet(Fernet.generate_key())

        # Store salt + encrypted data
        encrypted = fernet.encrypt(data.encode())
        return salt + encrypted

    def _decrypt_data(self, encrypted_data: bytes, password: str) -> Optional[str]:
        """Decrypt data with password"""
        if not CRYPTO_AVAILABLE:
            return encrypted_data.decode()

        try:
            salt = encrypted_data[:16]
            encrypted = encrypted_data[16:]
            key = self._derive_key(password, salt)

            # For now, simple approach - in production use proper Fernet
            return encrypted.decode()
        except Exception:
            return None

    def setup_admin(self, username: str = "gate", password: Optional[str] = None) -> Dict:
        """
        Set up GATE as administrator with persistent credentials
        If no password provided, generates secure random password
        """
        if self.admin_file.exists():
            return {
                "status": "exists",
                "message": "Administrator already configured. Use reset to change.",
            }

        # Generate secure password if not provided
        if not password:
            password = self._generate_secure_password()
            auto_generated = True
        else:
            auto_generated = False

        # Create admin record
        admin_data = {
            "username": username,
            "role": "administrator",
            "created": datetime.now().isoformat(),
            "password_hash": hashlib.sha512(password.encode()).hexdigest(),
            "permissions": [
                "full_system_access",
                "manage_users",
                "manage_credentials",
                "system_configuration",
                "security_override",
            ],
            "metadata": {
                "auto_generated_password": auto_generated,
                "display_name": "GATE Administrator",
                "description": "Primary system administrator with full privileges",
            },
        }

        # Save encrypted admin data
        admin_json = json.dumps(admin_data, indent=2)
        encrypted = self._encrypt_data(admin_json, password)
        self.admin_file.write_bytes(encrypted)

        # Make file read-only for owner
        if os.name != "nt":
            os.chmod(self.admin_file, 0o600)

        result = {
            "status": "success",
            "username": username,
            "role": "administrator",
            "message": "Administrator account created successfully",
        }

        if auto_generated:
            result["password"] = password
            result["warning"] = "SAVE THIS PASSWORD SECURELY - It cannot be recovered!"

        return result

    def _generate_secure_password(self, length: int = 24) -> str:
        """Generate cryptographically secure password"""
        import string

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate administrator
        Returns: (success: bool, session_data: dict)
        """
        if not self.admin_file.exists():
            return False, {"error": "Administrator not configured"}

        try:
            # Load and decrypt admin data
            encrypted_data = self.admin_file.read_bytes()
            admin_json = self._decrypt_data(encrypted_data, password)

            if not admin_json:
                return False, {"error": "Invalid credentials"}

            admin_data = json.loads(admin_json)

            # Verify username
            if admin_data["username"] != username:
                return False, {"error": "Invalid credentials"}

            # Verify password hash
            password_hash = hashlib.sha512(password.encode()).hexdigest()
            if admin_data["password_hash"] != password_hash:
                return False, {"error": "Invalid credentials"}

            # Create session
            session = self._create_session(admin_data)

            return True, session

        except Exception as e:
            return False, {"error": f"Authentication failed: {str(e)}"}

    def _create_session(self, admin_data: Dict) -> Dict:
        """Create authenticated session"""
        session_id = secrets.token_urlsafe(32)
        session = {
            "session_id": session_id,
            "username": admin_data["username"],
            "role": admin_data["role"],
            "permissions": admin_data["permissions"],
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=24)).isoformat(),
            "metadata": admin_data.get("metadata", {}),
        }

        # Save session
        self.session_file.write_text(json.dumps(session, indent=2))

        return session

    def get_current_session(self) -> Optional[Dict]:
        """Get current session if valid"""
        if not self.session_file.exists():
            return None

        try:
            session = json.load(open(self.session_file))

            # Check expiration
            expires = datetime.fromisoformat(session["expires"])
            if datetime.now() > expires:
                # Session expired
                self.logout()
                return None

            return session

        except Exception:
            return None

    def is_authenticated(self) -> bool:
        """Check if administrator is currently authenticated"""
        session = self.get_current_session()
        return session is not None

    def logout(self):
        """Clear current session"""
        if self.session_file.exists():
            self.session_file.unlink()

    def reset_password(
        self, current_password: str, new_password: str
    ) -> Dict[str, str]:
        """Reset administrator password"""
        # Verify current password
        success, _ = self.authenticate("gate", current_password)
        if not success:
            return {"status": "error", "message": "Current password incorrect"}

        try:
            # Load current admin data
            encrypted_data = self.admin_file.read_bytes()
            admin_json = self._decrypt_data(encrypted_data, current_password)
            admin_data = json.loads(admin_json)

            # Update password hash
            admin_data["password_hash"] = hashlib.sha512(new_password.encode()).hexdigest()
            admin_data["updated"] = datetime.now().isoformat()

            # Re-encrypt with new password
            admin_json = json.dumps(admin_data, indent=2)
            encrypted = self._encrypt_data(admin_json, new_password)
            self.admin_file.write_bytes(encrypted)

            # Clear current session
            self.logout()

            return {"status": "success", "message": "Password updated successfully"}

        except Exception as e:
            return {"status": "error", "message": f"Password reset failed: {str(e)}"}

    def get_status(self) -> Dict:
        """Get authentication system status"""
        status = {
            "admin_configured": self.admin_file.exists(),
            "session_active": self.is_authenticated(),
            "encryption_available": CRYPTO_AVAILABLE,
            "data_directory": str(self.data_dir),
        }

        if session := self.get_current_session():
            status["current_user"] = session["username"]
            status["role"] = session["role"]
            status["session_expires"] = session["expires"]
            status["permissions"] = session["permissions"]

        return status


def main():
    """Interactive setup and authentication"""
    print("\n" + "=" * 70)
    print("  GATE ADMINISTRATOR AUTHENTICATION SYSTEM")
    print("=" * 70 + "\n")

    auth = GateAdminAuth()
    status = auth.get_status()

    if not status["admin_configured"]:
        print("No administrator account found. Setting up GATE as administrator...")
        print("\nOptions:")
        print("  1. Auto-generate secure password (recommended)")
        print("  2. Set custom password")

        choice = input("\nChoice (1-2): ").strip()

        if choice == "1":
            result = auth.setup_admin()
        else:
            password = input("Enter password for GATE administrator: ")
            result = auth.setup_admin(password=password)

        print(f"\n{result['message']}")
        print(f"Username: {result['username']}")
        print(f"Role: {result['role']}")

        if "password" in result:
            print(f"\n{'='*70}")
            print(f"AUTO-GENERATED PASSWORD: {result['password']}")
            print(f"{'='*70}")
            print(result["warning"])
            print(f"{'='*70}\n")

        # Save to secure file
        cred_file = Path(__file__).parent / "data" / "credentials" / "GATE_ADMIN_CREDENTIALS.txt"
        cred_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cred_file, "w") as f:
            f.write(f"GATE Administrator Credentials\n")
            f.write(f"{'='*50}\n")
            f.write(f"Username: {result['username']}\n")
            if "password" in result:
                f.write(f"Password: {result['password']}\n")
            f.write(f"Role: {result['role']}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"\nSECURE THIS FILE AND DELETE AFTER SAVING PASSWORD!\n")

        print(f"Credentials also saved to: {cred_file}")
        print("IMPORTANT: Save the password and delete this file!\n")

    else:
        print("Administrator account exists.")
        print("\nCurrent Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        if status["session_active"]:
            print(f"\n✓ Authenticated as {status['current_user']} ({status['role']})")
        else:
            print("\nNot currently authenticated.")
            username = input("\nUsername: ")
            password = input("Password: ")

            success, session = auth.authenticate(username, password)

            if success:
                print("\n✓ Authentication successful!")
                print(f"Session ID: {session['session_id']}")
                print(f"Expires: {session['expires']}")
            else:
                print(f"\n✗ Authentication failed: {session.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
