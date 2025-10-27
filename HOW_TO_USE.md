# 📊 대시보드 사용법 (아주 간단!)

## 🔥 매주 하는 일 (일요일마다)

### 1️⃣ 숫자 업데이트
파일: `dashboard/update_data.py` 열기

```python
manual_metrics = {
    # 📱 이번 주 SNS 포스트 개수
    "socialContent": {
        "instagram": 4,   # ← 여기 수정
        "tiktok": 3,      # ← 여기 수정
        "hellotalk": 5    # ← 여기 수정
    },

    # 👥 사용자와 대화한 총 횟수 (채팅/이메일/줌/만남 다 포함)
    "userSessions": 134,  # ← 여기 수정

    # ☕ 공동창업자 후보와 커피챗 횟수
    "ctoMeetings": 5,     # ← 여기 수정

    # ✍️ 블로그/웹사이트 글 개수
    "blogPosts": 3,       # ← 여기 수정

    # 🏃‍♂️ 운동 횟수
    "workouts": {
        "running": 3,     # ← 러닝 횟수
        "gym": 2          # ← 헬스장 횟수
    }
}
```

### 2️⃣ 대시보드 업데이트 실행
```bash
cd /Users/apple/Desktop/Piesson

# 데이터 업데이트 (git commits는 자동으로 계산됨)
python3 dashboard/update_data.py

# 대시보드 이미지 생성
python3 dashboard/generate_svg.py

# GitHub에 업로드
git add .
git commit -m "📊 주간 대시보드 업데이트"
git push
```

## 📁 파일 구조

```
Piesson/
├── dashboard/
│   ├── data.json              # 데이터 저장소
│   ├── update_data.py         # ← 여기서 숫자 수정!
│   ├── generate_svg.py        # 이미지 생성
│   └── weekly_dashboard.svg   # 생성된 이미지
├── README.md                  # GitHub 프로필 (대시보드 표시됨)
└── .github/workflows/         # 자동화 설정
```

## 🤖 자동화 기능

### ✅ 자동으로 되는 것:
- **Git commits 개수**: 매일 자동 계산
- **대시보드 업데이트**: 매일 오후 6시 (한국시간) 자동 실행
- **GitHub 프로필 반영**: 자동으로 README에 표시

### 📝 수동으로 하는 것:
- 매주 일요일에 `update_data.py`에서 숫자만 수정

## 🚀 처음 설정할 때 (한 번만)

```bash
# 1. Piesson 폴더로 이동
cd /Users/apple/Desktop/Piesson

# 2. 첫 번째 대시보드 생성
python3 dashboard/update_data.py
python3 dashboard/generate_svg.py

# 3. GitHub에 올리기
git add .
git commit -m "📊 첫 번째 대시보드 설정"
git push
```

## 💡 팁

- **매주 일요일 저녁**에 숫자 업데이트하기
- **GitHub 프로필**에서 대시보드 확인: github.com/Piesson
- **실수했을 때**: 언제든 `update_data.py`에서 숫자 수정하고 다시 실행

## 🎯 각 지표 설명

| 지표 | 의미 | 예시 |
|------|------|------|
| 💻 **Code Commits** | GitHub에 올린 코드 변경사항 | 자동 계산됨 |
| 📱 **Social Posts** | 인스타+틱톡+헬로톡 포스트 | 이번 주 12개 올림 |
| 👥 **User Talks** | 사용자와의 모든 대화 | 채팅 50 + 줌콜 3 = 53 |
| ☕ **Coffee Chats** | 공동창업자 후보 커피챗 | 이번 주 2명과 만남 |
| ✍️ **Blog Posts** | AI/스타트업 관련 글 | 블로그에 3개 포스트 |
| 🏃‍♂️ **Workouts** | 러닝 + 헬스장 | 러닝 3회, 헬스 2회 |

---

**🔥 결론: `update_data.py` 파일만 수정하면 끝!**