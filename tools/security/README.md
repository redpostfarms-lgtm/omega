# Security Remediation Toolkit

Tools for scanning, purging, and preventing secret leaks in the Omega repository.

## Quick Reference

| Tool | Purpose |
|------|---------|
| `scan_secrets_git_history.sh` | Scan working tree, staged changes, and full history for secrets |
| `purge_exposed_pat.sh` | Rewrite git history to remove an exposed secret |
| `pre-commit-hook.sh` | Pre-commit hook that blocks commits containing secrets |

## Remediation Runbook

### Step 1: Scan for Exposed Secrets

```bash
bash tools/security/scan_secrets_git_history.sh
```

This scans three layers:
1. **Working tree** — current files on disk
2. **Staged diff** — changes about to be committed
3. **Full git history** — every commit ever made

Exit code `0` = clean, `1` = secrets found.

### Step 2: Revoke the Exposed Credential

**Before purging history, revoke the credential immediately.**

- **GitHub PAT**: GitHub Settings > Developer settings > Personal access tokens > Delete/Revoke
- **AWS Key**: IAM Console > Users > Security credentials > Deactivate/Delete
- **OpenAI Key**: platform.openai.com > API keys > Revoke

### Step 3: Purge from Git History

```bash
# Install git-filter-repo if not already installed
pip install git-filter-repo

# Run the purge (replace with your actual secret)
bash tools/security/purge_exposed_pat.sh "ghp_yourExposedTokenHere"
```

This will:
1. Create a backup of `.git` at `.git-backup-<timestamp>`
2. Rewrite all commits to replace the secret with `***REDACTED***`
3. Verify the secret no longer appears anywhere

### Step 4: Force Push and Notify

```bash
git push --force --all
git push --force --tags
```

**All collaborators must re-clone** — their local copies have the old (rewritten) commit hashes.

### Step 5: Install Prevention

```bash
# Install the pre-commit hook
cp tools/security/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The CI pipeline also runs secret scanning on every PR via the `secret-scan` job in `.github/workflows/ci.yml`.

## Secret Patterns Detected

| Pattern | Description |
|---------|-------------|
| `ghp_*` | GitHub classic personal access token |
| `github_pat_*` | GitHub fine-grained personal access token |
| `gho_*` | GitHub OAuth access token |
| `ghu_*` | GitHub user-to-server token |
| `ghs_*` | GitHub server-to-server token |
| `ghr_*` | GitHub refresh token |
| `AKIA*` | AWS Access Key ID |
| `sk-*` (48+ chars) | OpenAI API key |
| `sk-ant-*` | Anthropic API key |
| `xoxb-*` | Slack bot token |
| `xoxp-*` | Slack user token |

## Prevention Architecture

```
Developer workstation          CI/CD Pipeline
┌─────────────────┐    ┌──────────────────────┐
│  pre-commit hook │    │  secret-scan job      │
│  (blocks commit) │    │  (fails PR if found)  │
└────────┬────────┘    └──────────┬───────────┘
         │                        │
         ▼                        ▼
    Local reject            PR blocked
```

Both layers use the same pattern set to ensure no secrets reach the remote repository.
