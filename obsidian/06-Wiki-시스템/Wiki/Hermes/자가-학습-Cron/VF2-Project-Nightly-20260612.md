# VF2 Project Nightly — 2026-06-12 자가 점검 결과

> 점검 시각: 2026-06-12 06:31 KST (cron)
> Cron ID: `27c1b2555f38` (VF2-Project-Nightly)
> 비교 기준: VF2-Project-Nightly.md (cron 정의), 2026-06-11 점검 결과
> 점검 범위: 1) 백엔드 / 2) 프론트 / 3) 라우트 / 4) DB / 5) 리소스
> 단계 0 베이스파일: SOUL.md(`/home/comtop/workspace/Wiki/SOUL.md` + `/home/comtop/.hermes/SOUL.md`) / USER.md / MEMORY.md 모두 로드 완료.

---

## (a) 점검 대상

| # | 점검 항목 | 방법 | 비고 |
|:-:|:---------|:-----|:-----|
| 1 | 백엔드 API (5176) | `GET /api/health` + 7개 인증 엔드포인트 | uptime 하드코딩 버그 미해결 |
| 2 | 프론트엔드 (5174) | `curl http://localhost:5174/` + `ps` | **Vite dev 서버 미가동 ⚠️** |
| 3 | POST 라우트 | `main.go` `api.(GET/POST/PUT/DELETE)` 패턴 매칭 | 67개 라우트 (변동 없음) |
| 4 | DB | 4개 핵심 엔드포인트로 데이터 검증 | outbound vf 1,035,944 정상 |
| 5 | 시스템 리소스 | `df -h /`, `free -h`, `uptime` | 디스크 56%, 메모리 26%, 부하 0.00 |

---

## (b) 비교 방법

1. `python3`+`subprocess`+`curl`로 인증 헤더(`Authorization: Bearer *** `) 구성, GET-only로 7개 엔드포인트 조회
2. `grep -E "api\.(GET|POST|PUT|DELETE)" backend/main.go`로 라우트 등록 67개 추출
3. `ps -eo pid,etimes,cmd`로 vite/backend 프로세스 확인
4. `/api/inventory/unified` `/api/delivery/hourly` `/api/outbound/stats` `/api/baco/transfer-stats` 응답 카운트 비교
5. `ss -tlnp`로 Listen 포트 (5174/5176/5432) 확인
6. `df -h /`, `free -h`, `uptime`로 리소스 스냅샷

---

## (c) 검증 결과

### 1️⃣ 백엔드 API (port 5176)

| 엔드포인트 | HTTP | 결과 |
|:----------|:----:|:-----|
| `GET /api/health` (무인증) | **200** | `{status: ok, uptime: 100, database: connected, disk: root:56%}` |
| `GET /api/outbound/stats` | 200 | vf=1,035,944 / delivery=0 / 카테고리 48개 |
| `GET /api/production?date=2026-06-11` | 200 | items 정상 |
| `GET /api/baco/transfer-stats` | 200 | 1건 (test-route-003, ROUTE-WORKS) |
| `GET /api/inventory/unified` | 200 | items=**804**, lastUpload=2026-06-10T10:42:34 |
| `GET /api/delivery/hourly` | 200 | rows=**361**, 범위 2025-06-12 ~ 2026-06-10 |
| `GET /api/delivery/daily-prediction` | 200 | hourly_predictions 2026-06-12 정상 |
| `GET /api/vf-dashboard/vehicles` | 200 | total=138 |

✅ **7/7 엔드포인트 정상 응답 (200)**, 인증 토큰 OK

### 2️⃣ 프론트엔드 (port 5174)

| 항목 | 값 |
|:-----|:--|
| 프로세스 (`ps -eo pid,etimes,cmd \| grep -E "vite\|node"`) | **vite 프로세스 0건** ⚠️ |
| HTTP `curl http://localhost:5174/` | HTTP 000 (연결 실패) |
| 5174 포트 Listen (`ss -tlnp`) | **Listen 안 함** |
| `dist/` 빌드 산출물 | 존재 (JsBarcode.all.min.js, assets/, barcode-manager.html, vf-dashboard.html) |
| `dev_server.log` 마지막 정상 HMR | **21:52:23 PM** (어제) |

⚠️ **Vite dev 서버 중단 — 어제 21:52:23 PM 이후 Babel parser 에러로 사망**:
- `dev_server.log` 끝부분에 `@babel/parser` `TypeScriptParserMixin.parseExprOp` `parseExprOps` 스택트레이스 다수
- 첫 18-21라인에는 `Error: connect ECONNREFUSED 127.0.0.1:5176` (백엔드 의존성 에러)도 잔존
- 단, `dist/` 빌드 산출물은 유지되고 있어 정적 페이지 직접 서빙은 가능

**프로세스 (백엔드만 가동 중):**
| PID | ETIME | CMD |
|----:|------:|:----|
| 651975 | 3564초 (≈59분) | `./vf2_backend_bin` (port 5176 LISTEN) |

### 3️⃣ 라우트 점검 (main.go)

| 메서드 | 라우트 수 | 비고 |
|:------|----------:|:-----|
| GET | 29 | |
| POST | 32 | |
| PUT | 1 | `/api/master/specs/:id` |
| DELETE | 5 | |
| **합계** | **67** | 어제와 동일 |

**README drift (14개 추정 유지, 어제와 동일)** — 라우트 등록 수 변동 없음, 신규 추가 없음

### 4️⃣ DB

| 엔드포인트 | 데이터 | 비고 |
|:----------|:------|:-----|
| `outbound_stats.vf.totalQuantity` | **1,035,944** | 어제 1,035,944와 동일 |
| `outbound_stats.delivery.totalQuantity` | 0 | 정상 (delivery 데이터 미수집) |
| `inventory_unified.data` | 804 items | lastUpload 2026-06-10 |
| `delivery_hourly.data` | 361 rows | 2025-06-12 ~ 2026-06-10 |
| `baco.transfer-stats` | 1 raw, 1 data | test-route-003 (2026-06-07 등록) |
| `vf-dashboard.vehicles.total` | 138 | |

⚠️ **DB 직접 조회 미실행** — `psql` 인증이 마스킹된 `.env` 패스워드 불일치로 실패. 백엔드 `database: connected` 응답과 7개 엔드포인트 정상 응답으로 DB 가용성만 검증.

### 5️⃣ 리소스

| 항목 | 값 | 판정 |
|:-----|:--|:----:|
| 디스크 `/` | 56% (123G/233G 사용) | ✓ (어제 54% → +2%p) |
| 메모리 | 3.7G/14G (26%) | ✓ (어제 30% → -4%p) |
| 스왑 | 측정 미실행 | (어제 92% 경고) |
| 부하 (load avg) | 0.00 / 0.00 / 0.00 | ✓ |
| 가동 시간 | 10 days 21:40 | ✓ |

---

## ⚠️ 발견 사항 (사용자 확인 필요)

### ① 프론트엔드 Vite dev 서버 중단 (HIGH)

- **증상**: 5174 포트 Listen 안 함, vite/node 프로세스 0건
- **시점 추정**: 어제 21:52:23 PM 마지막 정상 HMR → 그 후 Babel parser 에러로 죽음
- **에러 단서**: `dev_server.log` 끝부분 `@babel/parser` `TypeScriptParserMixin.parseExprOp` 호출 스택, 그리고 시작 부분 `ECONNREFUSED 127.0.0.1:5176` (백엔드 의존)
- **영향**: 사용자가 브라우저로 5174 진입 시 빈 페이지 또는 vite 클라이언트 미연결 화면
- **완화**: `dist/` 산출물은 유지 → 정적 빌드 직접 서빙 가능 (단, HMR/HMR-기반 디버깅 불가)
- **조치 필요**: `npm run dev` 재기동 또는 코드 변경 사항 점검
- **권장**: ① dist/ 정적 서빙 전환 ② `npm run dev` 재기동 (백엔드 의존성 점검 후) ③ 변경된 .tsx 파일 (sidebar/dashboard/production-plan) Babel 파싱 검증

### ② `/api/health` Uptime 하드코딩 버그 (HIGH, 어제 미해결)

- 어제 06-11 점검에서 발견한 동일 이슈, **아직 패치되지 않음**
- 실제 가동 59분 / 응답 uptime=100초 — 거짓 보고 지속
- 헬스체크 모니터링에 사용 시 오판 위험

### ③ Git working tree 22개 파일 미커밋 (LOW, 어제와 동일)

| 상태 | 파일 | 비고 |
|:-----|:-----|:-----|
| M (10) | `backend/{handlers/ai,inventory,production,main}.go`, `models/models.go`, `frontend/{package*.json, sidebar.tsx, dashboard.tsx, production-plan.tsx}`, `.gitignore` | |
| ?? (12) | `--help`, `.codegraph/`, `backend/handlers/{sheets_sync,vf_dashboard}.go`, `backend/{production-log,vf-dashboard/}`, `backend/vf2_database.db.{bak,old}`, `frontend/.codegraph/`, `frontend/public/{JsBarcode.all.min.js,barcode-manager.html,vf-dashboard.html}`, `frontend/reasonix.toml`, `barcode_original.html` | 어제와 동일 목록 |

- **핸들러 신규 2개 (`sheets_sync.go`, `vf_dashboard.go`)는 `git add` 대기**
- **DB 백업 파일 2개** (`.bak` `.old`)는 `.gitignore` 검토 필요
- 프론트엔드 `dist/` 정적 산출물 3개도 untracked — `.gitignore` 검토 필요

### ④ README ↔ 라우트 drift 14개 (LOW, 어제와 동일 추정)

- 신규 라우트 추가 없음 → drift 14개 그대로

### ⑤ 변경/이슈 없음 영역

- 백엔드 7/7 엔드포인트 200 OK
- DB 카운트 변동 없음 (outbound vf 1,035,944 동일)
- 디스크/메모리/부하 모두 정상 범위

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
| 2026-06-12 | v1.1 — 프론트엔드 5174 미가동 ⚠️ 추가 (Babel parser 에러로 추정). ①~④ 4건 + ⑤(프론트) 신규. 어제 ②~④ 이슈 미해결 상태 유지 |
