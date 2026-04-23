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
#
# Historical incident (2026-04-17 → 2026-04-23): conflicts during subtree pull
# left several untracked files (200-Daily/*.md and others) permanently trapped
# inside stashes. The `git stash pop` branch logged "restored stashed state"
# even when pop was incomplete, because we were suppressing its stderr.
#
# Hardened flow:
#   (1) Record the list of untracked files in a manifest file BEFORE stashing.
#   (2) After `git stash pop` in cleanup, re-read the manifest and verify that
#       every listed path exists in the worktree.
#   (3) If any are missing, force-rescue them via `git checkout <stash>^3 -- <path>`.
#   (4) Only delete the manifest once every file is confirmed present.
STASH_TAG="piesson-tokens-auto-stash-$(date +%s)"
STASH_MANIFEST="${TMPDIR:-/tmp}/${STASH_TAG}.manifest"
STASHED=0
if [ -n "$(git status --porcelain)" ]; then
    # Snapshot untracked paths BEFORE stash push so we can audit after pop.
    # `-c core.quotepath=false` preserves UTF-8 filenames (e.g. Korean).
    git -c core.quotepath=false status --porcelain \
        | awk '/^\?\? /{ sub(/^\?\? /, ""); print }' \
        > "${STASH_MANIFEST}"
    if git stash push --include-untracked -m "${STASH_TAG}" >/dev/null; then
        STASHED=1
        untracked_count=$(wc -l < "${STASH_MANIFEST}" | tr -d ' ')
        echo "[$(ts)] stashed dirty vault state: ${STASH_TAG} (untracked_manifest=${untracked_count})"
    else
        rm -f "${STASH_MANIFEST}"
    fi
fi

# Verify every path in the manifest exists in the worktree. Any that are
# missing get rescued directly from the stash's untracked tree (the "^3"
# parent exists because we stashed with --include-untracked). Returns 0 only
# when every file in the manifest is confirmed present.
verify_manifest_or_rescue() {
    [ ! -f "${STASH_MANIFEST}" ] && return 0

    local stash_ref=""
    stash_ref=$(git stash list | grep -F "${STASH_TAG}" | awk -F: 'NR==1{print $1}')

    local missing_count=0
    local rescued=0
    local rescue_failed=0
    local f
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        [ -e "$f" ] && continue
        missing_count=$((missing_count + 1))
        if [ -n "$stash_ref" ]; then
            mkdir -p "$(dirname "$f")" 2>/dev/null || true
            if git -c core.quotepath=false checkout "${stash_ref}^3" -- "$f" 2>/dev/null; then
                # File was originally untracked — remove from index to keep
                # that status after rescue.
                git reset --quiet HEAD -- "$f" 2>/dev/null || true
                rescued=$((rescued + 1))
                echo "[$(ts)]   RESCUE ok:     $f" >&2
            else
                rescue_failed=$((rescue_failed + 1))
                echo "[$(ts)]   RESCUE FAILED: $f" >&2
            fi
        else
            rescue_failed=$((rescue_failed + 1))
            echo "[$(ts)]   RESCUE FAILED (stash ref not found): $f" >&2
        fi
    done < "${STASH_MANIFEST}"

    if [ "${missing_count}" -gt 0 ]; then
        echo "[$(ts)] manifest verify: missing=${missing_count} rescued=${rescued} failed=${rescue_failed}" >&2
    fi

    # Only drop the manifest when every listed path is present. Otherwise
    # keep it so stash-audit.sh and future runs can see what's outstanding.
    if [ "${rescue_failed}" -eq 0 ]; then
        rm -f "${STASH_MANIFEST}"
        return 0
    fi
    return 1
}

cleanup() {
    # Abort any pending merge first so stash pop can write a clean index.
    if [ -f .git/MERGE_HEAD ]; then
        echo "[$(ts)] cleanup: aborting pending merge" >&2
        git merge --abort 2>/dev/null || git reset --merge 2>/dev/null || true
    fi

    if [ "${STASHED}" = "1" ]; then
        # Look up the stash by tag rather than index, since intermediate git
        # operations may have shifted indices.
        local stash_ref
        stash_ref=$(git stash list | grep -F "${STASH_TAG}" | awk -F: 'NR==1{print $1}')
        if [ -n "${stash_ref}" ]; then
            # Capture pop output so we can surface real errors (the previous
            # `>/dev/null 2>&1` is what masked the 2026-04-23 incident).
            local pop_log
            pop_log=$(git stash pop "${stash_ref}" 2>&1) || true
            if git stash list | grep -qF "${STASH_TAG}"; then
                echo "[$(ts)] WARNING: stash pop did not complete; stash kept at ${stash_ref}" >&2
                echo "${pop_log}" | sed 's/^/[pop] /' >&2
            else
                echo "[$(ts)] stash popped"
            fi
        fi

        # Manifest verification runs whether or not pop appeared to succeed —
        # belt-and-suspenders against any code path that silently drops files.
        verify_manifest_or_rescue || true
    fi
}
trap cleanup EXIT

echo "[$(ts)] step 1: git pull --rebase origin main"
git pull --rebase origin main

echo "[$(ts)] step 2: git subtree pull apps/piesson <- piesson-upstream (pull-only)"
# The upstream workflow continuously regenerates dashboard/data.json with
# fresh commit counts and timestamps. That regeneration routinely conflicts
# with our in-flight copy. Step 3 rewrites tokens anyway, so on a data.json
# conflict we take upstream's version. Any *other* conflict is unexpected
# and we bail rather than silently paper over something important.
set +e
git subtree pull --prefix=apps/piesson piesson-upstream main --squash \
    -m "merge: sync apps/piesson from upstream"
pull_rc=$?
set -e

if [ "${pull_rc}" -ne 0 ]; then
    if [ ! -f .git/MERGE_HEAD ]; then
        echo "[$(ts)] subtree pull failed without merge state, aborting" >&2
        exit "${pull_rc}"
    fi

    # Auto-resolve conflicts on files that upstream regenerates on its own
    # (Piesson's profile-summary-cards.yml + update_dashboard.yml rewrite these
    # several times a day). Vault side never edits them intentionally; taking
    # --theirs is the documented recovery path in apps/piesson/CLAUDE.md.
    #
    # Anything outside the whitelist is a real divergence we want a human to
    # look at, so we abort instead of silently clobbering it.
    unresolved=$(git diff --name-only --diff-filter=U)
    # Full list of upstream-authoritative paths per apps/piesson/CLAUDE.md
    # "Files to NEVER Manually Edit":
    #   - dashboard/data.json               (slack_response.yml, update_dashboard.yml)
    #   - dashboard/weekly_dashboard.svg    (generate_svg.py)
    #   - dashboard/progress_sparklines.svg (generate_progress_chart.py)
    #   - dashboard/history/**              (generate_weekly_history.py on weekly reset)
    #   - profile-summary-card-output/**    (vn7n24fzkq action + generate_profile_card.py)
    #   - README.md                         (update_readme_*.py)
    whitelist_re='^apps/piesson/(dashboard/(data\.json$|weekly_dashboard\.svg$|progress_sparklines\.svg$|history/)|profile-summary-card-output/|README\.md$)'
    unexpected=$(printf '%s\n' "${unresolved}" | grep -v -E "${whitelist_re}" || true)

    if [ -n "${unexpected}" ]; then
        echo "[$(ts)] unexpected conflicts outside upstream-regen whitelist, aborting merge:" >&2
        printf '%s\n' "${unexpected}" >&2
        git merge --abort 2>/dev/null || git reset --merge 2>/dev/null || true
        exit 1
    fi

    echo "[$(ts)] auto-resolving upstream-regenerated conflicts (take --theirs):"
    printf '%s\n' "${unresolved}" | sed 's/^/  /'
    printf '%s\n' "${unresolved}" | while IFS= read -r conflict_file; do
        [ -z "${conflict_file}" ] && continue
        # checkout --theirs handles modify/modify and add/add; for delete cases
        # fall through to git rm. Then stage whichever path git now sees.
        if ! git checkout --theirs -- "${conflict_file}" 2>/dev/null; then
            git rm -f --quiet -- "${conflict_file}" 2>/dev/null || true
        fi
        git add -- "${conflict_file}" 2>/dev/null || \
            git rm -f --quiet -- "${conflict_file}" 2>/dev/null || true
    done
    git commit --no-edit -q
fi

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

# Mark today as handled so the Stop-hook backstop knows not to re-fire.
# Both triggers (LaunchAgent + Claude Code Stop) share this sentinel.
CACHE_DIR="${HOME}/Library/Caches/piesson-tokens"
mkdir -p "${CACHE_DIR}"
date +%Y-%m-%d > "${CACHE_DIR}/last-run-date"

echo "[$(ts)] update-weekly-tokens.sh done"
