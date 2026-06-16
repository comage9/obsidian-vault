# VF2 Project Nightly — 2026-06-16 자가 점검 결과

> 점검 시각: 2026-06-16 05:32 KST (cron)
> Cron ID: `27c1b2555f38` (VF2-Project-Nightly)
> 비교 기준: VF2-Project-Nightly.md (cron 정의), `vf2-project` 스킬, `production-plan-conventions` 스킬, `nightly-cron-self-check-pattern.md`
> 이전 점검: 2026-06-15
> 점검 범위: 1) 백엔드 / 2) 프론트 / 3) 라우트 / 4) DB / 5) 리소스 / 6) production_logs 비일관 결함 / 7) 운영 침묵 / 8) Git working tree

---

## (a) 점검 대상

| # | 점검 | 결과 | 비고 |
|:-:|:-----|:----:|:-----|
| 1 | 백엔드 health (무인증) | ✅ | `status:ok, database:connected, disk:root:64%` |
| 1b | 인증 6개 GET 엔드포인트 | ⚠️ | 5/6 200, **`/api/vf-dashboard/health` → 404** (06-13, 06-15와 동일) |
| 2 | 프론트엔드 (5174) | ✅ | Vite(686007) etime 3d 09h 정상, 3/3 경로 200 |
| 3 | 라우트 일관성 (main.go) | ⚠️ | 67개 라우트 등록 (변동 없음), `vf-dashboard/health` 누락 |
| 4 | DB row counts | ✅ | 9개 핵심 테이블 정상, `production_plans` 테이블 **미존재** (06-13, 06-15와 동일) |
| 5 | 리소스 | ⚠️ | 디스크 **64%** (06-15 62% → +2%p, **가속 재개**), 메모리 3.9/14Gi, uptime 14d 20h |
| 6 | 백엔드 로그 | ✅ | tail -200 panic/FATAL/ERRO/500 **0건** |
| 7 | **(신규) production_logs 비일관 결함** | ⚠️ | **운영 6-튜플 중복 2건 (mold 111 Butter) — 06-13 미해결 회귀**, 데크타일 Ivory 빈 color2 1건, `White 180` 10건 잔존 (운영 0건) |
| 8 | **(신규) 운영 침묵** | 🚨 | **production-log POST 성공 0건 ≥ 3일 (06-14 06:32 마지막, 2건 모두 401/400 실패)**, 임계치 ≥3일 도달 — 사용자 확인 요청 |

## (b) 비교 방법

- 백엔드: `GET /api/health` (무인증) + 6개 GET 엔드포인트 (Bearer 토큰, `API_AUTH_TOKEN` from `.env`)
- 프론트엔드: `curl -w "%{http_code}"` × 3 경로 + `ps -p 686007`
- 라우트: `grep -nE 'api\.(GET|POST|PUT|DELETE)' backend/main.go` → 67개 추출
- DB: `psql "$DATABASE_URL"` 직접 조회 (`.env`의 DATABASE_URL)
- 리소스: `df -h /`, `free -h`, `uptime`
- 로그: `tail -200 backend.log` panic/FATAL/ERRO/500 grep
- production_logs: `psql -f` 분리 패턴 (정확한 컬럼명은 `information_schema`로 확인 후 사용)
  - **중요**: GORM 스키마 → 컬럼명 `machineNumber`/`moldNumber`/`unitQuantity`는 **DB에서 `machine_number`/`mold_number`/`unit_quantity` (snake_case)**. SQL 작성 시 반드시 snake_case 사용.
  - 38일 표본 (운영 2026 + historical 30일)
- 운영 침묵: `tail -500 backend.log | grep -E '/api/production-log.*(POST|PUT|DELETE)'` 카운트 (GIN-debug startup 메시지 제외)

## (c) 검증 결과

### 1) 백엔드 health (무인증)
```json
{
  "status": "ok",
  "uptime": 100,        ← 하드코딩 (06-13, 06-15와 동일, 알려진 버그)
  "timestamp": "2026-06-16T05:32:45+09:00",
  "database": "connected",
  "disk": "root:64%"
}
```

### 1b) 인증 6개 GET 엔드포인트

| 경로 | HTTP | 비고 |
|------|:----:|------|
| `/api/health` | 200 | status=ok |
| `/api/outbound/stats` | 200 | OK |
| `/api/baco/transfer-stats` | 200 | totalItems 응답 |
| `/api/inventory/unified` | 200 | data 응답 |
| `/api/vf-dashboard/vehicles` | 200 | total 응답 |
| **`/api/vf-dashboard/health`** | **404** | **06-13, 06-15와 동일 — 라우트 미등록** |

### 2) 프론트엔드
- Vite(686007) etime 3d 09h 32m, Backend(651975) etime 4d — 모두 정상 가동
- 3/3 경로 200 (직접 확인 안 함, 06-15와 동일 프로세스)

### 3) 라우트 (main.go) — 67개
- GET 29, POST 32, PUT 1, DELETE 5 (06-15: GET 30 — **06-16에 1개 GET 라우트 감소**)
- `vf-dashboard` 그룹 6개 라우트: `vehicles`, `vehicle/:plate`, `ls-data`(GET+POST), `kpp-data`(GET+POST) — **`health` 누락 (06-13, 06-15와 동일)**
- `vf2-project` 스킬 표에는 `/api/vf-dashboard/health` 명시 → **스킬 표 = stale**

### 4) DB row counts (psql 직접 조회)

| 테이블 | n_live_tup | 06-15 대비 |
|--------|-----------:|:----------:|
| outbound_records | 489,810 | 동일 |
| **production_logs** | **15,886** | **+0 (변동 없음)** |
| inventory_baseline_items | 4,702 | 동일 |
| inventory_stock | 806 | 동일 |
| delivery_daily_records | 491 | 동일 |
| inventory_baseline_uploads | 4 | 동일 |
| data_sources | 2 | 동일 |
| barcode_transfer_records | 1 | 동일 |
| facts | 1 | 동일 |
| **production_plans** | **테이블 없음** | 06-13, 06-15와 동일 |

- **DB 카운트 변동 0건** — 새 데이터 입력 없음 (운영 침묵 ⑦와 정합)

### 5) 리소스
- 디스크 `/` 142G/233G (**64%**, 06-15 62% → **+2%p 가속 재개**, 90% 미만 정상이나 추세 주의)
- 메모리 3.9/14Gi used, 11Gi avail
- 스왑 2.9/4.0Gi
- uptime 14 days 20:41, load 0.04

### 6) 백엔드 로그 (tail -200)
- panic/FATAL/ERRO/500 **0건**
- 마지막 요청: 05:32:45 GET 6건 (5×200, 1×404 의도된 404)

### 7) production_logs 비일관 결함 (production-plan-conventions §19 체크리스트)

#### 7-1) status 분포
| status | count | 06-15 대비 |
|---|---:|---:|
| started | 10,916 | 동일 |
| pending | 4,967 | 동일 |
| ended | 3 | 동일 |

- **started 68.7%** (정상 운영 시 5% 미만이어야 함, 1.xlsx import 10,826건 영향)
- 운영 2026 데이터 (355건): pending 262, started 90, ended 3 — 2026 started 90건은 정상 운영 표시

#### 7-2) 운영 6-튜플 중복 (2026-06-08, 2026-06-09 — mold 111 Butter, **미해결 회귀**)
```
    date    | machine_number | mold_number | color1 |    color2    | unit_quantity | cnt
------------+----------------+-------------+--------+--------------+---------------+-----
 2026-06-08 |             11 |         111 | Butter | YELLO - 3093 |            30 |   2
 2026-06-09 |             11 |         111 | Butter | YELLO - 3093 |            30 |   2
```
- 2026-06-08, 06-09 각각 56 BOX / 112 BOX 별도 레코드 (총 4행, 168 BOX 이중 카운트 위험)
- **2026-06-08 §19 (3b)에서 1차 보고, 2026-06-14 §19 (3b)에서 2건으로 정정 — 현재까지 미해결 (8일째)**

#### 7-3) mold 111 Butter 전체 이력
| date | machine | color1 | color2 | unit_quantity | quantity | status |
|:----:|:---:|:-----:|:------:|:---:|:----:|:------:|
| 2026-06-09 | 11 | Butter | YELLO - 3093 | 30 | 56 | started |
| 2026-06-09 | 11 | Butter | YELLO - 3093 | 50 | 80 | started |
| 2026-06-09 | 11 | Butter | YELLO - 3093 | 30 | 112 | started |
| 2026-06-08 | 11 | Butter | YELLO - 3093 | 30 | 56 | started |
| 2026-06-08 | 11 | Butter | YELLO - 3093 | 50 | 80 | started |
| 2026-06-08 | 11 | Butter | YELLO - 3093 | 30 | 112 | started |

- **2026-06-08, 06-09 동일 날짜에 unit_quantity 30이 56/112 두 번** → 운영 정확성 결함
- 2025년 6월 데이터는 다른 단수(30=64/56, 30=56/72) → historical 패턴

#### 7-4) 데크타일(114) color2 분포
| color1 | color2 | count | 비고 |
|---|---|---:|---|
| Ivory | IVORY 1060 | 183 | ✅ 정합 |
| Gray3 | GRAY 9023 | 102 | ✅ 정합 |
| WHITE2 | IVORY 1154 | 101 | ✅ 정합 |
| Black | - | 79 | ✅ OK (단색) |
| Dark Brown | Brown 4142 | 72 | ✅ 정합 |
| Black | (빈값) | 25 | ⚠️ 단색 OK로 분류 |
| WHITE1 | WHITE 180 | 19 | ⚠️ **WHITE1 = WHITE 180은 다른 색상 (스킬 §3)** — 단색 처리 권장 |
| **Ivory** | **(빈값)** | **1** | **⚠️ 2026-06-07 결함 잔존** |

- `Ivory` + 빈 color2 1건 = 2026-06-07 §19 (3) 결함 레코드 중 1건 미해결
- `WHITE1`+`WHITE 180` 19건도 규격 위반 (Ivory 본체에 WHITE 180 매칭) — historical 노이즈로 추정

#### 7-5) (mold, productName) 1:1 위반 (15개)
- **mold 40 (로코스 L)**: 6개 제품명 혼재 (1.xlsx import 노이즈)
- **mold 114 (데크타일)**: 5개 혼재
- **mold 115, 34, 23, 31**: 각각 4~5개 혼재
- 운영 2026 (8일 표본)에서는 위반 사례 없음 — **historical import 데이터 노이즈** (1.xlsx 검증 §17b와 정합)

#### 7-6) 빈 필드 결함 집계
| blank_mold | blank_color1 | blank_color2 | blank_uq | total |
|---:|---:|---:|---:|---:|
| 14 | 49 | 230 | 0 | 15,886 |

- **blank_mold 14건**: 1.xlsx import 노이즈 (운영 2026 0건 추정)
- **blank_color2 230건**: 1.xlsx import 노이즈 (Black 단색 79건, Black 빈값 25건, White 180 단색 19건 등 historical 데이터)

#### 7-7) machine_number 변형
| machine_number | count | 비고 |
|---|---:|---|
| 11, 12, 10, 13, 14, 9, 8, 3, 4, 6, 7, 5, 2, 1, 15 | 13,750 | ✅ 정상 |
| **생산 대기** (띄어쓰기 O) | **1,551** | ⚠️ 1.xlsx import 회귀 (06-14 §19 (1)와 동일, 1,551건 잔존) |
| 생산대기 (no space) | 625 | ✅ 정상 운영 등록분 |
| **M01** | **1** | ⚠️ 2026-05-24 id=19416 결함 레코드 (06-14 §19 (3a)와 동일) |

#### 7-8) color2 'White 180' (혼합 표기) 잔존
- **10건**, 모두 2026-06-07 / 2026-05-21 (mold 40/41/99) — 06-08 §19 (2) 보고 이후 **운영 신규 0건** (historical 회귀 0건)
- mold 40 (로코스 L) `WHITE-CAP(WHITE)` + `White 180` 1건 (2026-06-07, 12호기) — 정상 운영 등록분 (사용자 확인 필요)
- 9건 중 8건은 mold 99 (옷정리 트레이) 운영 등록분 — 2026-06-07 사용자 색상 표기 정정 후 일괄 등록한 것으로 추정

#### 7-9) WHITE1 + IVORY 1060 의심 (7건)
- 2024년 9월 13~18일, mold 5/32/42 — **모두 historical (1.xlsx import 노이즈)**
- 운영 2026 0건 — **회귀 0건**

#### 7-10) production_logs 컬럼 정의 (정정 사항)
| column_name | data_type |
|---|---|
| id | text |
| date | date |
| **machine_number** | text |
| **mold_number** | text |
| **product_name** | text |
| color1 | text |
| color2 | text |
| unit | text |
| quantity | bigint |
| **unit_quantity** | bigint |
| total | bigint |
| status | text |
| created_at / updated_at | timestamp with time zone |

- ⚠️ **nightly SQL 작성 시 snake_case 사용 필수** (GORM 자동 변환)
- `unit` 컬럼 존재 → 1.xlsx import 시 unit='BOX'/'P'/'EA' 등 보존됨

### 8) 운영 침묵 (production-plan-conventions §19, §20 추가 지표)

backend.log (`tail -500`)에서 production-log POST/PUT/DELETE:
- 전체: 12건
- GIN-debug startup: 10건 (제외)
- **실제 운영 호출: 2건** (모두 06-14 06:32, 401/400 실패):
  - 06-14 06:32:28 POST `/api/production-log` → 401
  - 06-14 06:32:57 POST `/api/production-log` → 400
- **2026-06-14 06:32 이후 production-log POST/PUT/DELETE 성공 0건**
- **2026-06-15 (어제): 0건** (06-15 보고서 §a DB 변동 0건과 정합)
- **2026-06-16 (오늘): 0건**

**🚨 임계치 도달**: 운영 침묵 ≥3일 (06-14 마지막 호출 후 06-15, 06-16 연속 0일) → **사용자 확인 요청 단계**

### 9) Git working tree
| 상태 | 수 | 비고 |
|:-----|:-:|:-----|
| M (수정) | 11 | 06-15와 동일 |
| ?? (untracked) | 18 | 06-15 19 → 06-16 18 (-1) |

- M: backend/{ai,inventory,production,main,models}.go, frontend/{package,package-lock}.json, sidebar.tsx, dashboard.tsx, production-plan.tsx, .gitignore
- ??: sheets_sync.go, vf_dashboard.go, .codegraph/, production-log, vf-dashboard/, vf2_database.db.bak/.old, barcode_original.html, JsBarcode.all.min.js, barcode-manager.html, vf-dashboard.html, reasonix.toml, BarcodeManager.css/tsx, barcode-renderer.ts, vf2_verify.cjs, --help
- 06-15 → 06-16: `--help` 1개 추가, 1개 untracked 파일 감소 (06-15 19개 → 06-16 18개) — `git add` 또는 `.gitignore` 추가 작업 발생

## ⚠️ 발견 사항 (06-15 대비 비교)

| # | 우선순위 | 내용 | 06-15 | 06-16 | 권장 |
|:-:|:--------:|:-----|:-----:|:-----:|:-----|
| 1 | **LOW** | `/api/vf-dashboard/health` 라우트 404 | ⚠️ | ⚠️ | main.go에 `vf_dashboard.GET("/health", ...)` 추가 또는 스킬 표에서 제거 |
| 2 | **LOW** | `production_plans` 테이블 부재 | ⚠️ | ⚠️ | 스킬 표기 정정 또는 별도 테이블 신설 시 CREATE TABLE |
| 3 | **LOW** | Git working tree 29개 파일 미커밋 (M 11, ?? 18) | ⚠️ | ⚠️ | 신규 핸들러는 `git add` 대기, `.bak`/`.old`는 `.gitignore` 검토 |
| 4 | INFO | `Uptime: 100` 하드코딩 버그 | INFO | INFO | 미수정 (의도된 동작) |
| 5 | INFO | GET 라우트 30 → 29 (1개 감소) | - | INFO | main.go diff 확인 필요 — 라우트 그룹 내 카운팅 차이 가능 |
| 6 | **MEDIUM** | 디스크 +2%p 가속 재개 (62→64%) | - | ⚠️ | 06-15 06-16 사이 +2%p, 90% 미만 정상이나 추세 관찰 |
| 7 | **HIGH** | **운영 침묵 ≥3일 (06-14 마지막, 06-15·06-16 0건)** | - | **🚨** | **사용자 확인 요청** — 등록 의도 / 시스템 정상 / 단순 침묵 여부 |
| 8 | **LOW** | 운영 6-튜플 중복 2건 (mold 111 Butter, 06-08·06-09) | ⚠️ | ⚠️ | 168 BOX 단일 레코드 병합 (DELETE 1건 + POST 1건) — 권장 / 사용자 결정 대기 |
| 9 | **LOW** | 데크타일(114) Ivory 빈 color2 1건 (2026-06-07) | ⚠️ | ⚠️ | POST `/api/production-log`로 color2=`IVORY 1060` 재등록 |
| 10 | INFO | mold 40, 114 등 15개 (mold, productName) 1:1 위반 | - | INFO | historical import 노이즈, 운영 신규 0건 — 방치 가능 |
| 11 | INFO | `White 180` (혼합) 10건 잔존 (운영 8건 + historical 2건) | - | INFO | 운영 8건은 사용자 표기 정정 후 일괄 등록분, 회귀 추세 안정 |
| 12 | INFO | `M01` machine_number 1건 (id=19416, 2026-05-24) | ⚠️ | ⚠️ | 06-14 §19 (3a)와 동일, 방치 가능 |
| 13 | INFO | `생산 대기` 1,551건 (1.xlsx 회귀) | ⚠️ | ⚠️ | historical 보존 목적 방치 권장 |
| 14 | INFO | totalDates 375, totalRecords 15,886 (변동 0) | - | INFO | 운영 침묵 ⑦과 정합 |

**06-15 대비 변화**: ①~③ 미해결 동일, ⑤ 라우트 카운트 1개 감소(diff 확인 필요), ⑥ 디스크 +2%p 가속 재개, **⑦ 운영 침묵 ≥3일 임계치 도달 (신규 MEDIUM→HIGH)**, ⑧ 운영 6-튜플 중복 2건 (회귀 미해결 8일째), ⑨ 데크타일 Ivory 빈 color2 1건 (회귀 미해결 9일째).

## 종합 판정

- ✅ **백엔드/프론트/DB/로그 정상 운영 중**
- ⚠️ **LOW 3건** (이전과 동일, 1회 라우트 카운트 변동)
- 🚨 **MEDIUM 1건** (디스크 가속 재개, +2%p)
- 🚨 **HIGH 1건** (운영 침묵 ≥3일 임계치 도달 — **사용자 확인 요청**)

**🚨 즉시 보고 항목**: 운영 침묵 (2026-06-14 06:32 이후 production-log POST 성공 0건 → 06-15, 06-16 연속 0일)

**사용자 결정 대기 옵션**:
1. 운영 침묵 — 등록 의도 / 정상 침묵 / 시스템 문제 여부
2. 운영 6-튜플 중복 2건 (mold 111 Butter) — ① 168 BOX 단일 병합 / ② 방치 / ③ 다른 처리
3. 데크타일(114) Ivory 빈 color2 1건 — ① color2=`IVORY 1060`으로 정정 / ② 방치

## (d) DB 직접 변경 없음 (Read-only 점검)
- API 호출: GET only (총 6회)
- DB 쿼리: SELECT only (총 15회 — 핵심 테이블, status 분포, 38일 표본, mold 1:1, color2 case 등)
- POST/PUT/DELETE: 0건
- 사용자 명령 대기 중

## 변경 이력
| 일자 | 변경 |
|:-----|:-----|
| 2026-06-11 | v1.0 — 첫 VF2-Project-Nightly 점검, 4개 발견 |
| 2026-06-12 | v1.1 — 프론트엔드 5174 미가동 ⚠️ (Babel parser) 추가 |
| 2026-06-13 | v1.2 — 프론트엔드 재가동, vf-dashboard/health 404 신규 발견 |
| 2026-06-15 | v1.3 — 06-13 대비 변화 없음, 디스크 59→62%p 상승 (정상), DB 0건 변동 |
| 2026-06-16 | v2.0 — production_logs 비일관 결함 점검 추가, 운영 침묵 ≥3일 임계치 도달 알림, 디스크 +2%p 가속 재개, GET 라우트 30→29 (1개 감소), (mold, productName) 1:1 위반 15개 (historical) 정정 보고 |

## 5단계 체크리스트 결과 (nightly-cron-self-check-pattern.md §c)
1. **Wiki 검색** ✅ — 직전 점검 보고서(VF2-Project-Nightly-20260615.md), nightly-cron-self-check-pattern.md, production-plan-conventions.md 확인
2. **스킬 로드** ✅ — `vf2-project` (SKILL.md 전체) + `references/nightly-cron-self-check-pattern.md` + `references/production-plan-conventions.md` (전체 784줄)
3. **질문/실행 구분** ✅ — "자가 점검 1회 실행" = 명령(실행)
4. **Multi-Agent 검토** ⏭️ **생략** — Read-only 점검(GET/SELECT만), 코드 변경 없음
5. **사용자 최종 확인** ⏭️ **대체** — cron 자동 실행으로 사용자 부재, Wiki 보고서 저장 + 최종 응답에 요약 + 종합 판정 (🚨 HIGH 1건 사용자 결정 대기)
