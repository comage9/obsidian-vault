# VF2 Production Plan Nightly — 2026-08-16 자가 점검 보고

> 점검 시각: 2026-08-16 14:43 KST (cron, 토요일)
> Cron ID: `48144ff13cee` (VF2 Production Plan Nightly, 05:30 KST)
> 절차: SOUL.md 5단계 체크리스트 + `vf2/references/vf2-production-plan-nightly-canonical.md` (1순위) + `vf2/references/production-plan-conventions.md` §19·§20 (2순위) + `vf2/references/gorm-snakecase-columns-20260616.md` (snake_case)
> 비교: 직전 VF2-Production-Plan-Nightly-20260619.md (58일 전)

## SOUL.md 5단계 체크리스트

| 단계 | 동작 | 결과 |
|:-:|------|:----:|
| 1. Wiki 검색 | `session_search` + `search_files`로 직전 보고서 `VF2-Production-Plan-Nightly-20260619.md` + `production-plan-conventions.md` canonical 발견 | ✅ |
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
- DB: PostgreSQL, vf2_db, hermes 사용자 (Docker postgres_hermes)
- 백엔드 PID 6647 가동 중, PostgreSQL 연결 정상
- 프론트엔드 포트 5174 **미가동** (연결 실패)

---

## ① 시스템 상태

| # | 점검 | 06-19 | **08-16** | 변동 | 비고 |
|:-:|:-----|:-----:|:---------:|:----:|:-----|
| 1 | DB 연결 (PostgreSQL) | ✅ | ✅ | 0 | `database: connected, uptime: 100` |
| 2 | 백엔드 프로세스 | ✅ | ✅ | 0 | PID 6647, ./vf2_backend_bin 가동 중 |
| 3 | 프론트엔드 프로세스 | (확인 안됨) | ❌ | - | 포트 5174 연결 실패 |
| 4 | 디스크 `/` | 73% | **82%** | +9%p | **CRITICAL 근접** (90% 임계치 8%p 남음) |
| 5 | 메모리 | OK | OK | 0 | 3.8G 사용 / 11G 가용 (변동 없음) |
| 6 | DB 테이블 수 | 9/9 | **28/28** | +19 | 스키마 확장됨 (inventory, inbound, outbound 등) |
| 7 | `production_plans` 존재 | NULL | NULL | 0 | `to_regclass → NULL`, 1.xlsx import 누락 단서 잔존 |
| 8 | 운영 침묵 | 10일째 | **68일째** | +58일 | max_date 06-09 미변동, 06-10~08-16 production-log POST 0건 (1건 401) |

---

## ② 표준 SQL 7종 (production_logs, 2026 한정)

| # | 쿼리 | 06-19 | **08-16** | 변동 |
|:-:|------|:-----:|:---------:|:----:|
| (a) | total / dates / max_date | 15,886 / 375 / 2026-06-09 | 15,886 / 375 / 2026-06-09 | 0 |
| (b) | status 분포 | started 10,916 / pending 4,967 / ended 3 | 동일 | 0 |
| (c) | 2026 한정 범위 | 355행 / 2026-05-17~2026-06-09 | 355행 / 동일 | 0 |
| (d) | (mold, product) 1:1 위반 (운영 2026) | 0건 | 0건 | 0 |
| (e) | 6-튜플 중복 (운영 2026) | 2 그룹, **4행** (mold 111 Butter, 06-08·09) | 2 그룹, **4행** (동일) | 0 (69일째 잔존) |
| (f) | 빈 필드 (운영 2026) | blank_mold 1 / blank_color1 1 / blank_color2 3 / blank_product 0 | 동일 | 0 |
| (g) | color2 White/WHITE 180 (운영 2026) | White 180: 10 / **WHITE 180: 148** | White 180: 10 / **WHITE 180: 148** | 0 |

**정확 카운트 명시** (레퍼런스 §2.3): (e) cnt 합계 2+2 = **4행** (06-08·09 각 2건씩, mold 111 / Butter / YELLO 3093 / unit 30). `(date, machine_number, mold_number, color1, color2, unit_quantity)` 6-튜플 기준.

**06-19→16 carry-forward 금지**: 모든 SQL을 08-16 14:43에 재측정. 0건 변동 확인.

**상세 매핑** (빈 필드 4건 2026):
| id | date | machine | mold | product | color1 | color2 | unit | 비고 |
|---|---|---|---|---|---|---|---|---|
| 19416 | 2026-05-24 | M01 | (빈) | 로코스 L | (빈) | (빈) | 0 | mold+color1+color2 동시 빈값 1건 (id=19416) |
| 05326a40... | 2026-06-07 | 10 | 114 | 데크타일 | WHITE2 | (빈) | 9 | 데크타일 빈 color2 |
| afed0724... | 2026-06-07 | 10 | 114 | 데크타일 | Ivory | (빈) | 9 | 데크타일 빈 color2 |

---

## ③ 운영 침묵 측정 (skill A 지표)

- 정확 카운트: `grep -a "POST.*production-log" backend/backend.log | grep -v GIN-debug` = **1건** (2026/07/04 06:33:33, 401 Unauthorized)
- 마지막 production-log POST 성공 시점: **0건** (06-09 이후 성공 POST 없음)
- **침묵 일수: 68일째** (06-10 00:00 KST ~ 08-16 14:43 KST, max_date 06-09 기준)
- 침묵 일수 표: 06-13: 0일 / 06-14: 1일 / 06-15: 2일 / 06-16: 3일 / 06-17: 8일째 / 06-18: 9일째 / 06-19: 10일째 / **08-16: 68일째**
- 임계치(≥3일) **65일 연속 초과** → 사용자 확인 요청 (단순 침묵 ≠ 결함, 가능성 A/B/C/D)
- **단일 실패 POST**: 2026-07-04 06:33:33, 401 반환 → 인증 토큰 문제 가능성

---

## ④ 디스크 가속 추이 (skill B 지표)

| 일자 | 절대값 | 일변화 | 판정 |
|:----:|------:|------:|:----:|
| 06-13 | 59% | - | 정상 |
| 06-14 | 59% | 0%p | 정상 |
| 06-15 | 62% | +3%p | WARNING 진입 |
| 06-16 | 64% | +2%p | WARNING 유지 |
| 06-17 | 67% | +3%p | WARNING 재가속 |
| 06-18 | 70% | +3%p | WARNING 가속 유지 |
| 06-19 | 73% | +3%p | WARNING 4일 연속 +3%p 가속 유지 |
| **08-16** | **82%** | **+9%p/58일 (평균 +0.16%p/일)** | **CRITICAL 근접 (90%까지 8%p)** |

**장기 추이 분석**:
- 06-19(73%) → 08-16(82%) = 58일간 +9%p, 평균 +0.16%p/일
- 초기 4일간 +3%p/일 가속 패턴은 정체되었으나, 절대값 82%로 **임계치 90%까지 8%p만 남음**
- 현재 추세 유지 시 **약 50일 후(10월 초) 90% 도달 추정**
- 백엔드 로그, DB 백업 파일(252MB × 2 = 505MB), Docker 이미지 등이 주요 용량 차지 추정
- **CRITICAL 승격 권장** (절대값 82% + 90% 임계치 임박)

---

## ⑤ machine 표기 비일관 (운영 2026, §19(1))

| machine_number | 06-19 | **08-16** | 변동 |
|---|---:|---:|:----:|
| `생산대기` (no space) | 10 | 10 | 0 |
| `생산 대기` (띄어쓰기 O) | 4 | 4 | 0 |
| `M01` | 1 | 1 | 0 |
| **합계 (운영 2026 비표준)** | **15** | **15** | 0 |

→ 같은 의미인데 띄어쓰기 혼재 + M01 미사용 패턴. **06-19와 동일 15건 잔존**, 변동 0. upsert 키 분기 위험 (띄어쓰기 차이로 중복 등록 가능). 사용자 확인 후 일괄 통일 권장.

---

## ⑥ 발견된 문제 (06-19 대비)

### 🚨 CRITICAL (신규 승격)

| # | 항목 | 06-19 | **08-16** |
|:-:|------|:-----:|:---------:|
| 1 | **디스크 82% (90% 임계치 8%p 남음)** | MEDIUM (73%) | **CRITICAL** |

### ⚠️ MEDIUM (06-19 유지)

| # | 항목 | 06-19 | **08-16** |
|:-:|------|:-----:|:---------:|
| 2 | **운영 침묵 68일째** (production-log POST 성공 0건, max_date 06-09) | LOW (10일째) | **MEDIUM (68일째)** |

### ⚠️ LOW (06-19과 동일, 잔존)

| # | 항목 | 06-19 | **08-16** |
|:-:|------|:-----:|:---------:|
| 3 | 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09) | ⚠️ (11일째) | ⚠️ (69일째) |
| 4 | 빈 mold 1건 (id=19416, 2026-05-24) | ⚠️ | ⚠️ (변동 0) |
| 5 | 빈 color1 1건 (id=19416, 2026-05-24) | ⚠️ | ⚠️ (변동 0) |
| 6 | 데크타일(114) 빈 color2 2건 (2026-06-07) | ⚠️ | ⚠️ (변동 0) |
| 7 | `pending 4,967` (1.xlsx import 후 누적) | INFO | INFO |
| 8 | 빈 product_name 0건 (정상) | INFO | INFO |
| 9 | machine `생산대기` 10 / `생산 대기` 4 / `M01` 1 (총 15, 운영 2026) | ⚠️ | ⚠️ (변동 0) |
| 10 | color2 `WHITE 180` 148건 (대소문자 비일관) | ⚠️ | ⚠️ (변동 0) |

### 🆕 신규 발견 (08-16)

| # | 항목 | 내용 |
|:-:|------|------|
| 11 | **프론트엔드 미가동** (포트 5174 연결 실패) | 운영 환경에서 프론트엔드 서비스 중단 상태 |
| 12 | **DB 테이블 28개로 확장** (기존 9개) | inventory, inbound, outbound, barcode, machine_plans 등 신규 스키마 추가 |
| 13 | **2026-07-04 401 POST 1건** | 인증 토큰 문제로 production-log 등록 실패 사례 확인 |

---

## ⑦ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **디스크 82% (CRITICAL 근접)** | 시스템 중단 위험 | 🔴 즉시 정리 | 73%→82% (+9%p) |
| 2 | **운영 침묵 68일째** (production-log POST 성공 0건) | 등록 의도 | ⏳ 사용자 | 10일→68일째 |
| 3 | 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09) | 운영 정확성 | ⏳ 사용자 | 변동 0 (69일째) |
| 4 | id=19416 빈 mold+color1+color2 (2026-05-24, 로코스 L) | 데이터 정합성 | ⏳ 사용자 | 변동 0 |
| 5 | 데크타일(114) 빈 color2 2건 (2026-06-07) | 룰 위반 | ⏳ 사용자 | 변동 0 |
| 6 | machine `생산대기` 10 / `생산 대기` 4 / `M01` 1 (총 15, 운영 2026) | 표기 통일 | ⏳ 사용자 | 변동 0 |
| 7 | started 10,916건 / pending 4,967건 (옵션 1·2·3) | UI 표시 정책 | ⏳ 사용자 | 변동 0 |
| 8 | (mold, product) 1:1 위반 (운영 2026) | 룰 위반 | ✅ 0건 | 0 |
| 9 | color2 `WHITE 180` 148건 (대소문자 비일관) | 리포트/필터 | ⏳ 사용자 | 148 유지 |
| 10 | **프론트엔드 미가동** (포트 5174) | UI 접근 불가 | 🔴 즉시 재시작 | 신규 |
| 11 | **인증 토큰 401 오류** (2026-07-04) | API 접근 차단 | 🔴 토큰 갱신 | 신규 |

---

## ⑧ 사용자 확인 요청 (질문)

**Q1. 운영 침묵 68일째 — 어떻게 처리할까요?**
- A. 의도된 장기 휴무/영업 외 시간대 (68일 = 약 2개월)
- B. 1.xlsx import 후 정체 (2026-06-09 마지막)
- C. 등록 누락 (현장 작업 미반영)
- D. 시스템 문제 (DB/API 정상 → 가능성 낮음, 단 401 인증 오류 1건 확인)

**Q2. 디스크 82% (CRITICAL 근접) — 어떻게 처리할까요?**
- A. 원인 추적 (`du -h --max-depth=2 /` 1회 측정) 후 정리
- B. 관찰 유지 (90% 미만이나 임박)
- C. **즉시 정리** (오래된 로그/백업/Docker 이미지) — **CRITICAL 단계 진입 임박, 즉시 조치 권장**

**Q3. 운영 6-튜플 중복 mold 111 Butter (4행, 06-08·09) — 어떻게 처리할까요?**
- A. 168 BOX 단일 병합 (4행 → 1행)
- B. 방치
- C. 다른 처리

**Q4. machine 표기 `생산대기` 10건 vs `생산 대기` 4건 vs `M01` 1건 (총 15) — 어떻게 처리할까요?**
- A. `생산대기`로 일괄 통일 (SQL UPDATE, M01 별도 결정)
- B. 방치
- C. 다른 처리

**Q5. id=19416 (2026-05-24, 로코스 L) 빈 mold+color1+color2 — 어떻게 처리할까요?**
- A. 삭제 (placeholder 가능성)
- B. 정정 (로코스 L 금형40 + Ivory)
- C. 방치

**Q6. 프론트엔드 미가동 — 어떻게 처리할까요?**
- A. 즉시 재시작 (`cd frontend && npm run dev -- --host 0.0.0.0 --port 5174`)
- B. 백엔드 API만으로 운영 (프론트 불필요)
- C. 다른 처리

**Q7. 인증 토큰 401 오류 (2026-07-04) — 어떻게 처리할까요?**
- A. API_AUTH_TOKEN 갱신/재발급
- B. 토큰 없이 운영 (개발 환경)
- C. 다른 처리

---

## ⑨ 액션/옵션

- **즉시**: 없음 (read-only cron, 사용자 결정 대기)
- **시스템**: DB 연결 정상, 백엔드 가동 중, 프론트엔드 중단
- **Read-only 검증**: SQL 7종 + grep 1종, POST 성공 0건 (401 1건만)
- **권장 우선순위**: ① 디스크 정리 ② 프론트엔드 재시작 ③ 토큰 갱신 ④ 운영 침묵 원인 파악

---

## ⑩ 결론

- ✅ DB 28/28 정상, PostgreSQL 연결 정상, 백엔드 가동 중
- ✅ production_logs 15,886행 (2026 한정 355행, 5/17~6/9) — **58일간 변동 없음**
- 🚨 **CRITICAL 1건 (디스크 82%, 90% 임계치 8%p 남음)** — 즉시 정리 필요
- ⚠️ **MEDIUM 1건 (운영 침묵 68일째)** — 401 인증 오류 1건 확인, 원인 파악 필요
- ⚠️ LOW 8건 (06-19과 동일, 58~69일째 잔존)
- 🆕 **신규 3건**: 프론트엔드 미가동, DB 스키마 28개 확장, 401 인증 오류 1건
- 🚨 **프론트엔드 포트 5174 미가동** — UI 접근 불가

**종합 판정**: ✅ **DB/백엔드 정상 운영 중**, 🚨 **디스크 CRITICAL 임박 + 운영 침묵 68일째 + 프론트엔드 중단 + 인증 오류** → **즉시 조치 3건 + 사용자 확인 4건 요청**

---

## References

- `Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly.md` (cron 정의)
- `Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260619.md` (직전 동일 cron 보고서, 06-19 05:31)
- `Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260617.md` (6/17 통합 점검)
- `vf2/references/vf2-production-plan-nightly-canonical.md` (canonical 절차)
- `vf2/references/production-plan-conventions.md` §19·§20 (DB 비일관/급증)
- `vf2/references/gorm-snakecase-columns-20260616.md` (snake_case 매핑)
- `VF2/backend/.env` (DATABASE_URL)
- `VF2/backend/handlers/production.go` line 223 (upsert 키)
- ⚠️ `vf2-production-plan-conventions` 단일 스킬, `mandatory-verification` 스킬 모두 부재 → umbrella `vf2` references로 우회