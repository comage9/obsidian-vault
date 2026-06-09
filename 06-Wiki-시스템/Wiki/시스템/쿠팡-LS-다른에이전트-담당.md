# 쿠팡 LS (Linehaul Service) 일일 차량 등록 — 다른 에이전트 담당

저장일: 2026-06-09
상태: **참조 전용 — 본 에이전트(VF2/ki-ai-trader 에이전트)는 동작하지 않음**

## 1. 담당 구분

- **LS 일일 13:00 차량 등록 자동화** = **다른 에이전트 담당** (Windows 서버 등)
- 본 에이전트(VF2/ki-ai-trader 에이전트)는:
  - 알고만 있음 (참조 가능)
  - **동작 안 함** (실행/수정/조회 일체 금지)
  - **다른 사용자 지시가 있을 때만** 관련 작업 가능

## 2. 이전 cron 정보 (2026-06-09 삭제됨)

- **Job ID**: `5c28d341582a`
- **Name**: "LS 일일 13시 차량 등록 확인"
- **Schedule**: `0 13 * * *` (매일 13:00 KST)
- **Skill**: `ls-coupang`
- **Script**: `/opt/hermes/skills/automation/ls-coupang/scripts/daily-cron-vf67.py`
- **상태**: 본 에이전트가 **2026-06-09에 삭제** (실행 → cronjob 도구 remove). 다른 에이전트가 등록한 cron은 그대로 운영 중일 수 있음 (제 시스템에 등록된 것만 삭제)

## 3. 참조 자료 (읽기 전용)

- **스킬**: `/opt/hermes/skills/automation/ls-coupang/SKILL.md`
- **핵심 엔드포인트**:
  - `POST /truckOrder/templates/batch/creation/{date}` (배치 생성, body=`[90626,90628,90269]`)
  - `GET /truckOrderTracking?locationStart=VF67_H&statuses=SUBMITTED,CONFIRMED,CANCELED,BACK` (조회)
  - `GET /order?...&dateFrom=...&dateTo=...` (오더 목록, 클라이언트 필터링 필수)
  - `GET /linehaul/slip/generate?truckRequestId=...&locale=ko_KR` (운행확인서 PDF)
- **인증**: Keycloak OAuth2 (`mokicom` / `bonohouse0309^^`), 쿠키 `/tmp/coupang_cookies.txt`
- **톤수 동적**: `truckType.code` 응답 우선 따르기 (메모리 기본값 X)
- **상태값**: SUBMITTED, CONFIRMED, CANCELED, BACK

## 4. 본 에이전트의 행동 규칙

1. LS 관련 코드/스킬/스크립트/cron **일체 손대지 않음**
2. LS 관련 조회/실행 **요청 시 거절** (단, 다른 사용자 지시가 있으면 진행)
3. LS 관련 **에러/리포트**는 **읽기만** (다른 에이전트에 전달하지 않음)
4. 메모리/스킬에 LS 규칙 추가 시 "다른 에이전트 담당" 명시

## 5. 메모리 위치 (참조)

- `MEMORY.md` §3: "LS(Linehaul Service / 쿠팡) 작업은 담당하지 않음. 다른 에이전트가 전담. LS 관련 cron job/spec/등록 등一切 손대지 말 것."

## 6. 변경 이력

- 2026-06-09: 본 에이전트 cron `5c28d341582a` 삭제 (사용자 지시). 본 문서 생성. **다른 에이전트 시스템은 영향 없음**.
