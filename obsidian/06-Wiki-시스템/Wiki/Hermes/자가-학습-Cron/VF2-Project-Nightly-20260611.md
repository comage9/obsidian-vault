# VF2 Project Nightly — 2026-06-11 자가 점검 결과

> 점검 시각: 2026-06-11 06:36 KST (cron)
> Cron ID: `27c1b2555f38` (VF2-Project-Nightly)
> 비교 기준: VF2-Project-Nightly.md (cron 정의), Wiki `물류/VF-바코드-VF2-연동-가이드-20260606.md`, README.md
> 점검 범위: 1) 백엔드 / 2) 프론트 / 3) 라우트 / 4) DB / 5) 리소스

---

## (a) 점검 대상

| # | 점검 항목 | 방법 | 비고 |
|:-:|:---------|:-----|:-----|
| 1 | 백엔드 API (5176) | `GET /api/health` + 5개 인증 엔드포인트 | uptime 하드코딩 발견 |
| 2 | 프론트엔드 (5174) | `curl http://localhost:5174/` + `ps` | Vite dev 서버 2일째 가동 |
| 3 | POST 라우트 | `main.go` `api.(GET/POST/PUT/DELETE)` 패턴 매칭 | 67개 라우트, README와 14개 drift |
| 4 | DB | psql 9개 테이블 live row count | outbound_records 489,810건 정상 |
| 5 | 시스템 리소스 | `df -h /`, `free -h`, `uptime` | 디스크 54%, 메모리 30%, 부하 0.01 |

---

## (b) 비교 방법

1. `python3 urllib`로 인증 헤더(`Authorization: Bearer *** `)를 구성, GET-only로 6개 엔드포인트 조회
2. `grep -E 'api\.(GET|POST|PUT|DELETE)' backend/main.go`로 라우트 등록 67개 추출, README 표와 비교
3. `pg_stat_user_tables`로 주요 테이블 live row count (n_live_tup > 0)
4. README API 문서 섹션을 정규식 파싱하여 실제 라우트와 diff
5. `ps`, `ss`, `df`, `free`, `uptime`으로 프로세스/리소스 스냅샷

---

## (c) 검증 결과

### 1️⃣ 백엔드 API (port 5176)

| 엔드포인트 | HTTP | 결과 |
|:----------|:----:|:-----|
| `GET /api/health` (무인증) | **200** | `{status: ok, uptime: 100, database: connected, disk: root:54%}` |
| `GET /api/outbound/stats` | 200 | vf=1,035,944 / delivery=0 / 카테고리 48개 / 상위: 리빙박스 로코스 497,561 |
| `GET /api/production?date=2026-06-10` | 200 | 응답 dict, items 정상 (코덱 정상) |
| `GET /api/baco/transfer-stats` | 200 | data 1건 (test-route-003) |
| `GET /api/inventory/unified` | 200 | keys: data, lastUploadDate, summary |
| `GET /api/delivery/hourly` | 200 | keys: data, success |

✅ **6/6 엔드포인트 정상 응답**, 인증 토큰 OK

### 2️⃣ 프론트엔드 (port 5174)

| 항목 | 값 |
|:-----|:--|
| 프로세스 | `node vite` (PID 460571, ETIME 2-00:04:36 = 약 2일) |
| HTTP | 200, 1155 bytes (HTML with react-refresh shim) |
| `dist/` 빌드 산출물 | 존재 (JsBarcode.all.min.js, assets/, barcode-manager.html, favicon.svg, icons.svg) |

✅ Vite dev 서버 정상. 프로덕션 빌드 산출물도 유지됨.

### 3️⃣ 라우트 점검 (main.go)

| 메서드 | 라우트 수 | 비고 |
|:------|----------:|:-----|
| GET | 29 | |
| POST | 32 | |
| PUT | 1 | `/api/master/specs/:id` |
| DELETE | 5 | |
| **합계** | **67** | |

**README drift (14개 — 실제 존재, 문서 미기재):**

| 메서드 | 경로 | 추론 |
|:------|:-----|:-----|
| GET | `/api/delivery/daily-prediction` | Phase 4 일일예측 추가 (2026-05-29) |
| GET | `/api/inventory/missing-prices` | 전산재고 단가 관리 (최근 커밋 1263386) |
| GET | `/api/production-log` | 별칭 라우트 (POST와 짝) |
| GET | `/api/vf-dashboard/{vehicles,vehicle/:plate,ls-data,kpp-data}` | vf-dashboard 신규 (06-10) |
| POST | `/api/vf-dashboard/{ls-data,kpp-data}` | vf-dashboard 신규 (06-10) |
| POST | `/api/inventory/baseline-upload` | PostBaselineUpload 핸들러 (6ce0f16) |
| POST | `/api/inventory/price` | 전산재고 단가 (1263386) |
| POST | `/api/production-logs/sync` | production-logs sync (구 라우트) |
| POST | `/api/upload-production-file` | 별도 업로드 엔드포인트 |

### 4️⃣ DB (psql)

| 테이블 | live row | 비고 |
|:-------|---------:|:-----|
| `outbound_records` | **489,810** | 메인 출고 데이터 |
| `production_logs` | 15,886 | |
| `inventory_baseline_items` | 4,702 | |
| `inventory_stock` | 806 | Phase B |
| `delivery_daily_records` | 491 | |
| `inventory_baseline_uploads` | 4 | |
| `data_sources` | 2 | |
| `barcode_transfer_records` | 1 | test-route-003 |
| `facts` | 1 | |

✅ 9개 테이블 모두 정상 수집 중. 0건 테이블은 6개 (`outbound_analysis`, `master_color`, `master_unit` 등) — 등록 없음 정상.

### 5️⃣ 리소스

| 항목 | 값 | 판정 |
|:-----|:--|:----:|
| 디스크 `/` | 54% (118G/233G 사용) | ✓ |
| 메모리 | 4.2G/14G (30%) | ✓ |
| 스왑 | 3.7G/4.0G (92%) | ⚠️ **경고** — 스왑 92% 사용, 메모리 여유 2.9G |
| 부하 (load avg) | 0.01 / 0.02 / 0.00 | ✓ |

---

## ⚠️ 발견 사항 (사용자 확인 필요)

### ① `/api/health` Uptime 하드코딩 버그 (HIGH)

```go
// main.go 201행 부근
api.GET("/health", func(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "status": "ok",
        Uptime:    100,           // ← 하드코딩!
        Timestamp: time.Now(),
        Database:  dbStatus,
        Disk:      "root:" + diskStatus,
    })
})
```

- `startTime` 변수 자체가 없음 (`grep -nE "startTime|StartTime" main.go` → 0건)
- 실제 PID 482685의 ELAPSED = **1-20:11:44** (약 1일 20시간) 인데 응답은 100초로 거짓 보고
- 영향: 헬스체크 모니터링/자동재시작 트리거에 사용 시 오판
- 권장: `var startTime = time.Now()` + `Uptime: int(time.Since(startTime).Seconds())`

### ② 스왑 92% 사용 (MEDIUM)

- 메모리 여유 2.9G / 스왑 3.7G/4G
- Postgres (WAL/checkpointer) + Go 백엔드 + Vite 동시 가동 영향 추정
- 단기: 정상 운영, 단기 재부팅 권장하지 않음
- 중장기: 메모리 증설 또는 postgres 설정 튜닝 검토

### ③ Git working tree 22개 파일 미커밋 (LOW)

| 상태 | 파일 | 비고 |
|:-----|:-----|:-----|
| M (10) | `backend/{ai,inventory,production,main}.go`, `models/models.go`, `frontend/{package*.json, sidebar.tsx, dashboard.tsx, production-plan.tsx}`, `.gitignore` | |
| ?? (12) | `backend/handlers/{sheets_sync,vf_dashboard}.go`, `backend/{production-log, vf-dashboard/}`, `backend/vf2_database.db.{bak,old}`, `frontend/.codegraph/`, `barcode_original.html`, `--help` | `.bak` `.old`는 .gitignore 대상 확인 필요 |

- 핸들러 신규 2개 (`sheets_sync.go`, `vf_dashboard.go`)는 `git add` 대기
- DB 백업 파일 2개가 untracked — `.gitignore` 검토 필요

### ④ README ↔ 라우트 drift 14개 (LOW)

- README API 문서가 53개 라우트, 실제 67개 → 14개 누락
- 신규 기능 (vf-dashboard, 전산재고 단가, 일일예측) 문서화 누락
- 권장: 다음 README 갱신 시 한 번에 추가

---

## (d) DB 직접 변경 없음 (Read-only 점검)

- API 호출: **GET only**
- POST/PUT/DELETE: **0건**
- 사용자 명령 대기 중
- 가동 중 수정 없음

---

## 변경 이력

| 일자 | 변경 |
|:-----|:-----|
| 2026-06-11 | v1.0 — 5개 점검 항목 모두 통과, ①~④ 발견 사항 4건 보고 |
