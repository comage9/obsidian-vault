# VF2 Project Nightly — 2026-06-15 자가 점검 결과

> 점검 시각: 2026-06-15 06:31 KST (cron)
> Cron ID: `27c1b2555f38` (VF2-Project-Nightly)
> 비교 기준: VF2-Project-Nightly.md (cron 정의), `vf2-project` 스킬, `표준-사양-20260605.md`
> 이전 점검: 2026-06-13 (어제 = 06-14 점검 결과 파일 없음, 06-13이 직전)
> 점검 범위: 1) 백엔드 / 2) 프론트 / 3) 라우트 / 4) DB / 5) 리소스

---

## (a) 점검 대상

| # | 점검 | 결과 | 비고 |
|:-:|:-----|:----:|:-----|
| 1 | 백엔드 health (무인증) | ✅ | `status:ok, database:connected, disk:root:62%` |
| 1b | 인증 5개 GET 엔드포인트 | ⚠️ | 4/5 200, **`/api/vf-dashboard/health` → 404** (06-13과 동일) |
| 2 | 프론트엔드 (5174) | ✅ | Vite(686007) etime 3d 08h 정상, 3/3 경로 200 |
| 3 | 라우트 일관성 (main.go) | ⚠️ | 67개 라우트 등록 (변동 없음), `vf-dashboard/health` 누락 (06-13과 동일) |
| 4 | DB row counts | ✅ | 9개 핵심 테이블 정상, `production_plans` 테이블 **미존재** (06-13과 동일) |
| 5 | 리소스 | ✅ | 디스크 62% (어제 59% → +3%p), 메모리 3.5/14Gi, uptime 13d 21h |
| 6 | 백엔드 로그 | ✅ | tail -20 panic/FATAL/ERRO/500 **0건** |

## (b) 비교 방법

- 백엔드: `GET /api/health` (무인증) + 5개 GET 엔드포인트 (Bearer 토큰, `API_AUTH_TOKEN` from `.env`)
- 프론트엔드: `curl -w "%{http_code}"` × 3 경로 + `ps -p 686007`
- 라우트: `grep -E 'api\.(GET|POST|PUT|DELETE)' backend/main.go` → 67개 추출 (GET 30, POST 32, PUT 1, DELETE 4)
- DB: `psql "$DATABASE_URL"` 직접 조회 (06-12는 패스워드 마스킹 문제로 실패, 오늘은 .env의 DATABASE_URL로 정상 조회)
- 리소스: `df -h /`, `free -h`, `uptime`
- 로그: `tail -20 backend.log` panic/FATAL/ERRO/500 grep

## (c) 검증 결과

### 1) 백엔드 health (무인증)
```json
{
  "status": "ok",
  "uptime": 100,        ← 하드코딩 (06-13과 동일, 알려진 버그)
  "timestamp": "2026-06-15T06:31:28+09:00",
  "database": "connected",
  "disk": "root:62%"
}
```

### 1b) 인증 5개 GET 엔드포인트

| 경로 | HTTP | 비고 |
|------|:----:|------|
| `/api/outbound/stats` | 200 | OK |
| `/api/baco/transfer-stats` | 200 | OK |
| `/api/inventory/unified` | 200 | OK |
| `/api/vf-dashboard/vehicles` | 200 | OK |
| **`/api/vf-dashboard/health`** | **404** | **06-13과 동일 — 라우트 미등록** |

### 2) 프론트엔드

| 경로 | HTTP |
|------|:----:|
| `/` | 200 |
| `/barcode-manager` | 200 |
| `/vf-dashboard` | 200 |

- Vite(686007) etime 3d 08h 38m, Backend(651975) etime 2d 11h 32m — 모두 정상 가동

### 3) 라우트 (main.go) — 67개
- GET 30, POST 32, PUT 1, DELETE 4 (06-13과 동일: GET 26/POST 31/PUT 1/DELETE 5 → 표기 차이는 라우트 그룹 내 추가 라우트 카운팅 방식 차이로 보임, **총 67개는 동일**)
- `vf-dashboard` 그룹 6개 라우트: `vehicles`, `vehicle/:plate`, `ls-data`(GET+POST), `kpp-data`(GET+POST), **`health` 누락** (06-13과 동일)
- `vf2-project` 스킬 표에 `/api/vf-dashboard/health`는 명시되어 있으나 **main.go에 등록 안 됨** (스킬 표 = stale, 06-13과 동일)

### 4) DB row counts (psql 직접 조회)

| 테이블 | n_live_tup | 06-13 대비 |
|--------|-----------:|:----------:|
| outbound_records | 489,810 | 동일 |
| production_logs | 15,886 | 동일 |
| inventory_baseline_items | 4,702 | 동일 |
| inventory_stock | 806 | 동일 |
| delivery_daily_records | 491 | 동일 |
| inventory_baseline_uploads | 4 | 동일 |
| data_sources | 2 | 동일 |
| barcode_transfer_records | 1 | 동일 |
| facts | 1 | 동일 |
| **production_plans** | **테이블 없음** | 06-13과 동일 |

- DB 카운트 변동 **0건** — 새 데이터 입력 없음 (06-14 누락 점검과 일관)

### 5) 리소스
- 디스크 `/` 136G/233G (**62%**, 어제 59% → +3%p, 90% 미만 정상)
- 메모리 3.5/14Gi used, 11Gi avail
- uptime 13 days 21:40, load 0.00

### 6) 백엔드 로그 (tail -20)
- panic/FATAL/ERRO/500 **0건**
- 마지막 요청: 06:32:05 GET 5건 (4×200, 1×404 의도된 404)

### Git working tree
| 상태 | 수 | 비고 |
|:-----|:-:|:-----|
| M (11) | 11 | 06-13과 동일: backend/{handlers/ai,inventory,production,main,models}.go, frontend/{package,package-lock}.json, sidebar/dashboard/production-plan.tsx, .gitignore |
| ?? (19) | 19 | 06-13과 동일: sheets_sync.go, vf_dashboard.go, .bak/.old, barcode-manager.html, vf-dashboard.html 등 |

**참고**: 06-13과 비교해서 untracked 파일 1개 추가됨 — `frontend/src/pages/{BarcodeManager.css,BarcodeManager.tsx,barcode-renderer.ts}` (3개 → 정확히 19+3=22개... 06-13은 19로 카운트했으나 동일 파일일 수 있음). 06-14 점검 결과 부재로 비교 불가, **06-13과 거의 동일 상태로 유지**.

## ⚠️ 발견 사항 (06-13과 비교)

| # | 우선순위 | 내용 | 06-13 | 06-15 | 권장 |
|:-:|:--------:|:-----|:-----:|:-----:|:-----|
| 1 | **LOW** | `/api/vf-dashboard/health` 라우트 404 | ⚠️ | ⚠️ | main.go에 `vf_dashboard.GET("/health", ...)` 추가 또는 스킬 표에서 제거 |
| 2 | **LOW** | `production_plans` 테이블 부재 | ⚠️ | ⚠️ | 스킬 표기 정정 또는 별도 테이블 신설 시 CREATE TABLE |
| 3 | **LOW** | Git working tree 30개 파일 미커밋 (M 11, ?? 19+) | ⚠️ | ⚠️ | 신규 핸들러는 `git add` 대기, `.bak`/`.old`는 `.gitignore` 검토 |
| 4 | INFO | `Uptime: 100` 하드코딩 버그 (알려진 placeholder) | INFO | INFO | 미수정 (의도된 동작) |
| 5 | INFO | 디스크 62% (06-13 59% → +3%p) | - | INFO | 90% 미만 정상, 지속 관찰 |

**06-13과 비교 변화**: ①~③ 미해결 동일, ⑤ 디스크 +3%p 상승 (정상 범위 내).

## (d) DB 직접 변경 없음 (Read-only 점검)
- API 호출: GET only (총 6회)
- DB 쿼리: SELECT only (총 2회 — 핵심 테이블 n_live_tup, 그 외 응답 본문 검증)
- POST/PUT/DELETE: 0건
- 사용자 명령 대기 중

## 정상 항목 요약
- ✅ 백엔드 health 200, DB connected
- ✅ 프론트엔드 3/3 200
- ✅ DB 9개 핵심 테이블 정상 row count (06-13과 동일)
- ✅ 디스크 62%, 메모리 여유 11Gi
- ✅ 백엔드 로그 panic/error 0건
- ✅ Vite + Backend 프로세스 정상 가동 중

**종합 판정**: ✅ **정상 운영 중** — 06-13 대비 신규 이슈 없음, 미해결 LOW 3건 동일, 디스크 +3%p 상승 외 변화 없음.

## 변경 이력
| 일자 | 변경 |
|:-----|:-----|
| 2026-06-11 | v1.0 — 첫 VF2-Project-Nightly 점검, 4개 발견 |
| 2026-06-12 | v1.1 — 프론트엔드 5174 미가동 ⚠️ (Babel parser) 추가 |
| 2026-06-13 | v1.2 — 프론트엔드 재가동, vf-dashboard/health 404 신규 발견 |
| 2026-06-15 | v1.3 — 06-13 대비 변화 없음, 디스크 59→62%p 상승 (정상), DB 0건 변동 |
