---
name: kpp-pallet-management
description: 로지스올 WPPS KPP 파렛트 관리 — PBM110MW(납품/반납요청) + PBM140MW(출하통보등록) 등록/조회. PRD_COD=N11(11T), ARV_CST_COD=610060(부천1HUB), CST_COD=217273(유원피에스). JSON POST 필수 (form-urlencoded는 Tomcat 415).
category: automation
---

# KPP 파렛트 관리 (로지스올 WPPS)

## ⚠️ 첫 작업 전 필수 확인

1. **LS(쿠팡 Linehaul) 먼저 조회** — KPP 팔레트 등록 전에 LS에 오늘 등록된 차량 정보를 확인한다.
2. **WPPS 로그인은 반드시 JSON POST 방식** (아래 참조). 일반 form-urlencoded POST는 415 오류.
3. **PRD_COD(유형)** = **`N11`** = **11T 파렛트 종류** (🚨 차량 톤수 아님! 5T/11T 차량 모두 N11 등록, 6/1~6/2 운영 7건 일관). 다른 톤수 코드 불명 — 필요시 사용자 확인.
4. **fn_new 템플릿의 모든 필드를 포함**해야 저장 성공 — ZIP_NUM, ZIP1_NUM, ZIP_SEQ, REQ_ARV_ZIP_ADDR 등 depzip/cstarv 조회 결과를 함께 전송해야 한다.

## 🚨 PBM110MW vs PBM140MW — 메뉴 구분 (절대 혼동 금지)

| 메뉴 | URL | 용도 | 스킬 본문 |
|:---|:---|:---|:---|
| **PBM110MW** | /ps/PBM110MW | **납품/반납요청** | 본문 (스킬 기준) |
| **PBM140MW** | /ps/PBM140MW | **출하통보등록** (실제 운영 메뉴 — 6/1~6/2 데이터 모두 여기) | ⚠️ 별도 섹션 참조 |

**6/1~6/2 사용자 "1호차/2호차 등록" = PBM140MW (출하통보)**. "2호차까지 했다"는 PBM140MW 의미. PBM110MW는 "납품요청" 별도 메뉴.

**PBM140MW 핵심 차이**:
- `POST /ps/PBM140MW.search` (GET 아님)
- `POST /ps/PBM140MW.save` (.do 아님)
- 필드 **소문자** (chk, mod, dlv_dat, arv_dat, arv_cst_cod, prd_cod, dlv_qty)
- `fn_saveDataChk` 자동 처리: `user_id='P217273'`, `dlv_dat`/`arv_dat` 형식 변환, null→""
- 신규 페이로드 (line 1285~1309): mod="I", data_typ="01", car_own_typ="02" 등

→ 상세: `references/pbm140MW-api-details.md`
   - ⚠️ **주의: 페이지에 `fn_new` 함수는 없음. TANG_BTN이 동등 역할.** 상세는 `references/save-flow-2026-06.md` 참조.
5. **도메인 alias**: `wpps.logisall.com` = `wpps.logisall.net` (같은 서버). 둘 다 사용 가능. 상세는 `references/login-domain-troubleshooting-2026-06-03.md`.

### LS → KPP 차량 정보 매핑 (PBM110MW 등록 시)

LS `/order` API 응답의 `truckInfo` 객체에 KPP PBM110MW 등록에 필요한 차량 정보가 모두 포함되어 있다. **별도 시스템 조회 불필요**.

| LS 응답 필드 | KPP 컬럼 | 의미 | 예시 |
|:---|:---:|:---|:---|
| `truckInfo.plateNumber` | col31 | 차량번호 | `경기89자3822` |
| `truckInfo.driverName` | col32 | 기사명 | `유원석` |
| `truckInfo.driverPhone` | col33 | 연락처 | `010-3578-4363` |
| `truckType.code` | (참고) | 톤수 코드 | `T5000` (5T), `T11000` (11T) |
| `requestTime` | (참고) | 출발 요청시간 | `2026-06-02 23:50:00` |
| `truckRequestId` | (참고) | LS 오더 ID | `27375827` |
| `status` | (참고) | 상태 | `CONFIRMED` (배차완료) |
| `truckSeq` | (참고) | 호차 | `1`, `2`, `3` |
| `palletCount` | (참고) | 팔레트 수량 | `12` (없으면 사용자 지시 따름) |

**워크플로우**:
1. LS `/order` API로 오늘 VF67 차량 조회 (statuses=SUBMITTED,CONFIRMED,CANCELED,BACK, locationStart=VF67_H, dateFrom=dateTo=오늘)
2. 등록할 호차(2호/3호 등)의 `truckInfo` 추출
3. KPP PBM110MW 신규등록 시 위 컬럼 매핑으로 사용
4. 톤수는 사용자 지시 우선 (`palletCount=None`인 경우 2호 12개, 3호 14개 등)

## 로그인 및 접속

- 사이트: https://wpps.logisall.com
- 로그인: **P217273** / **P217273** (아이디=비밀번호 동일)
- 계정명: 유원피에스 (CST_COD=217273, DPT_COD=601045)

### 로그인 방식 (Python requests)

SpreadJS SPA 방식이므로 **JSON POST** 로그인이 필수:

```python
import requests, json
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
})
# 1. GET 로그인 페이지 (세션 쿠키 획득)
s.get("https://wpps.logisall.com/login")
# 2. JSON POST 로그인 (실제 form input 3필드 모두 전송)
r = s.post("https://wpps.logisall.com/login.do",
           data=json.dumps({"loginType":"IDPW","loginId":"P217273","password":"P217273"}))
# ↑ loginType="IDPW" 명시 (실제 HTML form의 hidden field와 일치)
# 2필드만 보내도 flg=Y 응답은 오지만, loginType 빠뜨리면 일부 환경에서 세션 권한 다를 수 있음
result = r.json()  # {"flg":"Y","redirectUrl":"/ps/index"}
# 3. 리다이렉트
s.get("https://wpps.logisall.com" + result["redirectUrl"])
```

**⚠️ 중요:** 일반 `form-urlencoded` POST는 415 오류. 반드시 `Content-Type: application/json` + `X-Requested-With: XMLHttpRequest`.

#### 왜 JSON POST 인가 (서버 측 명시 거부)

WPPS는 **Apache Tomcat 10.1.34** 위에서 동작하며 `/login.do`는 JSON만 수락:
- `application/x-www-form-urlencoded;charset=UTF-8` POST → **HTTP 415** (Content-Type 'application/x-www-form-urlencoded;charset=UTF-8' is not supported)
- `application/json` POST → HTTP 200 + `{"flg":"Y","redirectUrl":"/ps/index"}`

다른 에이전트가 `page.click('button.btn_login')` 만 호출하면 브라우저가 자동 form submit을 발동 → 415 → "로그인 후에도 URL이 /login 그대로" 증상. **fn_login() JS가 fetch()로 JSON POST로 변환**해주는 경로를 따라야 함.

#### Playwright 함정 (가장 흔한 실패 원인)

```python
# ❌ 이것만 하면 form-urlencoded 발동 (415 오류)
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
# result.flg == 'Y' 인지 확인 후 location.href = result.redirectUrl
```

#### 폼 구조 (실측 HTML)

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

#### 도메인 alias

- **`wpps.logisall.com`** (스킬 기준) = **`wpps.logisall.net`** (다른 에이전트 보고) = **같은 서버**
- 두 도메인 모두 HTTP 200, 10,439 bytes (login 페이지) 동일 응답
- 어느 도메인 사용해도 무관, 단 `Origin`/`Referer` 헤더는 **실제 호출한 도메인**과 일치해야 함

## 메뉴 접근

1. 로지스올 WPPS 로그인 (위 방식)
2. 메뉴 URL 직접 접근 (SPA 메뉴 클릭 대체):
   - 납품/반납요청: `GET /ps/PBM110MW`
   - 출하통보등록: `GET /ps/PBM140MW`
   - 메인: `GET /ps/index`

## PBM110MW — 납품/반납요청 신규등록

### SpreadJS Grid 컬럼 구조 (실측 2026-06 기준)

> ⚠️ **스킬 본문은 구버전 (2026-05 이전)**. 실제 페이지는 **30+개 컬럼**으로 확장됨.
> 아래 표는 2026-06-02 페이지 실측 (`/tmp/pbm110mw.html` grep 결과) 기준.

| 컬럼코드 | 필수 | 출처 | 비고 |
|---------|:---:|:---:|:---|
| CHK | | 클라 | 저장 시 체크된 행만 반영 |
| MOD | ✅ | 클라 | "I"=신규, "U"=수정 |
| REQ_DAT | ✅ | 자동 | 요청일자 (YYYYMMDD) — fn_prevReqCallback에서 nowDate 자동 세팅 |
| REQ_TYP | ✅ | 클라 | combo('015'), 01=납품, 02=반납 |
| UNLOAD_REQ_DAT | ✅ | 클라 | 하차요청일자 (YYYYMMDD) |
| UNLOAD_REQ_TIM | | 클라 | HHMM 형식 (예: "0000") — fn_prevReqCallback 기본값 |
| PRD_COD | ✅ | 팝업 | TB_CST_PRD_NEW 팝업 조회 |
| CAR_OWN_TYP | ✅ | 클라 | combo('016'), 01=일반, 02=USER운송 |
| CAR_WGT_TYP | ✅ | 클라 | combo('014'), 07=5T / 11=11T / 14=14T |
| CAR_QTY | ✅ | 클라 | 차량대수, 기본 1 |
| REQ_QTY | ✅ | 클라 | 요청수량 |
| REQ_EMP_NAM | | 클라 | 요청자명 |
| REQ_DPT_NAM | | 클라 | 요청부서명 |
| ARV_CST_COD | ✅ | 팝업 | 도착지 고객사 코드 (cstarv API) |
| ARV_CST_NAM | | 자동 | 서버가 ARV_CST_COD로 자동 세팅 |
| CST_COD | | 자동 | 로그인 계정의 CST_COD (보통 217273) |
| DEP_CST_COD | | 자동 | depzip API가 자동 세팅 |
| ZIP1_NUM | | depzip | 실도착지 우편번호 (예: "482") |
| ZIP2_NUM | | depzip | 실도착지 우편번호 추가 |
| ZIP_SEQ | | depzip | 실도착지 sequence |
| ZIP_NUM | | depzip | 실도착지 주소 (예: "경기 양주시 삼숭동") |
| REQ_ARV_ZIP_ADDR | | 클라 | 실도착지 상세주소 (예: "582-2") |
| RTN_DEP_CST_COD | | 팝업 | KPP물류센터 (CAR_OWN_TYP=02 일때만) |
| RTN_DEP_CST_NAM | | 자동 | 서버 자동 세팅 |
| RTN_ZIP1_NUM | | depzip | 물류센터 우편번호 |
| RTN_ZIP2_NUM | | depzip | 물류센터 우편번호 추가 |
| RTN_ZIP_SEQ | | depzip | 물류센터 sequence |
| RTN_ZIP_NUM | | depzip | 물류센터 주소 |
| RTN_ZIP_ADDR | | 클라 | 물류센터 상세주소 |
| ETC_DESC | | 클라 | 비고 (ETC_DESC_BTN으로 입력) |
| ETC_DESC_COD | | 클라 | 비고 코드 |
| ETC_DESC_COD_ADD | | 클라 | 비고 코드 추가 |
| ALC_STATUS | | 자동 | 배차진행상태, 신규 시 "" |
| ALC_REQ_FLG | | 자동 | 배차요청플래그, 신규 시 "" |
| TANG_BTN | | UI | 행추가 버튼 (SpreadJS ButtonClicked 이벤트로 신규 행 생성) |

**구버전과 차이**:
- ✗ `PRD_NAM` — 서버가 PRD_COD로 자동 세팅 (클라가 안 보내도 됨)
- ✗ `REG_DAT` — 컬럼 자체 없음 (서버 내부)
- ✗ `STC_CST_COD`, `REQ_CST_COD` — 스킬엔 별도였지만 `fn_saveCheck`가 **자동으로** `REQ_CST_COD = ARV_CST_COD` 매핑
- ✓ `REQ_DAT` (필수), `UNLOAD_REQ_TIM` (HHMM) — **신규 시 필수** (스킬에 없었음)
- ✓ `TANG_BTN` — UI 행추가, `fn_new`이 아닌 **이벤트 핸들러가 신규 행 생성**

### 신규등록 (API 직접 호출)

> ⚠️ **스킬 본문의 `fn_new()` 함수는 페이지에 존재하지 않음**. 실제 신규 행 추가는 **`TANG_BTN` 클릭 → SpreadJS `ButtonClicked` 이벤트**가 처리함.
> `fn_saveCheck`(line 1127~)가 저장 전 데이터를 자동 가공: `DTL_ADDR ← ZIP_NUM`, `REQ_CST_COD ← ARV_CST_COD`, `UNLOAD_REQ_DAT_CHK ← UNLOAD_REQ_DAT`.
> 즉 클라이언트는 ZIP_NUM만 보내면 서버는 DTL_ADDR로 자동 매핑.

**신규 행 페이로드 (TANG_BTN이 생성하는 템플릿, 2026-06-02 페이지 line 1352~1385 실측)**:

```python
save_data = [{
    # === 식별/플래그 ===
    "CHK": True,                # 저장 대상 표시
    "MOD": "I",                 # Insert (신규) — "U"는 수정

    # === 일자 ===
    "REQ_DAT": "20260602",      # 요청일자 (YYYYMMDD) — fn_prevReqCallback이 nowDate로 자동 세팅
    "UNLOAD_REQ_DAT": "20260602",  # 하차요청일자 (YYYYMMDD)
    "UNLOAD_REQ_TIM": "0000",   # HHMM 형식, fn_prevReqCallback 기본값

    # === 요청 분류 ===
    "REQ_TYP": "01",            # 01=납품, 02=반납
    "CAR_OWN_TYP": "01",        # 01=일반, 02=USER운송

    # === 팔레트 ===
    "PRD_COD": "...",           # 유형코드 (TB_CST_PRD_NEW 팝업 조회 필수)
    "CAR_WGT_TYP": "11",        # 07=5T, 11=11T, 14=14T
    "CAR_QTY": 1,               # 차량대수
    "REQ_QTY": 14,              # 요청수량 (예: 14팔레트)

    # === 요청자 ===
    "REQ_EMP_NAM": "...",       # 요청자명 (선택)
    "REQ_DPT_NAM": "...",       # 요청부서 (선택)

    # === 도착지 (LS의 BUC1_H → WPPS 고객코드 필요) ===
    "ARV_CST_COD": "...",       # 도착지 고객코드 (PBM110MW.cstarv API 조회)
    # "ARV_CST_NAM": "...",    # 서버가 자동 세팅 — 안 보내도 됨

    # === 실도착지 (depzip API 결과) ===
    "ZIP1_NUM": "482",          # 우편번호
    "ZIP2_NUM": "...",          # 우편번호 추가
    "ZIP_SEQ": "...",           # sequence
    "ZIP_NUM": "경기 양주시 삼숭동",  # 주소
    "REQ_ARV_ZIP_ADDR": "582-2",    # 상세주소

    # === KPP물류센터 (CAR_OWN_TYP=02 일때만) ===
    "RTN_DEP_CST_COD": "...",
    "RTN_DEP_CST_NAM": "...",
    "RTN_ZIP1_NUM": "...",
    "RTN_ZIP2_NUM": "...",
    "RTN_ZIP_SEQ": "...",
    "RTN_ZIP_NUM": "...",
    "RTN_ZIP_ADDR": "...",

    # === 비고 ===
    "ETC_DESC": "...",
    "ETC_DESC_COD": "...",
    "ETC_DESC_COD_ADD": "...",

    # === 자동 필드 (서버 검증) ===
    "ALC_STATUS": "",           # 신규 시 빈 문자열
    "ALC_REQ_FLG": "",          # 신규 시 빈 문자열
}]

r = s.post("https://wpps.logisall.com/ps/PBM110MW.do",
           data=json.dumps(save_data),
           headers={"Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"})
# 성공: {"flag": true, "message": "저장되었습니다."}
# 실패: {"flag": false, "message": "[유형] 필수사항입니다.!"}
```

**함정: 스킬 예제 코드에 있던 필드들** (현재는 안 보내도 됨):
- `STC_CST_COD`, `REQ_CST_COD` → `fn_saveCheck`가 `REQ_CST_COD = ARV_CST_COD`로 자동 매핑
- `PRD_NAM` → 서버가 자동 세팅
- `REG_DAT` → 컬럼 자체 없음 (서버 내부)

### 저장 오류 트러블슈팅

| 오류 메시지 | 원인 |
## 검증 함정 (조회 시)

1. `r.json()` 결과 타입은 `list` 또는 `dict` 둘 다 가능 → 타입체크 필수
2. 빈 결과 `[]` 또는 `{"rows": []}` ≠ "조회 실패" — 정상 0건일 수 있음
3. HTTP 200 이라도 본문이 `{"flag":false,"message":"..."}` 일 수 있음 → 양쪽 다 체크

4. **🚨 고객사 파라미터명은 `cst_cod` (소문자)** — `STC_CST_COD`/`REQ_CST_COD`(대문자)로 보내면 0건 응답함. **2026-06-03 실측 확인 완료**: `cst_cod=217273` 호출 시 2,592건 정상, `STC_CST_COD/REQ_CST_COD=217273` 호출 시 0건. 상세: `references/pbm110MW-query-param-case-2026-06-03.md`

5. **🚨 PBM110MW.save 200 OK ≠ 저장 성공 (2026-06-03 실측)** — 응답 `{"flag":true,"message":"저장되었습니다."}` 가 와도 GET 재조회 시 row 0건 가능. UI는 5단계 통합이지만 API는 1·2·3·4·5 모두 한 페이로드로 묶어 보내야 함 (fn_saveCheck silent drop 가능). **저장 직후 반드시 GET으로 재조회**해서 row 존재 확인 — response status만 보고 "저장 완료" 보고 금지. 6가지 silent drop 원인 (필수 필드 누락, ZIP 불일치, CAR_OWN_TYP=02인데 RTN_* 미포함, REQ_TYP 호환 안 됨, 중복 row, **세션 토큰 60분 만료**) — 저장 직전 토큰 갱신 필수. PBM140MW.save도 동일 패턴 적용. 상세: `references/save-success-pitfall-2026-06-03.md` ⭐

### 기존 데이터 조회
```python
# GET /ps/PBM110MW.do (params)
# ⚠️ 고객사 파라미터는 반드시 소문자 cst_cod! (대문자 변형은 0건 응답)
params = {
    "REQ_DAT_FR": "20260601",
    "REQ_DAT_TO": "20260630",
    "cst_cod": "217273",   # 소문자 필수
}
r = s.get("https://wpps.logisall.com/ps/PBM110MW.do", params=params)
# r.json() = [...]  (SpreadJS grid data array)
# 2026-06-03 실측: 6/1~6/30 한달치 2,592건 응답
```

### 내부 API 엔드포인트 (PBM110MW 기준)

| 엔드포인트 | 메서드 | 용도 |
|-----------|-------|------|
| `/ps/PBM110MW` | GET | 페이지 HTML 로드 |
| `/ps/PBM110MW.do` | GET | 데이터 조회 (SpreadJS grid) |
| `/ps/PBM110MW.do` | POST | 데이터 저장/수정 |
| `/ps/PBM110MW.depzip` | GET | 기본 배송지 정보 조회 (params: REQ_CST_COD) |
| `/ps/PBM110MW.cstarv` | GET | 고객사 도착지 정보 조회 (params: CST_COD) |
| `/ps/PBM110MW.trnqry` | GET | 유형×톤수별 수량 조회 (params: PRD_COD, CAR_WGT_TYP) |
| `/ps/PBM110MW.getmaxreqqty` | GET | 유형별 최대요청수량 (params: PRD_COD) |
| `/ps/PBM110MW.getmaxreqqty` | GET | 유형별 최대수량 (params: PRD_COD) — MAX_QTY=9999999이면 무제한 |

## PBM140MW — 출하통보등록 ⚠️ 실제 운영 메뉴

> **6/1~6/2 사용자 운영 데이터는 모두 PBM140MW**. "1호차/2호차/3호차 등록"은 PBM140MW 의미.
> PBM110MW는 "납품/반납요청" 별도 메뉴 (배차 요청 단계). 출하 후 통보 = PBM140MW.

**PBM140MW 핵심 차이 (PBM110MW 대비)**:
- `POST /ps/PBM140MW.search` (GET 아님) — **응답이 list 또는 dict 양쪽 가능 (타입 체크 필수)**
- `POST /ps/PBM140MW.save` (.do 아님)
- 필드 **소문자** (chk, mod, dlv_dat, arv_dat, arv_cst_cod, prd_cod, dlv_qty)
- `fn_saveDataChk` 자동 처리: `user_id='P217273'`, `dlv_dat`/`arv_dat` 형식 변환, null→""
- 신규 페이로드: mod="I", data_typ="02" (또는 "01"), web_mov_typ="01", err_typ="01", car_own_typ="02", kpp_confm_flg="N"
- **호차 구분**: `web_desc` 필드에 "1호차"/"2호차"/"3호차" 텍스트로 표기
- **`prd_cod="N11"` (11T 파렛트 종류)** — 차량 톤수와 무관, 5T/11T 차량 모두 N11

**PBM140MW search 응답 처리 (Python 패턴)**:
```python
r = s.post("https://wpps.logisall.com/ps/PBM140MW.search",
           json={"dfrDat":"20260602","dtoDat":"20260602","page":1,"rows":50})
raw = r.json()
# raw가 list 또는 dict 둘 다 가능 (서버 환경에 따라)
if isinstance(raw, list):
    rows = raw
elif isinstance(raw, dict):
    rows = raw.get('rows', raw.get('data', []))
else:
    rows = []
```

### 등록 항목
| 항목 | 예시 | 비고 |
|------|------|------|
| 파렛트 구분 | 특/AB | |
| 수량 | 12/14/16 | 톤수별 상이 |
| 하차지 | VF67_H | |
| 비고 | 특기사항 | |

### 톤수별 수량 기준
| 톤수 | 기본 수량 | 초과 시 LS 조건변경 |
|:----:|:---------:|:-----------------:|
| 5T | 12 | |
| 11T | 16 | 초과시 LS 변경 필요 |
| 14T | 18 | 초과시 LS 변경 필요 |

**상세 가이드**: `references/pbm140MW-api-details.md` (완전 페이로드 + 14필드 결정 근거)

## EDI 출력 (인쇄)

EDI 출력 시 Chrome `--kiosk-printing` 모드 사용.
Windows Hermes에서 Playwright 스크립트로 자동화 가능.
자세한 절차는 `references/edi-printing-automation.md` 참조.

## 템플릿 정보 (VF67 운송)

| 호차 | 템플릿 ID | 기본 톤수 | 비고 |
|:---:|:---------:|:---------:|:----:|
| 1호 | 90626 | 5T | |
| 2호 | 90628 | 5T | |
| 3호 | 90269 | 11T | |
| 4호 | 101740 | 5T | 추가요청시만 |

## 참고 파일

- `references/session-20260601-api-discovery.md` — 6/1 첫 API 발견 세션
- `references/login-troubleshooting-2026-06.md` — 로그인 트러블슈팅 (구버전)
- `references/login-domain-troubleshooting-2026-06-03.md` — 도메인 alias + 6/3 Playwright 함정 + 운영원칙 검증 ⭐
- `references/edi-printing-automation.md` — Chrome kiosk-printing 자동화
- `references/pbm110MW-api-details.md` — 6/1 API 명세 (구버전)
- `references/pbm110MW-query-param-case-2026-06-03.md` — **PBM110MW.do 조회 파라미터 대소문자 함정 (cst_cod 소문자 필수)** ⭐
- `references/pbm140MW-api-details.md` — **6/3 PBM140MW (출하통보) 완전 가이드** ⭐ — "2호차까지 했다"는 PBM140MW 의미
- `references/save-flow-2026-06.md` — 6/2 페이지 실측 저장 흐름 (TANG_BTN = fn_new, fn_saveCheck 자동 매핑, 30+ 컬럼) ⭐
- `references/verification-pitfalls-2026-06-03.md` — **검증 함정** (0건의 4가지 의미, list/dict 타입체크, loginType 필드, PRD_COD 정정) ⭐
- `references/save-success-pitfall-2026-06-03.md` — **PBM110MW/PBM140MW.save 200 OK ≠ 저장 성공** (6가지 silent drop 원인, 60분 토큰 만료, GET 재조회 필수) ⭐
- `scripts/login-and-verify.py` — 헤드리스 안전 로그인 + PBM110MW 도달 + READ ONLY 조회 검증 ⭐
- `scripts/kpp-verify-search.py` — **KPP 로그인 + PBM140MW 교차 조회 + 3호차 매칭 통합 스크립트** ⭐ (5가지 조건, list/dict 자동 처리)
