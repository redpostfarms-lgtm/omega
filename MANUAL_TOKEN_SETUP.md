# Manual GitHub Token Setup - Quick Guide

**Token:** `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`  
**Username:** `redpostfarms`

---

## Quick Setup (Windows Credential Manager)

### Step 1: Open Credential Manager
1. Press `Windows Key + R`
2. Type: `control /name Microsoft.CredentialManager`
3. Press Enter
4. Or: Control Panel → Credential Manager → Windows Credentials

### Step 2: Add GitHub Credential
1. Click: **"Add a generic credential"**
2. Fill in:
   - **Internet address:** `git:https://github.com`
   - **User name:** `redpostfarms`
   - **Password:** `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`
3. Click: **"OK"**

### Step 3: Verify
```bash
git fetch origin --dry-run
```

If it works (or says "repository not found" which is expected), authentication is configured! ✅

---

## Alternative: Via Command Line

```bash
# Set credential helper
git config --global credential.helper manager-core

# The token will be stored automatically on first use
# Or use the PowerShell script: configure_github_token.ps1
```

---

## VS Code

VS Code will automatically use the stored credentials. No additional setup needed!

---

**Status:** ✅ **Ready to use once repository is created on GitHub**
