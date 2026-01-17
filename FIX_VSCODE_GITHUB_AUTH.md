# Fix VS Code GitHub Authentication

**Date:** 2026-01-12  
**Status:** ✅ **SETUP GUIDE**

---

## VS Code GitHub Authentication Setup

### Method 1: VS Code Built-in Authentication (Recommended)

1. **Open VS Code**
2. **Open Command Palette:** `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. **Type:** `Git: Clone`
4. **Or:** `GitHub: Sign in`
5. **Follow prompts** to authenticate with GitHub

VS Code will automatically:
- Store credentials in Windows Credential Manager
- Configure Git to use VS Code's credential helper
- Handle authentication for all Git operations

---

### Method 2: Personal Access Token (PAT)

If VS Code authentication doesn't work:

1. **Generate Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click: "Generate new token" → "Generate new token (classic)"
   - Name: "VS Code - Omega System"
   - Select scopes: `repo` (full control)
   - Click: "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Configure Git to use token:**
   ```bash
   git config --global credential.helper manager-core
   ```

3. **When Git prompts for password:**
   - Username: your GitHub username
   - Password: paste your Personal Access Token

4. **Or add to Windows Credential Manager:**
   - Open: Control Panel → Credential Manager → Windows Credentials
   - Click: "Add a generic credential"
   - Internet address: `git:https://github.com`
   - Username: your GitHub username
   - Password: your Personal Access Token
   - Click: "OK"

---

### Method 3: SSH Authentication (Alternative)

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub:**
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click: "New SSH key"
   - Paste key and save

3. **Change remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:redpostfarms/The-Gatekeeper.git
   ```

---

### Method 4: Configure VS Code Settings

Add to VS Code settings (`.vscode/settings.json` or User Settings):

```json
{
  "git.autofetch": true,
  "git.confirmSync": false,
  "git.enableSmartCommit": true,
  "github.gitAuthentication": true
}
```text

---

## Troubleshooting

### Issue: "Authentication failed"

**Solution:**
1. Clear stored credentials:
   ```bash
   git credential-manager-core erase
   ```
2. Try authentication again
3. Use Personal Access Token if needed

### Issue: "Repository not found"

**Solution:**
1. Verify repository exists: https://github.com/redpostfarms/The-Gatekeeper
2. Check you have access to the repository
3. Verify remote URL:
   ```bash
   git remote -v
   ```

### Issue: VS Code not detecting Git

**Solution:**
1. Install Git: https://git-scm.com/download/win
2. Restart VS Code
3. Verify Git path in VS Code settings:
   ```json
   {
     "git.path": "C:\\Program Files\\Git\\cmd\\git.exe"
   }
   ```

---

## Quick Setup Script

Run this to configure everything:

```bash
# Set credential helper
git config --global credential.helper manager-core

# Verify remote
git remote -v

# Test authentication
git fetch origin
```text

---

## Status Check

After setup, verify authentication:

```bash
git config --global credential.helper
git remote -v
git fetch origin --dry-run
```text

If all commands succeed, authentication is working! ✅

---

**For VS Code specifically:** Use Command Palette → `GitHub: Sign in` for easiest setup.
