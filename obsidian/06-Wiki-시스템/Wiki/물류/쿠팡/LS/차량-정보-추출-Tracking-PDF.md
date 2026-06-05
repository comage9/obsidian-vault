# LS 차량 정보 추출 — Tracking API + PDF 다운로드 (2026-06-03 검증)

**최종 업데이트**: 2026-06-03
**대상**: 쿠팡 LS (ls.coupang.com) — 일일 차량 정보(차량번호, 톤수, 기사, 연락처) 추출
**목적**: 매일 KPP PBM140MW(출하 통보) 등록에 필요한 차량 정보 확보 자동화

## 1. 차량 정보 추출 2가지 소스

### 비교표

| 소스 | Endpoint | 데이터 | 시점 | 인증 |
|---|---|---|---|---|
| **Tracking API** | `GET /truckOrderTracking?orderStartDate=...` | 차량번호, 트럭타입(톤수), 트럭업체 | 출발 전~직후 (CONFIRMED) | 쿠키 |
| **PDF 다운로드** | `GET /linehaul/slip/generate?truckRequestId=...&locale=ko_KR` | 차량번호, 트럭바코드, 기사, 연락처 | 출발 후 (운행 중/완료) | 쿠키 |

**중요**: `truckInfo.driverName`, `truckInfo.driverPhone`는 **두 API 모두 None** — 기사는 PDF에만, 연락처는 **LS 페이지 UI에서만** 보임 (눈모양 아이콘 클릭). 자동화로는 PDF 파싱이 가장 확실.

## 2. Tracking API (1순위, JSON)

### 요청
```bash
GET https://ls.coupang.com/truckOrderTracking
  ?page=0&pageSize=50
  &orderStartDate=2026-06-03&orderEndDate=2026-06-03
  &locationStart=VF67_H
  &statuses=SUBMITTED,CONFIRMED,CANCELED,BACK

Headers:
  Cookie: <Netscape 쿠키 파일 또는 -b cookies.txt>
  Accept: application/json
  X-Requested-With: XMLHttpRequest
  Referer: https://ls.coupang.com/
```

### 응답 핵심 필드
```json
{
  "truckRequestId": 27375860,
  "truckOrderTemplateId": "90626",
  "orderDate": "2026-06-03",
  "status": "CONFIRMED",
  "requestTime": "2026-06-03 20:00:00",
  "truckInfo": {
    "plateNumber": "경기95자6464",
    "driverName": null,         ← API에는 없음
    "driverPhone": null,        ← API에는 없음
    "truckTypeCode": null
  },
  "truckType": {                ← 톤수는 별도 필드
    "truckTypeId": 4,
    "code": "T5000",
    "name": "5T",               ← 이게 톤수
    "loadCapacity": 1020,       ← kg
    "length": 7300, "width": 2300, "height": 2200   ← mm
  },
  "truckVendor": {
    "id": 6, "code": "KLP", "name": "케이엘피"
  }
}
```

### 톤수 매핑 (`truckType.name`)
- `5T` (T5000, loadCapacity=1020kg) — 5톤 트럭
- `11T` (T11000, loadCapacity=1360kg) — 11톤 트럭
- `14T` (T14000) — 14톤 (드묾)

### 템플릿 ID ↔ 톤수 (2026-06-03 확인, 사용자 진술)
- 90626 (1호차) = **5T** (예전엔 11T였음, 5T로 변경)
- 90628 (2호차) = **5T**
- 90269 (3호차) = **11T**
- 101740 (4호차, 예비) = 5T

## 3. PDF 다운로드 (2순위, 기사/연락처 필요시)

### 요청
```bash
GET https://ls.coupang.com/linehaul/slip/generate
  ?truckRequestId=27375860
  &locale=ko_KR

Headers:
  Cookie: <Netscape 쿠키 파일>
  Accept: application/json,application/pdf   ← 핵심
  X-Requested-With: XMLHttpRequest
  Referer: https://ls.coupang.com/
```

⚠️ **GET 방식 (POST 아님)**, Accept 헤더에 `application/json,application/pdf` 명시 필수.

### 응답
- HTTP 200, `Content-Type: application/pdf;charset=UTF-8`
- Body: PDF 1.5MB (단일 페이지, 한글 폰트 포함)

### PDF 파싱
```bash
pdftotext -layout /tmp/slip_${id}.pdf /tmp/slip_${id}.txt
```

### PDF 텍스트 구조
```
                                                   운행일자       2026-06-03
                                간선출차확인서            차량번호       경기95자6464
                                                               0113813470
                                       010-3910-
 운행정보        성함      손경준       연락처                 트럭바코드
                                          0850
```

### PDF 파싱 정규식
```python
import re, subprocess
txt = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], capture_output=True, text=True).stdout

# 운행일자
op_date = re.search(r'Operation\s+(\d{4}-\d{2}-\d{2})', txt)  # 또는 한국어 PDF면 "운행일자"
# → "운행일자\s+(\d{4}-\d{2}-\d{2})"

# 차량번호
veh = re.search(r'차량번호\s+(\S+)', txt)

# 성함 (이름)
name = re.search(r'성함\s+([가-힣]+)\s+연락처', txt)

# 연락처 (010-XXXX- + 다음 줄 4자리)
phone = None
full = re.search(r'010-(\d{4})-(\d{4})', txt)
if full:
    phone = full.group(0)
else:
    partial = re.search(r'010-(\d{3,4})-', txt)
    if partial:
        prefix = partial.group(0)
        after = txt[partial.end():]
        nxt = re.search(r'(\d{4})', after)
        if nxt:
            phone = prefix + nxt.group(1)
```

## 4. 인증 (Netscape 쿠키)

### 사용자 PC Chrome에서 추출
- `EditThisCookie` 확장 → Export → Netscape 형식
- 또는 `browser-cookie3` Python 패키지 (Linux)

### Netscape 형식
```
# Netscape HTTP Cookie File
.coupang.com	TRUE	/	TRUE	1812009288	_abck	51B0D26A...
.coupang.com	TRUE	/	FALSE	1780476177	ak_bmsc	...
```

### 필수 쿠키 (19개, 2026-06-03 시점)
- `_abck`, `ak_bmsc`, `bm_mi`, `bm_s`, `bm_so`, `bm_ss`, `bm_sv`, `bm_sz` — Akamai 봇 감지 (8개)
- `PCID` — 영구 PC 식별
- `sc_lid`, `sc_vid` — Supplier Hub ID (보노하우스9251, A00491514)
- `sh_at`, `sh_ct`, `sh_lid`, `sh_vid`, `shSessionIdNew` — Supplier Hub 세션 (5개)
- `ls_tz`, `WEB-GATEWAY-LAST-ACTION-AT`, `WEB-GATEWAY-SESSION` — LS 세션 (3개)

### python-requests로 사용
```python
import http.cookiejar, requests
cj = http.cookiejar.MozillaCookieJar('/tmp/coupang_cookies.txt')
cj.load(ignore_discard=True, ignore_expires=True)
session = requests.Session()
session.cookies = cj
```

## 5. 일일 운영 흐름

### 오전 (등록 후 30분~1시간, 또는 오후 3~4시)
1. Tracking API 호출 → CONFIRMED 오더의 차량번호/톤수 확보
2. (기사/연락처 필요시) PDF 다운로드 + 파싱
3. KPP PBM140MW에 1~3호차 단건 등록 (5T=12팔레트, 11T=14팔레트)

### 자동화 스크립트
- `~/.hermes/skills/automation/ls-vehicle-sync/scripts/parse_ls_pdfs.py` (PDF 파싱)
- `~/.hermes/skills/automation/ls-vehicle-sync/scripts/sync_ls_to_db.py` (Tracking API → DB)

## 6. Pitfalls (실제 경험 2026-06-03)

1. **LS API dateFrom/dateTo 무시**: 서버는 항상 최신 50건 (5808건 전체) 반환. **`orderDate` 필드로 클라이언트 필터 필수**
2. **truckInfo.driverName/driverPhone = None**: LS API로는 기사/연락처 못 가져옴 → **PDF 파싱 필수** (또는 사용자 PC 페이지)
3. **PDF endpoint POST 아님**: `GET /linehaul/slip/generate?truckRequestId=...&locale=ko_KR` + `Accept: application/json,application/pdf`
4. **PDF 전화번호 형식**: `010-XXXX-`로 잘려있고 다음 줄에 4자리 (예: "010-3753-" + "6321")
5. **Netscape 쿠키 httpOnly**: `#HttpOnly_` prefix 필수 (curl/MozillaCookieJar 모두 지원)
6. **사용자 페이지 눈모양 아이콘 = 자동화 불가**: 연락처는 사용자 화면에만, 자동화는 PDF 파싱이 최선
7. **PDF 파일 저장 불필요**: 정보만 추출하면 됨 (사용자 진술 2026-06-03)
8. **트럭 업체 = KLP(케이엘피)**: 6/3자 모두 KLP. 다른 날짜는 동방(DONGBANG) 등 가능

## 7. 6/3 실제 추출 데이터 (참고)

| 호차 | truckRequestId | Template | 시간 | 차량번호 | 트럭바코드 | 성함 | 연락처 | 톤수 |
|---|---|---|---|---|---|---|---|---|
| 1호차 | 27375860 | 90626 | 20:00 | 경기95자6464 | 0113813470 | 손경준 | 010-3910-0850 | **5T** |
| 2호차 | 27375861 | 90628 | 22:00 | 경기89바1454 | 0113823665 | 김동수 | 010-3940-9811 | **5T** |
| 3호차 | 27375859 | 90269 | 23:50 | 충북90아6169 | 0100906169 | 최문수 | 010-5342-6631 | **11T** |

## 8. KPP 팔레트 수량 규칙 (사용자 진술 2026-06-03)

| 톤수 | 팔레트 수량 |
|---|---|
| 5T | 12 |
| 11T | 14 |
| 14T | (미확인) |

## 관련
- 스킬: `~/.hermes/skills/automation/ls-coupang/SKILL.md`, `~/.hermes/skills/automation/ls-vehicle-sync/SKILL.md`
- KPP PBM140MW 등록: `~/.hermes/skills/automation/kpp-pallet-request/SKILL.md`
