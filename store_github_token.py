#!/usr/bin/env python3
"""
Directly store GitHub token in Windows Credential Manager
"""
import subprocess
import sys

def store_token(token: str, username: str = "redpostfarms"):
    """Store GitHub token using git credential-manager-core"""
    
    print("Storing GitHub token in Windows Credential Manager...")
    
    # Prepare credential input
    credential_input = f"protocol=https\nhost=github.com\nusername={username}\npassword={token}\n"
    
    try:
        # Use subprocess.Popen with stdin to send credentials
        process = subprocess.Popen(
            ['git', 'credential-manager-core', 'store'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        
        stdout, stderr = process.communicate(input=credential_input, timeout=10)
        
        if process.returncode == 0:
            print("✅ Token stored successfully!")
            return True
        else:
            print(f"⚠️  Return code: {process.returncode}")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error storing token: {e}")
        return False

if __name__ == "__main__":
    import os

    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("GITHUB_USERNAME", "redpostfarms")

    if not token:
        print("ERROR: Set GITHUB_TOKEN environment variable before running.")
        print("  Example: set GITHUB_TOKEN=ghp_your_token_here")
        sys.exit(1)

    if store_token(token, username):
        print("\nGitHub token configured!")
        print("\nTesting authentication...")
        try:
            result = subprocess.run(
                ['git', 'fetch', 'origin', '--dry-run'],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                print("Authentication successful!")
            else:
                print(f"Fetch test returned: {result.returncode}")
                if result.stderr:
                    print(f"   {result.stderr.strip()}")
        except Exception as e:
            print(f"Could not test: {e}")
    else:
        print("\nFailed to store token. Please use manual method.")
        print("\nManual setup:")
        print("1. Open Windows Credential Manager")
        print("2. Go to Windows Credentials")
        print("3. Add Generic Credential:")
        print("   - Internet address: git:https://github.com")
        print(f"   - Username: {username}")
        print("   - Password: <your token>")
