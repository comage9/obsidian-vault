# 키움 API 인증 실패 — 환경변수 미설정 디버깅 기록

## 증상

크론 job 실행 시:
```
🔑 키움 API 인증...
❌ 인증 실패
토큰 응답에 access_token 이 없음
```

## 진단 흐름

```bash
# 1. 스크립트 직접 실행해서 동일한 에러 확인
python3 condition_search_engine.py

# 2. 환경변수是否存在 확인
echo "KIWOOM_APP_KEY=${KIWOOM_APP_KEY:-NOT_SET}"

# 3. kiwoom_api.py의 환경변수 로드 방식 확인 (83~87줄)
grep -n "KIWOOM_APP_KEY\|KIWOOM_SECRET" kiwoom_api.py

# 4. .bashrc, .profile, /etc/environment 에도 없으면 검색
grep -rn "KIWOOM_APP_KEY" ~/.bashrc ~/.profile

# 5. kiwoom_api.py __init__이 실제로 읽는 환경변수명 확인
# os.getenv("KIWOOM_APP_KEY", "") — 빈 문자열이 기본값
```

## 현재 시스템 상태 (2026-05-03)

| 환경변수 | 상태 |
|----------|------|
| `KIWOOM_APP_KEY` | NOT_SET |
| `KIWOOM_SECRET_KEY` | SET (값 존재) |

## 결론

`KIWOOM_APP_KEY`가 시스템에 설정되어 있지 않아 `app_key=""`로 API 요청 → 토큰 응답 없음 → "access_token 이 없음" 에러.

## 해결책

크론 실행 시 환경변수가 로드되도록:
```bash
# 방법 1: crontab에 source 라인 추가
0 9 * * 1-5 source /home/comage/.bashrc && cd /home/comage/coding/ki-ai-trader && python3 ...

# 방법 2: .env 파일에 저장 후 로드
# ~/.hermes/.env 또는 프로젝트 루트 .env
KIWOOM_APP_KEY="..."
KIWOOM_SECRET_KEY="..."
```
