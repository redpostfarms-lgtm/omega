#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# scan_secrets_git_history.sh
# Scans working tree, staged diff, and ALL git history for
# secret patterns (GitHub PATs, generic tokens, API keys).
#
# Usage:  bash tools/security/scan_secrets_git_history.sh
# Exit codes:
#   0  — clean
#   1  — secrets found (details printed to stdout)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FOUND=0

# ── Secret patterns ──────────────────────────────────────────
PATTERNS=(
  'ghp_[A-Za-z0-9_]{36}'           # GitHub classic PAT
  'github_pat_[A-Za-z0-9_]{82}'    # GitHub fine-grained PAT
  'gho_[A-Za-z0-9_]{36}'           # GitHub OAuth token
  'ghu_[A-Za-z0-9_]{36}'           # GitHub user-to-server token
  'ghs_[A-Za-z0-9_]{36}'           # GitHub server-to-server token
  'ghr_[A-Za-z0-9_]{36}'           # GitHub refresh token
  'AKIA[0-9A-Z]{16}'               # AWS Access Key ID
  'sk-[A-Za-z0-9]{48}'             # OpenAI API key
  'sk-ant-[A-Za-z0-9_-]{90,}'      # Anthropic API key
  'xoxb-[0-9]+-[A-Za-z0-9]+'       # Slack bot token
  'xoxp-[0-9]+-[A-Za-z0-9]+'       # Slack user token
)

echo -e "${YELLOW}=== Omega Secret Scanner ===${NC}"
echo ""

# ── 1. Scan working tree ─────────────────────────────────────
echo -e "${YELLOW}[1/3] Scanning working tree...${NC}"
for pat in "${PATTERNS[@]}"; do
  if git grep -n -E "$pat" -- ':(exclude)tools/security/' ':(exclude).git/' 2>/dev/null; then
    echo -e "${RED}  FOUND in working tree: pattern $pat${NC}"
    FOUND=1
  fi
done

# ── 2. Scan staged diff ─────────────────────────────────────
echo -e "${YELLOW}[2/3] Scanning staged changes...${NC}"
for pat in "${PATTERNS[@]}"; do
  if git diff --cached -U0 2>/dev/null | grep -E "$pat" 2>/dev/null; then
    echo -e "${RED}  FOUND in staged diff: pattern $pat${NC}"
    FOUND=1
  fi
done

# ── 3. Scan ALL history ─────────────────────────────────────
echo -e "${YELLOW}[3/3] Scanning full git history (this may take a while)...${NC}"
for pat in "${PATTERNS[@]}"; do
  # Use git log -p to search all diffs in history
  if git log -p --all -S "$pat" --pickaxe-regex -- ':(exclude)tools/security/' 2>/dev/null | grep -E "$pat" | head -5; then
    echo -e "${RED}  FOUND in git history: pattern $pat${NC}"
    FOUND=1
  fi
done

# ── Summary ──────────────────────────────────────────────────
echo ""
if [ "$FOUND" -eq 1 ]; then
  echo -e "${RED}=== SECRETS DETECTED ===${NC}"
  echo -e "${RED}Action required: Revoke exposed credentials and run purge_exposed_pat.sh${NC}"
  exit 1
else
  echo -e "${GREEN}=== ALL CLEAN — no secrets detected ===${NC}"
  exit 0
fi
