#!/usr/bin/env bash
# test-update-weekly-tokens.sh — 자정 토큰 wrapper 시나리오 하네스
#
# 실행: bash apps/piesson/scripts/test-update-weekly-tokens.sh
# 실제 vault·upstream·ccusage 를 전혀 건드리지 않는다. 임시 디렉토리에
# 가짜 vault(origin bare 포함)·가짜 piesson upstream·가짜 ccusage/npx 를
# 만들어 wrapper 전체(안전 점검→merge→집계→commit→subtree push→sentinel)를
# 검증한다. PIESSON_* env 시드가 테스트 주입 지점.
#
# 회귀 대상 사고:
#   W2 — 미완료 작업과 복구 상태를 지우던 자동 초기화 제거
#   W5 — 2026-07-20 cmux NODE_OPTIONS 오염 (unset 방어)
set -uo pipefail
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
WRAPPER_SRC="${REPO_ROOT}/apps/piesson/scripts/update-weekly-tokens.sh"
DEPLOY_SRC="${REPO_ROOT}/scripts/subtree-deploy.sh"
TOKENS_PY="${REPO_ROOT}/apps/piesson/dashboard/get_weekly_tokens.py"

T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
check() { if [ "$1" = "$2" ]; then echo "  PASS: $3"; PASS=$((PASS+1)); else echo "  FAIL: $3 (expected $1, got $2)"; FAIL=$((FAIL+1)); fi; }

# ── 가짜 ccusage / npx (PATH 앞에 끼워넣음) ──────────────────────────────
SHIM="$T/shim"; mkdir -p "$SHIM"
cat > "$SHIM/ccusage" <<'S'
#!/bin/sh
# cmux 회귀(W5): NODE_OPTIONS 가 살아있으면 node 가 죽는 상황을 재현
if [ -n "${NODE_OPTIONS:-}" ]; then echo "Error: Cannot find module (simulated)" >&2; exit 1; fi
if [ -n "${FAKE_CCUSAGE_FAIL:-}" ]; then echo "simulated ccusage outage" >&2; exit 1; fi
echo '{"daily":[{"date":"2026-01-01","totalTokens":12345}]}'
S
cat > "$SHIM/npx" <<'S'
#!/bin/sh
if [ -n "${NODE_OPTIONS:-}" ]; then echo "Error: Cannot find module (simulated)" >&2; exit 1; fi
if [ -n "${FAKE_CCUSAGE_FAIL:-}" ]; then echo "simulated codex outage" >&2; exit 1; fi
echo '{"daily":[]}'
S
chmod +x "$SHIM/ccusage" "$SHIM/npx"

# ── 픽스처: 가짜 upstream + 가짜 vault(+bare origin) ────────────────────
MONDAY=$(python3 -c "from datetime import date,timedelta; t=date.today(); m=t-timedelta(days=t.weekday()); print(m.isoformat())")
SUNDAY=$(python3 -c "from datetime import date,timedelta; t=date.today(); m=t-timedelta(days=t.weekday()); print((m+timedelta(days=6)).isoformat())")

setup() {
  cd "$T"; rm -rf vault vault-origin.git up.git upsrc cron cache logs
  mkdir -p cache logs

  git init -q --bare -b main up.git
  git init -q -b main upsrc
  (cd upsrc && git config user.email u@u.u && git config user.name U \
    && mkdir -p dashboard scripts \
    && printf '{"lastUpdated":"2026-01-01","currentWeek":{"startDate":"%s","endDate":"%s","metrics":{"commits":0,"socialContent":{"instagram":0,"tiktok":0,"hellotalk":0},"userSessions":0,"ctoMeetings":0,"blogPosts":0,"workouts":{"running":0,"gym":0},"tokens":{"claude":0,"codex":0,"total":0,"updatedAt":null}}},"weeklyHistory":[]}\n' "$MONDAY" "$SUNDAY" > dashboard/data.json \
    && cp "$TOKENS_PY" dashboard/get_weekly_tokens.py \
    && cp "$WRAPPER_SRC" scripts/update-weekly-tokens.sh \
    && git add -A && git commit -qm up-init \
    && git push -q ../up.git HEAD:refs/heads/main)

  git init -q --bare -b main vault-origin.git
  git init -q -b main vault
  (cd vault && git config user.email t@t.t && git config user.name T \
    && mkdir -p scripts && cp "$DEPLOY_SRC" scripts/subtree-deploy.sh \
    && cp "$REPO_ROOT/scripts/automation-cron-common.sh" scripts/ \
    && echo vault > readme.md && git add -A && git commit -qm init \
    && git remote add origin ../vault-origin.git \
    && git remote add piesson-upstream ../up.git \
    && git subtree add --prefix=apps/piesson piesson-upstream main -m "add piesson subtree" >/dev/null 2>&1 \
    && git push -q origin main \
    && git worktree add -qb chore/cron-data "$T/cron")
}

run_wrapper() {
  (cd "$T/vault" && \
    PIESSON_CRON_SELF_UPDATED="${TEST_SELF_UPDATED-1}" \
    PIESSON_USER_VAULT="$T/vault" \
    PIESSON_CRON_VAULT="$T/cron" \
    PIESSON_LOG_DIR="$T/logs" \
    PIESSON_CACHE_DIR="$T/cache" \
    PIESSON_PATH_PREFIX="$SHIM" \
    bash "${1:-$T/vault/apps/piesson/scripts/update-weekly-tokens.sh}" > "$T/run.log" 2> "$T/run.err.log")
  echo $?
}
upstream_claude() {
  git -C "$T/up.git" show main:dashboard/data.json | python3 -c "import json,sys; print(json.load(sys.stdin)['currentWeek']['metrics']['tokens']['claude'])"
}

echo "── W1: 정상 전체 실행 (안전 점검→집계→commit→subtree push→sentinel)"
setup
check 0 "$(run_wrapper)" "exit 0"
check "$(grep 'update-weekly-tokens.sh starting' "$T/run.log")" "$(grep 'update-weekly-tokens.sh starting' "$T/run.err.log")" 'stdout and stderr share the exact run marker'
grep -q 'update-weekly-tokens.sh finished (exit 0)' "$T/run.err.log"; check 0 $? 'successful stderr run has a terminal boundary'
check 12345 "$(upstream_claude)" "upstream data.json 토큰 반영"
[ "$(cat "$T/cache/last-run-date" 2>/dev/null)" = "$(date +%Y-%m-%d)" ]; check 0 $? "sentinel 기록"

echo "── W2a: dirty + untracked must be preserved, not automatically erased"
setup
check 0 "$(run_wrapper)" "1차 실행으로 worktree 생성"
( cd "$T/cron" && echo corrupted >> readme.md && echo junk > junk.txt )
check 1 "$(run_wrapper)" "dirty worktree refuses automation"
check 2 "$(cd "$T/cron" && git status --porcelain | wc -l | tr -d ' ')" "both changes preserved"

echo "── W2b: 오래된 index.lock도 소유권 확인 없이 지우지 않음"
setup
check 0 "$(run_wrapper)" "1차 실행"
IDX=$(cd "$T/cron" && git rev-parse --git-path index.lock)
( cd "$T/cron" && touch "$IDX" && touch -t 202601010000 "$IDX" )
check 1 "$(run_wrapper)" "index.lock stops automation"
( cd "$T/cron" && [ -f "$(git rev-parse --git-path index.lock)" ] ); check 0 $? "index.lock preserved"

echo "── W2c: 중단된 rebase 상태 보존"
setup
check 0 "$(run_wrapper)" "1차 실행"
( cd "$T/cron" && mkdir -p "$(git rev-parse --git-path rebase-merge)" \
  && echo dummy > "$(git rev-parse --git-path rebase-merge)/head-name" )
check 1 "$(run_wrapper)" "interrupted rebase stops automation"
( cd "$T/cron" && [ -d "$(git rev-parse --git-path rebase-merge)" ] ); check 0 $? "rebase state preserved"

echo "── W2d: 중단된 cherry-pick/sequencer 상태 보존"
setup
check 0 "$(run_wrapper)" "1차 실행"
( cd "$T/cron" && git rev-parse HEAD > "$(git rev-parse --git-path CHERRY_PICK_HEAD)" \
  && mkdir -p "$(git rev-parse --git-path sequencer)" )
check 1 "$(run_wrapper)" "cherry-pick stops automation"
( cd "$T/cron" && [ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ] ); check 0 $? "cherry-pick preserved"

echo "── W3: mutex — 동시 실행 차단"
setup
mkdir -p "$T/cache/.wrapper.lock"
check 75 "$(run_wrapper)" "busy lock is an explicit temporary failure"
check 0 "$(upstream_claude)" "커밋 안 됨 (upstream 무변화)"
rmdir "$T/cache/.wrapper.lock"

echo "── W4: ccusage 전면 장애 → 0이 아닌 기존 값 보존 + 정직한 실패 (2026-07 사고 유형)"
setup
git clone -q up.git upclone
(cd upclone && git config user.email u@u.u && git config user.name U \
  && python3 -c "
import json
d = json.load(open('dashboard/data.json'))
d['currentWeek']['metrics']['tokens'] = {'claude': 777, 'codex': 222, 'total': 999, 'updatedAt': '2026-01-01T00:05:00+09:00'}
json.dump(d, open('dashboard/data.json','w'), indent=2)
" && git add -A && git commit -qm seed-nonzero && git push -q origin main)
UP_BEFORE=$(git -C "$T/up.git" rev-parse main)
export FAKE_CCUSAGE_FAIL=1
check 1 "$(run_wrapper)" "exit 1"
grep -q 'update-weekly-tokens.sh finished (exit 1)' "$T/run.err.log"; check 0 $? 'failed stderr run also has a terminal boundary'
unset FAKE_CCUSAGE_FAIL
check 777 "$(upstream_claude)" "0이 아닌 기존 값(777) 보존 — 0 덮어쓰기 버그를 잡을 수 있는 형태"
check "$UP_BEFORE" "$(git -C "$T/up.git" rev-parse main)" "upstream SHA 불변"

echo "── W5: cmux NODE_OPTIONS 오염 → wrapper 가 unset 해서 생존 (회귀 테스트)"
setup
export NODE_OPTIONS="--require=/tmp/nonexistent/restore.cjs"
check 0 "$(run_wrapper)" "오염된 env 에서도 exit 0"
unset NODE_OPTIONS
check 12345 "$(upstream_claude)" "토큰 정상 집계"

echo '── W6: legacy bootstrap downloaded only wrapper; local helper is absent'
setup
git -C "$T/vault" show origin/main:apps/piesson/scripts/update-weekly-tokens.sh > "$T/downloaded-wrapper.sh"
rm "$T/vault/scripts/automation-cron-common.sh"
MAIN_BEFORE=$(git -C "$T/vault" rev-parse HEAD)
check 0 "$(run_wrapper "$T/downloaded-wrapper.sh")" 'matching remote helper is loaded'
check 12345 "$(upstream_claude)" 'tokens delivered with version-consistent dependencies'
check "$MAIN_BEFORE" "$(git -C "$T/vault" rev-parse HEAD)" 'user checkout HEAD untouched'
[ ! -e "$T/vault/scripts/automation-cron-common.sh" ]; check 0 $? 'does not rewrite canonical checkout'

echo '── W7: dependency-only remote update is picked up without updating user main'
setup
git clone -q "$T/vault-origin.git" "$T/new-release"
git -C "$T/new-release" config user.email release@example.invalid
git -C "$T/new-release" config user.name Release
printf '\necho dependency-revision-loaded\n' >> "$T/new-release/scripts/automation-cron-common.sh"
git -C "$T/new-release" commit -qam dependency-update
git -C "$T/new-release" push -q origin main
MAIN_BEFORE=$(git -C "$T/vault" rev-parse HEAD)
export TEST_SELF_UPDATED=''
mkdir "$T/self-update-temp"
SAVED_TMPDIR="${TMPDIR:-/tmp}"
export TMPDIR="$T/self-update-temp"
printf 'unrelated\n' > "$TMPDIR/keep.txt"
# Exercise GNU mktemp locally when available, matching ubuntu-latest CI.
# The BSD-only `mktemp -t name` silently skips this remote dependency update.
SELF_UPDATE_PATH="$PATH"
if command -v gmktemp >/dev/null 2>&1; then
  mkdir -p "$T/gnu-bin"
  ln -s "$(command -v gmktemp)" "$T/gnu-bin/mktemp"
  export PATH="$T/gnu-bin:$PATH"
fi
check 0 "$(run_wrapper)" 'helper-only self-update works'
export PATH="$SELF_UPDATE_PATH"
unset TEST_SELF_UPDATED
grep -q dependency-revision-loaded "$T/run.log"; check 0 $? 'new dependency actually executed'
check "$MAIN_BEFORE" "$(git -C "$T/vault" rev-parse HEAD)" 'user main not fast-forwarded'
check 1 "$(find "$TMPDIR" -type f | wc -l | tr -d ' ')" 'self-update wrapper and dependencies removed'
check unrelated "$(cat "$TMPDIR/keep.txt")" 'unrelated temporary file retained'

echo '── W8: downloaded wrapper failure preserves exit code and cleans owned files'
printf '\necho self-update-failure-visible >&2\nexit 17\n' >> "$T/new-release/scripts/automation-cron-common.sh"
git -C "$T/new-release" commit -qam failing-dependency
git -C "$T/new-release" push -q origin main
export TEST_SELF_UPDATED=''
check 17 "$(run_wrapper)" 'self-update child failure is propagated'
grep -q self-update-failure-visible "$T/run.err.log"; check 0 $? 'self-update failure diagnostics reach stderr'
unset TEST_SELF_UPDATED
check 1 "$(find "$TMPDIR" -type f | wc -l | tr -d ' ')" 'failure also removes owned temporary files'
check unrelated "$(cat "$TMPDIR/keep.txt")" 'failure retains unrelated temporary file'
export TMPDIR="$SAVED_TMPDIR"

echo; echo "RESULT: $PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
