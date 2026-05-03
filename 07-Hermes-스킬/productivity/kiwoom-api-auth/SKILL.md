---
name: kiwoom-api-auth
description: "키움 OpenAPI Plus 인증 — HTTP 401 오류 해결"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [키움-API, Python, API, 인증]
    related_skills: [kiwoom-stock-bot]
---

# 키움 OpenAPI Plus 인증

## 문제

```
HTTP 401: login fail: Please carry the API secret key in the 'Authorization' field (1004)
```

## 원인

키움 API Plus는 토큰 발급 시 `Authorization: Basic {base64(appkey:secretkey)}` 헤더를 필수로 요구합니다.

## 해결 코드

`kiwoom_api.py`의 `authenticate()` 메서드:

```python
import base64

credentials = base64.b64encode(
    f"{self.app_key}:{self.secret_key}".encode()
).decode()

response = self.session.post(
    self.OAUTH_TOKEN_URL,
    json=auth_data,
    headers={'Authorization': f'Basic {credentials}'},
    timeout=10
)
```

## 인증 흐름

1. `appkey:secretkey` → base64 인코딩
2. `Authorization: Basic {credentials}` 헤더로 POST
3. 응답 200 → `token` 또는 `access_token` 저장

## 환경 변수 사전 확인 (크론/자동 실행 전 필수)

크론 작업에서 `kiwoom_api.py`가 환경변수를 읽으므로, **스크립트 실행 전** 반드시 확인해야 합니다:

```bash
# 확인
echo "KIWOOM_APP_KEY=${KIWOOM_APP_KEY:-NOT_SET}"
echo "KIWOOM_SECRET_KEY=${KIWOOM_SECRET_KEY:+SET}"

# 설정 (bashrc 또는 .env)
export KIWOOM_APP_KEY="your_app_key_here"
export KIWOOM_SECRET_KEY="your_secret_key_here"
```

키가 비어있으면 `authenticate()`가 **"토큰 응답에 access_token 이 없음"** 오류를 반환합니다 — 이 메시지는 API 서버가 토큰을 거부한 것이 아니라 요청 자체에 키가 없었기 때문입니다.

**검증 체크리스트:**
- [ ] `KIWOOM_APP_KEY` — 빈 문자열이 아닌 실제 값
- [ ] `KIWOOM_SECRET_KEY` — 빈 문자열이 아닌 실제 값
- [ ] 크론의 `source ~/.bashrc` 또는 `.env` 파일 로드 확인
- [ ] kiwoom_api.py의 `__init__`이 `os.getenv("KIWOOM_APP_KEY", "")`를 사용하므로, 환경변수가 없으면 빈 문자열로 시작

## 관련 파일

- `/home/comage/coding/ki-ai-trader/kiwoom_api.py` — 인증 구현 (83~87줄: 환경변수 로드)
- `references/missing-env-vars-diagnostic.md` — 환경변수 미설정 시 디버깅 흐름
