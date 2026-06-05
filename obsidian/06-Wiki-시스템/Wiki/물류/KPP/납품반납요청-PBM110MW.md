---
title: KPP 납품/반납요청 (PBM110MW) - 팔레트 입고 신청
tags: [KPP, PBM110MW, 팔레트, 납품, 자동화]
created: 2026-06-03
updated: 2026-06-03
category: 물류/KPP
---

# KPP 납품/반납요청 (PBM110MW) - 팔레트 입고 신청

> KPP(WPPS logisall) 시스템에서 **팔레트 입고를 신청**하는 메뉴.
> 출하통보(PBM140MW)와는 다른 별개 작업.

---

## 1. 운영 매뉴얼 (사람용)

### 1.1 언제 사용하는가?
- 우리 회사(217273 유원피에스)에 팔레트 입고가 필요할 때
- 빈도: **일주일에 1회 정도** (재고 부족 시)
- 출하량 12~16팔레트/일 대비, 입고는 200팔레트 단위로 큰 단위

### 1.2 어떻게 신청하는가?

#### 1단계: KPP 접속
- URL: `https://wpps.logisall.com` (또는 `wpps.logisall.net`)
- 로그인: ID=`P217273` / Password=`P217273` (ID=Password 동일)

#### 2단계: 메뉴 진입
- 좌측 메뉴: **"요청 및 조회관리"** 클릭 (드롭다운)
- 그 아래: **"납품/반납요청"** 클릭
- 페이지 도달: PBM110MW

#### 3단계: 신규 신청
- **상단 [신규] 버튼** 클릭 → 빈 행 추가
- 자동 세팅:
  - 요청일자: 오늘
  - 하차요청일자: 내일 (자동)
  - 요청구분: 납품
- 자동 채워지는 항목 확인 (실도착지, 제품, 수량 등)

#### 4단계: 저장
- **상단 [저장] 버튼** 클릭
- "저장하시겠습니까?" 확인 → **예**
- "저장되었습니다" 알림 → 등록 완료

#### 5단계: 결과 확인
- 화면 자동 새로고침 → 새 행 표시
- 배차진행상태: **01(미배차)** → 시간 경과 후 02→03→04 자동 진행

### 1.3 일자 변경/취소가 필요한 경우

🚨 **사용자가 직접 변경/삭제 불가**:
- 진행 중(상태 02/03) 또는 완료(상태 04) → 시스템이 잠금
- fn_deleteCheck에서 4가지 검증 + lockStatus=["02","03","04"] 모두 차단

**절차**:
1. KPP 관리자에게 **전화/이메일**로 일자 변경 또는 취소 요청
2. **우회**: 변경 일자로 신규 등록 (기존 건 유지)
3. AI 자동화는 페이로드 생성 후 사용자 "해" 받은 후 실행

### 1.4 자주 묻는 질문

**Q1. 일요일에 신청 가능한가?**
→ ❌ fn_saveCheck에서 자동 차단. "일요일로 요청이 불가 합니다" 메시지. KPP영업담당자와 협의.

**Q2. 토요일은?**
→ ⚠️ "토요일로 요청하시기 전에 확인 부탁드리겠습니다" confirm 표시됨. KPP 영업담당자 확인 후 진행.

**Q3. 수량은 기본 200인가?**
→ ✓ 11T 파렛트 N11, 200팔레트 단위가 표준.

**Q4. 도착지는 자동으로 우리 회사?**
→ ✓ REQ_CST_COD=217273 (유원피에스) 자동 세팅. 화면에서 "그룹거래처/요청거래처"가 217273으로 자동 입력됨.

---

## 2. 기술 문서 (개발자/자동화용)

### 2.1 시스템 정보
| 항목 | 값 |
|---|---|
| 사이트 | https://wpps.logisall.com (logisall.net 동일) |
| 백엔드 | Apache Tomcat 10.1.34 |
| 인증 | 로그인 후 JSESSIONID 쿠키 |
| 계정 | P217273 / P217273 (ID=Password) |
| MNG_GRD | 05 (일반 사용자) |
| CST_COD | 217273 (유원피에스) |
| DPT_COD | 601045 |

### 2.2 API 엔드포인트

| 메서드 | URL | 용도 |
|---|---|---|
| GET | `/login` | 로그인 페이지 (세션 준비) |
| POST | `/login.do` | 로그인 (JSON 필수) |
| GET | `/ps/index` | 메뉴 트리 |
| GET | `/ps/PBM110MW` | 페이지 진입 (HTML) |
| **GET** | **`/ps/PBM110MW.do`** | **조회 (요청일자/하차요청일자 기준)** |
| **POST** | **`/ps/PBM110MW.do`** | **저장 (신규/수정) — 배열 wrap 필수** |
| DELETE | `/ps/PBM110MW.do` | 삭제 (MNG_GRD=05 사용자는 권한 부족) |

### 2.3 로그인
```http
POST /login.do
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{"loginId":"P217273","password":"P217273"}

→ 200 {"flg":"Y","redirectUrl":"/ps/index"}
```
⚠️ **form-urlencoded는 Tomcat 415 명시 거부** → application/json 필수

### 2.4 조회 (GET /ps/PBM110MW.do)

#### 파라미터
| 파라미터 | 의미 | 사용 |
|---|---|---|
| REQ_DAT_TYPE | 1=요청일자, 2=하차요청일자 | 필수 |
| REQ_DAT_FR | 시작일 (YYYYMMDD) | 필수 |
| REQ_DAT_TO | 종료일 (YYYYMMDD) | 필수 |
| STC_CST_COD | 그룹거래처 코드 | "" 또는 217273 |
| REQ_CST_COD | 요청거래처 코드 | "" 또는 217273 |
| DPT_COD | 부서 코드 | 601045 (고정) |

#### 응답 (배열)
```json
[{
  "REQ_DAT": "20260529",
  "UNLOAD_REQ_DAT": "20260605",
  "REQ_TYP": "01",
  "UNLOAD_REQ_DAT_TIM": "0000",
  "PRD_COD": "N11",
  "CAR_OWN_TYP": "01",
  "CAR_WGT_TYP": "07",
  "CAR_QTY": 0,
  "REQ_QTY": 200,
  "ARV_CST_COD": "217273",
  "ARV_CST_NAM": "유원피에스",
  "ZIP1_NUM": "482",
  "ZIP2_NUM": "110",
  "ZIP_SEQ": 1,
  "ZIP_NUM": "경기 양주시 삼숭동",
  "REQ_ARV_ZIP_ADDR": "582-2",
  "ALC_STATUS": "03",
  "ALC_REQ_FLG": "Y",
  "REG_DAT": "2026-05-29 22:38:20"
}]
```

#### 🚨 함정: STC/REQ 둘 다 217273
```python
# ❌ WRONG: 0건 (의미 없는 필터)
{"STC_CST_COD": "217273", "REQ_CST_COD": "217273"}

# ✅ RIGHT: 우리 회사 입고건
{"STC_CST_COD": "", "REQ_CST_COD": "217273"}

# ✅ RIGHT: 우리 회사 요청건
{"STC_CST_COD": "217273", "REQ_CST_COD": ""}
```

### 2.5 저장 (POST /ps/PBM110MW.do)

#### 헤더
```
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

#### Body (배열 wrap 필수!)
```json
[{
  "CHK": true,
  "MOD": "I",                     // "I"=신규, "U"=수정
  "REQ_DAT": "20260603",          // 오늘 (YYYYMMDD)
  "REQ_TYP": "01",                // 01=납품, 02=반납
  "UNLOAD_REQ_DAT": "20260604",   // 자동 (내일)
  "UNLOAD_REQ_TIM": "0000",
  "PRD_COD": "N11",               // 11T 파렛트
  "CAR_OWN_TYP": "01",            // 01=KPP운송, 02=USER운송
  "CAR_WGT_TYP": "07",            // 차량톤수
  "CAR_QTY": 0,
  "REQ_QTY": 200,                 // 200팔레트
  "ARV_CST_COD": "217273",
  "ARV_CST_NAM": "유원피에스",
  "ZIP1_NUM": "482",
  "ZIP2_NUM": "110",
  "ZIP_SEQ": 1,
  "ZIP_NUM": "경기 양주시 삼숭동",
  "REQ_ARV_ZIP_ADDR": "582-2",
  "DTL_ADDR": "경기 양주시 삼숭동",   // = ZIP_NUM 자동 세팅
  "REQ_CST_COD": "217273",           // = ARV_CST_COD 자동 세팅
  "UNLOAD_REQ_DAT_CHK": "20260604",  // = UNLOAD_REQ_DAT 자동 세팅
  "ALC_REQ_FLG": "N",               // 신규 = N (배차요청 전)
  "ROTATE_NUM": 0
}]
```

#### 성공 응답
```json
{"flag": true, "message": "", "map": null, "list": null}
```

#### 🚨 함정
- **단일 객체 POST 시 404** → 반드시 배열 `[{}]`
- **form-urlencoded 415** → application/json 필수
- **fn_saveCheck 일요일 차단**
- **fn_saveCheck 토요일 경고**

### 2.6 삭제 (DELETE /ps/PBM110MW.do)

```python
r = s.delete(f"{BASE}/ps/PBM110MW.do",
             data=json.dumps(deleteData, ensure_ascii=False),
             headers={"Content-Type":"application/json"})
```

#### 차단 조건 (fn_deleteCheck)
1. `REQ_CST_COD == ''`
2. `REQ_DAT == ''`
3. `PRD_COD == ''`
4. `REQ_SEQ == ''`

#### 백엔드 추가 차단
- `lockStatus = ["02", "03", "04"]` (HTML line 1004) → 진행 중/완료 모두 잠금
- `MNG_GRD=05` (일반 사용자) 권한 부족
- 백엔드 응답에서 `REQ_CST_COD` 누락 → fn_deleteCheck 1번에서 차단

**결론: MNG_GRD=05 사용자는 임의 삭제 불가. KPP 관리자에게 연락 필수.**

### 2.7 상태 코드 (ALC_STATUS)
| 상태 | 의미 | code.js 정의 |
|---|---|---|
| **01** | 미배차 | 018001 |
| **02** | 운송의뢰 | 018002 |
| **03** | 상차대기 | 018003 |
| **04** | 배차완료 (입고 종료) | 018004 |

**진행 순서**: 01(미배차) → 02(운송의뢰) → 03(상차대기) → 04(배차완료)

DB에는 마지막 2자리만 저장됨. PBM110MW HTML의 `lockStatus = ["02","03","04"]`는 "잠금 처리되는 상태" (수정 불가).

### 2.8 자동화 예제 (Python)

```python
import requests, json, http.cookiejar, datetime

BASE = "https://wpps.logisall.com"
COOKIE = "/tmp/wpps_cookies_arrived.txt"

# 1) 로그인
cj = http.cookiejar.MozillaCookieJar(COOKIE)
s = requests.Session()
s.cookies = cj
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
})
s.get(f"{BASE}/login", timeout=15)
r = s.post(f"{BASE}/login.do",
           data=json.dumps({"loginId":"P217273","password":"P217273"}),
           headers={"Content-Type":"application/json"},
           timeout=15)
assert r.json()["flg"] == "Y"
s.cookies.save(COOKIE, ignore_discard=True, ignore_expires=True)

# 2) 페이지 진입
s.get(f"{BASE}/ps/index", timeout=15)
s.get(f"{BASE}/ps/PBM110MW", timeout=15)

# 3) 페이로드
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
payload = [{
    "CHK": True, "MOD": "I",
    "REQ_DAT": today.strftime("%Y%m%d"),
    "REQ_TYP": "01",
    "UNLOAD_REQ_DAT": tomorrow.strftime("%Y%m%d"),
    "UNLOAD_REQ_TIM": "0000",
    "PRD_COD": "N11", "CAR_OWN_TYP": "01", "CAR_WGT_TYP": "07",
    "CAR_QTY": 0, "REQ_QTY": 200,
    "ARV_CST_COD": "217273", "ARV_CST_NAM": "유원피에스",
    "ZIP1_NUM": "482", "ZIP2_NUM": "110", "ZIP_SEQ": 1,
    "ZIP_NUM": "경기 양주시 삼숭동", "REQ_ARV_ZIP_ADDR": "582-2",
    "DTL_ADDR": "경기 양주시 삼숭동", "REQ_CST_COD": "217273",
    "UNLOAD_REQ_DAT_CHK": tomorrow.strftime("%Y%m%d"),
    "ALC_REQ_FLG": "N", "ROTATE_NUM": 0
}]

# 4) 등록
r = s.post(f"{BASE}/ps/PBM110MW.do",
           data=json.dumps(payload, ensure_ascii=False),
           headers={"Content-Type":"application/json"},
           timeout=30)
assert r.json()["flag"] is True

# 5) 검증
verify = {
    "REQ_DAT_TYPE": "2",
    "REQ_DAT_FR": tomorrow.strftime("%Y%m%d"),
    "REQ_DAT_TO": tomorrow.strftime("%Y%m%d"),
    "STC_CST_COD": "", "REQ_CST_COD": "217273", "DPT_COD": "601045"
}
r = s.get(f"{BASE}/ps/PBM110MW.do", params=verify, timeout=30)
data = json.loads(r.text)
assert len(data) == 1
print(f"✓ 등록 확인: {tomorrow} 입고, {data[0]['REQ_QTY']}팔레트")
```

---

## 3. 작업 이력

### 2026-06-03 작업
1. KPP PBM110MW 페이지 도달 확인
2. 6월 하차요청일자 조회: 1건 (5/29 신청, 6/5 입고)
3. **6/4 입고 신규 등록 성공** (6/3 작업)
   - REQ_DAT=20260603, UNLOAD_REQ_DAT=20260604, PRD_COD=N11, REQ_QTY=200, ARV=217273
   - 응답: `{"flag":true,"message":"","map":null,"list":null}`
4. 메모리/스킬/위키 정식 저장

### 향후
- 일자 변경/취소 = KPP 관리자 연락 필수
- 6/5 건은 사용자가 KPP 관리자에게 별도 연락 예정
- 진행 상태 모니터링: 01(미배차) → 02 → 03 → 04 자동 진행

---

## 4. 관련 문서
- [[KPP_로그인_사양]]
- [[LS_주문_자동화]]
- [[출하통보_PBM140MW]]
- [[물류_운영_원칙]]
- [[운송_차량_톤수_기준]]
