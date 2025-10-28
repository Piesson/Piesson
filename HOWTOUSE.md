# 📖 GitHub 프로필 대시보드 사용법

> 15살도 쉽게 따라할 수 있는 완벽 가이드!

---

## 🎯 목차
1. [이게 뭐예요?](#-이게-뭐예요)
2. [매일 루틴](#-매일-루틴)
3. [Slack 입력 방법](#-slack-입력-방법)
4. [자동화 시스템](#-자동화-시스템)
5. [메트릭 설명](#-메트릭-설명)
6. [FAQ](#-자주-묻는-질문)

---

## 🎯 이게 뭐예요?

GitHub 프로필에 **자동으로 업데이트되는 2개의 멋진 카드**가 표시됩니다:

### 1. 프로필 카드 (위쪽 - 파이 차트)
```
┌─────────────────────────────────────┐
│  GitHub Activity Overview           │
│                                      │
│  ╱─────╲   📊 Total Commits: 1,476 │
│ ╱ 97%   ╲  📅 Joined: Jan 2025     │
│ ╲       ╱  ⚡ Daily avg: 4.9/day   │
│  ╲─────╱                            │
│                                      │
│  🔵 Commits: 1,476 (97%)           │
│  🟢 Reviews: 23 (2%)               │
│  🟡 PRs: 12 (1%)                   │
│  🔴 Issues: 8 (1%)                 │
└─────────────────────────────────────┘
```
- **업데이트**: 매시간 자동
- **소스**: GitHub GraphQL API
- **기간**: 2020-2025년 전체 (6년간 누적)
  - 각 연도별 쿼리 (2020, 2021, 2022, 2023, 2024, 2025)
  - 6년 커밋을 모두 합산 → Total Commits
- **범위**: 모든 레포지토리 (private 포함)
- **Join date**: 2025년 1월 1일 (하드코딩)
- **Daily avg**: 전체 커밋 ÷ (오늘 - 2025-01-01)
  - ⚠️ 주의: 6년 커밋을 2025년부터 나눠서 높게 표시됨

### 2. 주간 대시보드 (아래쪽 - 6개 메트릭)
```
┌──────────────────────────────────────────┐
│  Moved the needle this week? 📈          │
│  10/27/2025 — 11/02/2025                │
│                                          │
│  ┌──────┬──────┬──────┐                │
│  │ 120  │  15  │  9   │                │
│  │COMMIT│TALKS │SOCIAL│                │
│  ├──────┼──────┼──────┤                │
│  │  2   │  9   │  1   │                │
│  │CHATS │WORKOU│POSTS │                │
│  └──────┴──────┴──────┘                │
└──────────────────────────────────────────┘
```
- **업데이트**: Slack 입력 시 즉시
- **리셋**: 매주 월요일 오전 7시
- **히스토리**: 최근 12주 자동 저장

---

## ⏰ 매일 루틴

### 🌅 Step 1: 오전 7시 - Slack 리마인더 받기

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 ⏰ Time to grind
📅 Week 44: 10/27/2025 — 11/02/2025

📊 THIS WEEK SO FAR: (예시)
🚀 Code Commits: 120 (모든 레포지토리)
💬 User Talks: 15
📱 Social Posts: 9 (IG: 5, TT: 3, HT: 1)
☕ Coffee Chats: 2
🏃 Workouts: 9 (Run: 3, Gym: 6)
📝 Blog Posts: 1

🎯 UPDATE FORMAT:
1 0 0 2 0 0 1 1
(IG TT HT UserTalks Chats Posts Run Gym)

Let's ship it! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 💭 Step 2: 오늘 한 일 떠올리기

오늘 한 일:
- ✅ Instagram 포스트 1개 올림
- ✅ 유저 인터뷰 2번
- ✅ 런닝 1회

### ✍️ Step 3: 숫자로 정리

```
Instagram:    1
TikTok:       0
HelloTalk:    0
User Talks:   2
Coffee Chats: 0
Blog Posts:   0
Running:      1
Gym:          0
```

### 📲 Step 4: Slack에 입력

```
1 0 0 2 0 0 1 0
```

**중요**: 띄어쓰기로 구분! 순서만 맞으면 됩니다.

### ✅ Step 5: 확인 메시지 받기

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Well done! Progress updated successfully!

🔄 ADDED TODAY:
├─ Social: +1 (IG: +1, TT: +0, HT: +0)
├─ User Talks: +2
├─ Coffee Chats: +0
├─ Workouts: +1 (Run: +1, Gym: +0)
└─ Blog Posts: +0

📊 NEW TOTALS:
├─ Social Posts: 10 total (6 IG, 3 TT, 1 HT)
├─ User Talks: 17
├─ Coffee Chats: 2
├─ Workouts: 10 sessions (4 Run, 6 Gym)
└─ Blog Posts: 1

Keep building! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 🎉 Step 6: GitHub 프로필 확인

5분 후 https://github.com/Piesson 방문하면:
- 대시보드가 자동으로 업데이트됨 ✨
- 새로운 숫자가 표시됨
- 히스토리 차트도 업데이트됨

---

## 📥 Slack 입력 방법

### 기본 형식 (8개 숫자)

```
1 0 0 2 0 0 1 1
```

각 위치의 의미:
```
위치  메트릭           예시
━━━━━━━━━━━━━━━━━━━━━━━━━
1번   Instagram        1 = 오늘 포스트 1개
2번   TikTok           0 = 오늘 없음
3번   HelloTalk        0 = 오늘 없음
4번   User Talks       2 = 오늘 유저 대화 2번
5번   Coffee Chats     0 = 오늘 없음
6번   Blog Posts       0 = 오늘 없음
7번   Running          1 = 오늘 런닝 1회
8번   Gym              1 = 오늘 헬스장 1회
```

### 실전 예시

#### 예시 1: 바쁜 하루
```
오늘:
- Instagram 2개, TikTok 1개
- 유저 인터뷰 3번, 커피챗 1번
- 헬스장 1회

입력: 2 1 0 3 1 0 0 1
```

#### 예시 2: 조용한 하루
```
오늘:
- 런닝만 1회

입력: 0 0 0 0 0 0 1 0
```

#### 예시 3: 완전 쉬는 날
```
오늘:
- 아무것도 안 함

입력: 0 0 0 0 0 0 0 0
```

### 💡 입력 팁

1. **띄어쓰기 필수**: `10001001` (X) → `1 0 0 0 1 0 0 1` (O)
2. **순서 중요**: 항상 IG → TT → HT → Talks → Chats → Posts → Run → Gym
3. **오늘 한 일만**: 누적 아님! 오늘 추가할 값만 입력
4. **0도 입력**: 0이어도 입력하면 기록에 남음

### 🚫 흔한 실수

❌ **잘못된 입력**:
```
1 2 3          (숫자 부족 - 8개 필요)
1,0,0,2,0,0,1,1  (쉼표 사용 - 띄어쓰기만)
10 0 0 2 0 0 1 1  (총합 입력 - 오늘 한 일만)
```

✅ **올바른 입력**:
```
1 0 0 2 0 0 1 1   (8개, 띄어쓰기, 오늘 한 일)
```

---

## 🤖 자동화 시스템

### 시스템 1: GitHub 프로필 카드

```
[매시간 00분]
    ↓
GitHub Actions 자동 실행
    ↓
GitHub GraphQL API 호출
├─ 2020년 데이터 조회
├─ 2021년 데이터 조회
├─ 2022년 데이터 조회
├─ 2023년 데이터 조회
├─ 2024년 데이터 조회
└─ 2025년 데이터 조회 (현재)
    ↓
총합 계산 (1,476 커밋)
    ↓
파이 차트 SVG 생성
    ↓
Git 자동 커밋 & 푸시
    ↓
README에 최신 카드 표시 ✅
```

**당신이 할 일**: 없음! 완전 자동 ✨

### 시스템 2: 주간 대시보드

```
[Slack에 숫자 입력]
    ↓
GitHub Actions 수동 트리거
    ↓
slack_update.py 실행
├─ 입력 파싱: "1 0 0 2 0 0 1 1"
├─ data.json 로드
├─ 기존 값에 더하기 (가산)
│  예: IG 5개 + 오늘 1개 = 6개
└─ data.json 저장
    ↓
Slack 확인 메시지 전송 ✅
    ↓
update-dashboard job 자동 실행
├─ GitHub API에서 이번 주 커밋 조회
│  (모든 레포지토리 포함!)
├─ data.json 업데이트 (커밋 수)
├─ SVG 대시보드 생성 (520×330px)
├─ README 히스토리 업데이트
└─ README 차트 업데이트
    ↓
Git 자동 커밋 & 푸시
    ↓
README에 최신 대시보드 표시 ✅
```

**당신이 할 일**: Slack에 8개 숫자만 입력!

### 시스템 3: 주간 자동 리셋

```
[매주 월요일 오전 7시 KST]
    ↓
GitHub Actions 자동 실행
    ↓
check_weekly_reset.py 실행
├─ 현재 주 월요일 계산
├─ 저장된 월요일과 비교
└─ 새로운 주 감지! ✅
    ↓
주간 리셋 수행:
├─ 1. 지난주 데이터 저장
│     data.json → weeklyHistory[0]
│     Week 43: {commits: 42, social: 3, ...}
│
├─ 2. 히스토리 SVG 생성
│     dashboard/history/weekly_history_2025-W43.svg
│
├─ 3. README 업데이트
│     - 히스토리 테이블 (최근 12주)
│     - 누적 진행 차트
│
├─ 4. 현재 주 메트릭 리셋
│     모든 값 → 0 (커밋은 API에서 재계산)
│
└─ 5. Slack 주간 요약 전송
      📊 Week 43 Summary:
      🚀 Commits: 42 (avg 6.0/day)
      💬 User Talks: 2 (avg 0.3/day)
      ...
    ↓
Git 자동 커밋 & 푸시
    ↓
새로운 주 시작! 🎉
```

**당신이 할 일**: 없음! 월요일마다 자동 ✨

---

## 📊 메트릭 설명

### 🚀 Code Commits (코드 커밋)

**계산 방식**:
- GitHub GraphQL API에서 **자동으로** 계산
- 이번 주 월요일 00:00 KST부터 현재까지
- **모든 레포지토리** 포함 (private + public)
- 예: Piesson/Piesson, Piesson/MyApp, Private-Repo 등 모두 합산

**목표**: 하루 20개 커밋

**팁**:
- 작은 커밋도 OK (README 수정, 오타 수정 등)
- 여러 레포지토리에서 작업해도 전부 카운트됨
- 브랜치 상관없이 모든 커밋 포함

### 💬 User Talks (유저 대화)

**포함되는 것**:
- 유저 인터뷰 (1:1, 그룹)
- 사용자 피드백 세션
- 베타 테스터 미팅
- 사용자 서포트 통화

**목표**: 하루 1번

**팁**:
- 10분짜리 퀵 피드백도 카운트
- Zoom, 전화, 대면 모두 OK
- 같은 날 여러 번 해도 다 카운트

### 📱 Social Posts (소셜 포스팅)

**3가지 플랫폼**:
1. **Instagram**: 제품 사진, 개발 과정, 밈
2. **TikTok**: 짧은 영상, 튜토리얼
3. **HelloTalk**: 언어 학습 앱 콘텐츠

**팁**:
- 스토리도 포스트로 카운트
- 리포스트는 제외
- 각 플랫폼별로 따로 카운트

### ☕ Coffee Chats (커피챗)

**포함되는 것**:
- 동료 창업자 미팅
- 투자자 만남
- 멘토와의 대화
- 네트워킹 미팅

**목표**: 주 2회

**팁**:
- 온라인도 OK
- 30분 이상 권장
- 전략적 네트워킹 중요

### 🏃 Workouts (운동)

**2가지 타입**:
1. **Running**: 야외 러닝, 러닝머신
2. **Gym**: 웨이트, 요가, 크로스핏 등

**팁**:
- 20분 이상만 카운트
- 스트레칭만은 제외
- 같은 날 러닝 + 헬스장 → 2번 카운트

### 📝 Blog Posts (블로그 포스팅)

**포함되는 것**:
- AI 관련 글
- 스타트업 경험 공유
- 개발 튜토리얼
- 제품 업데이트

**팁**:
- 초안 작성도 카운트
- Medium, 개인 블로그 등
- 500자 이상 권장

---

## 🎯 사용 시나리오

### 시나리오 1: 일반적인 평일

```
월요일:
09:00 - 코딩 (커밋 15개)
11:00 - 유저 인터뷰 1번
14:00 - Instagram 포스트 1개
18:00 - 헬스장 1회

Slack 입력:
1 0 0 1 0 0 0 1

결과:
✅ 대시보드 업데이트됨
📊 Commits: 15 (API 자동), Social: 6→7, Talks: 10→11, Gym: 5→6
```

### 시나리오 2: 네트워킹 데이

```
화요일:
10:00 - 투자자 미팅 (커피챗)
13:00 - 멘토와 점심
16:00 - 동료 창업자 만남

Slack 입력:
0 0 0 0 3 0 0 0

결과:
✅ 커피챗 3번 추가됨
📊 CoffeeChats: 0→3
```

### 시나리오 3: 콘텐츠 크리에이터 모드

```
수요일:
오전 - TikTok 영상 3개 촬영/편집/업로드
오후 - Instagram 릴스 2개
저녁 - 블로그 글 1개 완성

Slack 입력:
2 3 0 0 0 1 0 0

결과:
✅ 소셜 5개, 블로그 1개 추가
📊 Social: 7→12, BlogPosts: 0→1
```

### 시나리오 4: 완전 쉬는 날

```
일요일:
쉼

Slack 입력:
0 0 0 0 0 0 0 0

결과:
✅ 기록됨 (휴식도 중요!)
📊 lastUpdated: 업데이트되어 저녁 리마인더 스킵됨
```

---

## ❓ 자주 묻는 질문

### Q1: Slack 리마인더가 안 와요!

**원인**:
- GitHub Actions의 cron 스케줄은 UTC 기준
- 오전 7시 KST = UTC 전날 22:00
- 저녁 7시 KST = UTC 10:00

**해결**:
- `.github/workflows/update_dashboard.yml` 확인
- `cron: '0 22 * * *'` (아침), `cron: '0 10 * * *'` (저녁)
- SLACK_WEBHOOK_URL 시크릿 설정 확인

### Q2: 입력했는데 대시보드가 안 바뀌어요!

**체크리스트**:
1. ✅ Slack 확인 메시지 받았는지 확인
2. ✅ GitHub Actions 탭에서 워크플로우 실행 확인
3. ✅ 5-10분 기다리기 (자동화 시간 필요)
4. ✅ 브라우저 캐시 새로고침 (Ctrl+Shift+R)

**로그 확인**:
```
https://github.com/Piesson/Piesson/actions
→ "Update Dashboard" 워크플로우 클릭
→ 최근 실행 확인
```

### Q3: 커밋 수가 0으로 나와요!

**원인**:
- GitHub API 호출 실패 또는 토큰 없음

**해결**:
1. `SUMMARY_CARDS_TOKEN` 시크릿 확인
2. 토큰 권한: `repo` 스코프 필요
3. GitHub Actions 로그에서 에러 확인

**로컬 테스트**:
```bash
cd dashboard
export GITHUB_TOKEN=your_token_here
export USERNAME=Piesson
python3 get_weekly_commits.py
```

### Q4: 주간 리셋이 안 돼요!

**월요일 7시에 자동 실행**:
- `check_weekly_reset.py`가 새로운 주 감지
- data.json의 `startDate`와 현재 주 월요일 비교
- 다르면 리셋 실행, 같으면 스킵

**수동 리셋**:
```bash
python3 dashboard/check_weekly_reset.py
```

### Q5: 프로필 카드에 더미 데이터가 보여요 (156 커밋)

**정상입니다!**
- 로컬 테스트 시: 더미 데이터 (156, 23, 12, 8)
- GitHub Actions 실행 시: 실제 데이터 (1,476, 23, 12, 8)
- 매시간 자동으로 실제 데이터로 업데이트됨

### Q6: 입력 형식을 틀렸어요!

**잘못된 입력 시**:
```
입력: 1 2 3  (숫자 부족)
결과: 파싱 실패, 에러 발생
```

**해결**:
- 다시 올바른 형식으로 입력
- 이전 입력은 무시됨 (누적 안 됨)

**올바른 재입력**:
```
1 0 0 2 0 0 1 1
```

### Q7: 히스토리가 안 보여요!

**확인사항**:
- README.md의 "Weekly History" 섹션 확인
- `dashboard/history/` 폴더에 SVG 파일 있는지 확인
- 최소 2주 이상 사용해야 히스토리 테이블 생성

**파일 위치**:
```
dashboard/history/
├── weekly_history_2025-W42.svg
├── weekly_history_2025-W43.svg
└── weekly_history_2025-W44.svg
```

### Q8: 두 번 입력했는데 어떻게 되나요?

**가산 방식**:
```
첫 번째 입력: 1 0 0 2 0 0 1 0
→ IG: 0+1=1, Talks: 0+2=2, Run: 0+1=1

두 번째 입력: 1 0 0 1 0 0 0 1
→ IG: 1+1=2, Talks: 2+1=3, Gym: 0+1=1

최종 결과:
IG: 2, Talks: 3, Run: 1, Gym: 1
```

**팁**: 여러 번 입력해도 OK! 다 누적됩니다.

### Q9: 월요일에 리마인더가 안 와요!

**정상입니다!**
- 월요일 오전 7시: 주간 리셋 + 요약 메시지
- 아침 리마인더는 스킵됨 (중복 방지)
- 대신 지난주 요약 메시지를 받음

**요약 메시지 예시**:
```
📊 Week 43 (10/20-10/26) Summary

Total:
🚀 Commits: 42
💬 User Talks: 2
...

Ready for Week 44! 💪
```

### Q10: 다른 레포지토리 커밋도 카운트되나요?

**YES! 🎉**
- 프로필 카드: 모든 레포지토리 (2020-2025)
- 주간 대시보드: 이번 주 모든 레포지토리
- Private 레포지토리도 포함
- 브랜치 상관없이 모든 커밋

**예시**:
```
월요일 커밋:
- Piesson/Piesson: 10개
- Piesson/MyApp: 5개
- Private-Project: 3개

대시보드 표시: 18개 (모두 합산)
```

---

## 🛠️ 고급 사용법

### 수동으로 워크플로우 실행하기

#### 방법 1: GitHub 웹사이트
```
1. https://github.com/Piesson/Piesson/actions 접속
2. 왼쪽에서 "Process Slack Response" 선택
3. "Run workflow" 버튼 클릭
4. metrics 입력: 1 0 0 2 0 0 1 1
5. "Run workflow" 클릭
```

#### 방법 2: GitHub CLI
```bash
# Slack 입력 시뮬레이션
gh workflow run slack_response.yml \
  -f metrics="1 0 0 2 0 0 1 1"

# 프로필 카드 강제 업데이트
gh workflow run profile-summary-cards.yml

# 대시보드 강제 업데이트
gh workflow run update_dashboard.yml
```

### 로컬에서 테스트하기

#### 주간 커밋 조회
```bash
cd dashboard
export GITHUB_TOKEN=ghp_your_token_here
export USERNAME=Piesson
python3 get_weekly_commits.py
```

#### Slack 업데이트 시뮬레이션
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
echo "1 0 0 2 0 0 1 1" | python3 slack_update.py
```

#### SVG 생성 테스트
```bash
python3 generate_svg.py
# 출력: dashboard/weekly_dashboard.svg
```

### 데이터 직접 수정하기 (긴급 시)

**주의**: 가능하면 Slack으로 입력하세요!

```bash
# 1. data.json 열기
vim dashboard/data.json

# 2. 값 수정 (예: instagram 5 → 6)
"instagram": 6,

# 3. 저장 후 커밋
git add dashboard/data.json
git commit -m "fix: manual data correction"
git push

# 4. 자동으로 대시보드 재생성됨
```

---

## 💡 프로 팁

### 1. 일관성이 핵심
```
✅ 매일 같은 시간에 입력
✅ 0이어도 입력 (기록 중요)
✅ 루틴화 (오전 7시 리마인더 받자마자)
```

### 2. 작은 것도 카운트
```
✅ 10분 유저 인터뷰 → User Talk 1
✅ 짧은 런닝 20분 → Running 1
✅ Instagram 스토리 → Social 1
```

### 3. 주간 목표 설정
```
커밋: 140개 (하루 20개)
유저 대화: 7번 (하루 1번)
소셜: 14개 (하루 2개)
커피챗: 2번 (주 2번)
운동: 6번 (주 6번)
블로그: 1개 (주 1개)
```

### 4. 히스토리 활용
```
✅ 매주 월요일 지난주 요약 확인
✅ README의 "Weekly History" 테이블 분석
✅ 누적 진행 차트로 트렌드 파악
✅ 투자자/채용담당자에게 보여주기
```

### 5. 동기부여 유지
```
✅ GitHub 프로필을 매일 확인
✅ 진행 상황 공유 (SNS, 블로그)
✅ 목표 달성 시 자축하기
✅ 낮은 주는 분석 후 개선
```

---

## 🎯 목표 설정 가이드

### 초급 (처음 시작)
```
🚀 Commits: 70/week (하루 10개)
💬 User Talks: 3/week
📱 Social Posts: 7/week
☕ Coffee Chats: 1/week
🏃 Workouts: 3/week
📝 Blog Posts: 0.5/week (2주에 1개)
```

### 중급 (안정화)
```
🚀 Commits: 140/week (하루 20개)
💬 User Talks: 7/week (하루 1번)
📱 Social Posts: 14/week (하루 2개)
☕ Coffee Chats: 2/week
🏃 Workouts: 5/week
📝 Blog Posts: 1/week
```

### 고급 (그라인드 모드)
```
🚀 Commits: 210/week (하루 30개)
💬 User Talks: 14/week (하루 2번)
📱 Social Posts: 21/week (하루 3개)
☕ Coffee Chats: 3/week
🏃 Workouts: 6/week
📝 Blog Posts: 2/week
```

---

## 🎉 마무리

### ✅ 핵심 요약

1. **매일**: Slack에 8개 숫자 입력
2. **자동**: 나머지는 GitHub Actions가 처리
3. **확인**: GitHub 프로필에서 진행 상황 추적
4. **분석**: 주간 히스토리로 트렌드 파악

### 🚀 다음 단계

1. **첫 주 완성**: 월요일부터 일요일까지 매일 입력
2. **루틴 만들기**: 오전 7시 리마인더 습관화
3. **목표 설정**: 자신에게 맞는 주간 목표
4. **공유하기**: GitHub 프로필을 이력서/포트폴리오에 추가

### 💪 당신은 할 수 있습니다!

이 시스템은 **당신의 노력을 가시화**하는 도구입니다.
매일 조금씩 진전을 만들고, 그 과정을 기록하세요.

**Remember**: "What gets measured gets managed" 📈

---

## 📞 도움말

### 버그 리포트
GitHub Issues: https://github.com/Piesson/Piesson/issues

### 기능 요청
Discussions: https://github.com/Piesson/Piesson/discussions

### 문서
- **CLAUDE.md**: 개발자용 상세 문서
- **SYSTEM_FLOW_EXPLAINED.md**: 시스템 구조 설명
- **dashboard/README.md**: 대시보드 설정 가이드

---

**만든 사람**: Piesson
**GitHub**: https://github.com/Piesson
**블로그**: https://www.kimkb.com

**마지막 업데이트**: 2025년 10월 28일

**버전**: 2.0 (GitHub API 통합, 모든 레포지토리 추적)
