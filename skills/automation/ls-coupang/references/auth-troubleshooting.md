# LS API 인증 문제 해결

## Keycloak OAuth2 인증 흐름

ls.coupang.com은 Keycloak + Akamai CDN + istio-envoy로 보호됨.

### 인증 단계
1. 사용자가 브라우저에서 `ls.coupang.com` 접속
2. Keycloak 로그인 페이지로 리다이렉트 (`xauth.coupang.com/auth/realms/fts`)
3. 사용자 로그인 (mokicom / bonohouse0309^^)
4. Keycloak이 OAuth2 code 발급 → LS 앱으로 리다이렉트
5. LS 앱이 session cookie (`AUTH_SESSION_ID`, `KC_RESTART`) 설정
6. Akamai CDN이 `bm_sz`, `_abck` 등의 bot management 쿠키 추가

### 쿠키 만료 증상

| 증상 | HTTP 응답 | 의미 |
|:----|:---------|:-----|
| 404 + location: img1a.coupangcdn.com | HTTP 404 | istio-envoy가 인증없는 요청 차단 |
| Keycloak 로그인 페이지 HTML 반환 | HTTP 200 | 쿠키 완전 만료, 재로그인 필요 |
| Keycloak 로그인 POST → HTTP 500 "An internal server error has occurred" | HTTP 500 | `session_code` 일회성 만료 (GET 후 너무 늦게 POST) |
| 빈 응답 (0 bytes) | HTTP 200 | CloudFront 차단 가능성 |
| `AttributeError: 'RequestsCookieJar' object has no attribute 'save'` | (Python) | **쿠키 jar가 MozillaCookieJar 아님** (가장 흔한 함정). `session.cookies = http.cookiejar.MozillaCookieJar(path)`로 교체 필요. |

**Keycloak 500 해결:** 로그인 페이지 GET과 credential POST를 같은 흐름에서 즉시 실행. session_code는 매 페이지 로드마다 새로 발급되며, 한 번 사용하면 소멸. 재시도시 반드시 새로 GET부터 다시 시작.

### 진단

```bash
# 쿠키 파일에 access_token/session 있는지 확인
grep -c "AUTH_SESSION_ID\|KC_RESTART" /tmp/coupang_cookies.txt

# curl -v로 실제 응답 확인
curl -v -s -b /tmp/coupang_cookies.txt "https://ls.coupang.com/" 2>&1 | head -20
```

### headless browser 접속 불가

Akamai CDN은 headless browser의 TLS fingerprint, User-Agent, WebDriver 탐지 등을 통해 차단.
**browser_navigate는 ls.coupang.com에서 작동하지 않음.** 무조건 사용자 PC 브라우저 필요.
