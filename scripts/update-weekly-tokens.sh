#!/usr/bin/env bash
# Daily 00:05 KST wrapper for the Piesson weekly token dashboard.
#
# Flow:
#   1. sync vault with its own upstream (obsidian-vault)
#   2. pull-only subtree pull from Piesson/Piesson so the apps/piesson/
#      subtree reflects upstream's latest reset state
#   3. run dashboard/get_weekly_tokens.py which reads currentWeek dates
#      from data.json and writes claude/codex/total tokens back to it
#   4. commit only dashboard/data.json (never sweeps other dirty files)
#   5. subtree-deploy.sh to push vault -> Piesson/Piesson

set -euo pipefail

# LaunchAgent does not load shell rc files, so every binary we call must
# be reachable via this explicit PATH.
export PATH="/opt/homebrew/bin:/Users/apple/.nvm/versions/node/v22.18.0/bin:/usr/local/bin:/usr/bin:/bin"

VAULT="/Users/apple/Documents/Obsidian Vault"
LOG_DIR="${HOME}/Library/Logs"
mkdir -p "${LOG_DIR}"

ts() { date '+%Y-%m-%dT%H:%M:%S%z'; }

echo "[$(ts)] update-weekly-tokens.sh starting"

cd "${VAULT}"

# Vault is typically dirty from Obsidian edits. Stash those so pull/rebase
# and subtree pull can run, then restore at the end.
STASH_TAG="piesson-tokens-auto-stash-$(date +%s)"
STASHED=0
if [ -n "$(git status --porcelain)" ]; then
    if git stash push --include-untracked -m "${STASH_TAG}" >/dev/null; then
        STASHED=1
        echo "[$(ts)] stashed dirty vault state: ${STASH_TAG}"
    fi
fi

cleanup() {
    if [ "${STASHED}" = "1" ]; then
        # Look up the stash by tag rather than index, since intermediate git
        # operations may have shifted indices.
        local stash_ref
        stash_ref=$(git stash list | grep -F "${STASH_TAG}" | head -1 | cut -d: -f1)
        if [ -n "${stash_ref}" ]; then
            if ! git stash pop "${stash_ref}" >/dev/null; then
                echo "[$(ts)] WARNING: stash pop had conflicts; stash left at ${stash_ref}" >&2
            else
                echo "[$(ts)] restored stashed state"
            fi
        fi
    fi
}
trap cleanup EXIT

echo "[$(ts)] step 1: git pull --rebase origin main"
git pull --rebase origin main

echo "[$(ts)] step 2: git subtree pull apps/piesson <- piesson-upstream (pull-only)"
git subtree pull --prefix=apps/piesson piesson-upstream main --squash \
    -m "merge: sync apps/piesson from upstream"

echo "[$(ts)] step 3: run dashboard/get_weekly_tokens.py"
cd "${VAULT}/apps/piesson"
python3 dashboard/get_weekly_tokens.py

echo "[$(ts)] step 4: scoped commit of data.json (if changed)"
cd "${VAULT}"
if ! git diff --quiet -- apps/piesson/dashboard/data.json; then
    git commit --only apps/piesson/dashboard/data.json \
        -m "chore(piesson): update weekly token usage"
    echo "[$(ts)] committed"
else
    echo "[$(ts)] no token changes to commit"
fi

echo "[$(ts)] step 5: subtree-deploy.sh (push)"
bash scripts/subtree-deploy.sh apps/piesson piesson-upstream

echo "[$(ts)] update-weekly-tokens.sh done"
