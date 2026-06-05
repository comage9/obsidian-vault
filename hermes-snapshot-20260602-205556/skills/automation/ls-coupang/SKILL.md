---
name: ls-coupang
description: 쿠팡 LS(Linehaul Service) Truck Order 자동화 — Batch Create Order + Tracking 확인 + Cancel
category: automation
---

# 쿠팡 LS (Linehaul Service) Truck Order

## 접속 정보

- 사이트: https://ls.coupang.com
- 로그인: mokicom / bonohouse0309^^
- 인증: Keycloak OAuth2 (Akamai CDN 보호)
- 쿠키 저장: `/tmp/coupang_cookies.txt`

## 차량 템플릿

| 호차 | 템플릿 ID | 기본 톤수 | 비고 |
|:---:|:---------:|:---------:|:----:|
| 1호 | 90626 | 5T | 기본 포함 |
| 2호 | 90628 | 5T | 기본 포함 |
| 3호 | 90269 | 11T | 기본 포함 |
| 4호 | 101740 | 5T | 추가요청시만 |

## 출발지/도착지

| 명칭 | 코드 | 설명 |
|:----|:----|:-----|
| VF67(유원)HUB | VF67_H | 출발지 |
| 부천1HUB | 610060 (BUC1_H) | 도착지 |
| Tracking locationStart | VF67_H | 추적용 |

## API

### 조회
```bash
GET /order/{id}
# 쿼리 파라미터 필수: statuses=SUBMITTED,CONFIRMED,CANCELED,BACK
# (기본값=CONFIRMED만 반환 → SUBMITTED 상태(배차 전) 누락 방지)
```

### 생성
```bash
POST batch/creation/{date}
```

### 수정
```bash
PUT /order/{id}
# 전체 객체 필요 (부분 업데이트 불가)
```

### 취소
```bash
PUT cancel/{id}
```

## 상태값

| 상태 | 설명 |
|:----|:------|
| SUBMITTED | 배차 전 (등록만 됨) |
| CONFIRMED | 배차 완료 |
| CANCELED | 취소 |
| BACK | 반송 |

## 조회 필수 규칙

반드시 `statuses=SUBMITTED,CONFIRMED,CANCELED,BACK` 파라미터를 포함할 것.
기본값이 CONFIRMED만 반환하므로 SUBMITTED 상태(배차 전 등록)가 누락될 수 있음.

## 톤수별 적재 기준

| 톤수 | 기본 수량 | 비고 |
|:----:|:---------:|:----:|
| 5T | 12 | |
| 11T | 16 | 초과시 LS 조건변경 |
| 14T | 18 | 초과시 LS 조건변경 |

## 보고 규칙

LS 조회 결과는 "N건" 단답 형식으로 보고.
불필요한 분석/부연 금지.
