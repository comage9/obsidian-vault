# VF2 Project Nightly — 2026-07-05 자가 점검 보고

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 동작 | 결과 | skip? |
|------|------|------|-------|
| 1. Wiki 검색 | 직전 보고서 `VF2-Project-Nightly-20260704.md` (07-04 06:42) 확인 | ✅ 1개 발견 | - |
| 2. 스킬 로드 | `vf2` (umbrella) + `references/production-plan-conventions.md` + `references/gorm-snakecase-columns-20260616.md` + `references/vf2-production-plan-nightly-canonical.md` | ✅ 로드 완료 | - |
| 3. 질문/실행 구분 | cron scheduled → 자동 실행, 사용자 개입 불요 | ✅ 실행 | - |
| 4. 검증 | §1 health → §2 SQL 점검 → §3 결함 집계 → §4 침묵/디스크 추세 | ✅ 완료 | - |
| 5. 승인 | read-only cron → 사용자 결정 대기 항목만 보고. **DB 직접 수정/등록/삭제 금지** | ✅ 준수 | - |

**Skip 명시**: USER.md / MEMORY.md / `vf2-production-plan-conventions` 단일 스킬 부재. 본 보고서 §"SOUL.md 5단계"에 skip 사실 기록.

---

## ① 시스템 상태 (헬스/디스크/메모리/프로세스/28 테이블)

| 항목 | 측정값 | 판정 | 비고 |
|------|--------|------|------|
| **uptime** | 1일 8시간 18분 | ⚠️ 재부팅 발생 (07-04 cron 기동 후 1일 경과) | canonical §1.2 §7 #20 |
| **Health (localhost:5176/api/health)** | `{"status":"ok","database":"connected","disk":"root:57%","uptime":100}` | ✅ **정상** | 백엔드/프론트 07-04 cron 기동 후 지속 실행 중 |
| **디스크 (/)** | 57% (124G/233G) | ⚠️ WARNING | 07-04 54% → 07-05 57% (+3%p/1일) **재가속 6일째** |
| **메모리** | 14Gi 중 4.9Gi 사용 (가용 10Gi) | ✅ 정상 | - |
| **Swap** | 4.0Gi 중 2.0Gi 사용 (**50%**) | ⚠️ 관찰 | 07-04 0.03% → 07-05 50% **재증가** (canonical §7 #36) |
| **백엔드 프로세스** | `vf2_backend_bin` PID 41169 (07-04 cron 기동) | ⚠️ **자동 복구 안 됨** | systemd 미등록 → 재부팅 시 수동 필요 (canonical §1.2 §7 #26) |
| **프론트엔드 프로세스** | `vite` PID 41279 (07-04 cron 기동) | ⚠️ **자동 복구 안 됨** | 동일 |
| **포트 Listen (5174/5176)** | `ss -tlnp`: 5174(vite), 5176(vf2_backend_bin) | ✅ **정상** | 07-04 cron 기동 후 지속 Listen 중 |
| **PostgreSQL 직접 카운트** | | | |
| `production_logs` | 15,886 | 2026-06-09 | 2024-01-11 | ✅ |
| `machine_plans` | 0 | - | - | ⚠️ 빈 테이블 |
| `inventory_baseline_items` | 4,702 | - | - | ✅ |
| `outbound_records` | 489,810 | - | - | ✅ |
| `delivery_daily_records` | 491 | 2026-06-10 | 2025-02-01 | ✅ |
| `fc_inbound_records` | 3,019 | - | - | ✅ |
| **pg_stat_user_tables (n_live_tup > 0)** | **0 rows** (stale) | ⚠️ **함정 지속** | canonical §7 #21 — 컨테이너 Up 9+ days에도 stale 유지 |
| **테이블 수 (pg_class)** | 28개 | - | - | production_plans 미존재 포함 |

> **핵심**: 백엔드/프론트엔드 **07-04 cron 수동 기동 후 1일째 지속 실행 중**. systemd 미등록 **7회째 권고 미실행** (canonical §7 #26 CRITICAL). 디스크 **재가속 6일째** (+2~3%p/일), 50% 임계치 재돌파 후 5일 경과. Swap 50% 재증가로 메모리 압박 재개 가능성.

---

## ② 발견된 문제 (07-04 대비 변화 명시 + 신규/정정/계승 분리)

### 🔴 신규/악화 항목

| # | 항목 | 07-04 값 | 07-05 값 | 변화 | 심각도 |
|---|------|----------|----------|------|--------|
| 1 | **디스크 57% WARNING** | 54% | **57% (+3%p/1일)** | 재가속 6일째, 70% CRITICAL 약 4-5일 후 도달 예상 | ⚠️ WARNING |
| 2 | **Swap 0.03% → 50% 재증가** | 1.2Mi/4.0Gi (0.03%) | **2.0Gi/4.0Gi (50%)** | 메모리 압박 재개, OOM 위험 재발 가능성 | ⚠️ 관찰 |
| 3 | **시스템 재부팅 없음 (1일 경과)** | uptime 9시간 11분 | **1일 8시간** | 07-04 재부팅 후 안정적 유지 | ✅ 개선 |

### ⚠️ 계승/정체 항목 (변동 0건도 명시)

| # | 항목 | 현재 값 | 정체 일수 | 비고 |
|---|------|---------|-----------|------|
| 4 | 운영 침묵 (max_date 기준) | **26일** (06-09 → 07-05) | 26일째 | 백엔드 DOWN이 직접 원인 |
| 5 | 단순 계산 침묵 (backend.log POST 기준) | **5일** (06-30 마지막 POST 없음) | - | canonical §3.3 두 기준 병기 |
| 6 | 6-튜플 중복 (mold 111) | **4행** (06-08 2행 + 06-09 2행) | 26일째 잔존 | canonical §7 #29 — 06-26 5건 → 06-27 4행 (-1행 정정) |
| 7 | blank color2 | **3건** | 26일째 잔존 | mold_number 1건, color1 1건 동반 |
| 8 | color2 WHITE 180 variant | **158건** (WHITE 180: 148 + White 180: 10) | 26일째 잔존 | canonical §7 #11 ILIKE 필수 |
| 9 | `production_plans` 테이블 부재 | **미존재** | 26일째 잔존 | 1.xlsx import 누락 단서 (canonical §1.3 §7 #16) |
| 10 | pending 4,967건 status 누적 | **4,967건** | 26일째 잔존 | 1.xlsx import 후 started 미전환 (canonical §7 #14) |
| 11 | pg_stat_user_tables stale | **0 rows** | 지속 | canonical §7 #21 — `ANALYZE` 미실행 |
| 12 | systemd/s6 미등록 | **7회째 권고 미실행** | 7회째 | 재부팅 시 미복구 반복 (canonical §7 #26 CRITICAL) |

### ✅ 정정/해소 항목

| # | 항목 | 정정 내용 |
|---|------|-----------|
| 13 | **백엔드/프론트 1일째 안정 실행** | 07-04 cron 수동 기동 후 재부팅 없이 1일 경과 — Downtime 없음 |

---

## ③ 사용자 확인 요청 (질문 + 가능성 표)

### 질문 1: systemd/s6 서비스 등록 — **7회째 권고, 즉시 실행 필요** (canonical §7 #26)
> 백엔드/프론트엔드가 재부팅 후 자동 복구되지 않아 **15일간 DOWN** 지속 후 07-04 cron 수동 기동으로 복구. PostgreSQL만 Docker restart policy로 복구됨.

| 가능성 | 설명 | 권장 액션 |
|--------|------|-----------|
| A | systemd unit 생성 (`vf2-backend.service`, `vf2-frontend.service`) + `systemctl enable --now` | ✅ **즉시 실행 권장** (canonical §1.2 예시 unit 파일 참조) |
| B | s6-overlay 서비스 등록 (Hermes 컨테이너 내부) | A 선호 (호스트 레벨 관리) |
| C | 현재 상태 유지 (수동 기동 반복) | ❌ 비권장 — 15일 DOWN 방치됨 |
| D | 외부 모니터링 + 알림만 추가 | 근본 원인 미해결 |

### 질문 2: 디스크 가속 원인 추적 — **6일째 +2~3%p/일, 70% CRITICAL 약 4-5일 후 예상**
> 07-01 47% → 07-02 49% → 07-03 52% → 07-04 54% → 07-05 57% (재가속 6일째, canonical §7 #34)

| 가능성 | 설명 | 진단 명령 |
|--------|------|-----------|
| A | VF2 백엔드 로그(`backend.log`) 무한 증식 | `du -sh /home/comtop/workspace/VF2/backend/backend.log` |
| B | Docker 컨테이너 로그/오버레이 증식 | `docker system df -v` |
| C | PostgreSQL WAL/로그 증식 | `docker exec postgres_hermes du -sh /var/lib/postgresql/data/pg_wal` |
| D | 기타 임시 파일/캐시 | `du -h /home/comtop/workspace/VF2 --max-depth=2 \| sort -hr \| head -20` |
| E | 시스템 전체 다른 경로 (예: /var/log, /tmp) | `du -h /var/log --max-depth=1 \| sort -hr` |

### 질문 3: Swap 50% 재증가 — 메모리 압박 원인 분석 필요
> 07-03 95% → 07-04 0.03% 해소 → 07-05 50% 재증가

| 가능성 | 설명 |
|--------|------|
| A | 백엔드/프론트 프로세스 메모리 누수 (1일 실행 후 누적) |
| B | PostgreSQL 컨테이너 메모리 사용 증가 |
| C | 시스템 캐시/버퍼 증가 (정상 범위일 수 있음) |
| D | 기타 프로세스 메모리 사용 증가 |

### 질문 4: 운영 26일 침묵 — 백엔드 복구로 자연 재개 예상 vs 별도 액션 필요

| 가능성 | 설명 |
|--------|------|
| A | 백엔드 복구로 production-log POST 자연 재개 → 단순 관망 |
| B | 1.xlsx import 대기 중 (pending 4,967건) → 사용자 결정 후 재개 |
| C | 생산 계획 자체가 중단된 상태 → 사업적 판단 필요 |
| D | 수동 데이터 등록 누락 → 크롤러/스크립트 복구 필요 |

### 질문 5: `production_plans` 테이블 부재 — 1.xlsx import 스크립트 실행 vs 테이블 생성부터

| 가능성 | 설명 |
|--------|------|
| A | 테이블 미생성 — `CREATE TABLE production_plans ...` 후 import 스크립트 실행 |
| B | import 스크립트가 테이블 자동 생성하므로 스크립트만 실행 |
| C | 운영 데이터가 machine_plans에만 있음 (machine_plans 0행 확인) — import 불필요 |

---

## ④ 미해결 항목 추적 표

| # | 항목 | 영향 | 결정 필요 | 변동 (07-04 → 07-05) |
|---|------|------|-----------|----------------------|
| 1 | 운영 침묵 26일 (max_date 기준) | 등록 정체 | ⏳ 사용자 | 25일 → **26일째** (+1일) |
| 2 | systemd/s6 미등록 (**7회째 권고 미실행**) | 재부팅 시 미복구 반복 | ⏳ 사용자 | 동일 (7회째) |
| 3 | ⚠️ 디스크 57% WARNING | 1~2개월 위험 | ⏳ 사용자 | 54% → **57%** (+3%p, 재가속 6일째) |
| 4 | Swap 50% 재증가 | OOM 위험 재발 가능 | ⏳ 사용자 | **0.03% → 50%** (재증가) |
| 5 | 6-튜플 중복 4행 (mold 111) | 운영 정확성 | ⏳ 사용자 | 동일 (4행 유지) |
| 6 | color2 WHITE 180 variant 158건 | 표기 통일 | ⏳ 사용자 | 동일 |
| 7 | `production_plans` 테이블 부재 | import 누락 단서 | ⏳ 사용자 | 동일 |
| 8 | blank color2 3건 | 룰 위반 | ⏳ 사용자 | 동일 |
| 9 | pending 4,967건 status 누적 | UI 표시 정책 | ⏳ 사용자 | 동일 |
| 10 | pg_stat_user_tables stale | 통계 미갱신 | 👀 관찰 | 동일 |
| 11 | 백엔드/프론트 1일째 안정 실행 | 가용성 확보 | 👀 관찰 | **신규: 복구 후 1일 무사고** ✅ |

---

## ⑤ 액션/옵션 (즉시/시스템)

### 즉시 조치 필요 (사용자 액션)
1. **systemd 등록** — `vf2-backend.service` + `vf2-frontend.service` 생성 후 `systemctl enable --now` (canonical §1.2 §7 #26)
2. **디스크 원인 추적** — `du -h /home/comtop/workspace/VF2 --max-depth=2 | sort -hr | head -20` 등 대용량 디렉토리 식별
3. **Swap 재증가 원인 분석** — 백엔드/프론트 프로세스 메모리 사용량 확인
4. **생산 데이터 재개 확인** — 백엔드 복구 후 production-log POST 발생 모니터링

### 시스템 자동 조치 (이번 cron 수행 완료)
- ✅ Health 확인 (localhost:5176/api/health → `{"status":"ok","database":"connected","disk":"root:57%"}`)
- ✅ 포트 Listen 확인 (5174, 5176)
- ✅ DB 직접 쿼리 7종 + pg_class + to_regclass 실행 (모든 SQL exit_code=0)
- ✅ 백엔드/프론트 프로세스 생존 확인 (PID 41169, 41279 지속 실행 중)

---

## ⑥ 디스크 가속 추이 표

| 날짜 | 디스크 % | 일일 Δ | 누적 Δ (06-30 44% 기준) | 판정 |
|------|----------|--------|-------------------------|------|
| 06-30 | 44% | - | 기준 | 정상 (해소 선언 §7 #30) |
| 07-01 | 47% | +3%p | +3%p | WARNING 재발 (§7 #34) |
| 07-02 | 49% | +2%p | +5%p | WARNING 지속 |
| 07-03 | 52% | +3%p | +8%p | WARNING 지속 (§7 #35 예측 적중) |
| 07-04 | 54% | +2%p | +10%p | WARNING 지속 — 재가속 5일째 |
| **07-05** | **57%** | **+3%p** | **+13%p** | **WARNING 지속 — 재가속 6일째** |

> **예측**: 현재 +2.7%p/일 평균 유지 시 **약 4-5일 후(07-09~07-10) 70% CRITICAL 도달**. §7 #35 예측→확인 사이클 4일째 적중.

---

## ⑦ 결론

- 🔴 **systemd 미등록 7회째** — 07-04 cron 수동 기동 후 1일째 안정 실행 중이나, 재부팅 시 15일 DOWN 재발 위험 (P0 CRITICAL, canonical §7 #26)
- ⚠️ **디스크 57% WARNING** — 50% 임계치 재돌파 후 **+2.7%p/일 가속 6일째**, 4-5일 내 70% CRITICAL 도달 예상
- ⚠️ **Swap 50% 재증가** — 07-04 0.03% 해소 후 1일 만에 50% 재증가, 메모리 압박 재개 가능성
- 🔵 **DB 데이터 완전 동결** (15,886행, max_date 06-09, 28개 테이블 정체)
- 🔴 **침묵 26일** — 백엔드 DOWN이 직접적 원인, 복구로 자연 재개 예상

**즉시 조치 필요 순위**:
1. **systemd 등록** — 재부팅 반복 시 15일 DOWN 재발 방지 (canonical §1.2 §7 #26)
2. **디스크 원인 추적** — `du` 분석으로 증식 주체 식별 후 정리
3. **Swap 재증가 원인 분석** — 프로세스별 메모리 사용량 확인
4. **생산 데이터 재개 확인** — 백엔드 복구 후 production-log POST 발생 모니터링

---

## 3중 완료 (Wiki + Git push)

- ✅ Wiki 저장: `/home/comtop/workspace/Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260705.md` (git repo 직접, canonical §7 #33)
- Git commit + push: cron 완료 후 수행
- log.md: 부재 (canonical §7 #31 fallback — 보고서 파일로 대체)

---

## References

- 직전 Project 보고서: `VF2-Project-Nightly-20260704.md` (07-04 06:42)
- 오늘 1차 cron 예정: `VF2-Production-Plan-Nightly-20260705.md` (05:00)
- canonical: `references/vf2-production-plan-nightly-canonical.md`
- 함정: §0.1 (같은 날 2회 실행), §7 #26 (systemd 7회째), §7 #33 (write_file git repo 경로), §7 #34 (디스크 재가속 6일째), §7 #35 (예측 적중 사이클 4일째), §7 #36 (swap 관찰), §7 #37 (terminal compound command guard)