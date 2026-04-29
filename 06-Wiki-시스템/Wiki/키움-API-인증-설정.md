# 키움 OpenAPI Plus 인증 설정

생성: 2026-04-28
수정: 2026-04-28

## 문제 현상

HTTP 401 오류 발생:
```
HTTP 401: login fail: Please carry the API secret key in the 'Authorization' field of the request header (1004)
```

## 원인

키움 API는 토큰 발급 요청 시 **appkey:secretkey를 Basic Auth Authorization 헤더**로 전달해야 합니다.

기존 코드에서는 appkey와 secretkey를 JSON body에만 실어 보내고 있었습니다.

## 해결 방법

`kiwoom_api.py`의 `authenticate()` 메서드에서:

```python
import base64

# Authorization 헤더에 secret key 포함
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

1. `appkey:secretkey` → `base64.b64encode()` → `Basic {credentials}` 문자열
2. POST 요청 시 `Authorization: Basic {credentials}` 헤더 추가
3. 키움 API가 헤더에서 credentials 파싱 → 인증 처리
4. 200 응답 시 `token` 또는 `access_token` 수신 → 저장

## 관련 파일

| 파일 | 경로 | 비고 |
|------|------|------|
| kiwoom_api.py | /home/comage/coding/ki-ai-trader/ | 인증 구현 |
| kiwoom_api.py | 254줄 이후 | unreachable dead code → 삭제완료 |
| ki_project_monitor.py | /home/comage/coding/ki-ai-trader/ | 거래 기록 저장 |
| ki-project-status.py | /home/comage/.hermes/scripts/ | 시장 마감 브리핑 |
| ki-trade-log.json | /home/comage/.hermes/cron/output/ | 오늘 거래 내역 |

## 수정 이력

- 2026-04-28: Authorization 헤더 추가 + dead code 삭제
