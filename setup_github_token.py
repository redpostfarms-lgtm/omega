#!/usr/bin/env python3
"""
Setup GitHub Personal Access Token
==================================
Securely configures GitHub token for Git authentication.
"""

import subprocess
import sys
from pathlib import Path

def setup_github_token(token: str, username: str = "redpostfarms"):
    """Setup GitHub token in Windows Credential Manager"""
    
    print("=" * 80)
    print("GITHUB TOKEN SETUP")
    print("=" * 80)
    print()
    
    # Verify token format
    if not token.startswith("ghp_"):
        print("⚠️  Warning: Token doesn't start with 'ghp_' - may not be valid")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    print(f"[1/3] Configuring Git credential helper...")
    try:
        subprocess.run(['git', 'config', '--global', 'credential.helper', 'manager-core'], 
                      check=True, capture_output=True)
        print("✅ Credential helper configured")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"[2/3] Testing token with GitHub API...")
    try:
        import urllib.request
        import base64
        
        # Test token by accessing GitHub API
        url = "https://api.github.com/user"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'token {token}')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            user_data = response.read().decode('utf-8')
            import json
            user_info = json.loads(user_data)
            print(f"✅ Token is valid! Authenticated as: {user_info.get('login', 'Unknown')}")
    except Exception as e:
        print(f"⚠️  Could not verify token: {e}")
        print("   Token will still be configured, but verification failed")
    
    print(f"[3/3] Configuring Git to use token...")
    print()
    print("To complete setup, run this command and enter your credentials:")
    print()
    print("  git credential-manager-core store")
    print()
    print("Then enter:")
    print(f"  Protocol: https")
    print(f"  Host: github.com")
    print(f"  Username: {username}")
    print(f"  Password: {token}")
    print()
    print("Or use Windows Credential Manager:")
    print("  1. Control Panel → Credential Manager → Windows Credentials")
    print("  2. Add generic credential")
    print(f"  3. Internet address: git:https://github.com")
    print(f"  4. Username: {username}")
    print(f"  5. Password: {token}")
    print()
    
    # Try to set it programmatically via git credential
    print("Attempting automatic setup...")
    try:
        # Use git credential fill to trigger credential manager
        process = subprocess.Popen(
            ['git', 'credential-manager-core', 'store'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        credential_input = f"protocol=https\nhost=github.com\nusername={username}\npassword={token}\n\n"
        stdout, stderr = process.communicate(input=credential_input, timeout=5)
        
        if process.returncode == 0:
            print("✅ Token configured successfully!")
        else:
            print("⚠️  Automatic setup may have failed. Use manual method above.")
    except Exception as e:
        print(f"⚠️  Automatic setup failed: {e}")
        print("   Use manual method above to configure token")
    
    print()
    print("=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Test authentication with:")
    print("  git fetch origin")
    print()
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_github_token.py <token> [username]")
        print()
        print("Example:")
        print("  python setup_github_token.py ghp_xxxxxxxxxxxx redpostfarms")
        sys.exit(1)
    
    token = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "redpostfarms"
    
    setup_github_token(token, username)
