# GitHub Profile Dashboard - Complete Documentation (2025)

**목적**: 자동화된 GitHub 프로필 대시보드. 코드 작성 → Slack 입력 → README 자동 업데이트.

---

## 📚 Table of Contents

1. [기초 개념 (Essential Concepts)](#기초-개념-essential-concepts)
2. [시스템 아키텍처 (System Architecture)](#시스템-아키텍처-system-architecture)
3. [자동화 플로우 (Automation Flow)](#자동화-플로우-automation-flow)
4. [구성 요소 상세 (Component Details)](#구성-요소-상세-component-details)
5. [트러블슈팅 (Troubleshooting)](#트러블슈팅-troubleshooting)

---

# 기초 개념 (Essential Concepts)

## 1. 인터넷 통신 기초 (Internet Communication Basics)

### HTTP 요청/응답 (Request/Response)

인터넷에서 두 컴퓨터가 대화하는 방법:

```
당신의 컴퓨터 (Client)          서버 (Server)
      |                              |
      | ---- HTTP 요청 (Request) --> |
      |      "데이터 주세요!"          |
      |                              |
      | <--- HTTP 응답 (Response) -- |
      |      "여기 데이터입니다"       |
      |                              |
```

**HTTP 메서드 (Methods)**:
- `GET`: 데이터 읽기 (예: 웹페이지 보기)
- `POST`: 데이터 보내기 (예: 폼 제출, 댓글 작성)
- `PUT`: 데이터 수정
- `DELETE`: 데이터 삭제

**HTTP 상태 코드 (Status Codes)**:
- `200 OK`: 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 필요
- `404 Not Found`: 찾을 수 없음
- `500 Internal Server Error`: 서버 오류

### REST API란?

**REST API** = 웹에서 데이터를 주고받는 표준 방법

**예시**: GitHub API
```
GET https://api.github.com/users/Piesson
→ Piesson 사용자 정보 반환

POST https://api.github.com/repos/Piesson/Piesson/dispatches
→ GitHub Actions workflow 실행
```

**특징**:
- URL로 리소스 식별
- HTTP 메서드로 작업 수행
- JSON 형식으로 데이터 교환

---

## 2. Webhooks 개념

### Webhook이란?

**비유**: 문자 알림 서비스
- **API (전통적 방법)**: 매 5분마다 "새 메시지 있어?" 물어보기 (Polling)
- **Webhook (현대적 방법)**: 새 메시지가 오면 자동으로 알림 (Push)

### Webhook 작동 방식

```
[이벤트 발생]               [Webhook]                [당신의 앱]
   Slack                  Cloudflare              GitHub Actions
    |                      Worker                     |
    | 사용자가 메시지 입력        |                     |
    | "/grind 1 0 0 2"        |                     |
    |                        |                     |
    | --- POST 요청 -------> |                     |
    |    (JSON 데이터)         |                     |
    |                        |                     |
    |                        | 데이터 변환 + 인증     |
    |                        | 토큰 추가             |
    |                        |                     |
    |                        | --- POST 요청 ---> |
    |                        |    (인증된 요청)     |
    |                        |                     |
    |                        |                     | Workflow 실행
    |                        |                     | Dashboard 업데이트
    |                        |                     |
    | <----- 성공 응답 ----------------------- |
    | "✅ 업데이트 완료!"                           |
```

**Webhook의 장점**:
- ✅ 실시간 업데이트 (즉시)
- ✅ 서버 부하 감소 (이벤트 발생시에만)
- ✅ 효율적 (불필요한 요청 없음)

**Webhook vs API**:
| 비교 | API (Polling) | Webhook (Push) |
|------|---------------|----------------|
| 방식 | 주기적으로 확인 | 이벤트 발생시 알림 |
| 속도 | 느림 (5분 간격) | 빠름 (즉시) |
| 효율 | 낮음 (불필요한 요청) | 높음 (필요시만) |
| 예시 | 매 5분마다 "새 메일?" | 새 메일 오면 즉시 알림 |

---

## 3. 중간 다리 (Middleware) 개념

### 왜 중간 다리가 필요한가?

**문제 상황**:
```
Slack                           GitHub
  |                               |
  | "1 0 0 2 0 0 1 1"            |
  | (Slack 형식)                 |
  |                               |
  | --- 직접 전달 불가! --------> X
  |                               |
  | ❌ 다른 언어를 사용           |
  | ❌ 인증 토큰이 없음           |
  | ❌ 포맷이 맞지 않음           |
```

**해결책: 중간 다리 (Cloudflare Worker)**:
```
Slack                Cloudflare Worker              GitHub
  |                         |                          |
  | "1 0 0 2 0 0 1 1"      |                          |
  | (Slack 형식)           |                          |
  |                         |                          |
  | ------ POST --------> |                          |
  |                         |                          |
  |                         | 1. 데이터 추출           |
  |                         |    "1 0 0 2 0 0 1 1"    |
  |                         |                          |
  |                         | 2. 형식 변환              |
  |                         |    JSON으로 변환          |
  |                         |                          |
  |                         | 3. 인증 토큰 추가         |
  |                         |    Bearer ghp_xxx...     |
  |                         |                          |
  |                         | 4. GitHub API 호출       |
  |                         |                          |
  |                         | -------- POST -------> |
  |                         |    (인증된 요청)          |
  |                         |                          |
  |                         |                          | ✅ Workflow 실행
  | <---- 성공 응답 ----------------------- |         |
```

### 중간 다리가 하는 일 3가지

#### 1️⃣ 언어 번역 (Data Transformation)

**Slack이 보내는 형식** (Form-encoded):
```
token=abc123&text=1+0+0+2+0+0+1+1&user_name=Piesson
```

**GitHub이 이해하는 형식** (JSON):
```json
{
  "ref": "main",
  "inputs": {
    "metrics": "1 0 0 2 0 0 1 1"
  }
}
```

#### 2️⃣ 보안 인증 (Authentication)

**Slack**: 인증 토큰을 보낼 방법이 없음
```
POST https://api.github.com/...
(헤더 없음) ❌
```

**Cloudflare Worker**: 안전하게 보관된 토큰 추가
```
POST https://api.github.com/...
Authorization: Bearer ghp_xxxxxxxxxxxxx ✅
```

#### 3️⃣ 프로토콜 변환 (Protocol Conversion)

**Slack**: `application/x-www-form-urlencoded`
**GitHub**: `application/json`

중간 다리가 이 두 형식을 변환합니다.

### 왜 Cloudflare Workers를 선택했나?

**다른 옵션들**:
- ❌ **AWS Lambda**: 복잡한 설정, 비용 발생 가능
- ❌ **Zapier/IFTTT**: 월 사용료, 제한적 기능
- ❌ **직접 서버 운영**: 유지보수 필요, 24/7 가동

**✅ Cloudflare Workers**:
- 완전 무료 (하루 100,000 요청)
- 서버 관리 불필요
- 전 세계 배포 (빠른 응답)
- 5분만에 설정 완료

---

## 4. GitHub Actions 기초

### GitHub Actions란?

**CI/CD 플랫폼** = 코드 변경을 자동으로 빌드/테스트/배포하는 시스템

**예시**:
- 코드 push → 자동으로 테스트 실행
- 이슈 생성 → 자동으로 라벨 추가
- Slack 입력 → 자동으로 대시보드 업데이트

### Workflow 구조

**Workflow** = `.github/workflows/` 폴더의 YAML 파일

```yaml
name: Update Dashboard          # Workflow 이름

on:                              # 트리거 (언제 실행?)
  push:                          # Push 이벤트
    paths:
      - 'dashboard/data.json'    # 이 파일 변경시
  schedule:                      # 스케줄
    - cron: '0 22 * * *'        # 매일 10PM UTC (7AM KST)

jobs:                            # 실행할 작업들
  update-dashboard:              # Job 이름
    runs-on: ubuntu-latest       # 실행 환경
    steps:                       # 단계별 명령
      - name: Checkout           # 1단계: 코드 가져오기
        uses: actions/checkout@v4

      - name: Run script         # 2단계: 스크립트 실행
        run: python script.py
```

### Workflow 트리거 방식

#### 1️⃣ Push Event
```yaml
on:
  push:
    paths:
      - 'dashboard/data.json'    # 이 파일이 push되면 실행
```

#### 2️⃣ Schedule (Cron)
```yaml
on:
  schedule:
    - cron: '0 22 * * *'         # 매일 10PM UTC
    - cron: '0 22 * * 1'         # 매주 월요일 10PM UTC
```

**Cron 문법**:
```
분 시 일 월 요일
│ │ │ │  │
│ │ │ │  └─ 0-6 (일요일=0)
│ │ │ └──── 1-12 (1월=1)
│ │ └─────── 1-31
│ └──────────── 0-23 (UTC)
└────────────────── 0-59
```

예시:
- `0 22 * * *` = 매일 10PM UTC (7AM KST)
- `0 22 * * 1` = 매주 월요일 10PM UTC
- `15 12 * * *` = 매일 12:15PM UTC (9:15PM KST)

#### 3️⃣ Workflow Dispatch (수동 실행)
```yaml
on:
  workflow_dispatch:             # GitHub UI에서 수동 실행 버튼
    inputs:                      # 입력 파라미터
      metrics:
        description: 'Metrics'
        required: true
        type: string
```

### 중요한 보안 이슈: GITHUB_TOKEN의 한계

**문제**: 기본 `GITHUB_TOKEN`으로 push한 커밋은 다른 workflow를 트리거하지 않습니다.

```yaml
# ❌ 작동하지 않음
- uses: actions/checkout@v4     # 기본 GITHUB_TOKEN 사용
- run: |
    git add .
    git commit -m "update"
    git push                      # 이 push는 다른 workflow 실행 안 함!
```

**이유**: 무한 루프 방지
```
Workflow A → push → Workflow B → push → Workflow A → ... (무한)
```

**해결책**: Personal Access Token (PAT) 사용
```yaml
# ✅ 작동함
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.PAT_TOKEN }}   # PAT 사용
- run: |
    git add .
    git commit -m "update"
    git push                           # 이 push는 다른 workflow 실행!
```

---

## 5. GitHub Personal Access Token (PAT)

### PAT란?

**Personal Access Token** = GitHub 비밀번호를 대신하는 안전한 토큰

**비유**: 호텔 키 카드
- 비밀번호 = 마스터 키 (모든 것에 접근)
- PAT = 특정 방 키 카드 (제한된 권한)

### PAT 종류 (2025년 기준)

#### 1️⃣ Classic PAT (구식)
```
장점: 간단함
단점: 모든 repo에 접근, 만료 없음 가능, 너무 많은 권한
```

#### 2️⃣ Fine-grained PAT (권장 ⭐)
```
장점:
- 특정 repo만 선택 가능
- 50개 이상의 세밀한 권한
- 조직 관리자가 승인 가능
- 자동 만료 설정
```

### PAT Scopes (권한)

우리 프로젝트에 필요한 권한:

```
Repository Permissions:
├─ Actions: Read and write       # Workflow 트리거
├─ Contents: Read and write      # 코드 push
└─ Metadata: Read-only           # 기본 repo 정보
```

**Scopes 선택 규칙**: **최소 권한 원칙**
- ✅ 필요한 것만 부여
- ❌ 불필요한 권한은 절대 부여하지 않음

### PAT 보안 Best Practices (2025)

1. **절대로 코드에 넣지 말 것**
   ```python
   # ❌ 절대 안 됨!
   token = "ghp_xxxxxxxxxxxx"

   # ✅ 환경변수 사용
   token = os.getenv('GITHUB_TOKEN')
   ```

2. **GitHub Secrets에 저장**
   ```bash
   gh secret set MY_PAT_TOKEN
   ```

3. **만료 기간 설정**
   - 90일 권장
   - 무기한은 위험

4. **정기적으로 갱신**
   - 3개월마다 새 토큰 생성
   - 이전 토큰 삭제

5. **용도별로 분리**
   ```
   PAT_WORKFLOW_TRIGGER  # Workflow 트리거 전용
   PAT_PACKAGE_PUBLISH   # Package 배포 전용
   PAT_READ_ONLY         # 읽기 전용
   ```

---

## 6. Slack App과 Slash Commands

### Slack App이란?

**Slack App** = Slack에 기능을 추가하는 프로그램

**종류**:
- **Bot** (챗봇): 메시지 보내고 받기
- **Slash Command**: `/명령어` 형태로 실행
- **Workflow**: GUI로 자동화 구성
- **Incoming Webhook**: 외부 → Slack 메시지 전송

### Slash Command

**형식**:
```
/grind 1 0 0 2 0 0 1 1
│      └─ 파라미터
└─ 명령어
```

**작동 방식**:
```
1. 사용자가 Slack에서 입력
   /grind 1 0 0 2 0 0 1 1

2. Slack이 지정된 URL로 POST 요청
   POST https://your-worker.workers.dev
   Body: token=xxx&text=1+0+0+2&user_name=Piesson

3. Worker가 처리하고 응답
   Response: {"text": "✅ 성공!"}

4. Slack이 응답 표시
   "✅ 성공!"
```

### Incoming Webhook

**용도**: 외부 프로그램 → Slack 메시지 전송

**예시**: GitHub Actions가 Slack에 알림 보내기
```python
import requests

webhook_url = "https://hooks.slack.com/services/T.../B.../xxx"
message = {
    "text": "✅ 업데이트 완료!",
    "username": "GrindBot",
    "icon_emoji": ":rocket:"
}

requests.post(webhook_url, json=message)
```

---

## 7. Cloudflare Workers 상세

### Serverless란?

**Serverless** = 서버 없이 코드 실행

**전통적 방식**:
```
1. 서버 구매/임대 💸
2. 운영체제 설치 ⚙️
3. 웹 서버 설정 🛠️
4. 24/7 관리 필요 😰
5. 트래픽 증가시 서버 추가 📈
```

**Serverless (Cloudflare Workers)**:
```
1. 코드 작성 ✍️
2. 배포 🚀
3. 끝! 😎
(서버 관리 = Cloudflare가 자동으로)
```

### Cloudflare Workers 작동 원리

```
[사용자 요청]
     ↓
[가장 가까운 Cloudflare 데이터센터]
     ↓
[Worker 실행] ← 여기서 코드 실행! (밀리초 단위)
     ↓
[응답 반환]
```

**특징**:
- ⚡ 빠름: 전 세계 300+ 도시에 배포
- 💰 무료: 하루 100,000 요청
- 🚀 확장 자동: 트래픽 증가해도 OK
- ❄️ Cold Start 없음: 항상 빠른 응답

### 우리 Worker의 역할

```javascript
// 1. Slack 요청 받기
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 2. 데이터 추출 및 변환
async function handleRequest(request) {
  const formData = await request.formData()
  const text = formData.get('text')  // "1 0 0 2 0 0 1 1"

  // 3. GitHub API 호출
  const response = await fetch('https://api.github.com/...', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GITHUB_TOKEN}`,  // 환경변수
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      ref: 'main',
      inputs: { metrics: text }
    })
  })

  // 4. Slack에 응답
  return new Response(JSON.stringify({
    text: '✅ Workflow triggered!'
  }))
}
```

---

# 시스템 아키텍처 (System Architecture)

## 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Profile                           │
│  https://github.com/Piesson                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     README.md                              │ │
│  │ ┌─────────────────┐  ┌─────────────────┐                 │ │
│  │ │  Profile Card   │  │ Weekly Dashboard│                 │ │
│  │ │   (500x220px)   │  │   (520x330px)   │                 │ │
│  │ └─────────────────┘  └─────────────────┘                 │ │
│  │ ┌─────────────────────────────────────────┐               │ │
│  │ │      Consistent enough? (Charts)        │               │ │
│  │ └─────────────────────────────────────────┘               │ │
│  │ ┌─────────────────────────────────────────┐               │ │
│  │ │      Weekly History (Table)             │               │ │
│  │ └─────────────────────────────────────────┘               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           ▲ ▲ ▲
                           │ │ │
        ┌──────────────────┘ │ └─────────────────┐
        │                    │                   │
┌───────┴────────┐  ┌────────┴────────┐  ┌──────┴─────────┐
│ GitHub Actions │  │ GitHub Actions  │  │ GitHub Actions │
│ Workflow 1     │  │ Workflow 2      │  │ Workflow 3     │
│ Profile Card   │  │ Dashboard       │  │ Slack Input    │
│ (Daily 7AM)    │  │ (Schedule/Push) │  │ (Manual)       │
└────────────────┘  └─────────────────┘  └────────────────┘
                                                  ▲
                                                  │
                                          ┌───────┴────────┐
                                          │  Cloudflare    │
                                          │  Worker        │
                                          │  (중간 다리)     │
                                          └───────┬────────┘
                                                  ▲
                                                  │
                                            ┌─────┴──────┐
                                            │   Slack    │
                                            │  /grind    │
                                            └────────────┘
```

## 데이터 흐름 (Data Flow)

### Flow 1: Profile Card 업데이트 (매일 자동)

```
[Schedule: Daily 7AM KST]
         ↓
[profile-summary-cards.yml 실행]
         ↓
┌────────────────────────────────────┐
│ 1. GitHub GraphQL API 호출         │
│    - 2020-2025 전체 커밋 데이터      │
│    - 코드 리뷰, PR, Issue 수집      │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 2. generate_profile_card.py 실행   │
│    - 4분할 파이 차트 생성            │
│    - 통계 계산 (총 커밋, 일평균)     │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 3. SVG 생성                        │
│    - 0-profile-details.svg         │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 4. Git Commit + Push               │
│    - 메시지: "update: profile card"│
└────────┬───────────────────────────┘
         ↓
    [README 자동 표시]
```

### Flow 2: Slack 입력 → Dashboard 업데이트

```
[사용자가 Slack에 입력]
   /grind 1 0 0 2 0 0 1 1
         ↓
┌────────────────────────────────────┐
│ Slack App (Slash Command)         │
│  - POST 요청 생성                   │
│  - Request URL: Worker URL         │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Cloudflare Worker                  │
│  1. Slack 데이터 파싱               │
│     text: "1 0 0 2 0 0 1 1"       │
│                                    │
│  2. 숫자 추출                       │
│     numbers: [1,0,0,2,0,0,1,1]    │
│                                    │
│  3. 형식 변환                       │
│     JSON: {ref: "main",           │
│            inputs: {metrics: ...}}│
│                                    │
│  4. GitHub API 호출                │
│     POST /repos/.../dispatches    │
│     Header: Authorization: Bearer │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ GitHub Actions                     │
│ slack_response.yml 트리거           │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 1. slack_update.py 실행             │
│    - data.json 읽기                 │
│    - 메트릭 추가 (additive)          │
│    - lastUpdated 업데이트            │
│    - data.json 저장                 │
│    - get_weekly_commits() 호출      │
│    - Slack 확인 메시지 전송          │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 2. generate_svg.py 실행             │
│    - Git으로 커밋 수 계산            │
│    - data.json에서 메트릭 로드       │
│    - weekly_dashboard.svg 생성      │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 3. Git Commit + Push (PAT 사용)    │
│    - dashboard/ 폴더 전체            │
│    - 메시지: "update: daily metrics"│
└────────┬───────────────────────────┘
         ↓
    [Push 이벤트 발생]
         ↓
┌────────────────────────────────────┐
│ update_dashboard.yml 트리거         │
│ (push 이벤트)                       │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 1. generate_svg.py 재실행           │
│ 2. update_readme_charts.py 실행     │
│ 3. update_readme_history.py 실행    │
│ 4. Git Commit + Push               │
└────────┬───────────────────────────┘
         ↓
    [README 업데이트 완료]
```

### Flow 3: 주간 리셋 (매주 월요일 7AM KST)

```
[Schedule: Monday 7AM KST]
         ↓
[update_dashboard.yml 실행]
         ↓
┌────────────────────────────────────┐
│ check_weekly_reset.py 실행          │
│  - 현재 주 월요일 계산 (KST)         │
│  - data.json의 startDate와 비교     │
│  - 새로운 주 감지?                   │
└────────┬───────────────────────────┘
         ↓
    [Yes: 새로운 주]
         ↓
┌────────────────────────────────────┐
│ 1. 지난 주 데이터 저장               │
│    - weeklyHistory에 추가 (index 0)│
│    - 최근 12주만 유지                │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 2. 메트릭 리셋                      │
│    - 모든 값 0으로 초기화             │
│    - commits는 git에서 재계산        │
│    - startDate/endDate 업데이트     │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 3. generate_weekly_history.py      │
│    - 각 주별 SVG 생성                │
│    - history/weekly_history_xxx.svg│
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 4. update_readme_history.py        │
│    - README에 히스토리 테이블 업데이트│
│    - 누적 차트 URL 업데이트          │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 5. update_readme_charts.py         │
│    - 개별 메트릭 차트 URL 업데이트    │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 6. Git Commit + Push               │
│    - 메시지: "Weekly reset"         │
└────────┬───────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ 7. generate_weekly_summary.py      │
│    - 지난 주 요약 메시지 생성         │
│    - Slack Incoming Webhook 전송   │
└────────────────────────────────────┘
```

---

# 자동화 플로우 (Automation Flow)

## Slack 입력부터 Dashboard 업데이트까지 (완전한 흐름)

### Step 1: Slack에서 명령어 입력

```
사용자 액션:
  /grind 1 0 0 2 0 0 1 1

Slack 내부 처리:
  1. Slash Command 인식
  2. App 설정 확인
     - Command: /grind
     - Request URL: https://slack-github-bridge.kyungbeenkim.workers.dev
  3. POST 요청 생성
```

**실제 HTTP 요청**:
```http
POST https://slack-github-bridge.kyungbeenkim.workers.dev
Content-Type: application/x-www-form-urlencoded

token=gIkuvaNzQIHg97ATvDxqgjtO
&team_id=T0001
&team_domain=example
&channel_id=C2147483705
&channel_name=test
&user_id=U2147483697
&user_name=Piesson
&command=/grind
&text=1+0+0+2+0+0+1+1
&response_url=https://hooks.slack.com/commands/1234/5678
```

### Step 2: Cloudflare Worker 처리

**Worker 코드 실행 흐름**:

```javascript
// 1. 요청 받기
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// 2. 요청 처리
async function handleRequest(request) {
  // 2-1. Form 데이터 파싱
  const formData = await request.formData()
  const slackData = {
    token: formData.get('token'),
    text: formData.get('text'),          // "1 0 0 2 0 0 1 1"
    user_name: formData.get('user_name')
  }

  // 2-2. Verification Token 검증
  if (slackData.token !== SLACK_VERIFICATION_TOKEN) {
    return new Response('Invalid token', { status: 401 })
  }

  // 2-3. 숫자 추출
  const numbers = slackData.text.match(/\d+/g)
  // ["1", "0", "0", "2", "0", "0", "1", "1"]

  if (numbers.length !== 8) {
    return new Response(JSON.stringify({
      text: '❌ 형식 오류. 8개 숫자 필요: 1 0 0 2 0 0 1 1'
    }), { status: 200 })
  }

  const metrics = numbers.join(' ')  // "1 0 0 2 0 0 1 1"

  // 2-4. GitHub API 호출
  const githubResponse = await fetch(
    'https://api.github.com/repos/Piesson/Piesson/actions/workflows/slack_response.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,      // ← 환경변수에서
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: {
          metrics: metrics  // "1 0 0 2 0 0 1 1"
        }
      })
    }
  )

  // 2-5. Slack에 응답
  if (githubResponse.status === 204) {  // 204 = 성공
    return new Response(JSON.stringify({
      text: `✅ Workflow triggered!\n📊 Metrics: \`${metrics}\``
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  } else {
    return new Response(JSON.stringify({
      text: `❌ Failed: ${githubResponse.status}`
    }), { status: 200 })
  }
}
```

**처리 시간**: 약 100-300ms

### Step 3: GitHub Actions Workflow 실행

**slack_response.yml 트리거**:

```yaml
name: Process Slack Response

on:
  workflow_dispatch:
    inputs:
      metrics:
        description: 'Metrics from Slack'
        required: true
        type: string

jobs:
  update-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.SUMMARY_CARDS_TOKEN }}  # ← PAT 사용!

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Update metrics
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          GITHUB_TOKEN: ${{ secrets.SUMMARY_CARDS_TOKEN }}
          USERNAME: ${{ github.repository_owner }}
        run: |
          echo "${{ github.event.inputs.metrics }}" | python3 dashboard/slack_update.py

      - name: Generate dashboard
        env:
          GITHUB_TOKEN: ${{ secrets.SUMMARY_CARDS_TOKEN }}
          USERNAME: ${{ github.repository_owner }}
        run: python3 dashboard/generate_svg.py

      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add dashboard/
          git commit -m "update: daily metrics from Slack"
          git push
```

**Step 3-1: slack_update.py 실행**

```python
# 1. stdin에서 입력 읽기
text = sys.stdin.read()  # "1 0 0 2 0 0 1 1"

# 2. 숫자 파싱
numbers = re.findall(r'\d+', text)
# [1, 0, 0, 2, 0, 0, 1, 1]

metrics = {
    'usertalks': 1,     # numbers[0]
    'instagram': 0,     # numbers[1]
    'tiktok': 0,        # numbers[2]
    'hellotalk': 0,     # numbers[3]
    'coffeechats': 2,   # numbers[4]
    'blogposts': 0,     # numbers[5]
    'running': 0,       # numbers[6]
    'gym': 1            # numbers[7]
}

# 3. data.json 읽기
with open('dashboard/data.json', 'r') as f:
    data = json.load(f)

# 4. 현재 값에 추가 (Additive!)
current = data['currentWeek']['metrics']
data['currentWeek']['metrics']['socialContent']['instagram'] += metrics['instagram']
data['currentWeek']['metrics']['socialContent']['tiktok'] += metrics['tiktok']
data['currentWeek']['metrics']['socialContent']['hellotalk'] += metrics['hellotalk']
data['currentWeek']['metrics']['userSessions'] += metrics['usertalks']
data['currentWeek']['metrics']['ctoMeetings'] += metrics['coffeechats']
data['currentWeek']['metrics']['blogPosts'] += metrics['blogposts']
data['currentWeek']['metrics']['workouts']['running'] += metrics['running']
data['currentWeek']['metrics']['workouts']['gym'] += metrics['gym']

# 5. lastUpdated 업데이트
KST = timezone(timedelta(hours=9))
data['lastUpdated'] = datetime.now(KST).strftime("%Y-%m-%d")

# 6. data.json 저장
with open('dashboard/data.json', 'w') as f:
    json.dump(data, f, indent=2)

# 7. 커밋 수 조회 (GitHub API)
commits = get_weekly_commits()  # GITHUB_TOKEN 필요!

# 8. Slack 확인 메시지 전송
message = {
    "text": f"""✅ Well done! Progress updated successfully!

🔄 ADDED TODAY:
├─ 📱 Social: +{added_social}
├─ 💬 User Talks: +{added_talks}
├─ ☕ Coffee Chats: +{added_coffee}
├─ 🏃 Workouts: +{added_workouts}
└─ 📝 Blog Posts: +{added_blog}

📊 NEW TOTALS:
├─ 🚀 Code Commits: {commits} builds
├─ 📱 Social Posts: {total_social} total
├─ 💬 User Talks: {total_talks} sessions
├─ ☕ Coffee Chats: {total_coffee} meetings
├─ 🏃 Workouts: {total_workouts} sessions
└─ 📝 Blog Posts: {total_blog} articles

Keep building! 🚀"""
}

requests.post(SLACK_WEBHOOK_URL, json=message)
```

**Step 3-2: generate_svg.py 실행**

```python
# 1. Git에서 커밋 수 계산 (최신 데이터)
KST = timezone(timedelta(hours=9))
today = datetime.now(KST)
monday = today - timedelta(days=today.weekday())
monday_utc = monday.astimezone(timezone.utc)

# Git 명령어 실행
result = subprocess.run([
    'git', 'rev-list', '--count',
    f'--since={monday_utc.strftime("%Y-%m-%d %H:%M:%S")}',
    'HEAD'
], capture_output=True, text=True)

commits = int(result.stdout.strip())  # 예: 134

# 2. data.json 업데이트 (커밋 수)
with open('dashboard/data.json', 'r+') as f:
    data = json.load(f)
    data['currentWeek']['metrics']['commits'] = commits  # ← 덮어쓰기!
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()

# 3. SVG 생성
svg_content = f'''<svg width="520" height="330">
  <!-- Commits Card -->
  <text>{commits}</text>

  <!-- User Talks Card -->
  <text>{data['currentWeek']['metrics']['userSessions']}</text>

  <!-- ... 나머지 카드들 ... -->
</svg>'''

# 4. SVG 파일 저장
with open('dashboard/weekly_dashboard.svg', 'w') as f:
    f.write(svg_content)
```

**Step 3-3: Git Commit & Push**

```bash
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
git add dashboard/
git commit -m "update: daily metrics from Slack"
git push  # ← PAT를 사용하므로 다른 workflow 트리거!
```

**처리 시간**: 약 15-20초

### Step 4: Push 이벤트로 update_dashboard.yml 트리거

**왜 자동으로 트리거 되는가?**
```yaml
# update_dashboard.yml
on:
  push:
    paths:
      - 'dashboard/data.json'  # ← 이 파일이 변경됨!
```

**update-dashboard job 실행**:

```yaml
jobs:
  update-dashboard:
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Generate Dashboard SVG
        env:
          GITHUB_TOKEN: ${{ secrets.SUMMARY_CARDS_TOKEN }}
          USERNAME: ${{ github.repository_owner }}
        run: python dashboard/generate_svg.py

      - name: Update README with history
        run: python3 dashboard/update_readme_history.py

      - name: Update README with charts
        run: python3 dashboard/update_readme_charts.py

      - name: Commit and push if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add dashboard/data.json dashboard/weekly_dashboard.svg README.md
          if ! git diff --staged --quiet; then
            git commit -m "update: automated dashboard generation"
            git pull --rebase
            git push
          else
            echo "No changes to commit"
          fi
```

**처리 시간**: 약 12-18초

### 전체 타임라인

```
T+0ms     사용자가 Slack에 입력
T+50ms    Slack이 Worker에 POST
T+200ms   Worker가 GitHub API 호출
T+250ms   Slack에 "✅ Triggered!" 표시
T+5s      GitHub Actions slack_response.yml 시작
T+10s     slack_update.py 실행, Slack 확인 메시지 전송
T+15s     generate_svg.py 실행
T+20s     Git push (PAT 사용)
T+25s     GitHub Actions update_dashboard.yml 시작 (push 이벤트)
T+30s     SVG 재생성, README 업데이트
T+35s     Git push
T+40s     완료!
```

**총 소요 시간**: 약 40초

---

# 구성 요소 상세 (Component Details)

## 1. Cloudflare Worker 환경변수

Worker Dashboard에서 설정:

```
Variables and Secrets:
├─ GITHUB_TOKEN (Secret)
│  └─ Value: ghp_xxxxxxxxxxxx (Fine-grained PAT)
│     Scopes: Actions (Read/Write), Contents (Read/Write)
│
├─ GITHUB_OWNER (Text)
│  └─ Value: Piesson
│
├─ GITHUB_REPO (Text)
│  └─ Value: Piesson
│
└─ SLACK_VERIFICATION_TOKEN (Secret)
   └─ Value: xYzAbC123... (Slack App Credentials에서)
```

## 2. GitHub Secrets

Repository → Settings → Secrets → Actions:

```
Secrets:
├─ SLACK_WEBHOOK_URL
│  └─ https://hooks.slack.com/services/T.../B.../xxx
│
└─ SUMMARY_CARDS_TOKEN
   └─ ghp_xxxxxxxxxxxx (Fine-grained PAT)
      Scopes: Actions, Contents, Metadata
```

## 3. Slack App 설정

### Slash Command 설정

```
Settings → Slash Commands:
  Command: /grind
  Request URL: https://slack-github-bridge.kyungbeenkim.workers.dev
  Short Description: Update GitHub metrics
  Usage Hint: 1 0 0 2 0 0 1 1
  Escape channels, users, and links: ☐ (Off)
```

### Incoming Webhook 설정

```
Settings → Incoming Webhooks:
  Activate: ☑ (On)
  Add New Webhook to Workspace
    → Select channel: #general (또는 원하는 채널)
    → Webhook URL: https://hooks.slack.com/services/...
```

### App Credentials

```
Settings → Basic Information → App Credentials:
  Client ID: 1234567890.1234567890
  Client Secret: abc123... (사용 안 함)
  Signing Secret: abc123... (사용 안 함)
  Verification Token: xYzAbC123... (Worker에 사용)
```

## 4. 데이터 구조 (data.json)

```json
{
  "lastUpdated": "2025-10-28",
  "currentWeek": {
    "startDate": "2025-10-27",
    "endDate": "2025-11-02",
    "metrics": {
      "commits": 134,                    // Git에서 자동 계산
      "socialContent": {
        "instagram": 0,                  // Slack 입력
        "tiktok": 0,                     // Slack 입력
        "hellotalk": 0                   // Slack 입력
      },
      "userSessions": 2,                 // Slack 입력
      "ctoMeetings": 0,                  // Slack 입력
      "blogPosts": 0,                    // Slack 입력
      "workouts": {
        "running": 3,                    // Slack 입력
        "gym": 2                         // Slack 입력
      }
    }
  },
  "weeklyHistory": [                     // 최근 12주
    {
      "week": "2025-W43",
      "startDate": "10/20/2025",
      "endDate": "10/26/2025",
      "metrics": { /* ... */ }
    }
  ]
}
```

## 5. Slack 입력 형식

### 표준 형식 (8개 숫자)

```
/grind 1 0 0 2 0 0 1 1

순서:
1. User Talks     (💬) = 1
2. Instagram      (📱) = 0
3. TikTok         (📱) = 0
4. HelloTalk      (📱) = 2
5. Coffee Chats   (☕) = 0
6. Blog Posts     (📝) = 0
7. Running        (🏃) = 1
8. Gym            (🏃) = 1
```

### 지원하는 다른 형식

**7개 숫자** (Workouts 통합):
```
/grind 3 2 1 10 2 1 5
→ Running: 2, Gym: 3 (총 5개를 2:3으로 분할)
```

**6개 숫자** (Social 통합):
```
/grind 5 10 2 1 3 2
→ IG: 1, TT: 1, HT: 3 (총 5개를 1:1:3으로 분할)
```

**Named 형식**:
```
/grind Instagram: 3, TikTok: 2, UserTalks: 10, ...
```

---

# 트러블슈팅 (Troubleshooting)

## 일반적인 문제들

### 1. Slack에서 "invalid_payload" 오류

**원인**: stdout에 print 문이 섞여서 JSON이 깨짐

```python
# ❌ 잘못된 코드
print("Warning: No token")          # stdout으로 출력
return json.dumps({"text": "..."}) # JSON과 섞임

# ✅ 올바른 코드
import sys
print("Warning: No token", file=sys.stderr)  # stderr로 출력
return json.dumps({"text": "..."})          # 순수한 JSON
```

**해결**: 모든 디버그 메시지를 `stderr`로 리다이렉트

### 2. Workflow가 push 이벤트로 트리거 안 됨

**원인**: 기본 GITHUB_TOKEN 사용

```yaml
# ❌ 작동 안 함
- uses: actions/checkout@v4
  # 기본 GITHUB_TOKEN 사용
- run: git push  # 다른 workflow 트리거 안 됨!

# ✅ 작동함
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.SUMMARY_CARDS_TOKEN }}  # PAT 사용
- run: git push  # 다른 workflow 트리거!
```

**해결**: PAT를 사용하여 checkout

### 3. 커밋 수가 0으로 표시

**원인**: 환경변수 GITHUB_TOKEN이 없음

```python
def get_weekly_commits():
    token = os.getenv('GITHUB_TOKEN')  # None!
    if not token:
        return 0  # ← 0 반환
```

**해결**: Workflow에 환경변수 추가

```yaml
- name: Update metrics
  env:
    GITHUB_TOKEN: ${{ secrets.SUMMARY_CARDS_TOKEN }}
    USERNAME: ${{ github.repository_owner }}
  run: python dashboard/slack_update.py
```

### 4. Slack Slash Command가 응답 없음

**체크리스트**:
```
☐ Worker가 배포되었나?
☐ Worker URL이 올바른가?
☐ Slack App에서 /grind 명령어가 설정되었나?
☐ Slack App이 workspace에 설치되었나?
☐ Worker 환경변수가 모두 설정되었나?
```

**디버깅 방법**:
```bash
# 1. Worker 테스트
curl -X POST https://your-worker.workers.dev \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=test&text=1+0+0+2+0+0+1+1"

# 2. Cloudflare Dashboard에서 Logs 확인
Workers → your-worker → Logs → Begin log stream
```

### 5. GitHub Actions가 실행 안 됨

**가능한 원인**:
1. Workflow가 비활성화됨 (이전 실패로 인해)
2. Cron 표현식이 잘못됨
3. 파일 경로 필터가 맞지 않음

**해결**:
```bash
# 1. Workflow 상태 확인
gh workflow list

# 2. Workflow 활성화
gh workflow enable update_dashboard.yml

# 3. 수동 실행 테스트
gh workflow run update_dashboard.yml

# 4. 로그 확인
gh run list --limit 3
gh run view [RUN_ID] --log
```

### 6. "Method not allowed" 오류

**상황**: 브라우저로 Worker URL 접속시

**설명**: 정상입니다! Worker는 POST만 받습니다.
```javascript
if (request.method !== 'POST') {
  return new Response('Method not allowed', { status: 405 })
}
```

브라우저는 GET 요청을 보내므로 405 오류가 맞습니다.

---

## 디버깅 팁

### Cloudflare Worker 로그 확인

```
1. Cloudflare Dashboard 접속
2. Workers & Pages 클릭
3. Worker 선택
4. "Logs" 탭 클릭
5. "Begin log stream" 클릭
6. Slack에서 명령어 입력
7. 실시간 로그 확인
```

### GitHub Actions 로그 확인

```bash
# 최근 실행 목록
gh run list --limit 5

# 특정 실행 로그
gh run view [RUN_ID] --log

# 특정 workflow만
gh run list --workflow=slack_response.yml

# 실패한 실행만
gh run list --status=failure

# 실시간 로그 (진행 중인 실행)
gh run watch
```

### Git 커밋 수 수동 확인

```bash
# 이번 주 월요일부터 커밋 수
git rev-list --count --since="2025-10-27 00:00:00 +0900" HEAD

# 모든 브랜치
git rev-list --count --all --since="2025-10-27 00:00:00 +0900"
```

---

## 유지보수 가이드

### PAT 갱신 (3개월마다)

```
1. GitHub → Settings → Personal access tokens → Fine-grained tokens
2. 기존 토큰 만료일 확인
3. "Generate new token" 클릭
4. 같은 권한으로 새 토큰 생성 (Actions, Contents)
5. GitHub Secrets 업데이트
   gh secret set SUMMARY_CARDS_TOKEN
6. Cloudflare Worker 환경변수 업데이트
   Dashboard → Worker → Settings → Variables → Edit GITHUB_TOKEN
7. 이전 토큰 삭제
```

### Slack Webhook URL 갱신 (필요시)

```
1. Slack App → Incoming Webhooks
2. 기존 Webhook "Remove" 클릭
3. "Add New Webhook to Workspace" 클릭
4. 채널 선택
5. 새 URL 복사
6. GitHub Secrets 업데이트
   gh secret set SLACK_WEBHOOK_URL
```

### Workflow 스케줄 변경

```yaml
# 예: 저녁 리마인더를 8시로 변경
on:
  schedule:
    - cron: '0 11 * * *'  # 8PM KST = 11AM UTC
```

**주의**: UTC 기준으로 설정!
- KST = UTC + 9시간
- 7PM KST = 10AM UTC (10시간 차이는 DST 고려)

---

## 성능 최적화

### 1. Cloudflare Worker 최적화

```javascript
// ❌ 느림
const response = await fetch(url)
const data = await response.json()
// 두 번의 await

// ✅ 빠름
const response = await fetch(url)
return response  // 응답을 바로 전달
```

### 2. GitHub Actions 캐싱

```yaml
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 3. Git Fetch Depth 최소화

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # 최신 커밋만 (빠름)
    # fetch-depth: 0  # 전체 히스토리 (느림)
```

---

## 보안 Best Practices

### 1. Secrets 관리

```
✅ DO:
- GitHub Secrets 사용
- Cloudflare 환경변수에 Secret 타입으로 저장
- PAT 만료일 설정 (90일 권장)
- 최소 권한 원칙

❌ DON'T:
- 코드에 토큰 하드코딩
- 공개 저장소에 .env 파일 커밋
- "No expiration" PAT
- 과도한 권한 부여
```

### 2. Webhook 보안

```javascript
// ✅ Verification Token 검증
if (slackData.token !== SLACK_VERIFICATION_TOKEN) {
  return new Response('Unauthorized', { status: 401 })
}

// ✅ Rate Limiting (옵션)
const ip = request.headers.get('CF-Connecting-IP')
// Rate limit per IP

// ✅ Input Validation
if (!/^\d+(\s+\d+)*$/.test(metrics)) {
  return new Response('Invalid format', { status: 400 })
}
```

### 3. Git 설정

```yaml
# ✅ 항상 user 설정
- run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"

# ✅ 변경사항이 있을 때만 커밋
- run: |
    if ! git diff --staged --quiet; then
      git commit -m "update"
      git push
    fi
```

---

## FAQ (자주 묻는 질문)

### Q1: Slack 메시지가 늦게 와요 (5분 후)

**A**: GitHub Actions의 스케줄은 5-15분 지연이 정상입니다.
- Slack 입력 → Worker 응답은 즉시 (0.2초)
- GitHub Actions 실행은 큐 대기 가능

### Q2: 커밋 수가 실제보다 많아요

**A**: Private repo 커밋도 포함됩니다.
- `SUMMARY_CARDS_TOKEN`이 모든 repo 접근 가능
- 특정 repo만 카운트하려면 코드 수정 필요

### Q3: Worker 비용이 걱정됩니다

**A**: 무료입니다!
- 하루 100,000 요청 무료
- 우리 사용량: 하루 5-10회 정도
- CPU 시간 10ms 이내

### Q4: data.json 직접 수정해도 되나요?

**A**: 가능하지만 권장하지 않습니다.
- Slack 입력 사용 권장
- 직접 수정시 lastUpdated 업데이트 필수
- Git commit 후 push 이벤트 트리거

### Q5: 주간 리셋을 토요일로 변경 가능한가요?

**A**: 가능합니다.
```python
# check_weekly_reset.py
# 월요일 (weekday=0) → 토요일 (weekday=5)로 변경
saturday = today - timedelta(days=(today.weekday() + 2) % 7)
```

---

## 추가 리소스

### 공식 문서
- [GitHub Actions](https://docs.github.com/en/actions)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Slack API](https://api.slack.com/)
- [GitHub REST API](https://docs.github.com/en/rest)

### 유용한 도구
- [Crontab Guru](https://crontab.guru/) - Cron 표현식 테스트
- [RegEx101](https://regex101.com/) - 정규표현식 테스트
- [JSON Formatter](https://jsonformatter.org/) - JSON 검증

### 추천 읽을거리
- [REST API Complete Guide 2025](https://www.knowi.com/blog/rest-api-complete-guide-from-concepts-to-implementation-2025/)
- [GitHub Actions Tutorial 2025](https://everhour.com/blog/github-actions-tutorial/)
- [Webhooks Explained](https://hookdeck.com/webhooks/guides/what-are-webhooks-how-they-work)

---

**Last Updated**: 2025-10-28
**Version**: 2.0
**Author**: Piesson
**License**: MIT
