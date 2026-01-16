# GitHub Setup and Authentication Guide

## Overview
This guide covers setting up GitHub integration for The Gatekeeper project.

## Prerequisites
- GitHub account
- Git installed locally
- Python 3.8+

## Setup Steps

### 1. Create GitHub Personal Access Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org` (if working with organization)
4. Copy the generated token

### 2. Configure Local Environment
1. Copy `.env.example` to `.env`
2. Add your GitHub token:
   ```
   GITHUB_TOKEN=your_token_here
   GITHUB_USERNAME=your_username
   GITHUB_REPO=your_repo_name
   ```

### 3. Initialize Git Repository (if not done)
```bash
git init
git remote add origin https://github.com/USERNAME/REPO.git
```

### 4. Test Connection
```bash
python scripts/test_github_connection.py
```

## Security Best Practices
- Never commit `.env` file
- Rotate tokens regularly
- Use fine-grained tokens when possible
- Limit token scope to minimum required

## Troubleshooting
- **Authentication failed**: Check token is valid and has correct scopes
- **Permission denied**: Verify repository access rights
- **Rate limiting**: Implement token rotation or wait for reset

## Additional Resources
- [GitHub Token Documentation](https://docs.github.com/en/authentication)
- [Git Best Practices](https://git-scm.com/book/en/v2)
