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

# ── Self-update preamble ──────────────────────────────────────────────────
# Closes the propagation gap from PR merges to LaunchAgent. The vault main
# working tree (where this file lives on disk) doesn't auto-pull from
# origin/main, so a PR that fixes the wrapper itself never reaches
# LaunchAgent without a manual `git pull`. Without this preamble, every
# PR-merge-driven wrapper fix takes effect only on the user's next manual
# pull, which can be days. We close that gap by fetching origin/main here
# (read-only on the working tree) and re-execing the origin version when
# it's newer than what's on disk.
#
# Safety gates (ALL must hold to re-exec):
#   (a) Not already self-updated in this exec chain (env-var guard)
#   (b) Wrapper and companion files have no uncommitted local edits
#   (c) Local HEAD is ancestor of origin/main (no unpushed local commits)
#   (d) origin/main changed the wrapper or one of its companion scripts
#
# Best-effort: any failure here is non-fatal — fall through to the local
# (possibly stale) version. Companion loading and dependency-only updates are
# covered by the in-repository wrapper harness.
{
    if [ -z "${PIESSON_CRON_SELF_UPDATED:-}" ]; then
        USER_VAULT="${PIESSON_USER_VAULT:-/Users/apple/Documents/Obsidian Vault}"
        TARGET_REL="apps/piesson/scripts/update-weekly-tokens.sh"

        if git -C "${USER_VAULT}" fetch origin main --quiet 2>/dev/null; then
            LOCAL_HEAD_BLOB=$(git -C "${USER_VAULT}" rev-parse "HEAD:${TARGET_REL}" 2>/dev/null || true)
            LOCAL_FILE_BLOB=$(git hash-object "${BASH_SOURCE[0]}" 2>/dev/null || true)
            ORIGIN_BLOB=$(git -C "${USER_VAULT}" rev-parse "origin/main:${TARGET_REL}" 2>/dev/null || true)
            DEPENDENCIES_CLEAN=1
            DEPENDENCIES_CHANGED=0
            for dependency in scripts/automation-cron-common.sh scripts/subtree-deploy.sh; do
                head_dep=$(git -C "${USER_VAULT}" rev-parse --verify --quiet "HEAD:${dependency}" 2>/dev/null || true)
                file_dep=$(git hash-object "${USER_VAULT}/${dependency}" 2>/dev/null || true)
                remote_dep=$(git -C "${USER_VAULT}" rev-parse --verify --quiet "origin/main:${dependency}" 2>/dev/null || true)
                [ "$head_dep" = "$file_dep" ] || DEPENDENCIES_CLEAN=0
                [ "$head_dep" = "$remote_dep" ] || DEPENDENCIES_CHANGED=1
            done

            if [ -n "${LOCAL_FILE_BLOB}" ] && [ "${LOCAL_FILE_BLOB}" = "${LOCAL_HEAD_BLOB}" ] && \
               [ "$DEPENDENCIES_CLEAN" = 1 ] && [ -n "${ORIGIN_BLOB}" ] && \
               { [ "${ORIGIN_BLOB}" != "${LOCAL_HEAD_BLOB}" ] || [ "$DEPENDENCIES_CHANGED" = 1 ]; } && \
               git -C "${USER_VAULT}" merge-base --is-ancestor HEAD origin/main 2>/dev/null; then
                FRESH=$(mktemp "${TMPDIR:-/tmp}/piesson-cron-self-update.XXXXXX" 2>/dev/null || true)
                if [ -n "${FRESH}" ] && \
                   git -C "${USER_VAULT}" show "origin/main:${TARGET_REL}" > "${FRESH}" 2>/dev/null; then
                    export PIESSON_CRON_SELF_UPDATED=1
                    # Keep the creator alive to own cleanup on child success
                    # and failure. Never delete a path supplied by an env var.
                    trap 'rm -f -- "$FRESH"' EXIT
                    if /bin/bash "${FRESH}" "$@"; then
                        exit 0
                    else
                        exit $?
                    fi
                fi
                [ -n "${FRESH}" ] && rm -f "${FRESH}"
            fi
        fi
    fi
} || true

set -euo pipefail

# LaunchAgent does not load shell rc files, so every binary we call must
# be reachable via this explicit PATH. PIESSON_PATH_PREFIX is a test seam —
# the harness prepends a shim dir (fake ccusage/npx); unset in production.
export PATH="${PIESSON_PATH_PREFIX:+${PIESSON_PATH_PREFIX}:}/opt/homebrew/bin:/Users/apple/.nvm/versions/node/v22.18.0/bin:/usr/local/bin:/usr/bin:/bin"

# The Stop-hook entry point inherits the Claude session's env. cmux.app
# injects NODE_OPTIONS=--require=$TMPDIR/cmux-.../restore-node-options.cjs
# there, and macOS temp cleanup deletes that file while cmux stays open —
# then EVERY node process (ccusage, npx) dies with MODULE_NOT_FOUND and the
# token update silently skips a day (observed 2026-07-20). Sanitize.
unset NODE_OPTIONS

# PIESSON_* env vars are test seams (fixture vault/worktree/cache paths);
# unset in production, so defaults below are the real locations.
USER_VAULT="${PIESSON_USER_VAULT:-/Users/apple/Documents/Obsidian Vault}"
CRON_VAULT="${PIESSON_CRON_VAULT:-${HOME}/Documents/Obsidian-Vault-cron}"
LOG_DIR="${PIESSON_LOG_DIR:-${HOME}/Library/Logs}"
CACHE_ROOT="${PIESSON_CACHE_DIR:-${HOME}/Library/Caches/piesson-tokens}"
mkdir -p "${LOG_DIR}"

ts() { date '+%Y-%m-%dT%H:%M:%S%z'; }

# The legacy bootstrap downloads only this file. Resolve its companions from
# the SAME verified revision, not from a potentially older canonical checkout.
COMMON_SCRIPT="${USER_VAULT}/scripts/automation-cron-common.sh"
DEPLOY_SCRIPT="${USER_VAULT}/scripts/subtree-deploy.sh"
DEPENDENCY_DIR=""
cleanup_dependencies() {
    if [ -n "$DEPENDENCY_DIR" ]; then
        rm -f "$DEPENDENCY_DIR/common.sh" "$DEPENDENCY_DIR/deploy.sh"
        rmdir "$DEPENDENCY_DIR"
    fi
}
trap cleanup_dependencies EXIT
if [ "${PIESSON_CRON_SELF_UPDATED:-0}" = 1 ] && \
   [ "${BASH_SOURCE[0]}" != "${USER_VAULT}/apps/piesson/scripts/update-weekly-tokens.sh" ]; then
    RELEASE_REV=$(git -C "$USER_VAULT" rev-parse origin/main)
    EXPECTED_BLOB=$(git -C "$USER_VAULT" rev-parse "${RELEASE_REV}:apps/piesson/scripts/update-weekly-tokens.sh")
    [ "$(git hash-object "${BASH_SOURCE[0]}")" = "$EXPECTED_BLOB" ] || { echo 'ERROR: self-update revision changed; retry without mixing versions' >&2; exit 1; }
    DEPENDENCY_DIR=$(mktemp -d "${TMPDIR:-/tmp}/piesson-cron-dependencies.XXXXXX")
    git -C "$USER_VAULT" show "${RELEASE_REV}:scripts/automation-cron-common.sh" > "$DEPENDENCY_DIR/common.sh"
    git -C "$USER_VAULT" show "${RELEASE_REV}:scripts/subtree-deploy.sh" > "$DEPENDENCY_DIR/deploy.sh"
    COMMON_SCRIPT="$DEPENDENCY_DIR/common.sh"
    DEPLOY_SCRIPT="$DEPENDENCY_DIR/deploy.sh"
fi

# All writers, including the daily PR adapter, share this mutex. Never steal
# an old lock: a slow or suspended process may still own it.
source "$COMMON_SCRIPT"
RUN_START=""
finish_wrapper() {
    local rc=$1
    cleanup_dependencies || rc=1
    # Close diagnostics before unlocking so a following health check sees
    # the whole run, never a later invocation's preflight failure.
    if [ -n "$RUN_START" ]; then
        echo "[$(ts)] update-weekly-tokens.sh finished (exit $rc)" >&2
    fi
    automation_cron_finish "$rc"
    return "$rc"
}
trap 'rc=$?; finish_wrapper "$rc"; exit "$rc"' EXIT
automation_cron_lock

RUN_START="[$(ts)] update-weekly-tokens.sh starting"
echo "$RUN_START"
# The health report correlates diagnostics to this exact run, not a stale
# error-log tail. Keep raw stderr local; the report exports fixed categories.
echo "$RUN_START" >&2
automation_cron_prepare
VAULT="${CRON_VAULT}"
cd "${VAULT}"

cleanup() {
    # Preflight proved there was no operation before this run. Abort only a
    # merge started by this locked run; never discard unrelated dirty files.
    if [ -f "$(git rev-parse --git-path MERGE_HEAD)" ]; then
        git merge --abort || return 1
    fi
}
trap 'rc=$?; cleanup || rc=1; finish_wrapper "$rc"; exit "$rc"' EXIT

echo "[$(ts)] step 1: merged origin/main without replaying subtree history"

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
    # Worktree-safe MERGE_HEAD check (same fix as in cleanup()): the path
    # `.git/MERGE_HEAD` doesn't resolve in a worktree because `.git` is a
    # gitdir-pointer FILE there, not a directory. Use git plumbing instead.
    if [ ! -f "$(git rev-parse --git-path MERGE_HEAD 2>/dev/null)" ]; then
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
        git merge --abort
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
SUBTREE_DEPLOY_CONSERVATIVE=1 bash "$DEPLOY_SCRIPT" apps/piesson piesson-upstream

# Mark today as handled so the Stop-hook backstop knows not to re-fire.
# Both triggers (LaunchAgent + Claude Code Stop) share this sentinel.
mkdir -p "${CACHE_ROOT}"
date +%Y-%m-%d > "${CACHE_ROOT}/last-run-date"

echo "[$(ts)] update-weekly-tokens.sh done"
