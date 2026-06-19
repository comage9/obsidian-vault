---
title: VF 출고 바코드 시스템
created: 2026-06-06
tags: [물류, VF, 바코드, 대시보드, 하네스]
---

# VF 출고 바코드 시스템

## 개요

보노하우스 VF 물류 출고 관리를 위한 **바코드 생성 + 시간대별 출고 데이터 전송** 웹 애플리케이션. 단일 HTML 파일로 동작.

- **위치**: `E:\coding\VF 출고 바코드\vf 출고 바코드 생성 (1).html`
- **README**: `E:\coding\VF 출고 바코드\README.md`
- **스킬**: 없음 (단일 HTML, 별도 스킬 불필요)

## 주요 기능

### 1. 데이터 처리
- 탭/공백/CSV 데이터 붙여넣기 → trackingNo(첫필드) + barcode(7필드) 추출
- 중복 trackingNo는 제거 (기존 히스토리 기준)
- 1행=1건 (수량 합계 안 함)
- fallback regex: `\d{10,}` = trackingNo, `[RC]\d+` = barcode

### 2. 시간대별 검증 (데이터 처리 전)
- 대시보드 API(`bonohouse.p-e.kr:5176`)로 오늘 시간별 입력 상태 확인
- 현재 시각 이전 시간대 중 미입력이 1개라도 있으면 **바코드 생성 차단**
- `h < now` 방식 (현재 시각 미포함)

### 3. 시간 데이터 전송
- 입력값을 API에 **그대로** 전송
- **계산 없음** (`lastCumul += val` → `val` 직접 사용)
- API: `POST /api/delivery/hourly` — body: `[{hour:15, quantity:250}]`

### 4. 출고 데이터 전송
- trackingNo + barcode → `POST /api/baco/transfer-stats`
- `sentTrackingNos` localStorage로 중복 전송 방지

### 5. 제품 DB
- **892개 VF 제품** HTML 내장 (`DEFAULT_PRODUCT_DB`)
- 엑셀/CSV 업로드 시 기존 바코드 = 덮어쓰기, 신규 = 추가
- 제품명 → 분류 자동 추출 (15개 규칙)

## 대시보드 API 명세

| Endpoint | Method | Body | 용도 |
|----------|--------|------|------|
| `/api/delivery/hourly?days=1` | GET | — | 오늘 시간대별 현황 조회 |
| `/api/delivery/hourly` | POST | `[{hour, quantity}]` | 시간대 데이터 전송 |
| `/api/baco/transfer-stats` | POST | `[{trackingNo, barcode, productName, category}]` | 출고 기록 전송 |

## 하네스 교차 검증 (2026-06-06)

M3(MiniMax) + nemotron(OpenRouter 무료) 교차 검증 완료.

### 발견된 이슈 및 수정
1. **`parseInt()` radix 누락** → `parseInt(x, 10)`로 수정
2. **`isNaN(hour)` 체크 누락** → `hour` 검증 추가
3. **전송값 계산 오류** → `lastCumul += val` → `val` 직접 전송
4. **시간 체크 버그** → `h <= now` → `h < now`

## 사용 흐름

1. 브라우저로 HTML 열기
2. 쿠팡 발주서/데이터 복사 → 텍스트 영역에 붙여넣기
3. 🔍 아이콘 클릭 → 미입력 시간대 확인
4. 수량 입력 → 📤 전송
5. 자동 생성된 바코드 확인 → 인쇄

## 관련 링크

- 대시보드: `http://bonohouse.p-e.kr:5176`
- 프로젝트 개요: `물류/프로젝트-개요.md`
- LS(쿠팡 Linehaul): `물류/쿠팡/LS/`
- KPP(WPPS): `물류/KPP/`
- 서플라이허브: `물류/쿠팡/Supplier-Hub/`

## 수정 이력

- 2026-06-05: 초기 생성
- 2026-06-06: 하네스 교차 검증 완료, 4개 이슈 수정, README 갱신
