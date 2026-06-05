---
name: ls-coupang
description: 쿠팡 LS(Linehaul Service) Truck Order 자동화 — Batch Create Order + Tracking 확인 + Cancel + 차량 정보 PostgreSQL 저장. 트리거 LS 등록, 쿠팡 차량, 트럭오더, VF67 차량 요청, LinehaulSlip.
---

# 쿠팡 LS (Linehaul Service) Truck Order

## 🚨 사용자 단순화 원칙 (2026-06-03 추가, 절대 위반 금지)

### "너무 복잡하게 가지 말고 하라는 것만"
- 사용자가 **한 가지 작업만** 지시하면 **그 작업만** 수행
- "LS 차량 정보 가져와" → LS만, **KPP/DB/위키 작업 자동 진행 금지**
- 이전 일자 데이터 파싱/매핑 작업 자동 수행 금지 — 사용자가 명시한 날짜만

### "단답만"
- **0건 / N건** 단답 + 핵심 표. 부연/추측/"된다"장담 금지
- 톤수 물으면 "1호차=5T, 2호차=5T, 3호차=11T" 식 표만
- 진행 보고 시 (a) 무엇 (b) 어떻게 (c) 어떻게 검증 — 이 3가지만

### "KPP/LS는 별개 서비스"
- LS 작업 중 KPP 자동 진행 X
- KPP 작업 중 LS 자동 진행 X
- **3개 프로젝트 분리**: LS (ls.coupang.com) / KPP (wpps.logisall.com) / Supplier Hub (supplier.coupang.com)

## 🚨🚨 LS 호차 정의 (2026-06-04 사용자 확정, 정정)

**호차 = 등록 순서** (시간 기준이 아님)
- 4개 템플릿 한꺼번에 등록 시: 17:30=1호차, 20:00=2호차, 22:00=3호차, 23:50=4호차
- 3개만 등록 시: 등록한 순서대로 1·2·3호차 배정
- **시간 자체가 호차를 결정하는 게 아니라, 그 시간에 등록한 게 N번째면 N호차**
- 템플릿 ID(90626/90628/90269/101740)는 톤수/노선 정보일 뿐 호차와 무관

## 🚨🚨 LS 자동 등록 규칙 (2026-06-04 사용자 확정)

### 데이터 소스
- **LS 홈페이지** (https://ls.coupang.com) 가 **유일한 정본**
- API 응답 데이터로 복잡한 비교/추측 ❌ → **홈페이지 직접 조회**가 기준

### 등록 규칙
1. **등록된 게 있으면 → 등록 안 함** (중복 방지)
2. **등록된 게 없으면 (별다른 지시 없으면) → 13시에 맞춰서 자동 등록**

### 1호차 첫차 시간 = 19:00 (6/4 기준, 호차=등록순서)

- 6/4 사용자 확정 상태: 19:00(1호차) + 22:00(2호차) + 23:50(3호차) 등록됨
- 20:00, 4호차, 5호차: 등록 안 함 (별도 지시 없음)
- 20:00은 1호차(19:00) 내용 수정해서 사용 가능
- **자동 등록 완료** → 추가 등록 작업 없음

## 🚨🚨 정본 경로 정정 (2026-06-04)

**잘못된 경로**: `/media/comage/data/hermes-backup/`
**올바른 경로**: `/media/comage/data1/hermes-backup/`

`/media/comage/data/`는 빈 디렉토리. 실제 외부 디스크는 `/media/comage/data1/`. 정본 동기화 시 주의.

## 차량 템플릿

| 호차 | 템플릿 ID | 기본 톤수 | 비고 |
|:---:|:---------:|:---------:|:----:|
| 1호 | 90626 | **5T** | LS Tracking API `truckType.name` 직접 확인 (2026-06-03 검증) |
| 2호 | 90628 | 5T | LS Tracking API `truckType.name` 직접 확인 |
| 3호 | 90269 | 11T | LS Tracking API `truckType.name` 직접 확인 |
| 4호 | 101740 | 5T | 추가요청시만 (예비) |

**⚠️ 2026-06-03 정정**: 이전 SKILL.md는 90626=11T였으나 **현재 5T**. 템플릿 ID와 톤수가 1:1로 매핑되지 않을 수 있으므로 **항상 `truckType.name`으로 확인**.

**톤수 → 팔레트 수량 (KPP PBM140MW, 사용자 진술 2026-06-03)**:
- 5T → 12팔레트
- 11T → 14팔레트
- 14T → 18팔레트
- (구버전 5T=8~12, 11T=13~16 → **고정값 변경됨**)

## 🚨 19:00 3건 표시 Pitfall (2026-06-04 확정)

**사용자 질문**: "왜 같은 시간대가 동일하게 3번씩이나 입력되는 거야?"

**진짜 원인**: **3건이 동일하게 입력된 게 아님**. LS `/order` API 응답 구조상 같은 시각(19:00)에 다른 날짜의 CANCELED 행이 섞여서, 시각 정렬만 보면 3건처럼 보임.

**검증 데이터 (6/4 10:30+ API 50건 중 19:00 매칭)**:
| 날짜 | 시각 | 상태 | 건수 |
|---|---|---|---|
| 6/4 | 19:00 | SUBMITTED 1건 + CANCELED 2건 | 3건 (사용자 진술대로) |
| 5/30 | 19:00 | CANCELED 3건 | 3건 (어제 잔여) |
| 5/30 | 19:30 | CANCELED 1건 | 1건 (어제 잔여) |

→ **시각만 보면 7건**이지만, 날짜별로 보면 (6/4 3건) + (5/30 4건)이 다른 날짜 + 다른 상태의 데이터가 합쳐진 것.

**대응 절차**:
1. `/order` API 조회 시 `dateFrom=dateTo=오늘` 필터
2. 응답 받으면 **날짜별 분리 출력** (`requestTime[:10]` 기준)
3. 같은 시각 N건 표시되어도 `status=CANCELED` 다수면 어제 잔여로 간주 (건드리지 않음)
4. 오늘자 SUBMITTED 건만 카운트 대상

**상세**: `Wiki/물류/쿠팡/LS/19시00분-3건-표시-원인-2026-06-04.md` 참조

**톤수 추출법 3가지**:
1. **LS Tracking API** (`/truckOrderTracking` 응답의 `truckType.name`) — 가장 빠름
2. **PDF 다운로드 후 `pdftotext -layout`** — 단, PDF는 출발 후 발급
3. **LS 페이지 UI** (사용자만 가능) — 헤드리스 Akamai 차단

## PDF 다운로드 (LinehaulSlip, 2026-06-03 발견)

**Endpoint**: `GET /linehaul/slip/generate?truckRequestId={id}&locale=ko_KR`
**헤더**: `Accept: application/json,application/pdf` (둘 다 명시 필수, application/pdf 단독 → 406)
**응답**: `Content-Type: application/pdf;charset=UTF-8`, 1.5MB PDF 1페이지
**인증**: `truckRequestId` (LS `/order` 또는 `/truckOrderTracking`에서 추출)

```bash
curl -sS -b /tmp/coupang_cookies.txt \
  "https://ls.coupang.com/linehaul/slip/generate?truckRequestId=27375860&locale=ko_KR" \
  -H "Accept: application/json,application/pdf" \
  -o /tmp/slip_27375860.pdf
# HTTP 200, size 1,501,873 B
```

**PDF 파싱** (`pdftotext -layout`):
- "운행일자" = 발송일
- "차량번호" = plateNumber
- "트럭바코드" = barcode
- "성함" = 기사명
- "연락처" = L5 "010-XXXX-" + L6 "XXXX" 결합 (한 줄에 안 들어감)

## 접속 정보

- 사이트: https://ls.coupang.com
- 로그인: mokicom / bonohouse0309^^
- 인증: Keycloak OAuth2 (Akamai CDN 보호)
- 쿠키 저장: `/tmp/coupang_cookies.txt`
- **정본 위치**: `~/다운로드/ls-coupang/`

## 인증 문제 해결

### 증상: curl API 호출 시 404 또는 로그인 페이지 HTML 반환
**원인:** 쿠키 만료. Keycloak 세션이 무효화되면 API가 404(istio-envoy) 또는 Keycloak 로그인 페이지를 반환함.
**해결:** 사용자에게 `ls.coupang.com` 재로그인 요청.

### 증상: browser_navigate 타임아웃 (Akamai CDN 차단)
**해결:** headless browser 사용 금지. python-requests 또는 curl로 진행.

### 증상: Chrome Cookies SQLite 직접 추출 시 `length(value)=0`
**해결:** `browser-cookie3` Python 패키지 또는 `google-chrome --remote-debugging-port=9222`

## 사용 규칙 (필수)

### 스킬을 먼저 로드할 것
사용자가 LS/쿠팡/트럭오더 관련 지시를 하면 **무조건 먼저 이 스킬(skill_view)을 로드**할 것.

### 인증 실패 시 행동
1. cookies.txt 만료 확인
2. Python requests session으로 자동 재인증 (references/python-auth-flow.md)
3. 실패 시 사용자에게 재로그인 요청
4. browser_navigate 시도 금지 (Akamai 차단)

## 출발지/도착지

| 명칭 | 코드 | 설명 |
|:----|:----|:-----|
| VF67(유원)HUB | VF67_H | 출발지 |
| 부천1HUB | 610060 (BUC1_H) | 도착지 |

## API

⚠️ **모든 API 경로는 root `/` 기준 (ls.coupang.com 직접). `/api/v1` 프리픽스 없음!**

### 조회 (트래킹)
```bash
GET /truckOrderTracking
# 파라미터: page, pageSize, orderStartDate, orderEndDate, locationStart, statuses
# truckType.name = 톤수 (5T/11T/14T), truckType.code = T5000/T11000
# truckInfo.plateNumber = 차량번호, truckVendor.name = 트럭업체
```

### 조회 (오더 목록/단건)
```bash
GET /order                # 오더 목록 조회
GET /order/{orderId}      # 단건 조회
```

### 배치 생성
```bash
POST /truckOrder/templates/batch/creation/{orderDate}
# Body: [templateId1, templateId2, ...]
```

### 개별 생성/수정
```bash
POST /order                              # 생성
PUT  /order/{orderId}                    # 수정
```

### 취소/반송
```bash
PUT /order/cancel/{requestId}
PUT /order/back/{requestId}
```

### 트래킹 (업데이트/엑셀)
```bash
PUT  /truckOrderTracking/{truckRequestId}
GET  /truckOrderTracking/excelDownload
```

### PDF 다운로드 (운행확인서, 2026-06-03 발견)
```bash
GET /linehaul/slip/generate?truckRequestId={id}&locale=ko_KR
# Headers: Accept: application/json,application/pdf (필수)
# 응답: application/pdf, ~1.5MB, 1페이지
# JS 소스: printLinehaulSlip 액션 → linehaulSlipSprintApi.truckOrderTrackingPrintLinehaulSlipApi
# ⚠️ POST 아님, GET 방식
# ⚠️ Accept 헤더에 application/json,application/pdf 둘 다 명시 필수
# PDF 파일 저장 불필요, 정보만 추출 후 폐기 (사용자 진술 2026-06-03)
```

### PDF 파싱 (2026-06-03 검증)
- `pdftotext -layout {pdf} -` (출력)
- 운행일자: `운행일자\s+(\d{4}-\d{2}-\d{2})` (한국어 페이지)
- 차량번호: `차량번호\s+(\S+)`
- 트럭바코드: `트럭바코드\s+(\d+)` 또는 차량번호 다음 줄 숫자
- 성함: `성함\s+([가-힣]+)\s+연락처`
- 연락처: `010-(\d{4})-(\d{4})` (완전형) OR `010-(\d{3,4})-` 잘림 + 다음 4자리
```

### 쿼리 파라미터 필수
- `statuses=SUBMITTED,CONFIRMED,CANCELED,BACK` (기본값=CONFIRMED만 반환 → SUBMITTED 누락)
- `/order` API: `page`(0부터) + `pageSize` 필수
- `dateFrom/dateTo`는 **서버가 무시** → 클라이언트에서 `orderDate` 필터 필수

## 상태값

| 상태 | 설명 |
|:----|:------|
| SUBMITTED | 배차 전 (등록만 됨) |
| CONFIRMED | 배차 완료 |
| CANCELED | 취소 |
| BACK | 반송 |

## API 응답 필드명

### `/order` API 응답
| 실제 필드명 | 설명 |
|:-----------|:-----|
| `truckOrderTemplateId` | 템플릿 ID (90626, 90628, 90269) |
| `requestTime` | `"2026-06-02 20:00:00"` 형식 (str) |
| `truckRequestId` | 오더 ID |
| `from` / `dest` | 출발지/도착지 |
| `status` | SUBMITTED/CONFIRMED/CANCELED/BACK |
| `orderDate` | `"2026-06-02"` |

### `/truckOrderTracking` API 응답 (트럭 정보 포함)
| 실제 필드명 | 설명 |
|:-----------|:-----|
| `truckOrderTemplateId` | 템플릿 ID |
| `truckType.name` | **톤수 (5T/11T/14T)** |
| `truckType.code` | T5000/T11000/T14000 |
| `truckType.loadCapacity` | 적재용량 (kg) |
| `truckInfo.plateNumber` | 차량번호 |
| `truckVendor.name` | 트럭업체 (케이엘피 등) |
| `truckInfo.driverName/Phone` | **None (API 한계, PDF로)** |
| `requestTime` | epoch milliseconds (int) |
| `truckRequestId` | 오더 ID |
| `status` | 상태값 |
| `orderDate` | 오더 날짜 |

> ⚠️ **`requestTime` 타입 차이**: Tracking API는 epoch milliseconds (int), `/order` API는 `"2026-06-02 20:00:00"` 형식 (str).

## Batch Create 주의사항

```json
{"message":null,"code":200,"data":{"succeed":[],"failed":[90269,90626,90628]},"succeed":true}
```
- HTTP 200이지만 `succeed: [], failed: [ids]` = **이미 오더 존재** (정상)
- 신규 등록 전 Tracking 또는 `/order` API로 중복 확인

## Cron Job 실행

매일 13:00 KST cron job:
- `execute_code` 블록됨 — Python은 파일로 작성 후 `python3 xxx.py` 실행
- Telegram 전송은 `.env`의 `TELEGRAM_BOT_TOKEN` 사용
- 최종 결과 자동 전송

## 톤수 → 팔레트 수량 (KPP PBM140MW 등록 시, 2026-06-03 확정)

| 톤수 | 팔레트 수량 |
|---|---|
| 5T | 12 |
| 11T | 14 |
| 14T | 18 |

## 보고 규칙

LS 조회 결과는 "N건" 단답 형식으로 보고.
불필요한 분석/부연 금지.

## Pitfalls

### ❌ 이전 일자 데이터 자동 파싱/매핑
- "LS 차량 정보 가져와" → 오늘자만, 어제 PDF/이전 DB 자동 X
- 사용자가 명시한 날짜만 처리

### ❌ KPP/LS 혼동
- LS 작업 중 KPP 자동 진행 X
- "LS에서 차량 정보 가져와" → LS만, KPP/DB/위키 작업 자동 X

### ❌ PDF endpoint POST
- POST → 500 "Request method 'POST' is not supported"
- GET만 가능

### ❌ PDF Accept: application/pdf 단독
- 406 Not Acceptable
- `application/json,application/pdf` 둘 다 명시

### ❌ 템플릿 ID = 톤수 1:1 매핑 가정
- 90626 = 5T (현재) / 예전엔 11T였음
- **항상 `truckType.name`으로 확인**

### ❌ "됐다" 단독 진술
- "이 파일이 `/tmp/xxx` size=20915 B로 존재" 처럼 **객관 사실**(경로+크기+타임스탬프+응답코드) 만 사용

### ❌ 추측 ("될 것 같다", "아마", "보통")
- 모르면 "모른다" 또는 "검증 필요" 명시

## 참고 파일
- `references/auth-troubleshooting.md` — Keycloak 인증 문제 해결
- `references/python-auth-flow.md` — Python requests 기반 자동 로그인
- `references/js-api-endpoints.md` — JS 소스에서 발견한 전체 API 엔드포인트
- `references/headless-environment-check.md` — 헤드리스 환경 체크리스트
- `references/truck-info-source-comparison.md` — **트럭 정보 소스 비교 (API vs PDF)**
- `references/vehicle-info-sources.md` — **3가지 소스 + PDF endpoint + 톤수 매핑 (2026-06-03)**
- `scripts/daily-cron-vf67.py` — 매일 13:00 KST cron job 실행
