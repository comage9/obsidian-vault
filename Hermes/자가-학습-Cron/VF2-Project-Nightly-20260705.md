# VF2 Project Nightly — 2026-07-05 자가 점검 보고

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 동작 | 결과 |
|:---:|------|------|
| 1. Wiki 검색 | 직전 보고서 `VF2-Project-Nightly-20260703-2nd-cron.md` (07-03 2차 cron) 발견 | ✅ |
| 2. 스킬 로드 | `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md` + `references/gorm-snakecase-columns-20260616.md` | ✅ |
| 3. 질문/실행 구분 | cron scheduled → 자동 실행 | ✅ |
| 4. 검증 | §1 health → §2 SQL 점검 → §3 결함 집계 → §4 침묵/디스크 추세 | ✅ |
| 5. 승인 | read-only cron → 사용자 결정 대기 항목만 보고, DB 직접 수정/등록/삭제 금지 | ✅ |

**Skip 명시**: USER.md / MEMORY.md / `mandatory-verification` skill / `vf2-production-plan-conventions` 단일 스킬 부재 — 보고서 §"SOUL.md 5단계"에 기록.

---

## ① 시스템 상태 (헬스/디스크/메모리/프로세스/DB 테이블)

| 항목 | 상태 | 상세 |
|:---|:---:|:---|
| **Uptime** | ✅ 정상 | `1 day, 9:12` — 재부팅 없음 (07-04 오전 기동 후 연속 가동) |
| **백엔드 Health** | ✅ 정상 | `curl localhost:5176/api/health` → `{"status":"ok","database":"connected","disk":"root:57%"}` |
| **프론트엔드 Health** | ✅ 정상 | `curl localhost:5174/` → 200 OK (HTML 반환) |
| **디스크 (/)** | ⚠️ WARNING 재가속 | `57%` (124G/233G) — 07-01 44% → 07-02 47% → 07-03 52% → **07-05 57% (+5%p/2일, 평균 +2.5%p/일)** |
| **메모리** | ⚠️ 관찰 | Swap `50%` (2.0Gi/4.0Gi) — 07-03 95%에서 다소 개선, 지속 관찰 필요 |
| **백엔드 프로세스** | ✅ 정상 | PID 41169 (`vf2_backend_bin`), 07-04 기동 후 연속 |
| **프론트엔드 프로세스** | ✅ 정상 | PID 41279 (`vite`), 07-04 기동 후 연속 |
| **포트 Listen (5174/5176)** | ✅ 정상 | `ss -tlnp` → 5174(node), 5176(vf2_backend_bin) 모두 LISTEN |
| **PostgreSQL 컨테이너** | ✅ 정상 | `docker ps` → `postgres_hermes` Up (Docker restart policy) |
| **DB 테이블 수 (pg_class)** | ⚠️ 28개 | 06-23 9개 → 07-03 28개 (+19개 신규, 06-26~07-03 간 마이그레이션) |
| **pg_stat_user_tables** | ⚠️ Stale | 0 rows 반환 (통계 미갱신, `pg_class` + `count(*)` fallback 사용) |
| **production_plans 테이블** | ❌ 부재 | `to_regclass('public.production_plans')` → NULL (06-18부터 NN일째) |

---

## ② 발견된 문제 (07-03 2차 cron 대비 변화 명시)

| # | 항목 | 07-03 2차 | 07-05 현재 | 변동 | 분류 |
|:---|:---|:---:|:---:|:---:|:---|
| 1 | **운영 침묵 (max_date 기준)** | 24일 (06-09 → 07-03) | **26일** (06-09 → 07-05) | **+2일** | 🔴 지속 악화 |
| 2 | **운영 침묵 (단순 계산)** | backend.log 0건 | backend.log 0건 | 변동 없음 | 🔴 지속 |
| 3 | **디스크 사용률** | 52% | **57%** | **+5%p/2일** (+2.5%p/일) | 🔴 재가속 지속 |
| 4 | **Swap 사용률** | 95% (3.8/4.0Gi) | **50%** (2.0/4.0Gi) | **-45%p 개선** | 🟢 호전 |
| 5 | **production_logs 총 행수** | 15,886 | 15,886 | 0 | 🟢 동결 |
| 6 | **status 분포** | started=10916 / pending=4967 / ended=3 | 동일 | 0 | 🟢 동결 |
| 7 | **운영 (mold, product) 1:1 위반** | 0건 | 0건 | 0 | 🟢 정상 |
| 8 | **6-튜플 중복 (운영)** | 4행 (mold 111, 2일×2건) | **4행** (동일) | 0 | 🟢 정체 |
| 9 | **빈 필드 결함** | blank_mold=1, blank_color1=1, blank_color2=3 | 동일 | 0 | 🟢 정체 |
| 10 | **color2 White 180 variants** | WHITE 180=148, White 180=10 (총 158) | 동일 | 0 | 🟢 정체 |
| 11 | **DB 신규 테이블 (vs 06-23 9개)** | +19개 (28개) | +19개 (28개) | 0 | 🟢 정체 |
| 12 | **production_plans 부재** | NULL | NULL | 지속 | 🟡 미해결 |

**신규 발견**: 없음 — 모든 지표가 07-03 2차 cron 대비 변동 없거나 악화(침묵 +2일, 디스크 +5%p)만 확인.

**정정 사항**: 없음 — 07-03 보고서와 모든 SQL 결과 일치.

---

## ③ 사용자 확인 요청 (질문 + 가능성 표)

침묵 **≥ 3일 임계치 초과 (max_date 기준 26일)** + 디스크 **WARNING 재가속 지속** → 사용자 확인 요청.

### 질문 1: production-log 등록 재개 의향?

| 가능성 | 설명 | 근거 |
|:---|:---|:---|
| **A. 의도된 중단 (공휴일/작업 없음)** | 06-09 이후 실질 생산 없음 | max_date 06-09 고정, pending 4,967건(1.xlsx import 후 대기) |
| **B. 1.xlsx import 후 정체** | 사용자 승인 대기 중 (status='pending' 4,967건) | UI 옵션 1·2·3 결정 보류 중 (06-17부터) |
| **C. 등록 누락/단순 미작업** | 백엔드/프론트 가동 중이나 수동 등록 안 함 | 백엔드 07-04 이후 정상 가동, API health OK |
| **D. 백엔드 다운 기간 중 구조적 불가** | 06-22~07-03 백엔드 DOWN으로 POST 불가 | 07-04 기동 후에도 미등록 → A~C 중 복합 |

### 질문 2: 디스크 가속 재가속 대응?

| 가능성 | 설명 | 근거 |
|:---|:---|:---|
| **A. 1.xlsx 등 배치 import 잔여 데이터 증가** | 대량 import 후 점진적 증가 | 06-30 44% 대규모 정리 후 재가속 패턴 (§7 #34) |
| **B. 로그/임시 파일 누적** | backend.log, Docker 로그, 스왑 파일 등 | Swap 50% 개선되었으나 디스크는 계속 증가 |
| **C. PostgreSQL WAL/통계/인덱스 증가** | pg_stat_user_tables stale, ANALYZE 미수행 | 통계 갱신 시 디스크 사용량 변동 가능 |
| **D. 알 수 없는 누수** | 애플리케이션 레벨 버그 | 지속 관찰 필요 |

### 질문 3: production_plans 테이블 생성/1.xlsx import 진행?

- 06-18부터 부재 (NN일째), 1.xlsx import 대상 테이블로 누락 단서
- 현재 pending 4,967건이 production_plans로 이동 대기 가능성

---

## ④ 미해결 항목 추적 표

| # | 항목 | 영향 | 결정 필요 | 변동 (07-03 → 07-05) |
|:---:|:---|:---|:---:|:---|
| 1 | **운영 침묵 26일 (max_date 기준)** | 등록 의도 불명 | ⏳ 사용자 | 24일 → **26일** (+2일) |
| 2 | **디스크 가속 재가속 (+2.5%p/일)** | 1~2개월 내 CRITICAL 위험 | 👀 관찰 + 원인 추적 | 52% → **57%** (+5%p/2일) |
| 3 | **운영 6-튜플 중복 mold 111 (4행)** | 운영 정확성 | ⏳ 사용자 | 변동 없음 (4행 정체) |
| 4 | **데크타일(114) color2 빈값 3건** | 룰 위반 | ⏳ 사용자 | 변동 없음 (3건 잔존) |
| 5 | **machine `생산 대기` 표기 통일** | 표기 통일 | ⏳ 사용자 | 변동 없음 |
| 6 | **빈 moldNumber (id=19416 SQLite 잔존)** | 노이즈 | ⏳ 사용자 | 변동 없음 (PG에 없음) |
| 7 | **started 10,916건 (옵션 1·2·3)** | UI 표시 정책 | ⏳ 사용자 | 변동 없음 |
| 8 | **pending 4,967건 (1.xlsx import 후 대기)** | 사용자 승인 대기 | ⏳ 사용자 | 변동 없음 |
| 9 | **production_plans 테이블 부재** | 1.xlsx import 불가 | ⏳ 사용자 | 지속 부재 |
| 10 | **Swap 50% (개선됨, 관찰 지속)** | OOM 위험 잔존 | 👀 관찰 | 95% → **50%** 호전 |

---

## ⑤ 액션/옵션

| 구분 | 내용 |
|:---|:---|
| **즉시 실행 가능 (시스템)** | - systemd 서비스 등록으로 백엔드/프론트 자동 기동 보장 (§7 #26, 06-23 권고 → 07-05 13일째 미실행)<br>- `ANALYZE` 실행으로 pg_stat_user_tables 통계 갱신<br>- Docker 로그 로테이션 설정 (`--log-opt max-size=10m --log-opt max-file=3`) |
| **사용자 결정 대기** | ① production-log 등록 재개 (A/B/C/D 중 선택)<br>② 디스크 가속 원인 조사 및 정리 실행<br>③ production_plans 테이블 생성 및 1.xlsx import 진행<br>④ pending 4,967건 상태 결정 (옵션 1·2·3: started 전환/유지/삭제) |

---

## ⑥ 디스크 가속 추이 표

| 날짜 | 사용률 | 일일 Δ | 누적 Δ | 판정 |
|:---|---:|---:|---:|:---|
| 06-26 | 89% | — | — | CRITICAL |
| 06-27 | 93% | +4%p | +4%p | CRITICAL |
| 06-30 | 44% | -49%p | -45%p | **해소 (대규모 정리)** |
| 07-01 | 47% | +3%p | -42%p | 정체 → 재가속 시작 (§7 #34) |
| 07-02 | 49% | +2%p | -40%p | 재가속 지속 |
| 07-03 | 52% | +3%p | -37%p | **WARNING 재선언** (§7 #35 예측 적중) |
| **07-05** | **57%** | **+5%p/2일** | **-32%p** | **WARNING 재가속 지속** |

**예측**: 현재 +2.5%p/일 추세 지속 시 **약 13일 후 (07-18 전후) 90% 도달 → CRITICAL 재진입**.

---

## ⑦ 결론

1. **백엔드/프론트엔드**: 07-04 기동 후 정상 가동 중 (systemd 미등록으로 재부팅 시 재발 위험, §7 #26 즉시 실행 의무)
2. **운영 침묵**: max_date 기준 **26일째** (06-09 이후 등록 0건) — 임계치 ≥3일 대폭 초과, 사용자 결정 필요
3. **디스크**: **57%, +2.5%p/일 재가속 중** — 06-30 해소 선언 후 5일째 재가속, §7 #34/#35 패턴 반복
4. **DB 상태**: production_logs 15,886행 동결, 28개 테이블(06-23 대비 +19개 신규) 정체, production_plans 부재 지속
5. **결함 지표**: 6-튜플 중복 4행/빈 필드 5건/color2 White 180 158건 — 모두 07-03 대비 변동 없음 (정체)
6. **Swap**: 95% → 50% 개선, 관찰 지속
7. **핵심 액션**: systemd 등록(즉시) + 사용자 결정(침묵/디스크/production_plans/pending)

---

## References

- `references/vf2-production-plan-nightly-canonical.md` (canonical 절차)
- `references/vf2-nightly-2026-07-03-2nd-cron.md` (직전 07-03 2차 cron 보고서)
- `references/vf2-nightly-2026-07-03.md` (07-03 1차 cron 학습 시사점)
- `references/vf2-nightly-2026-07-02.md` (07-02 학습 시사점: inline 1-liner 확정, pg_stat stale, 디스크 재가속)
- `references/vf2-nightly-2026-07-01.md` (07-01 학습 시사점: heredoc approval_pending, inline 1-liner, 디스크 재가속)
- `~/Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260703-2nd-cron.md` (직전 보고서 원본)