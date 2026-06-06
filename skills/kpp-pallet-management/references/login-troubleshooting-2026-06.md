# KPP 로그인 트러블슈팅 (2026-06-02)

## 문제: 다른 에이전트 KPP 로그인 실패

### 증상
- `wpps.logisall.com/login` 또는 `wpps.logisall.net/login` 도달 OK
- ID/PW 입력 + 제출 OK
- 제출 후에도 URL이 `/login` 그대로 (페이지 내용 동일)
- "로그인이 안 됐다" 증상

### 진짜 원인 (1개)

**`application/x-www-form-urlencoded` POST로 전송 → Apache Tomcat 10.1.34 명시 거부**

```http
HTTP 415 – 지원되지 않는 Media Type
메시지: Content-Type 'application/x-www-form-urlencoded;charset=UTF-8' is not supported.
설명: Payload가 대상 리소스에 대한 이 메소드에 의해 지원되지 않는 포맷이기 때문에, Origin 서버가 요청을 서비스하기를 거부합니다.
Apache Tomcat/10.1.34
```

### 사용자 추정 원인 (재평가)

| # | 추정 | 실제 |
|:---:|:---|:---:|
| 1 | SPA라 `wait_for_load_state("networkidle")` 미작동 | △ (부수적) |
| 2 | 자동로그인 체크박스 추가 필드 | ✗ (선택, 전송 불필요) |
| 3 | ID 필드 fallback | △ (Playwright는 정상) |
| 4 | 자격증명 틀림 | ✗ (**정상** P217273/P217273) |

### 진단 명령어 (즉시 확인)

```bash
# 1) form-urlencoded → 415 확인 (다른 에이전트 방식)
curl -X POST "https://wpps.logisall.com/login.do" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "loginId=P217273&password=P217273&loginType=ps" -L
# → HTTP 415

# 2) JSON → 200 확인 (스킬 정답)
curl -X POST "https://wpps.logisall.com/login.do" \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"loginId":"P217273","password":"P217273"}'
# → HTTP 200 {"flg":"Y","redirectUrl":"/ps/index"}
```

### 폼 HTML (실측)

```html
<form action="/login.do" method="post" id="loginForm">
    <input type="hidden" name="loginType" id="loginType" value="">
        ← JS가 'ps'(WPPS) 또는 'ns'(UNPS) 자동 세팅
    <input type="text" name="loginId" id="loginId" required>
    <input type="password" name="password" id="password" required>
    <input type="checkbox" class="checkbox" id="rememberYn">
        ← 자동로그인 (선택, 전송 불필요)
    <button type="button" class="btn_login" onclick="fn_login()">로그인</button>
        ← type="button" → form submit 안 일어남, JS 함수 호출
</form>
```

### Playwright 해결 코드

```python
# ❌ 이것만 하면 form-urlencoded 발동
page.click('button.btn_login')

# ✅ 해결 1: fetch 직접 호출
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

# ✅ 해결 2: 네트워크 응답 가로채기
with page.expect_response(lambda r: '/login.do' in r.url) as resp_info:
    page.click('button.btn_login')
result = (await resp_info.value).json()
if result.get('flg') == 'Y':
    page.goto('https://wpps.logisall.com' + result['redirectUrl'])
```

### Python requests (헤드리스 안전, 권장)

```python
import requests, json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://wpps.logisall.com",
    "Referer": "https://wpps.logisall.com/login",
})

# 1) 세션 시작
session.get("https://wpps.logisall.com/login", timeout=15)

# 2) JSON POST 로그인
session.headers["Content-Type"] = "application/json"
r = session.post("https://wpps.logisall.com/login.do",
                  data=json.dumps({"loginId": "P217273", "password": "P217273"}),
                  timeout=15)
# r.json() = {"flg": "Y", "redirectUrl": "/ps/index"}

# 3) 리다이렉트 따라가기
session.headers.pop("Content-Type", None)
session.get("https://wpps.logisall.com/ps/index", timeout=15)

# 4) PBM110MW 페이지 도달
session.get("https://wpps.logisall.com/ps/PBM110MW", timeout=15)
# → 94KB SpreadJS 페이지 로드
```

### 실행 결과 (2026-06-02 23:55 KST)

| 단계 | HTTP | 크기 | 결과 |
|:---:|:---:|:---:|:---|
| GET /login | 200 | 9,841 B | JSESSIONID 발급 (CF9BD07A8AFEB0C18996...) |
| POST /login.do (JSON) | 200 | 37 B | `{"flg":"Y","redirectUrl":"/ps/index"}` |
| GET /ps/index | 200 | 37,366 B | WPPS 메인 |
| GET /ps/PBM110MW | 200 | 94,060 B | SpreadJS 페이지 |
| GET /ps/PBM110MW.do (오늘) | 200 | 2 B | 빈 결과 (0건) |

**49개 쿠키 자동 발급** (Tomcat 세션 + 부수). `wpps.logisall.com` = `wpps.logisall.net` (같은 서버, 10,439 bytes 동일).

### 핵심 한 줄

```python
session.post('https://wpps.logisall.com/login.do',
             headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
             data=json.dumps({'loginId':'P217273','password':'P217273'}))
```
