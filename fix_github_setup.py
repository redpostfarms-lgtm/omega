#!/usr/bin/env python3
"""
Fix GitHub Setup and Authentication
===================================
Fixes GitHub repository setup, authentication, and push/pull issues.
"""

import subprocess
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def check_git_installed():
    """Check if Git is installed"""
    result = run_command("git --version", check=False)
    if result and result.returncode == 0:
        print(f"✅ Git installed: {result.stdout.strip()}")
        return True
    else:
        print("❌ Git is not installed")
        return False

def check_git_initialized():
    """Check if repository is initialized"""
    if not Path(".git").exists():
        print("❌ Git repository not initialized")
        return False
    print("✅ Git repository initialized")
    return True

def setup_git_user():
    """Setup Git user configuration"""
    print("\nSetting up Git user configuration...")
    
    # Check current config
    result = run_command("git config user.name", check=False)
    if result and result.returncode == 0 and result.stdout.strip():
        print(f"✅ Git user.name: {result.stdout.strip()}")
    else:
        # Set default
        run_command('git config user.name "Omega System"')
        print("✅ Set Git user.name to 'Omega System'")
    
    result = run_command("git config user.email", check=False)
    if result and result.returncode == 0 and result.stdout.strip():
        print(f"✅ Git user.email: {result.stdout.strip()}")
    else:
        # Set default
        run_command('git config user.email "omega@gatekeeper.local"')
        print("✅ Set Git user.email to 'omega@gatekeeper.local'")

def setup_remote():
    """Setup GitHub remote"""
    print("\nSetting up GitHub remote...")
    
    # Check existing remotes
    result = run_command("git remote -v", check=False)
    if result and result.returncode == 0:
        remotes = result.stdout.strip()
        if remotes:
            print(f"Current remotes:\n{remotes}")
            
            # Check if origin exists
            if "origin" in remotes:
                print("✅ Origin remote exists")
                return True
    
    # Add origin remote
    remote_url = "https://github.com/redpostfarms/The-Gatekeeper.git"
    print(f"Adding origin remote: {remote_url}")
    
    result = run_command(f"git remote add origin {remote_url}", check=False)
    if result and result.returncode == 0:
        print("✅ Origin remote added")
        return True
    else:
        # Try setting URL if remote exists
        result = run_command(f"git remote set-url origin {remote_url}", check=False)
        if result and result.returncode == 0:
            print("✅ Origin remote URL updated")
            return True
        else:
            print("❌ Failed to setup remote")
            return False

def setup_credential_helper():
    """Setup credential helper for Windows"""
    print("\nSetting up credential helper...")
    
    # Use Windows Credential Manager
    run_command("git config --global credential.helper manager-core")
    print("✅ Configured credential.helper to manager-core")
    
    # Also try wincred as fallback
    run_command("git config --global credential.helper wincred")
    print("✅ Added wincred as fallback credential helper")

def test_remote_access():
    """Test if remote is accessible"""
    print("\nTesting remote access...")
    
    # Try to fetch (dry run)
    result = run_command("git fetch origin --dry-run", check=False)
    if result:
        if result.returncode == 0:
            print("✅ Remote is accessible")
            return True
        else:
            print(f"⚠️  Remote access issue: {result.stderr.strip()}")
            print("\nPossible solutions:")
            print("1. Check if repository exists: https://github.com/redpostfarms/The-Gatekeeper")
            print("2. Verify you have access to the repository")
            print("3. Use Personal Access Token (PAT) for authentication")
            print("4. Run: git config --global credential.helper manager-core")
            return False
    return False

def setup_personal_access_token():
    """Instructions for setting up Personal Access Token"""
    print("\n" + "=" * 80)
    print("GITHUB PERSONAL ACCESS TOKEN SETUP")
    print("=" * 80)
    print()
    print("If authentication fails, you need to set up a Personal Access Token:")
    print()
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token' → 'Generate new token (classic)'")
    print("3. Give it a name (e.g., 'Omega System')")
    print("4. Select scopes: repo (full control)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (you won't see it again!)")
    print()
    print("7. When Git prompts for password, use the token instead")
    print("8. Or set it in Windows Credential Manager:")
    print("   - Open Credential Manager")
    print("   - Windows Credentials")
    print("   - Add generic credential")
    print("   - Internet address: git:https://github.com")
    print("   - Username: your GitHub username")
    print("   - Password: your Personal Access Token")
    print()
    print("=" * 80)

def create_initial_commit():
    """Create initial commit if needed"""
    print("\nChecking for initial commit...")
    
    result = run_command("git log --oneline -1", check=False)
    if result and result.returncode == 0 and result.stdout.strip():
        print("✅ Repository has commits")
        return True
    
    # Check if there are files to commit
    result = run_command("git status --porcelain", check=False)
    if result and result.stdout.strip():
        print("⚠️  Repository has uncommitted changes")
        print("To create initial commit, run:")
        print("  git add .")
        print("  git commit -m 'Initial commit'")
        return False
    
    print("✅ Repository is clean")
    return True

def main():
    """Main function"""
    print("=" * 80)
    print("GITHUB SETUP AND AUTHENTICATION FIX")
    print("=" * 80)
    print()
    
    # Check Git installation
    if not check_git_installed():
        print("\nPlease install Git from: https://git-scm.com/download/win")
        return
    
    # Check if initialized
    if not check_git_initialized():
        print("\nInitializing Git repository...")
        run_command("git init")
        if not check_git_initialized():
            print("❌ Failed to initialize Git repository")
            return
    
    # Setup Git user
    setup_git_user()
    
    # Setup credential helper
    setup_credential_helper()
    
    # Setup remote
    if not setup_remote():
        print("❌ Failed to setup remote")
        return
    
    # Test remote access
    remote_ok = test_remote_access()
    
    # Check for initial commit
    create_initial_commit()
    
    # Instructions for PAT if needed
    if not remote_ok:
        setup_personal_access_token()
    
    print("\n" + "=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. If authentication fails, set up Personal Access Token (see above)")
    print("2. Test push: git push -u origin master")
    print("3. Test pull: git pull origin master")
    print()

if __name__ == "__main__":
    main()
