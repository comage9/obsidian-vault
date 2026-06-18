# VF2 Production Plan Nightly — 2026-06-19 자가 점검 보고

> 점검 시각: 2026-06-19 05:31 KST (cron, 금요일)
> Cron ID: `48144ff13cee` (VF2 Production Plan Nightly, 05:30 KST)
> 절차: SOUL.md 5단계 체크리스트 + `vf2/references/vf2-production-plan-nightly-canonical.md` (1순위) + `vf2/references/production-plan-conventions.md` §19·§20 (2순위) + `vf2/references/gorm-snakecase-columns-20260616.md` (snake_case)
> 비교: 직전 VF2-Production-Plan-Nightly-20260618.md

## SOUL.md 5단계 체크리스트

| 단계 | 동작 | 결과 |
|:-:|------|:----:|
| 1. Wiki 검색 | `session_search` + `search_files`로 직전 보고서 `VF2-Production-Plan-Nightly-20260618.md` (06-18 05:31) + `production-plan-conventions.md` canonical 발견 | ✅ |
| 2. 스킬 로드 | `vf2-production-plan-conventions` 단일 스킬 부재 → `vf2` umbrella + references 우회 로드 | ⚠️ Skip (단일) |
| 3. 질문/실행 구분 | "자가 점검 1회 실행" = **명령(자동 실행)** | ✅ |
| 4. 검증 | §1 시스템 → §2 SQL 7종 → §3 침묵 → §4 디스크 → §5 machine 비일관 | ✅ |
| 5. 승인 | read-only cron → DB 직접 변경 0건, 보고서 Wiki 저장 + log.md + Git push | ✅ |

**Skip 명시**:
- `vf2-production-plan-conventions` 단일 스킬 부재 (job invocation에서 시스템이 not found로 통지)
- `mandatory-verification` 스킬 부재 (skill_view 시도 시 not found)
- → **우회**: `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md` (1순위) + `references/production-plan-conventions.md` (2순위) + `references/gorm-snakecase-columns-20260616.md` (snake_case)

**환경 노트**:
- DB 비밀번호 마스킹(`***` 자동 처리) — `set -a; . .env; set +a`로 DATABASE_URL 주입 후 psql 직접 연결
- DB: PostgreSQL, vf2_db, hermes 사용자
- 백엔드 PID 651975 가동 중, PostgreSQL 연결 정상

## ① 시스템 상태

| # | 점검 | 06-18 | **06-19** | 변동 | 비고 |
|:-:|:-----|:-----:|:---------:|:----:|:-----|
| 1 | DB 연결 (PostgreSQL) | ✅ | ✅ | 0 | `database: connected, uptime: 100` |
| 2 | 백엔드 프로세스 | ✅ | ✅ | 0 | PID 651975, ./vf2_backend_bin 가동 중 |
| 3 | 디스크 `/` | 70% | **73%** | +3%p | **WARNING 4일 연속 +3%p/1일 가속 유지** |
| 4 | 메모리 | OK | OK | 0 | 3.8G 사용 / 11G 가용 |
| 5 | DB 9 테이블 | 9/9 | 9/9 | 0 | `outbound_records 489,810 / production_logs 15,886 / ...` |
| 6 | `production_plans` 존재 | NULL | NULL | 0 | `to_regclass → NULL`, 1.xlsx import 누락 단서 잔존 |
| 7 | 운영 침묵 | 9일째 | **10일째** | +1일 | max_date 06-09 미변동, 06-10~06-19 production-log POST 0건 |

## ② 표준 SQL 7종 (production_logs, 2026 한정)

| # | 쿼리 | 06-18 | **06-19** | 변동 |
|:-:|------|:-----:|:---------:|:----:|
| (a) | total / dates / max_date | 15,886 / 375 / 2026-06-09 | 15,886 / 375 / 2026-06-09 | 0 |
| (b) | status 분포 | started 10,916 / pending 4,967 / ended 3 | 동일 | 0 |
| (c) | 2026 한정 범위 | 355행 / 2026-05-17~2026-06-09 | 355행 / 동일 | 0 |
| (d) | (mold, product) 1:1 위반 (운영 2026) | 0건 | 0건 | 0 |
| (e) | 6-튜플 중복 (운영 2026) | 2 그룹, **4행** (mold 111 Butter, 06-08·09) | 2 그룹, **4행** (동일) | 0 (11일째 잔존) |
| (f) | 빈 필드 (운영 2026) | blank_mold 1 / blank_color1 1 / blank_color2 3 / blank_product 0 | 동일 | 0 |
| (g) | color2 White/WHITE 180 (운영 2026) | White 180: 10 / **WHITE 180: 148** | White 180: 10 / **WHITE 180: 148** | 0 |

**정확 카운트 명시** (레퍼런스 §2.3): (e) cnt 합계 2+2 = **4행** (06-08·09 각 2건씩, mold 111 / Butter / YELLO 3093 / unit 30). `(date, machine_number, mold_number, color1, color2, unit_quantity)` 6-튜플 기준.

**06-18→19 carry-forward 금지**: 모든 SQL을 06-19 05:31에 재측정. 0건 변동 확인.

**상세 매핑** (빈 필드 4건 2026):
| id | date | machine | mold | product | color1 | color2 | unit | 비고 |
|---|---|---|---|---|---|---|---|---|
| 19416 | 2026-05-24 | M01 | (빈) | 로코스 L | (빈) | (빈) | 0 | mold+color1+color2 동시 빈값 1건 (id=19416) |
| 05326a40... | 2026-06-07 | 10 | 114 | 데크타일 | WHITE2 | (빈) | 9 | 데크타일 빈 color2 |
| afed0724... | 2026-06-07 | 10 | 114 | 데크타일 | Ivory | (빈) | 9 | 데크타일 빈 color2 |

## ③ 운영 침묵 측정 (skill A 지표)

- 정확 카운트: `tail -5000 backend.log | grep -aE "production-log (POST|PUT|DELETE|GET /api/production-log)" | grep -v GIN-debug` = **0건**
- 마지막 production-log POST 시점: **0건** (06-19 05:31 시점 backend.log 신규 POST 없음)
- **침묵 일수: 10일째** (06-10 00:00 KST ~ 06-19 05:31 KST, max_date 06-09 기준)
- 침묵 일수 표: 06-13: 0일 / 06-14: 1일 / 06-15: 2일 / 06-16: 3일 / 06-17: 8일째 / 06-18: 9일째 / **06-19: 10일째**
- 임계치(≥3일) **8일 연속 초과** → 사용자 확인 요청 (단순 침묵 ≠ 결함, 가능성 A/B/C/D)
- **단순 계산 (마지막 POST 시점)**: 06-14 06:32 (실패) 기준 5일째 (운영 침묵 본질은 max_date 기준 우선)

## ④ 디스크 가속 추이 (skill B 지표)

| 일자 | 절대값 | 일변화 | 판정 |
|:----:|------:|------:|:----:|
| 06-13 | 59% | - | 정상 |
| 06-14 | 59% | 0%p | 정상 |
| 06-15 | 62% | +3%p | WARNING 진입 |
| 06-16 | 64% | +2%p | WARNING 유지 |
| 06-17 | 67% | +3%p | WARNING 재가속 |
| 06-18 | 70% | +3%p | WARNING 가속 유지 |
| **06-19** | **73%** | **+3%p** | **WARNING 4일 연속 +3%p 가속 유지** |

**4일 연속 +3%p/1일 가속 패턴 (심각화)**:
- 06-15(+3) → 06-16(+2 일시정체) → 06-17(+3 재가속) → 06-18(+3 가속 유지) → **06-19(+3 가속 지속)**
- 절대값 73% 도달. 임계치 90%까지 약 17%p 여유 (약 5~6일 후 90% 도달 추정)
- `WARNING 일시 정체`에서 **`WARNING 가속 지속`**으로 재선언 (canonical §4.2 기준)
- **MEDIUM 승격 권장** (4일 연속 가속 + 절대값 70% 초과)

## ⑤ machine 표기 비일관 (운영 2026, §19(1))

| machine_number | 06-18 | **06-19** | 변동 |
|---|---:|---:|:----:|
| `생산대기` (no space) | 10 | 10 | 0 |
| `생산 대기` (띄어쓰기 O) | 4 | 4 | 0 |
| `M01` | 1 | 1 | 0 |
| **합계 (운영 2026 비표준)** | **15** | **15** | 0 |

→ 같은 의미인데 띄어쓰기 혼재 + M01 미사용 패턴. **06-18과 동일 15건 잔존**, 변동 0. upsert 키 분기 위험 (띄어쓰기 차이로 중복 등록 가능). 사용자 확인 후 일괄 통일 권장.

## ⑥ 발견된 문제 (06-18 대비)

### ⚠️ MEDIUM (06-18 유지 → **4일 연속 가속으로 MEDIUM 유지**)

| # | 항목 | 06-17 | 06-18 | **06-19** |
|:-:|------|:-----:|:-----:|:---------:|
| 1 | **디스크 +3%p/1일 가속 지속** (67→70→**73%**) | MEDIUM | MEDIUM | **MEDIUM (4일 연속 +3%p, 절대값 73%)** |

### ⚠️ LOW (06-18과 동일, 잔존)

| # | 항목 | 06-18 | **06-19** |
|:-:|------|:-----:|:---------:|
| 2 | 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09, unit 30) | ⚠️ (10일째) | ⚠️ (11일째) |
| 3 | 빈 mold 1건 (id=19416, 2026-05-24) | ⚠️ | ⚠️ (변동 0) |
| 4 | 빈 color1 1건 (id=19416, 2026-05-24) | ⚠️ | ⚠️ (변동 0) |
| 5 | 데크타일(114) 빈 color2 2건 (2026-06-07) | ⚠️ | ⚠️ (변동 0) |
| 6 | `pending 4,967` (1.xlsx import 후 누적) | INFO | INFO |
| 7 | 빈 product_name 0건 (정상) | INFO | INFO |
| 8 | machine `생산대기` 10 / `생산 대기` 4 / `M01` 1 (총 15, 운영 2026) | ⚠️ | ⚠️ (변동 0) |
| 9 | color2 `WHITE 180` 148건 (대소문자 비일관) | ⚠️ | ⚠️ (변동 0) |

### 🆕 신규 발견 (06-19)

**없음** (06-18 대비 신규 결함 0건. 모든 SQL 결과 동일, 침묵 일수만 +1일 증가)

## ⑦ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **운영 침묵 10일째** (production-log POST 0건, max_date 06-09) | 등록 의도 | ⏳ 사용자 | 9일 → 10일째 |
| 2 | **디스크 4일 연속 +3%p/1일 가속** (70→73%, 절대값 73%) | 5~6일 후 90% 위험 | 👀 관찰+원인 | MEDIUM 유지, 가속 지속 |
| 3 | 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09) | 운영 정확성 | ⏳ 사용자 | 변동 0 (11일째) |
| 4 | id=19416 빈 mold+color1+color2 (2026-05-24, 로코스 L) | 데이터 정합성 | ⏳ 사용자 | 변동 0 |
| 5 | 데크타일(114) 빈 color2 2건 (2026-06-07) | 룰 위반 | ⏳ 사용자 | 변동 0 |
| 6 | machine `생산대기` 10 / `생산 대기` 4 / `M01` 1 (총 15, 운영 2026) | 표기 통일 | ⏳ 사용자 | 변동 0 |
| 7 | started 10,916건 / pending 4,967건 (옵션 1·2·3) | UI 표시 정책 | ⏳ 사용자 | 변동 0 |
| 8 | (mold, product) 1:1 위반 (운영 2026) | 룰 위반 | ✅ 0건 | 0 |
| 9 | color2 `WHITE 180` 148건 (대소문자 비일관) | 리포트/필터 | ⏳ 사용자 | 148 유지 |

## ⑧ 사용자 확인 요청 (질문)

**Q1. 운영 침묵 10일째 — 어떻게 처리할까요?**
- A. 의도된 공휴일/영업 외 시간대 (금요일 05:31 KST)
- B. 1.xlsx import 후 정체 (2026-06-09 마지막)
- C. 등록 누락
- D. 시스템 문제 (DB/API 정상 → 가능성 낮음)

**Q2. 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09) — 어떻게 처리할까요?**
- A. 168 BOX 단일 병합 (4행 → 1행)
- B. 방치
- C. 다른 처리

**Q3. 디스크 4일 연속 +3%p/1일 가속 (73%) — 어떻게 처리할까요?**
- A. 원인 추적 (`du -h --max-depth=2` 1회 측정)
- B. 관찰 유지 (90% 미만)
- C. 즉시 정리 (오래된 로그/백업) — **MEDIUM 단계 진입 검토 권장**

**Q4. machine 표기 `생산대기` 10건 vs `생산 대기` 4건 vs `M01` 1건 (총 15) — 어떻게 처리할까요?**
- A. `생산대기`로 일괄 통일 (SQL UPDATE, M01 별도 결정)
- B. 방치
- C. 다른 처리

**Q5. id=19416 (2026-05-24, 로코스 L) 빈 mold+color1+color2 — 어떻게 처리할까요?**
- A. 삭제 (placeholder 가능성)
- B. 정정 (로코스 L 금형40 + Ivory)
- C. 방치

## ⑨ 액션/옵션

- **즉시**: 없음 (read-only cron, 사용자 결정 대기)
- **시스템 정상**: DB 연결 정상, 백엔드 가동 중
- **Read-only 검증**: SQL 7종 + grep 1종, POST/PUT/DELETE 0건

## ⑩ 결론

- ✅ DB 9/9 정상, PostgreSQL 연결 정상
- ✅ production_logs 15,886행 (2026 한정 355행, 5/17~6/9)
- ⚠️ **MEDIUM 1건 (디스크 4일 연속 +3%p 가속, 70→73%, 절대값 73%)** — MEDIUM 단계 진입 검토 시점
- ⚠️ LOW 8건 (06-18과 동일, 잔존)
- 🆕 신규 0건 (06-18 대비 모든 SQL 결과 동일)
- 🚨 **운영 침묵 10일째** (단순 침묵 ≠ 결함, 사용자 확인 요청)

**종합 판정**: ✅ **DB/시스템 정상 운영 중**, ⚠️ **운영 침묵 10일째 + 디스크 가속 4일 연속 지속** → 사용자 확인 요청

## References

- `Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly.md` (cron 정의)
- `Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260618.md` (직전 동일 cron 보고서, 06-18 05:31)
- `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md` (6/17 통합 점검)
- `vf2/references/vf2-production-plan-nightly-canonical.md` (canonical 절차)
- `vf2/references/production-plan-conventions.md` §19·§20 (DB 비일관/급증)
- `vf2/references/gorm-snakecase-columns-20260616.md` (snake_case 매핑)
- `VF2/backend/.env` (DATABASE_URL)
- `VF2/backend/handlers/production.go` line 223 (upsert 키)
- ⚠️ `vf2-production-plan-conventions` 단일 스킬, `mandatory-verification` 스킬 모두 부재 → umbrella `vf2` references로 우회
