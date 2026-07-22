#!/usr/bin/env bash
# test-update-weekly-tokens.sh — 자정 토큰 wrapper 시나리오 하네스
#
# 실행: bash apps/piesson/scripts/test-update-weekly-tokens.sh
# 실제 vault·upstream·ccusage 를 전혀 건드리지 않는다. 임시 디렉토리에
# 가짜 vault(origin bare 포함)·가짜 piesson upstream·가짜 ccusage/npx 를
# 만들어 wrapper 전체(자가치유→pull→집계→commit→subtree push→sentinel)를
# 5개 시나리오로 검증한다. PIESSON_* env 시드가 테스트 주입 지점.
#
# 회귀 대상 사고:
#   W2 — 2026-05-30~07-13 45일 장애 (오염된 cron worktree 자가치유)
#   W5 — 2026-07-20 cmux NODE_OPTIONS 오염 (unset 방어)
set -uo pipefail

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
    && echo vault > readme.md && git add -A && git commit -qm init \
    && git remote add origin ../vault-origin.git \
    && git remote add piesson-upstream ../up.git \
    && git subtree add --prefix=apps/piesson piesson-upstream main -m "add piesson subtree" >/dev/null 2>&1 \
    && git push -q origin main)
}

run_wrapper() {
  (cd "$T/vault" && \
    PIESSON_CRON_SELF_UPDATED=1 \
    PIESSON_USER_VAULT="$T/vault" \
    PIESSON_CRON_VAULT="$T/cron" \
    PIESSON_LOG_DIR="$T/logs" \
    PIESSON_CACHE_DIR="$T/cache" \
    PIESSON_PATH_PREFIX="$SHIM" \
    bash "$T/vault/apps/piesson/scripts/update-weekly-tokens.sh" > "$T/run.log" 2>&1)
  echo $?
}
upstream_claude() {
  git -C "$T/up.git" show main:dashboard/data.json | python3 -c "import json,sys; print(json.load(sys.stdin)['currentWeek']['metrics']['tokens']['claude'])"
}

echo "── W1: 정상 전체 실행 (자가치유→집계→commit→subtree push→sentinel)"
setup
check 0 "$(run_wrapper)" "exit 0"
check 12345 "$(upstream_claude)" "upstream data.json 토큰 반영"
[ "$(cat "$T/cache/last-run-date" 2>/dev/null)" = "$(date +%Y-%m-%d)" ]; check 0 $? "sentinel 기록"

echo "── W2a: 오염된 cron worktree (dirty+untracked) 자가치유 (45일 장애 회귀 테스트)"
setup
check 0 "$(run_wrapper)" "1차 실행으로 worktree 생성"
( cd "$T/cron" && echo corrupted >> readme.md && echo junk > junk.txt )
check 0 "$(run_wrapper)" "오염 상태에서도 exit 0 (예전 코드는 여기서 45일간 죽었음)"
check 0 "$(cd "$T/cron" && git status --porcelain | wc -l | tr -d ' ')" "worktree 청결 복구"

echo "── W2b: stale index.lock 자가치유 (killed git process 잔해)"
setup
check 0 "$(run_wrapper)" "1차 실행"
IDX=$(cd "$T/cron" && git rev-parse --git-path index.lock)
( cd "$T/cron" && touch "$IDX" && touch -t 202601010000 "$IDX" )
check 0 "$(run_wrapper)" "index.lock 잔해에도 exit 0"
( cd "$T/cron" && [ -f "$(git rev-parse --git-path index.lock)" ] ); check 1 $? "index.lock 제거됨"

echo "── W2c: 중단된 rebase 잔해 자가치유"
setup
check 0 "$(run_wrapper)" "1차 실행"
( cd "$T/cron" && mkdir -p "$(git rev-parse --git-path rebase-merge)" \
  && echo dummy > "$(git rev-parse --git-path rebase-merge)/head-name" )
check 0 "$(run_wrapper)" "rebase 잔해에도 exit 0"
( cd "$T/cron" && [ -d "$(git rev-parse --git-path rebase-merge)" ] ); check 1 $? "rebase 잔해 제거됨"

echo "── W2d: 중단된 cherry-pick/sequencer 잔해 자가치유"
setup
check 0 "$(run_wrapper)" "1차 실행"
( cd "$T/cron" && git rev-parse HEAD > "$(git rev-parse --git-path CHERRY_PICK_HEAD)" \
  && mkdir -p "$(git rev-parse --git-path sequencer)" )
check 0 "$(run_wrapper)" "cherry-pick 잔해에도 exit 0"
( cd "$T/cron" && [ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ] ); check 1 $? "cherry-pick 잔해 제거됨"

echo "── W3: mutex — 동시 실행 차단"
setup
mkdir -p "$T/cache/.wrapper.lock"
check 0 "$(run_wrapper)" "잠금 보유 중 → 조용히 exit 0"
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
unset FAKE_CCUSAGE_FAIL
check 777 "$(upstream_claude)" "0이 아닌 기존 값(777) 보존 — 0 덮어쓰기 버그를 잡을 수 있는 형태"
check "$UP_BEFORE" "$(git -C "$T/up.git" rev-parse main)" "upstream SHA 불변"

echo "── W5: cmux NODE_OPTIONS 오염 → wrapper 가 unset 해서 생존 (회귀 테스트)"
setup
export NODE_OPTIONS="--require=/tmp/nonexistent/restore.cjs"
check 0 "$(run_wrapper)" "오염된 env 에서도 exit 0"
unset NODE_OPTIONS
check 12345 "$(upstream_claude)" "토큰 정상 집계"

echo; echo "RESULT: $PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
