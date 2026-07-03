# VF2 Project Nightly — 2026-07-04 자가 점검 보고

**점검 시각**: 2026-07-04 05:35 KST (cron `27c1b2555f38`)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
**직전 보고서**: `VF2-Project-Nightly-20260703.md` (07-03 06:32 2차 cron)
**오늘 1차 cron**: `VF2-Production-Plan-Nightly-20260704.md` (예정, 05:00)
**비교 기준**: 직전 Project Nightly (07-03 06:32) 대비 변동

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:--:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 + 오늘 1차 cron 예정 확인 |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + canonical reference 로드 완료 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health 5종, DB SQL 7종, pg_class 28 tables, 침묵, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재.

---

## ① 시스템 상태 (직전 07-03 2차 cron 06:32 대비 변동)

| 지표 | 직전 (07-03 06:32) | **현재 (07-04 05:35)** | 변동 |
|------|---:|---:|:----:|
| **Health (51) Health (5176)** | `curl: (7)` | `curl: (7)` (port 미 Listen) | 🔴 동일 DOWN |
| **2) 백엔드 PID** | 0건 | **0건** | 🔴 **15일째 DOWN** |
| **3) Vite PID** | 0건 | **0건** | 🔴 **15일째 DOWN** |
| **4) uptime** | 10일 10시간 | **10일 11시간** | 재부팅 없음 |
| **5) 디스크 `/`** | 52% | **55%** | ⚠️ **+3%p/1일** |
| **6) 메모리** | 5.0Gi/14Gi | **6.5Gi/14Gi** | +1.5Gi 사용 증가 |
| **7) swap** | 3.8Gi/4.0Gi (95%) | **3.8Gi/4.0Gi (95%)** | ⚠️ 동일 (과다) |
| **8) PostgreSQL** | Up 10 days | **Up 10 days** | ✅ 동일 |
| **9) backend.log 마지막** | 06-19 16:58:37 | **06-19 16:58:37** | 변동 없음 (15일 전) |
| **10) DB 테이블** | 28개 | **28개** | ✅ 변동 0 |

**핵심**: 백엔드/프론트엔드 **15일째 DOWN** (06-19 16:58 이후), systemd/s6 미등록 **7회째** 권고 미실행. 디스크 55%로 WARNING 임계치(≥50% + ≥2%p/일) 진입 — §7 #34 재가속 패턴 5일째(07-01~07-04, 평균 +2.8%p/일).

---

## ② DB 정확 카운트 (SQL 재측정, carry-forward 금지)

| 항목 | 직전 (07-03 06:30) | **현재 (07-04 05:35)** | 변동 |
|------|---:|---:|:----:|
| production_logs 총 행 | 15,886 | **15,886** | 0 ✅ |
| started | 10,916 | **10,916** | 0 ✅ |
| pending | 4,967 | **4,967** | 0 ✅ |
| ended | 3 | **3** | 0 ✅ |
| max_date | 2026-06-09 | **2026-06-09** | 0 ✅ |
| (mold,product) 1:1 위반 (운영 2026) | 0건 | **0건** | 0 ✅ |
| 6-튜플 중복 (운영 2026) | 4행 | **4행** (06-08×2, 06-09×2) | 0 ✅ |
| blank mold (운영 2026) | 1 | **1** | 0 ✅ |
| blank color1 (운영 2026) | 1 | **1** | 0 ✅ |
| blank color2 (운영 2026) | 3 | **3** | 0 ✅ |
| color2 WHITE 180 variant | 148+10=158 | **148+10=158** | 0 ✅ |
| production_plans 테이블 | NULL (부재) | **NULL (부재)** | 동일 |

**결론**: DB 데이터 **완전 동결** — 백엔드 DOWN으로 어떤 데이터 변경도 불가능. pg_stat_user_tables 0 rows (stale 통계) → pg_class fallback으로 28개 테이블 확인 (06-17 9개 → 06-26 28개로 +19개 신규 후 정체). canonical §7 #24 §7 #25 테이블명 carry-forward 오기재 방지 차원에서 `to_regclass` 검증 완료.

---

## ③ 운영 침묵 — **25일** (max_date 기준)

- max_date: 2026-06-09 → **침묵 25일** (07-04 기준, 직전 24일 → +1일)
- 백엔드 DOWN 15일로 POST 자체 불가 → 침묵은 구조적으로 보장됨
- 단순 계산 (backend.log 마지막 POST 06-19 06:31): 15일 — max_date 기준이 더 보수적이고 본질적 의미

**판정**: 침묵 ≥ 3일 임계치 초과 지속 — 사용자 확인 요청 유지 (canonical §3.2).

---

## ④ 디스크 가속 추세

| 날짜 | 사용% | 일일 Δ | 판정 |
|------|---:|---:|:----:|
| 06-30 | 44% | (대규모 정리) | 정상 |
| 07-01 | 47% | +3%p | 정상 |
| 07-02 | 49% | +2%p | 정상 |
| 07-03 | 52% | +3%p | ⚠️ **WARNING (≥ 50% + ≥ 3%p/일)** |
| **07-04** | **55%** | **+3%p** | ⚠️ **WARNING 지속** |

- §7 #34 재가속 패턴 **5일째** (07-01~07-04, 평균 +2.8%p/일)
- §7 #35 예측 적중: 07-02 "약 1일 후 50% 도달" → 07-03 52% 정확히 적중 → 07-04 55% 지속
- 추세 지속 시 **~5일 후 70% 도달** (CRITICAL)

---

## ⑤ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 (직전 대비) |
|:-:|------|------|:---------:|:----:|
| 1 | 🔴 백엔드/프론트엔드 DOWN **15일째** | 전체 시스템 마비 | ⏳ 사용자 | +1일 |
| 2 | systemd/s6 미등록 (**7회째 권고 미실행**) | 재부팅 시 미복구 반복 | ⏳ 사용자 | 동일 |
| 3 | 운영 침묵 **25일** (max_date 기준) | 등록 정체 | ⏳ 사용자 | +1일 |
| 4 | ⚠️ 디스크 **55% WARNING** | 1~2개월 위험 | ⏳ 사용자 | 52%→55% |
| 5 | swap 95% (3.8Gi/4.0Gi) | 메모리 압박 → OOM 위험 | 👀 관찰 | 동일 |
| 6 | pending 4,967건 status 누적 | UI 표시 정책 | ⏳ 사용자 | 동일 |
| 7 | 6-튜플 중복 4행 (mold 111) | 운영 정확성 | ⏳ 사용자 | 동일 |
| 8 | color2 WHITE 180 variant 158건 | 표기 통일 | ⏳ 사용자 | 동일 |
| 9 | `production_plans` 테이블 부재 | import 누락 단서 | ⏳ 사용자 | 동일 |
| 10 | blank color2 3건 | 룰 위반 | ⏳ 사용자 | 동일 |

---

## ⑥ 결론

- 🔴 백엔드/프론트엔드 **15일째 DOWN** — systemd 미등록 **7회째** 권고 미실행 (P0 CRITICAL, canonical §7 #26)
- ⚠️ 디스크 **55% WARNING** — 50% 임계치 재돌파 후 +2.8%p/일 가속 5일째, 5일 내 70% CRITICAL 도달 예상
- DB 데이터 **완전 동결** (15,886행, max_date 06-09, 28개 테이블 정체)
- 침묵 **25일** — 백엔드 DOWN이 직접적 원인
- ⚠️ swap **95%** — 메모리 압박 지속, OOM killer 위험 (canonical §7 #36)

**즉시 조치 필요**:
1. **systemd 등록** — `vf2-backend.service` + `vf2-frontend.service` 생성 후 `systemctl enable --now` (canonical §1.2 §7 #26)
2. **디스크 원인 추적** — `du -h /home/comtop/workspace/VF2` 등 대용량 디렉토리 식별
3. **swap 압박 해소** — 메모리 누수 프로세스 식별 또는 swap 증설

---

## 3중 완료 (Wiki + Git push)

- ✅ Wiki 저장: `/home/comtop/workspace/Wiki/Hermes/자가-학습-Cron/VF2-Project-Nightly-20260704.md` (git repo 직접, canonical §7 #33)
- Git commit + push: cron 완료 후 수행
- log.md: 부재 (canonical §7 #31 fallback — 보고서 파일로 대체)

---

## References

- 직전 Project 보고서: `VF2-Project-Nightly-20260703.md` (07-03 06:32)
- 오늘 1차 cron 예정: `VF2-Production-Plan-Nightly-20260704.md` (05:00)
- canonical: `references/vf2-production-plan-nightly-canonical.md`
- 함정: §0.1 (같은 날 2회 실행), §7 #26 (systemd 7회째), §7 #33 (write_file git repo 경로), §7 #34 (디스크 재가속 5일째), §7 #35 (예측 적중 사이클 3일째), §7 #36 (swap 관찰), §7 #37 (terminal compound command guard)