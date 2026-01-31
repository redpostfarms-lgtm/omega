#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# purge_exposed_pat.sh
# Uses git-filter-repo to replace an exact secret string across
# ALL commits in the repository history.
#
# Prerequisites:
#   pip install git-filter-repo
#
# Usage:
#   bash tools/security/purge_exposed_pat.sh <SECRET_STRING>
#
# Example:
#   bash tools/security/purge_exposed_pat.sh "ghp_abc123..."
#
# What it does:
#   1. Creates a full backup of the repo (.git-backup-<timestamp>)
#   2. Builds a replacements file mapping SECRET → ***REDACTED***
#   3. Runs git-filter-repo --replace-text across all history
#   4. Verifies the secret no longer appears anywhere
#
# WARNING: This rewrites ALL commit hashes. All collaborators
#          must re-clone after this operation.
# ──────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -lt 1 ]; then
  echo -e "${RED}Usage: $0 <SECRET_STRING>${NC}"
  echo "  Provide the exact secret to purge from all git history."
  exit 1
fi

SECRET="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=".git-backup-${TIMESTAMP}"
REPLACEMENTS_FILE=$(mktemp)

# ── Preflight checks ────────────────────────────────────────
echo -e "${YELLOW}=== Omega Secret Purge Tool ===${NC}"
echo ""

# Check git-filter-repo is installed
if ! command -v git-filter-repo &>/dev/null; then
  echo -e "${RED}ERROR: git-filter-repo is not installed.${NC}"
  echo "  Install it with: pip install git-filter-repo"
  exit 1
fi

# Check we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo -e "${RED}ERROR: Not inside a git repository.${NC}"
  exit 1
fi

# ── Step 1: Backup ──────────────────────────────────────────
echo -e "${YELLOW}[1/4] Creating full backup → ${BACKUP_DIR}${NC}"
cp -r .git "${BACKUP_DIR}"
echo -e "${GREEN}  Backup created at ${BACKUP_DIR}${NC}"

# ── Step 2: Build replacements file ─────────────────────────
echo -e "${YELLOW}[2/4] Building replacements file...${NC}"
# Format: literal:SECRET==>***REDACTED***
echo "literal:${SECRET}==>***REDACTED***" > "${REPLACEMENTS_FILE}"
echo -e "${GREEN}  Replacements file ready${NC}"

# ── Step 3: Run git-filter-repo ─────────────────────────────
echo -e "${YELLOW}[3/4] Running git-filter-repo (rewriting history)...${NC}"
echo -e "${YELLOW}  This may take a while on large repositories.${NC}"
git filter-repo --replace-text "${REPLACEMENTS_FILE}" --force
echo -e "${GREEN}  History rewritten successfully${NC}"

# ── Step 4: Verify purge ────────────────────────────────────
echo -e "${YELLOW}[4/4] Verifying secret is purged from all history...${NC}"

# Check working tree
if git grep -r "${SECRET}" 2>/dev/null; then
  echo -e "${RED}  WARNING: Secret still found in working tree!${NC}"
  VERIFY_FAIL=1
else
  echo -e "${GREEN}  Working tree: clean${NC}"
  VERIFY_FAIL=0
fi

# Check all history
if git log -p --all -S "${SECRET}" 2>/dev/null | grep -c "${SECRET}" 2>/dev/null | grep -qv "^0$"; then
  echo -e "${RED}  WARNING: Secret still found in git history!${NC}"
  VERIFY_FAIL=1
else
  echo -e "${GREEN}  Git history: clean${NC}"
fi

# Cleanup temp file
rm -f "${REPLACEMENTS_FILE}"

# ── Summary ──────────────────────────────────────────────────
echo ""
if [ "${VERIFY_FAIL}" -eq 0 ]; then
  echo -e "${GREEN}=== PURGE COMPLETE ===${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. REVOKE the exposed credential on GitHub/provider"
  echo "  2. Force push all branches:  git push --force --all"
  echo "  3. Force push tags:          git push --force --tags"
  echo "  4. All collaborators must re-clone the repository"
  echo "  5. Delete the backup when confirmed: rm -rf ${BACKUP_DIR}"
else
  echo -e "${RED}=== PURGE INCOMPLETE — manual review needed ===${NC}"
  echo "  Backup is available at: ${BACKUP_DIR}"
fi
