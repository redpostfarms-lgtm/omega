#!/usr/bin/env python3
"""
Setup Admin User - Initialize Admin User in Authenticator
==========================================================
Sets up and saves the admin user in the persistent user storage system.
"""

import sys
from pathlib import Path

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

try:
    from omega_user_storage import get_user_storage
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure omega_user_storage.py exists and werkzeug is installed.")
    sys.exit(1)

def main():
    print("=" * 80)
    print("OMEGA AUTHENTICATOR - ADMIN USER SETUP")
    print("=" * 80)
    print()
    
    # Get user storage
    storage = get_user_storage()
    
    # Ensure admin user exists and is properly configured
    print("Setting up admin user...")
    success = storage.ensure_admin_exists()
    
    if success:
        print("✅ Admin user configured and saved")
    else:
        print("❌ Failed to configure admin user")
        return False
    
    # Verify admin user
    admin_user = storage.get_user('admin')
    if admin_user:
        print()
        print("Admin User Details:")
        print(f"  Username: admin")
        print(f"  Role: {admin_user.get('role', 'admin')}")
        print(f"  Status: {'✅ Active' if admin_user.get('active', True) else '❌ Inactive'}")
        print(f"  Password: [HASHED - Stored Securely]")
        print()
    else:
        print("❌ Admin user not found after setup")
        return False
    
    # List all users
    print("All Users in Authenticator:")
    users = storage.list_users()
    for username, data in users.items():
        role_icon = "👑" if data['role'] == 'admin' else "🔧" if data['role'] == 'operator' else "👁️"
        status = "✅ Active" if data['active'] else "❌ Inactive"
        print(f"  {role_icon} {username}: {data['role']} - {status}")
    
    print()
    print("=" * 80)
    print("✅ ADMIN USER SUCCESSFULLY SET UP IN AUTHENTICATOR")
    print("=" * 80)
    print()
    print("The admin user is now saved in: omega_users.json")
    print("Default credentials:")
    print("  Username: admin")
    print("  Password: admin2026")
    print("  Role: admin (Administrator)")
    print()
    print("⚠️  IMPORTANT: Change the default password in production!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
