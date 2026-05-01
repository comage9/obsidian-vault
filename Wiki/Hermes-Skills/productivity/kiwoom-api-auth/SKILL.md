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

## 관련 파일

- `/home/comage/coding/ki-ai-trader/kiwoom_api.py` — 인증 구현
- `/home/comage/coding/ki-ai-trader/kiwoom_api.py` — 254줄 이후 unreachable dead code → 삭제済み
