#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# pre-commit hook — blocks commits that contain secret patterns
#
# Install:
#   cp tools/security/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
# ──────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

FOUND=0

# Secret patterns to check
PATTERNS=(
  'ghp_[A-Za-z0-9_]{36}'
  'github_pat_[A-Za-z0-9_]{82}'
  'gho_[A-Za-z0-9_]{36}'
  'ghu_[A-Za-z0-9_]{36}'
  'ghs_[A-Za-z0-9_]{36}'
  'ghr_[A-Za-z0-9_]{36}'
  'AKIA[0-9A-Z]{16}'
  'sk-[A-Za-z0-9]{48}'
  'sk-ant-[A-Za-z0-9_-]{90,}'
  'xoxb-[0-9]+-[A-Za-z0-9]+'
  'xoxp-[0-9]+-[A-Za-z0-9]+'
)

# Only scan the staged diff (what's about to be committed)
DIFF=$(git diff --cached --diff-filter=ACMR)

if [ -z "$DIFF" ]; then
  exit 0
fi

for pat in "${PATTERNS[@]}"; do
  if echo "$DIFF" | grep -E "$pat" 2>/dev/null; then
    echo -e "${RED}[SECRET BLOCKED] Found pattern matching: $pat${NC}"
    FOUND=1
  fi
done

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo -e "${RED}COMMIT BLOCKED: Staged changes contain secret patterns.${NC}"
  echo "  Remove the secrets, then try again."
  echo "  If this is a false positive, bypass with: git commit --no-verify"
  exit 1
fi

exit 0
