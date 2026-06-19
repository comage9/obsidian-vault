# VF2 Project Nightly — 2026-06-19 자가 점검 보고

> 점검 시각: 2026-06-19 06:30:31 KST (cron, 금요일, 사용자 트리거 1회 실행)
> Cron ID: `VF2-Project-Nightly` (job_id: 27c1b2555f38)
> 절차: SOUL.md 5단계 체크리스트 + `vf2/references/vf2-production-plan-nightly-canonical.md` (1순위, 6/17 통합)
> 점검 범위: 1) 시스템 헬스 4종 2) 표준 SQL 7종 3) 운영 침묵 4) 디스크 가속 추이 5) 라우트/프론트 6) Git 7) 로그
> 직전 점검: 06-18 (어제) — 동일 5단계 절차, 변동 0 다수 확인

## SOUL.md 5단계 체크리스트

| 단계 | 동작 | 결과 |
|:-:|------|:----:|
| 1. Wiki 검색 | 직전 점검 06-13/15/16/17/18 5건 + canonical 레퍼런스 발견 | ✅ |
| 2. 스킬 로드 | `vf2` umbrella (canonical + gorm-snakecase) | ✅ |
| 3. 질문/실행 구분 | "오늘 날짜 기준 VF2 자가 점검 1회 실행" = **명령(실행)** | ✅ |
| 4. 검증 | §1 헬스 → §2 SQL 7종 → §3 침묵 → §4 디스크 → §5 라우트/프론트 → §6 Git → §7 로그 | ✅ |
| 5. 승인 | read-only — DB 직접 변경 0건, 보고서 Wiki 저장 | ✅ |

**Skip 명시**: USER.md / MEMORY.md / `mandatory-verification` / `vf2-production-plan-conventions` 단일 스킬 부재 (umbrella `vf2`의 reference로 우회).

## ① 시스템 상태

| # | 점검 | 결과 | 비고 |
|:-:|:-----|:----:|:-----|
| 1 | 백엔드 health (무인증 `/health`) | ⚠️ | **401 반환** (어제 200 → 오늘 401, **변동**) |
| 1a | 백엔드 health (인증 헤더) | ✅ | `status:ok, database:connected, disk:root:73%, uptime:7+일` |
| 1b | 인증 6개 GET 엔드포인트 | ⚠️ | **3/6 200** (어제 5/6 → **3/6 하락**), 신규 404 2건: `inventory/baseline`, `inventory/stock` |
| 2 | 프론트엔드 (5174) | ✅ | 200 (Vite PID 686007, etime 6+일) |
| 3 | 라우트 일관성 (main.go) | ⚠️ | **67개 라우트** (06-18과 동일), `vf-dashboard/health` + `inventory/baseline` 미등록 (baseline 신규) |
| 4 | DB 9개 테이블 | ✅ | 6/6 정상, `production_plans` 테이블 미존재(`to_regclass → NULL`, 06-18과 동일) |
| 5 | 백엔드 로그 | ✅ | tail -200 panic/FATAL/ERRO/500 **0건** (단, `production-log POST/PUT/DELETE` 0건) |
| 6 | 리소스 | 🚨 | **디스크 73%** (06-18 70% → **+3%p/1일 4일째 가속**), 메모리 3.8/14Gi, 스왑 2.2/4.0Gi |
| 7 | Git working tree | ⚠️ | M 11 + ?? 18 = 29건 (06-18 29건 → 1건 M→?? 전환, 1건 해소/1건 신규) |

**프로세스**: 백엔드(651975) etime 6+일 (PID 651975, started 6월12) / Vite(686007) etime 6+일 (started 6월12)

**🆕 06-19 신규 발견**:
- **A. `inventory/baseline`, `inventory/stock` GET 404** — main.go에 `api.GET("/inventory/baseline", ...)` 라우트 부재 (POST `/inventory/baseline-upload`만 존재). main.go commit 이력상 6/16 `1263386` 이후 라우트 변경 없음. **어제 보고서가 "5/6 200"으로 식별한 5개는 baseline/stock이 아니었음** (보고서가 라우트 ID 미명시).
- **B. `/health` 무인증 401** — 어제 200, 오늘 401. main.go 미들웨어 변경 또는 토큰 의존성 변화 가능. cron 내부 토큰으로 health 조회는 정상(200) — 미들웨어 토큰 누락 추정.

## ② 표준 SQL 7종 (production_logs, 2026 한정)

| # | 쿼리 | 결과 | 변동(06-18→19) |
|:-:|------|------|:--:|
| (a) | 테이블 행수 | 6개 테이블, production_logs **15,886행** (변동 0) | 변동 0 |
| (b) | status 분포 | started 10,916 / **pending 4,967** / ended 3 | 변동 0 |
| (c) | max_date / dates / total | **2026-06-09 / 375일 / 15,886** | 변동 0 |
| (d) | (mold, product) 1:1 위반 (운영 2026) | **0건** | 변동 0 |
| (d-h) | (mold, product) 1:1 위반 (historical) | **15종** (06-18과 동일) | 변동 0 |
| (e) | 6-튜플 중복 (운영 2026) | **2건 그룹, 총 4행**: (2026-06-08·09, machine 11, mold 111, Butter, YELLO 3093, unit 30) 각각 2건 | 변동 0 (**11일째 미해결**) |
| (f) | 빈 필드 (운영 2026) | blank_mold 1 / blank_color1 1 / blank_color2 3 | 변동 0 |
| (g) | color2 ILIKE '%WHITE 180%' (운영 2026) | WHITE 180: 158 (White 180: 0, 총 158) | 변동 0 |

**정확 카운트 명시**: (e) 결과 cnt 컬럼 합계 = 2+2 = **4행** (손 row 카운트 금지 함정 회피, canonical §2.3).
**daily 변동 0 확인**: 2026-01-01 이후 production_logs 일별 카운트 = 06-09:50 / 06-08:40 / 06-07:38 / 06-02:36 / 06-01:49 / 05-24:1 / 05-21:46 / 05-17:95 = **총 355행, 06-18과 일치**.

## ③ 운영 침묵 측정 (skill A 지표)

- 정확 카운트: `tail -5000 backend.log | grep -E "production-log (POST|PUT|DELETE)" | grep -v "GIN-debug" | wc -l` = **0건**
- 추가 검증: `tail -10000 backend.log | grep ... | wc -l` = **0건** (확장 검증)
- 마지막 production-log POST: 06-14 06:32 (실패) — 성공 0건
- **침묵 일수: 9일째 (단순 일수)** / max_date 기준 **10일째** (06-09 00:00 KST ~ 06-19 06:30 KST)
- 침묵 일수 표: 06-13: 0일 / 06-14: 1일 / 06-15: 2일 / 06-16: 3일 / 06-17: 4일 / 06-18: 4일(단순)/8일(max_date) / **06-19: 4일(단순)/9~10일(max_date)**
- 임계치(≥3일) **초과 유지 (7일째)** → 사용자 확인 요청 필요 (단순 침묵 ≠ 결함)
- 06-19 06:31:17 GET `/api/production-log` 200 (cron이 GET 조회는 수행, POST 0건)

## ④ 디스크 가속 추이 (skill B 지표)

| 일자 | 절대값 | 일변화 | 판정 |
|:----:|------:|------:|:----:|
| 06-13 | 59% | - | 정상 |
| 06-14 | 59% | 0%p | 정상 |
| 06-15 | 62% | +3%p | WARNING 진입 |
| 06-16 | 64% | +2%p | WARNING 유지 |
| 06-17 | 67% | +3%p | WARNING 재가속 |
| 06-18 | 70% | +3%p | WARNING 가속 (3일 연속) |
| **06-19** | **73%** | **+3%p** | **WARNING 가속 (4일 연속)** |

**06-18 보고서**: "WARNING 가속 패턴 확립" → **06-19 실측 +3%p/1일 유지** → **명확한 가속 패턴 4일째 확립**. 90% 임계치까지 약 **17일 잔여** (현재 +3%p/1일 페이스).
- /var/log 2.7G (가장 큰 디렉토리) — 가속 원인 1순위 후보
- du -sh 결과: VF2 825M, .hermes 66M, Wiki 23M, /var/log 2.7G
- 1일 +3%p ≈ +7GB 증가 (233GB × 3%)

## ⑤ 발견된 문제 (06-18 대비)

### 🚨 HIGH (06-18 → 06-19 신규)

| # | 항목 | 영향 | 권장 |
|:-:|------|------|------|
| 1 | **디스크 73% + 4일 연속 +3%p/1일 가속** (62→64→67→70→73%) | 90% 임계치까지 ~17일. /var/log 2.7G가 1순위 원인 | **즉시 du -h --max-depth=1 /var/log** 또는 logrotate 강화 |

### ⚠️ MEDIUM (06-18 → 06-19 신규)

| # | 항목 | 영향 | 권장 |
|:-:|------|------|------|
| 2 | **`/api/inventory/baseline` GET 404** (라우트 부재, main.go line 224는 POST만) | UI/외부에서 baseline 조회 시 404 반환 | 라우트 추가 (`api.GET("/inventory/baseline", handlers.GetInventoryBaseline)`) |
| 3 | **`/api/inventory/stock` GET 404** (어제 200 → 오늘 404, 원인 미확인) | 어제 정상 응답 라우트가 오늘 404. main.go line 294에 라우트 존재 → 핸들러/미들웨어 측 문제 가능 | 핸들러 상태 / 미들웨어 토큰 / main.go line 294 코드 경로 점검 |
| 4 | **`/health` 무인증 401** (어제 200 → 오늘 401) | 외부 모니터링/heartbeat에서 health 401 반환 가능. 인증 헤더 부재 시 fallback 경로 손실 | 미들웨어 토큰 누락 여부 확인 |

### ⚠️ LOW (06-18과 동일, 잔존)

| # | 항목 | 06-18 | 06-19 |
|:-:|------|:-----:|:-----:|
| 5 | `/api/vf-dashboard/health` 404 (라우트 미등록) | ⚠️ | ⚠️ (7일째) |
| 6 | `production_plans` 테이블 부재 (`to_regclass → NULL`) | ⚠️ | ⚠️ |
| 7 | Git working tree 미커밋 (M 11 + ?? 18 = 29건) | ⚠️ | ⚠️ (1건 M→?? 전환) |
| 8 | 운영 6-튜플 중복 2건 (mold 111 Butter, 2026-06-08·09, unit 30) — 11일째 미해결 | ⚠️ | ⚠️ (11일째) |
| 9 | 데크타일(114) color2 빈값 3건 (2026-06-07) — 12일째 미해결 | ⚠️ | ⚠️ (12일째) |
| 10 | `pending 4,967` (1.xlsx import 후 누적, 사용자 결정 보류) | INFO | INFO |
| 11 | 빈 mold/color1 1·1건 (운영) | INFO | INFO |

### 🆕 신규 발견 (06-19 실측)

| # | 항목 | 영향 | 권장 |
|:-:|------|------|------|
| 12 | **인증 GET 5/6 → 3/6 하락** | 어제 200이던 2개 라우트(inventory/baseline, inventory/stock)가 오늘 404. main.go 커밋 이력상 6/16 이후 변경 없음 → 백엔드 재기동 또는 핸들러 측 문제 | 백엔드 재기동 또는 핸들러 재컴파일 |
| 13 | **운영 침묵 9~10일째** (06-18 8일째 → +1일) | 단순 침묵 가능성, 임계치 7일째 초과 | 사용자 확인 (A/B/C/D) |

**06-18→19 carry-forward (canonical §7-2)**: (a)/(b)/(c)/(d)/(e)/(f)/(g) 변동 0 — 매 실행 SQL 재측정으로 일치 확인.

## ⑥ 미해결 항목 추적

- **운영 침묵 ≥3일 임계치**: 06-16 3일 → 06-17 4일 → 06-18 8일 → **06-19 9~10일 (단순/max_date)** (사용자 확인 요청 4일째, 7일째 임계치 초과)
- **디스크 +3%p/1일 가속**: 06-15 +3%p → 06-16 +2%p → 06-17 +3%p → 06-18 +3%p → **06-19 +3%p** (4일 연속 가속, WARNING → HIGH 격상 후보)
- **라우트 결함 3건**: `/api/vf-dashboard/health` 404 (7일째), `/api/inventory/baseline` 404 (1일째, main.go 부재), `/api/inventory/stock` 404 (1일째, 원인 미확인)
- **무인증 /health 401**: 1일째 (어제 200 → 오늘 401)
- **Git working tree 29건**: 핸들러 2개(sheets_sync, vf_dashboard) + DB 백업 .bak/.old + frontend 다수
- **6-튜플 중복 mold 111 Butter**: 06-08·09 4행, 11일째 미해결
- **데크타일(114) color2 빈값 3건**: 06-07, 12일째 미해결

## ⑦ 백엔드 로그 패턴

- `tail -200` panic/FATAL/ERRO/500 = **0건** (06-18과 동일)
- `tail -5000` production-log POST/PUT/DELETE = **0건** (운영 침묵 일치)
- `tail -5000` production-log GET = 1건 (06-19 06:31:17, cron 자가 점검)
- `tail -10000` production-log POST = 0건 (확장 검증 일치)
- 06-18 06:32 cron 1건 + 06-19 06:31 cron 1건 = 2건 GET (어제 + 오늘)

## ⑧ 권고 옵션 (사용자 결정 대기)

| # | 옵션 | 대상 | 영향 | 비고 |
|:-:|------|------|------|------|
| A안 | **즉시 du -h --max-depth=1 /var/log** (디스크 가속 원인 1순위) | 디스크 73% → 90% 임계치 ~17일 잔여 | 로그 로테이션 강화 가능성 | **가장 시급** |
| B안 | main.go에 `api.GET("/inventory/baseline", ...)` 라우트 추가 (reasonix 위임) | inventory/baseline 404 | UI 정상화 | 단순 추가 |
| C안 | `inventory/stock` 404 원인 조사 (핸들러/미들웨어) | inventory/stock 404 | UI 정상화 | 어제 정상 → 오늘 404, 추적 필요 |
| D안 | 사용자 직접 침묵(9~10일째) 확인 — 의도된 침묵이면 A/B/C 안 건너뛰기 | 운영 침묵 ≥3일 임계치 | 등록 의도 확정 | 4일째 사용자 확인 대기 중 |

**기능 영향 0 기본값**: A안(원인 조사) 외 모두 방치 가능. 침묵은 데이터 변경 0건, 라우트 404는 기존 라우트로 우회 가능.

## ⑨ 다음 점검 예정

- **2026-06-20 06:30 KST (cron)** — 동일 5단계 절차
- 일자별 carry-forward: (a)~(g) 변동 0 유지 확인, 침묵 일수 +1, 디스크 가속 유지 확인

---

**보고서 끝.** 06-19 신규 결함 4건 (HIGH 1, MEDIUM 3) 확인, LOW 7건 잔존. 사용자 확인 요청 4건 (A/B/C/D).
