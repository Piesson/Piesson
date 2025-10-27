# Slack 자동화 설정 가이드

## 1️⃣ 현재 작동 방식
- 매일 오후 6시 Slack 알림
- 메시지 형식: `Instagram: 0, TikTok: 0, HelloTalk: 1, ...`

## 2️⃣ 수동 응답 처리 (현재)

### 방법 A: GitHub Actions UI 사용
1. https://github.com/Piesson/Piesson/actions
2. "Process Slack Response" 선택
3. "Run workflow" 클릭
4. Slack에서 받은 메시지 복사 → 붙여넣기
5. "Run workflow" 실행

### 방법 B: 로컬에서 실행
```bash
cd /Users/apple/Desktop/Piesson
echo "Instagram: 3, TikTok: 2, HelloTalk: 5, UserTalks: 10, CoffeeChats: 2, BlogPosts: 1, Running: 3, Gym: 2" | python3 dashboard/slack_update.py
python3 dashboard/generate_svg.py
git add . && git commit -m "update: daily metrics" && git push
```

## 3️⃣ 완전 자동화 (선택사항)

### Personal Access Token 생성
1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)"
3. Name: `SLACK_AUTOMATION`
4. Scopes: `repo`, `workflow`
5. Token 복사

### Slack Slash Command 생성
1. Slack App → "Slash Commands" → "Create New Command"
2. Command: `/metrics`
3. Request URL: 임시로 `https://github.com` (나중에 변경)
4. Usage Hint: `Instagram: 3, TikTok: 2, ...`

### GitHub API 직접 호출 (Slack에서)
```bash
# Slack에서 이 명령어를 사용
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/Piesson/Piesson/dispatches \
  -d '{"event_type":"update-metrics","client_payload":{"metrics":"Instagram: 3, TikTok: 2, ..."}}'
```

## 🎯 추천: 현재는 방법 A 사용
- 가장 간단하고 안전
- GitHub UI에서 직접 실행
- Token 관리 불필요