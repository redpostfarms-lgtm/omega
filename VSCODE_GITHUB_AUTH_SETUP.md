# VS Code GitHub Authentication - Complete Setup

**Date:** 2026-01-12  
**Status:** ✅ **SETUP GUIDE**

---

## Current Configuration

✅ **Git Credential Helper:** `manager-core` (Windows Credential Manager)  
⚠️ **Remote:** `https://github.com/redpostfarms/The-Gatekeeper.git` (Repository needs to be created on GitHub)  
✅ **VS Code Settings:** Configured for GitHub authentication

---

## ⚠️ Important: Repository Setup

**The repository doesn't exist on GitHub yet.** You have two options:

### Option 1: Create the Repository on GitHub

1. Go to: https://github.com/new
2. **Repository name:** `The-Gatekeeper`
3. **Owner:** `redpostfarms`
4. **Visibility:** Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have files)
6. Click: **"Create repository"**
7. Then follow the authentication setup below

### Option 2: Use Existing Repository

If you have a different repository, update the remote:
```bash
git remote set-url origin https://github.com/your-username/your-repo.git
```text

---

## Quick Setup (Easiest Method)

### Step 1: Open VS Code Command Palette
- Press: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)

### Step 2: Sign in to GitHub
- Type: `GitHub: Sign in`
- Select: `GitHub: Sign in`
- Follow the browser prompts to authenticate

VS Code will automatically:
- Store your credentials securely
- Configure Git to use VS Code's authentication
- Enable all GitHub features in VS Code

---

## Alternative: Personal Access Token

If the built-in authentication doesn't work:

### Step 1: Generate Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click: **"Generate new token"** → **"Generate new token (classic)"**
3. **Name:** `VS Code - Omega System`
4. **Expiration:** Choose your preference (90 days recommended)
5. **Select scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows) - Optional
6. Click: **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

### Step 2: Add Token to Windows Credential Manager

**Option A: Via Command Line**
```bash
git credential-manager-core store
```text
Then enter:
- Protocol: `https`
- Host: `github.com`
- Username: `your-github-username`
- Password: `your-personal-access-token`

**Option B: Via Windows Credential Manager**
1. Open: **Control Panel** → **Credential Manager** → **Windows Credentials**
2. Click: **"Add a generic credential"**
3. Fill in:
   - **Internet address:** `git:https://github.com`
   - **User name:** `your-github-username`
   - **Password:** `your-personal-access-token`
4. Click: **"OK"**

### Step 3: Test Authentication
```bash
git fetch origin
```text

If successful, authentication is working! ✅

---

## VS Code Settings (Already Configured)

The `.vscode/settings.json` file has been configured with:
- ✅ `"github.gitAuthentication": true` - Enables GitHub authentication
- ✅ `"git.credentialHelper": "manager-core"` - Uses Windows Credential Manager
- ✅ `"git.autofetch": true` - Auto-fetches from remote
- ✅ `"git.enableSmartCommit": true` - Smart commit features

---

## Troubleshooting

### Issue: "Authentication failed" in VS Code

**Solution 1: Clear stored credentials**
```bash
git credential-manager-core erase
```text
Then try signing in again via VS Code Command Palette.

**Solution 2: Use Personal Access Token**
Follow the "Alternative: Personal Access Token" steps above.

### Issue: VS Code not detecting Git

**Solution:**
1. Verify Git is installed: `git --version`
2. Restart VS Code
3. Check Git path in VS Code settings:
   - Open Settings (`Ctrl+,`)
   - Search: `git.path`
   - Set to: `C:\Program Files\Git\cmd\git.exe` (or your Git path)

### Issue: "Repository not found"

**Solution:**
1. Verify repository exists: https://github.com/redpostfarms/The-Gatekeeper
2. Check you have access to the repository
3. Verify remote URL:
   ```bash
   git remote -v
   ```
4. If wrong, update it:
   ```bash
   git remote set-url origin https://github.com/redpostfarms/The-Gatekeeper.git
   ```

### Issue: "Permission denied" or "403 Forbidden"

**Solution:**
1. Your Personal Access Token may have expired
2. Generate a new token with `repo` scope
3. Update credentials in Windows Credential Manager

---

## Verify Authentication

### Test in VS Code:
1. Open Source Control panel (`Ctrl+Shift+G`)
2. Try to push/pull
3. Should work without prompting for credentials

### Test in Terminal:
```bash
# Test fetch
git fetch origin

# Test push (if you have commits)
git push origin master
```text

If both work, authentication is properly configured! ✅

---

## VS Code GitHub Features Enabled

Once authenticated, you can use:
- ✅ **Source Control** panel for Git operations
- ✅ **GitHub Pull Requests** extension (if installed)
- ✅ **GitHub Copilot** (if subscribed)
- ✅ **GitHub Actions** integration
- ✅ **Repository browsing** in VS Code

---

## Security Notes

- ✅ Credentials stored in Windows Credential Manager (encrypted)
- ✅ Personal Access Tokens are more secure than passwords
- ✅ Tokens can be revoked at any time
- ✅ Use token expiration for additional security

---

## Quick Reference

**Sign in to GitHub in VS Code:**
1. `Ctrl+Shift+P`
2. Type: `GitHub: Sign in`
3. Follow prompts

**Generate Personal Access Token:**
- URL: https://github.com/settings/tokens
- Scope: `repo` (full control)

**Add token to Windows:**
- Control Panel → Credential Manager → Windows Credentials
- Add: `git:https://github.com`

**Test authentication:**
```bash
git fetch origin
```text

---

**Status:** ✅ **VS Code GitHub Authentication Ready**

Your VS Code is now configured for GitHub authentication. Use Command Palette → `GitHub: Sign in` for easiest setup!
