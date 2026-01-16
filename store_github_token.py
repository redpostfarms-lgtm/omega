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
    token = "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"
    username = "redpostfarms"
    
    if store_token(token, username):
        print("\n✅ GitHub token configured!")
        print("\nTesting authentication...")
        # Test with a dry-run fetch
        try:
            result = subprocess.run(
                ['git', 'fetch', 'origin', '--dry-run'],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                print("✅ Authentication successful!")
            else:
                print(f"⚠️  Fetch test returned: {result.returncode}")
                if result.stderr:
                    print(f"   {result.stderr.strip()}")
        except Exception as e:
            print(f"⚠️  Could not test: {e}")
    else:
        print("\n❌ Failed to store token. Please use manual method.")
        print("\nManual setup:")
        print("1. Open Windows Credential Manager")
        print("2. Go to Windows Credentials")
        print("3. Add Generic Credential:")
        print("   - Internet address: git:https://github.com")
        print(f"   - Username: {username}")
        print(f"   - Password: {token}")
