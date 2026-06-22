# VF2 Project Nightly — 2026-06-23 자가 점검 보고 (2차)

> 크론: VF2-Project-Nightly (scheduled cron)
> 절차: SOUL.md 5단계 + canonical §1~§7
> 직전 보고: 05:34 Production-Plan-Nightly (동일 시스템 상태)

## SOUL.md 5단계 체크리스트

| 단계 | 수행 결과 | skip |
|:-:|------|:--:|
| 1. Wiki 검색 | 직전 05:34 보고서 `VF2-Production-Plan-Nightly-20260623.md` 확인 | — |
| 2. 스킬 로드 | `vf2` umbrella + canonical reference + 06-23 nightly reference 로드 | — |
| 3. 질문/실행 구분 | cron scheduled → 자동 실행 | — |
| 4. 검증 | §1 헬스 → §2 SQL 7종 → §3 침묵 → §4 디스크 | — |
| 5. 승인 | read-only cron, 사용자 결정 대기 항목만 보고 | — |

> USER.md / MEMORY.md / mandatory-verification 단일 스킬 부재 — skip 명시.

## ① 시스템 상태 (05:34 대비 변동)

| # | 점검 | 06-23 2차 (06:31) | 06-23 1차 (05:34) | 변동 |
|:-:|:-----|:----:|:----:|:--:|
| 1 | uptime | 10h 18m | 9h 19m | 동일 부트 (재부팅 없음) |
| 2 | 백엔드 5176 | 🚨 **DOWN** (curl exit 7) | 🚨 DOWN | **변동 없음** |
| 3 | 프론트엔드 5174 | 🚨 **DOWN** | 🚨 DOWN | **변동 없음** |
| 4 | 백엔드 프로세스 | 🚨 **0건** | 🚨 0건 | **변동 없음** |
| 5 | Vite 프로세스 | 🚨 **0건** | 🚨 0건 | **변동 없음** |
| 6 | PostgreSQL 컨테이블 | ✅ Up 10 hours | ✅ Up 9 hours | — (Docker restart policy) |
| 7 | DB 접속 (psql direct) | ✅ 정상 (15,886건) | ✅ 정상 | — |
| 8 | 디스크 | ⚠️ **75%** | ⚠️ 75% | **변동 0** |
| 9 | 메모리 | ✅ 5.4G/14G | ✅ 5.4G/14G | **변동 0** |
| 10 | Git working tree | ✅ clean (29건 유지, VF2 repo) | ⚠️ 29건 | — |
| 11 | backend.log 마지막 | 2026/06/19 - 16:58:37 | 동일 | — |

**요약**: 05:34 1차 점검 이후 **1시간 경과, 모든 지표 변동 0**.

## ② DB 점검 (SQL 7종 — 05:34 대비 변동 0)

| # | 쿼리 | 06-23 2차 결과 | 1차 대비 변동 |
|:-:|------|------|:--:|
| (a) | production_logs 행수 | **15,886** | 변동 0 |
| (b) | status 분포 | started 10,916 / pending 4,967 / ended 3 | 변동 0 |
| (c) | max_date | **2026-06-09** (375 distinct dates) | 변동 0 |
| (d) | 1:1 위반 (운영 2026) | **0건** | 변동 0 |
| (d-h) | 1:1 위반 (historical) | **15종** (mold 40→6, 115→5, 114→5 ...) | 변동 0 |
| (e) | 6-튜플 중복 (운영 2026) | **2그룹 4행** (mold 111 Butter, 06-08·09, unit_qty=30, YELLO-3093) | 변동 0 (15일째) |
| (f) | 빈 필드 | mold 1 / color1 1 / color2 3 | 변동 0 |
| (g) | WHITE 180 ILIKE | WHITE 180: 148 / White 180: 10 = **158건** | 변동 0 |
| (h) | production_plans | `to_regclass → NULL` (부재) | NN일째 |
| (i) | 2026 일자별 | 06-09:50 / 06-08:40 / 06-07:38 / 06-02:36 / 06-01:49 / 05-24:1 / 05-21:46 / 05-17:95 = **355행** | 변동 0 |

> ⚠️ 정확 카운트: 모든 수치는 SQL `COUNT(*)` 결과 (손 row 카운트 아님).

## ③ 운영 침묵 측정

- backend.log production-log POST/PUT/DELETE: **0건** (백엔드 다운, 06-19 16:58 마지막 로그)
- max_date 기준: **2026-06-09 → 14일째 침묵**
- 단순 계산: 4일 (06-19 마지막 로그 → 06-23)
- 임계치 ≥3일 **11일째 초과**
- ⚠️ 백엔드 다운으로 인한 인위적 침묵 포함 (DB는 정상이므로 max_date 기준은 유효)

## ④ 디스크 가속 추세

| 일자 | 절대값 | 일변화 | 판정 |
|:----:|------:|------:|:----:|
| 06-19 | 73% | +3%p/일 | 가속 4일째 |
| 06-23 (1차) | 75% | +2%p/4일 ≈ 0.5%p/일 | **일시 둔화** |
| **06-23 (2차)** | **75%** | **0%p/1시간** | **일시 정체 유지** |

- 90%까지 ~30일 잔여 (추정)
- 백엔드 다운 중 활동 감소로 가속 둔화 가능성 → "일시 둔화" 표기 유지 (canonical §4.2)

## ⑤ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 🚨 백엔드/프론트엔드 DOWN (재부팅 후 미복구) | 서비스 전면 중단 | ⏳ 사용자 | 1차와 동일 |
| 2 | 운영 침묵 14일째 (max_date 기준) | 등록 의도 | ⏳ 사용자 | +0일 (동일) |
| 3 | 6-튜플 중복 mold 111 Butter (4행) | 운영 정확성 | ⏳ 사용자 | 15일째 |
| 4 | 데크타일(114) color2 빈값 3건 | 룰 위반 | ⏳ 사용자 | 16일째 |
| 5 | VF2 Git working tree 29건 | 정리 필요 | ⏳ 사용자 | 동일 |
| 6 | `production_plans` 테이블 부재 | import 대상 누락 | ⏳ 사용자 | NN일째 |
| 7 | `inventory/baseline` GET 404 | API 라우트 누락 | ⏳ 사용자 | 5일째 |
| 8 | `inventory/stock` GET 404 | API 라우트 누락 | ⏳ 사용자 | 5일째 |
| 9 | WHITE 180 대소문자 158건 | 표기 통일 | ⏳ 사용자 | 동일 |

## ⑥ 결론

**06-23 2차 점검 (06:31 KST) 결과: 05:34 1차 점검 대비 변동 0건.**

- 🚨 **CRITICAL**: 백엔드/프론트엔드 DOWN 상태 지속 (재부팅 후 ~10시간 미복구)
- DB는 정상 (15,886건, 모든 SQL 결과 동일)
- 디스크 75% (일시 정체 유지)
- 운영 침묵 14일째 (백엔드 다운으로 인한 인위적 침묵 포함)

**사용자 액션 필요**:
1. 🔴 **백엔드/프론트엔드 복구**: `cd /home/comtop/workspace/VF2/backend && ./start.sh` + `cd frontend && npm run dev`
2. 백엔드 복구 후 침묵 상태 재평가 필요

## References

- canonical: `references/vf2-production-plan-nightly-canonical.md` (6/17 통합)
- 06-23 1차: `references/vf2-nightly-2026-06-23.md`
- 직전 보고서: `Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260623.md`
