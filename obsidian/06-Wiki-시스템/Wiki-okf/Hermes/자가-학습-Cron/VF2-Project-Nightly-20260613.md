# VF2 Project Nightly — 2026-06-13 자가 점검 결과

> 점검 시각: 2026-06-13 06:30:49 KST (cron)
> Cron ID: `27c1b2555f38` (VF2-Project-Nightly)
> 비교 기준: VF2-Project-Nightly.md (cron 정의), `vf2-project` 스킬, `nightly-cron-self-check-pattern.md`
> 점검 범위: 1) 백엔드 / 2) 프론트 / 3) 라우트 / 4) DB / 5) 리소스

## (a) 점검 대상

| # | 점검 | 결과 | 비고 |
|:-:|:-----|:----:|:-----|
| 1 | 백엔드 health (무인증) | ✅ | `status:ok, database:connected, disk:root:59%` |
| 1b | 인증 6개 GET 엔드포인트 | ⚠️ | 5/6 200, **`/api/vf-dashboard/health` → 404** |
| 2 | 프론트엔드 (5174) | ✅ | `/`, `/barcode-manager`, `/vf-dashboard`, 두 `.html` 모두 200 |
| 3 | 라우트 일관성 (main.go) | ⚠️ | 67개 라우트 등록, `vf-dashboard/health` 누락 (문서상에는 있으나 main.go에 없음) |
| 4 | DB row counts | ✅ | 6개 핵심 테이블 정상, `production_plans` 테이블 **미존재** |
| 5 | 리소스 | ✅ | 디스크 59%, 메모리 4.1/14Gi, 스왑 2.7/4.0Gi, uptime 11d 21h |
| 6 | 백엔드 로그 | ✅ | tail -100 중 panic/FATAL/ERRO/500 **0건** |

## (b) 비교 방법

- 백엔드: `GET /api/health` (무인증) + 6개 GET 엔드포인트 (Bearer 토큰)
- 프론트엔드: `curl -w "%{http_code}"` × 4 경로 + `ps -p 686007`
- 라우트: `grep -E 'api\.(GET|POST|PUT|DELETE)' main.go` → 67개 추출
- DB: `psql -c "SELECT relname, n_live_tup FROM pg_stat_user_tables WHERE n_live_tup > 0"` + 핵심 테이블 count
- 리소스: `df -h /`, `free -h`, `uptime`
- 로그: `tail -100 backend.log` panic/FATAL/ERRO/500 grep

## (c) 검증 결과

### 1) 백엔드 health (무인증)
```json
{
  "status": "ok",
  "uptime": 100,        ← 하드코딩 (Section 8.1, 예상된 동작)
  "timestamp": "2026-06-13T06:31:32+09:00",
  "database": "connected",
  "disk": "root:59%"
}
```

### 1b) 인증 6개 GET 엔드포인트
| 경로 | HTTP | 비고 |
|------|:----:|------|
| `/api/health` | 200 | status=ok |
| `/api/outbound/stats` | 200 | 응답 본문 OK |
| `/api/baco/transfer-stats` | 200 | totalItems=1 |
| `/api/inventory/unified` | 200 | data.length=804 |
| `/api/vf-dashboard/vehicles` | 200 | 응답 OK |
| **`/api/vf-dashboard/health`** | **404** | **라우트 미등록** |

### 2) 프론트엔드
| 경로 | HTTP |
|------|:----:|
| `/` | 200 |
| `/barcode-manager` | 200 |
| `/vf-dashboard` | 200 |
| `/barcode-manager.html` | 200 |
| `/vf-dashboard.html` | 200 |

- Vite(686007) etime 10:41:39, Backend(651975) etime 1d 00h 59m — 모두 정상 가동

### 3) 라우트 (main.go) — 67개
- GET 26개, POST 31개, PUT 1개, DELETE 5개, 라우트 그룹 4개
- `vf-dashboard` 그룹 5개 라우트: `vehicles`, `vehicle/:plate`, `ls-data`, `kpp-data`(GET+POST), `health` 누락
- `vf2-project` 스킬 표에 `/api/vf-dashboard/health`는 명시되어 있으나 **main.go에 등록 안 됨** (스킬 표 = stale)

### 4) DB row counts
| 테이블 | n_live_tup |
|--------|-----------:|
| outbound_records | 489,810 |
| production_logs | 15,886 |
| inventory_baseline_items | 4,702 |
| inventory_stock | 806 |
| delivery_daily_records | 491 |
| inventory_baseline_uploads | 4 |
| data_sources | 2 |
| barcode_transfer_records | 1 |
| facts | 1 |
| **production_plans** | **테이블 없음 (relation does not exist)** |

### 5) 리소스
- 디스크 `/` 129G/233G (**59%**)
- 메모리 4.1/14Gi used, 10Gi avail
- 스왑 2.7/4.0Gi (**68%** — 80% 미만 정상)
- uptime 11d 21h, load 0.05

### 6) 백엔드 로그 (tail -100)
- panic/FATAL/ERRO/500 **0건**
- 마지막 요청: 06:31:33 GET `/api/vf-dashboard/vehicles` 200 (383µs) + 404 (의도된 404)

### Git working tree
| 상태 | 수 | 비고 |
|:-----|:-:|:-----|
| M (11) | 11 | backend/{ai,inventory,production,main,models}.go, frontend/{package,package-lock}.json, sidebar/dashboard/production-plan.tsx, .gitignore |
| ?? (19) | 19 | sheets_sync.go, vf_dashboard.go 신규, vf2_database.db.bak/.old, barcode-manager.html, vf-dashboard.html 등 |

## ⚠️ 발견 사항 (사용자 확인 필요)

| # | 우선순위 | 내용 | 영향 | 권장 |
|:-:|:--------:|:-----|:-----|:-----|
| 1 | **LOW** | `/api/vf-dashboard/health` 라우트 404 | vf-dashboard 프론트에서 health 폴링 시 실패. 실제 차량 데이터(`/vehicles`)는 정상 | main.go에 `vf_dashboard.GET("/health", ...)` 추가 또는 스킬 표에서 제거 |
| 2 | **LOW** | `production_plans` 테이블 부재 | `vf2-project` 스킬 §6.5에서 production plan 업로드 API가 `production_logs`에 저장 (테이블명 표기는 부적합) | 스킬 표기 정정 또는 별도 테이블 신설 시 CREATE TABLE |
| 3 | **LOW** | Git working tree 30개 파일 미커밋 (M 11, ?? 19) | 신규 핸들러 2개(sheets_sync, vf_dashboard) 미추가, DB 백업 2개 미정리 | 신규 핸들러는 `git add` 대기, `.bak`/`.old`는 `.gitignore` 검토 |
| 4 | INFO | `Uptime: 100` 하드코딩 (Section 8.1, 알려진 버그) | 모니터링/자동재시작 트리거가 신뢰하면 안 됨 | 미수정 (의도된 placeholder) |
| 5 | INFO | 스왑 68% (80% 미만 정상) | 현재 정상 범위 | 지속 관찰 |

## (d) DB 직접 변경 없음 (Read-only 점검)
- API 호출: GET only (총 6회)
- DB 쿼리: SELECT only (총 9회)
- POST/PUT/DELETE: 0건
- 사용자 명령 대기 중

## 정상 항목 요약
- ✅ 백엔드 health 200, DB connected
- ✅ 프론트엔드 4/4 200
- ✅ DB 6개 핵심 테이블 정상 row count (outbound 489K, production_log 15K, inventory 4.7K 등)
- ✅ 디스크 59%, 메모리 여유 10Gi
- ✅ 백엔드 로그 panic/error 0건
- ✅ Vite + Backend 프로세스 정상 가동 중

**종합 판정**: ✅ **정상 운영 중** (LOW 발견 3건, 사용자 확인 불필요 시 그대로 유지 가능)
