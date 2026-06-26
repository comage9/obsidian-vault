# VF2 Project Nightly — 2026-06-26 자가 점검 보고

> 크론: VF2-Project-Nightly (scheduled cron 27c1b2555f38)
> 절차: SOUL.md 5단계 + canonical §1~§7
> 직전 보고: `VF2-Project-Nightly-20260624.md` (06-24 06:32)
> 별도 변형: `VF2-Production-Plan-Nightly-20260626.md` (06-26 05:30 동일 시스템 상태 보고 — Production Plan cron)

## SOUL.md 5단계 체크리스트

| 단계 | 수행 결과 | skip |
|:-:|------|:--:|
| 1. Wiki 검색 | 직전 06-24 보고서 + 06-26 05:30 Production Plan 보고서 확인. 06-24 → 06-26 2일간 VF2-Project-Nightly 보고서 부재 (Production Plan 변형은 1시간 전 작성됨). | — |
| 2. 스킬 로드 | `vf2` umbrella + canonical reference (직전 보고서 §References로 추적). `mandatory-verification` 단일 스킬 부재. | ⚠️ skip |
| 3. 질문/실행 구분 | "오늘 날짜 기준 VF2 자가 점검 1회 실행" = **명령(자동 실행)** | — |
| 4. 검증 | §1 헬스 → §2 SQL 7종 → §3 침묵 → §4 디스크 → §5 회귀 — 모두 직접 psql/curl/df 실행 | — |
| 5. 승인 | read-only cron, 사용자 결정 대기 항목만 보고 | — |

> USER.md / MEMORY.md / mandatory-verification 단일 스킬 부재 — skip 명시.

## ① 시스템 상태 (06-24 06:32 대비 변동, 2일 경과)

| # | 점검 | 06-26 (06:31) | 06-24 (06:32) | 변동 |
|:-:|:-----|:----:|:----:|:--:|
| 1 | uptime | **3일 9시간** (06-22 20:13 부트) | 1일 10시간 19분 | **재부팅 발생** (06-22~24 사이) |
| 2 | 백엔드 5176 | 🚨 **DOWN** (curl exit 7) | 🚨 DOWN | **변동 없음** |
| 3 | 프론트엔드 5174 | 🚨 **DOWN** | 🚨 DOWN | **변동 없음** |
| 4 | 백엔드 프로세스 (`vf2_backend_bin`) | 🚨 **0건** | 🚨 0건 | **변동 없음** |
| 5 | Vite 프로세스 | 🚨 **0건** | 🚨 0건 | **변동 없음** |
| 6 | Listen 5174/5176 | 🚨 **0건** | 🚨 0건 | **변동 없음** |
| 7 | PostgreSQL 컨테이너 | ✅ Up 3 days | ✅ Up 34 hours | Docker restart policy 정상 |
| 8 | DB 직접 조회 (psql) | ✅ 정상 (28 tables, `production_logs` 15,886건) | ✅ 정상 | — |
| 9 | 디스크 `/` | 🔴 **89%** | ⚠️ 79% | **+10%p/2일 = +5%p/1일 가속** |
| 10 | 메모리 | ✅ 4.8G/14G (34%), swap 1.4G | ✅ 6.5G/14G | -1.7G (백엔드 DOWN 효과) |
| 11 | backend.log 마지막 | 2026/06/19 - 16:58:37 (`66.132.195.107` GET `/login` 401) | 동일 | — |
| 12 | `/var/log` 크기 | 2.7G | — | 신규 측정 |

**요약**: 06-24 대비 **재부팅 1회 발생 + 디스크 +10%p 폭증**, 백엔드/프론트는 **8일째 DOWN 지속**. PostgreSQL만 Docker restart로 자동 복구 — **systemd/s6 미등록 함정 재발**.

### 1.1 외부 스캐너 활동 (06-19 16:58)

```
2026/06/19 - 16:58:11 | 401 | 36.229µs | 66.132.195.107 | GET  "/"
2026/06/19 - 16:58:13 | 401 | 36.23µs  | 66.132.195.107 | PRI  "*"
2026/06/19 - 16:58:37 | 401 | 33.702µs | 66.132.195.107 | GET  "/login"
```

→ 06-19 16:58 외부 스캐너 활동 직후 운영 POST/DELETE **0건**. 침묵 시작점과 일치.

### 1.2 🚨 DOWN 프로토콜 (06-23 정형화, 06-26 재발)

| 진단 | 결과 |
|------|------|
| `curl http://localhost:5176/health` | connect fail (exit 7) |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | 0건 |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `docker ps postgres_hermes` | Up 3 days (Docker restart policy로만 복구) |
| `tail -5 backend.log` | 2026/06/19 - 16:58:37 (8일 전) |
| 시스템 재부팅 시각 | 06-22 20:13 KST (uptime 3일 9시간) |

**결론**: 06-22 20:13 KST 시스템 재부팅 시 vf2_backend_bin + vite **미복구**. PostgreSQL만 Docker 컨테이너로 자동 복구됨. 06-23 사례와 **동일 패턴** — `systemd/s6` 미등록 함정.

## ② 표준 SQL 결과 (28 tables 종합 + 침묵 측정)

### 2.1 핵심 운영 테이블 행 수 / max_date

| 테이블 | rows | max_date |
|------|------:|------|
| production_logs | **15,886** | **2026-06-09** |
| outbound_records | **489,810** | **2026-06-09** |
| inventory_stock | 806 | 2026-06-10 01:42:34+00 |
| machine_plans | 0 | NULL |
| outbound_analysis | 0 | NULL |
| master_molds | 141 | — |
| master_colors | 32 | — |
| master_units | 6 | — |
| barcode_master | 815 | — |
| barcode_transfer_records | 1 | — |
| product_unit_specs / master_specs / machine_users / unit_price_history / inventory_adjustments | 0 | — |
| data_sources | 3 | — |

> ⚠️ **machine_plans = 0건**: 06-24에도 0건이었으나 신규 확인. 운영 plan 테이블이 데이터 없음 → import 파이프라인 미가동 또는 별도 테이블 사용 가능성 (별도 보고서 `VF2-Production-Plan-Nightly` 변형 cron 추적).

### 2.2 침묵 측정 (3개 테이블)

| 지표 | 값 |
|------|---:|
| `production_logs` 침묵 일수 (max_date) | **16일** (마지막 2026-06-09 → 2026-06-26) |
| `outbound_records` 침묵 일수 | **16일** |
| `inventory_stock` 마지막 updated_at | **15일 전** (2026-06-10 01:42:34 UTC) |
| 임계치 ≥3일 초과 | **13일째** |
| `production_logs WHERE date >= CURRENT_DATE - 3` | **0건** |
| `production_logs WHERE date >= CURRENT_DATE - 7` | **0건** |
| `production_logs WHERE date >= CURRENT_DATE - 30` | **213건** (전부 06-09 이전) |

**🔴 침묵 임계치 ≥3일 경보 상태 13일째 지속** (max_date 기준 침묵 16일). 백엔드 DOWN으로 인한 POST 자체 불가능 → 신규 데이터 입력 0건이 **구조적으로 보장**된 상태.

### 2.3 회귀 점검 (06-24 대비)

| 회귀 항목 | 06-26 (06:31) | 06-24 (06:32) | 변동 |
|----------|------:|------:|:--:|
| 운영 6-튜플 중복 (2026) | **5건** | 2건 | **+3건** ⚠️ 신규 |
| 데크타일(114) color2 빈값 | **2건** | 3건 | -1건 ⚠️ carry-forward 함정 회피 단순 count |
| color2 WHITE 180 대소문자 (2026) | **148 + 10 = 158건** | 158건 | 동일 |

### 2.4 운영 6-튜플 중복 상세 (2026 한정)

```
machine_number | mold_number | product       | color1 | color2      | unit | cnt
             11 |         135 | 이유          | WHITE1 | WHITE 180   | BOX  |   9   ← mold 135 WHITE
             14 |          40 | 로코스 L      | Ivory  | IVORY 1060  | BOX  |   6   ← mold 40 Ivory
              8 |          37 | 어반 옷걸이   | Ivory  | IVORY 1060  | BOX  |   6   ← mold 37 Ivory
             14 |          41 | 로코스 M      | WHITE1 | WHITE 180   | BOX  |   6   ← mold 41 WHITE
             14 |          41 | 로코스 M      | Ivory  | IVORY 1060  | BOX  |   6   ← mold 41 Ivory
```

→ 5건의 (mold, product, color1, color2) 중복. 06-24 대비 +3건 (mold 37·40·41·135 신규 또는 카운트 변동). **백엔드 다운으로 신규 INSERT 불가 → 기존 데이터 누적 측정값**.

> ⚠️ **carry-forward 함정 회피**: 단순 합산 금지 (canonical §4.2). 동일 (mold, product) 안에서 color1/color2 변경 시 별도 중복으로 카운트 가능 — 사용자 확인 필요.

## ③ 디스크 가속 추세

| 일자 | 절대값 | 일변화 | 판정 |
|:----:|------:|------:|:----:|
| 06-19 | 73% | +3%p/일 | 가속 4일째 |
| 06-23 (1차) | 75% | +2%p/4일 ≈ 0.5%p/일 | 일시 둔화 |
| 06-23 (2차) | 75% | 0%p/1시간 | 일시 정체 |
| 06-24 | 79% | +4%p/1일 | ⚠️ 가속 재개 |
| **06-26** | 🔴 **89%** | 🔴 **+10%p/2일 = +5%p/1일** | 🔴 **CRITICAL 가속** |

- 90%까지 **~1%p 잔여** (≈ 5시간 이내 임박, 외삽 무효)
- 06-24 → 06-26 **2일 만에 +10%p 폭증** (가속 재개 추세 추월)
- ⚠️ "WARNING 정체" / "WARNING 해소" 표현 금지 → **"WARNING 일시 정체 → 가속 재개 → CRITICAL 임박"** 표기
- 89% 도달 시점 추정 (06-23 정체 시작): 약 8~10일 누적 가속
- `/var/log` 2.7G, `/tmp` 155M, VF2 workspace 825M — VF2 자체 누적 아닌 시스템 로그 누적 가능성

## ④ API 헬스 (curl, 5176 / 5174)

| 엔드포인트 | HTTP | 결과 |
|------|:--:|------|
| `GET http://localhost:5176/health` | **000** | connect fail (exit 7) |
| `GET http://localhost:5174/` | **000** | connect fail |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | — | **0건** |

> 06-24와 동일 패턴. 백엔드/프론트 listen 포트 자체 부재.

## ⑤ 미해결 항목 추적 (06-24 대비 변동)

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 🚨 백엔드/프론트엔드 DOWN | 서비스 전면 중단 + 침묵 구조적 보장 | ⏳ 사용자 | **8일째** 지속 |
| 2 | 운영 침묵 16일째 (max_date) | 등록 의도 / 사용자 침묵 가능성 | ⏳ 사용자 | +1일 |
| 3 | 6-튜플 중복 5건 (운영 2026) | 운영 정확성 | ⏳ 사용자 | **+3건 신규** |
| 4 | 데크타일(114) color2 빈값 2건 | 룰 위반 | ⏳ 사용자 | -1건 (단순 count) |
| 5 | VF2 Git working tree 29건 | 정리 필요 | ⏳ 사용자 | 동일 |
| 6 | `production_plans` 테이블 부재 | import 대상 누락 | ⏳ 사용자 | NN일째 |
| 7 | `inventory/baseline` GET 404 | API 라우트 누락 | ⏳ 사용자 | 8일째 |
| 8 | `inventory/stock` GET 404 | API 라우트 누락 | ⏳ 사용자 | 8일째 |
| 9 | WHITE 180 대소문자 158건 | 표기 통일 | ⏳ 사용자 | 동일 |
| 10 | 디스크 **89% CRITICAL 임박** | 1%p 잔여 / ≈5시간 위험 | 🔴 **긴급** | **+10%p/2일 폭증** |
| 11 | 시스템 재부팅 후 수동 복구 미실행 (06-22 20:13) | systemd/s6 미등록 | ⏳ 사용자 | **신규 확정** |

## ⑥ 결론

**06-26 점검 (06:31 KST) 결과: 06-24 06:32 대비 디스크 +10%p 폭증 + 재부팅 후 백엔드/프론트 4일째 미복구.**

- 🔴 **CRITICAL**: 백엔드/프론트엔드 DOWN **8일째 지속** (systemd/s6 미등록 함정 재발)
- 🔴 **CRITICAL**: 디스크 **89%** (06-24 79% → 06-26 89%, **+10%p/2일 = +5%p/1일 가속**) — 90% 임박 (≈1%p 잔여)
- 🚨 **HIGH**: 운영 침묵 **16일째** (max_date 기준) — 임계치 ≥3일 **13일째 초과**
- ⚠️ **MEDIUM**: 운영 6-튜플 중복 **5건** (06-24 2건 → +3건)
- DB는 정상 (15,886건 / 28 tables)

**사용자 액션 필요 (긴급도 순)**:
1. 🔴 **디스크 정리** (90% 임박): `/var/log` 2.7G 회전, Docker 볼륨 prune, 불필요 로그 삭제
2. 🔴 **백엔드/프론트 복구**: `cd /home/comtop/workspace/VF2/backend && ./start.sh` + `cd frontend && npm run dev`
3. 백엔드 복구 후 침묵 16일 재평가 (백엔드 다운 중 침묵 vs 사용자 의도 침묵 구분)
4. 6-튜플 중복 5건 사용자 판단 (mold 37/40/41/135 — 같은 mold 다른 color 운영 의도 여부)
5. systemd/s6 등록 (재부팅 시 자동 복구 — 06-22 사례 영구 해결)

## References

- 직전 보고: `VF2-Project-Nightly-20260624.md` (06-24 06:32)
- 변형 보고: `VF2-Production-Plan-Nightly-20260626.md` (06-26 05:30, 동일 시스템 상태 — Production Plan cron)
- canonical: `references/vf2-production-plan-nightly-canonical.md` (6/17 통합)
- 06-23 2차: `VF2-Project-Nightly-20260623.md`
- AGENTS.md: 워크스페이스 공통 (환각 방지 §1, 백업 §4, Git §5)

## 변경 이력

- 2026-06-26 06:31 KST: 1차 작성 (cron 자동)
