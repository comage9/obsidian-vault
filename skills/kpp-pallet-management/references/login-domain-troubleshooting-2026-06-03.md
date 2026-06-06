# KPP 로그인 트러블슈팅 (2026-06-02/03 업데이트)

다른 에이전트들이 자주 빠지는 함정 + 운영원칙 검증 결과.

## 1. 핵심 함정: form-urlencoded POST → 415

**증상**: 로그인 후 URL이 `/login` 그대로 (제목/본문 동일)

**원인**: 다른 에이전트가 `page.click('button.btn_login')`만 호출 → 브라우저 form submit이 발동 → `Content-Type: application/x-www-form-urlencoded`로 POST → Tomcat 10.1.34가 명시 거부

**검증 결과 (curl 직접)**:
```
$ curl -X POST https://wpps.logisall.com/login.do \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "loginId=P217273&password=P217273&loginType=ps"

HTTP 415 – 지원되지 않는 Media Type
메시지: Content-Type 'application/x-www-form-urlencoded;charset=UTF-8' is not supported.
Apache Tomcat/10.1.34
```

**해결 (3가지)**:

### 1.1 Python requests (헤드리스 안전, 권장)
```python
import requests, json
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 Chrome/120.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
    "Origin": "https://wpps.logisall.com",
    "Referer": "https://wpps.logisall.com/login",
})
s.get("https://wpps.logisall.com/login")
r = s.post("https://wpps.logisall.com/login.do",
           data=json.dumps({"loginId":"P217273","password":"P217273"}))
# → {"flg":"Y","redirectUrl":"/ps/index"}
```

### 1.2 Playwright fetch 직접 호출
```python
page.evaluate("""
    () => fetch('/login.do', {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'X-Requested-With': 'XMLHttpRequest'},
        body: JSON.stringify({loginId: 'P217273', password: 'P217273'})
    }).then(r => r.json()).then(d => {
        if (d.flg === 'Y') location.href = d.redirectUrl;
    })
""")
```

### 1.3 Playwright 네트워크 응답 가로채기
```python
with page.expect_response(lambda r: '/login.do' in r.url) as resp_info:
    page.click('button.btn_login')
result = (await resp_info.value).json()
if result['flg'] == 'Y':
    page.goto('https://wpps.logisall.com' + result['redirectUrl'])
```

## 2. 도메인 alias

| 도메인 | 응답 | 사용 |
|---|---|---|
| `wpps.logisall.com` | HTTP 200, 10,439 bytes | 스킬 기준 (권장) |
| `wpps.logisall.net` | HTTP 200, 10,439 bytes | 다른 에이전트 보고 |

**결론**: 같은 서버. 어느 도메인 사용해도 무관, 단 **`Origin`/`Referer` 헤더는 실제 호출 도메인과 일치**해야 함.

## 3. 폼 HTML 구조 (실측)

```html
<form action="/login.do" method="post" id="loginForm">
    <input type="hidden" name="loginType" id="loginType" value="">  ← JS가 'ps'/'ns' 자동 세팅
    <input type="text" name="loginId" id="loginId" required>
    <input type="password" name="password" id="password" required>
    <input type="checkbox" class="checkbox" id="rememberYn">         ← 선택, 전송 불필요
    <button type="button" class="btn_login" onclick="fn_login()">로그인</button>
</form>
```

**`type="button"`** → form submit 자동 발동 안 함 → JS 함수가 가로채서 fetch로 JSON POST 발송.

## 4. 자동로그인 체크박스 (`rememberYn`)

선택사항. 안 체크해도 로그인 정상. **서버 전송 시 제외**해도 OK.

## 5. PBM110MW.do POST 시 Content-Type

PBM110MW.do도 JSON POST. `fn_save` JS (line 1148~):
```javascript
gfn_ajax({
    'type': 'POST',
    'url': '/ps/PBM110MW.do',
    'contentType': 'application/json',
    'dataType': 'json',
    'data': JSON.stringify(saveData),
    ...
});
```

## 6. 세션 유지

- **JSESSIONID** (Tomcat 세션) — 한 번 로그인하면 만료 전까지 모든 `/ps/*` API 호출 가능
- `requests.Session` + JSESSIONID 쿠키 자동 관리
- 49개 쿠키 자동 발급 (Tomcat 기본 + 부수 쿠키)

## 7. PBM110MW.do 응답이 `[]` (빈 배열)인 경우

6/1, 6/2, 6/3 모두 `[]` 응답 확인. 의미:
- 정상 (조회 조건에 맞는 데이터 없음)
- 또는 권한 부족 (CST_COD 불일치)
- **저장 후 재조회**로 검증 가능

## 8. 권한 부족 시나리오

다른 사용자가 다른 CST_COD로 로그인하면 다른 데이터만 보임. **CST_COD=217273 (유원피에스 계정) 외 계정 사용 시 권한 다름**.

## 9. 운영원칙 검증 (READ ONLY 준수)

저장 작업 전 반드시:
1. `GET /PBM110MW.do?REQ_DAT_FR=...` 로 **기존 데이터 조회** → 0건 확인
2. 신규 등록 POST 실행
3. `GET /PBM110MW.do?REQ_DAT_FR=...` 재조회 → 1건 확인

POST 실행 전 사용자에게 **"등록 진행해도 될까요?"** 확인 필수 (운영원칙: 임의 데이터 생성/변경 금지).
