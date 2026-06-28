# VF2 Project Nightly — 2026-06-29 자가 점검 보고

## 0. SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 동작 | 결과 |
|:-:|------|------|
| 1. Wiki 검색 | 직전 보고서 `VF2-Project-Nightly-20260627.md` 발견 | ✅ 발견 (2일 부재, 8일 미만 → §7 #23 단기 부재) |
| 2. 스킬 로드 | `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md` | ✅ 로드 완료 |
| 3. 질문/실행 구분 | cron scheduled → 자동 실행 (read-only) | ✅ 실행 |
| 4. 검증 | §1 health → §2 SQL 7종 → §3 침묵 → §4 디스크 | ✅ 완료 (DB 28 tables, production_logs 15,886 정상) |
| 5. 승인 | 사용자 결정 대기 항목만 보고. DB 직접 수정 금지 | ✅ read-only |

**Skip 명시**: USER.md / MEMORY.md / `vf2-production-plan-conventions` (단일 스킬) 부재 → skip. `mandatory-verification` 부재 → skip.

## ① 시스템 상태

| # | 항목 | 값 | 판정 |
|:-:|------|----|:----:|
| 1 | uptime | 6일 10시간 (마지막 재부팅 ~06-22 20:13) | ⚠️ §1.2 백엔드 DOWN 프로토콜 발동 확인 |
| 2 | 5176 Listen | **NONE (curl exit 7)** | 🚨 **백엔드 DOWN 7일째** (06-22~) |
| 3 | 5174 Listen | **NONE** | 🚨 **프론트엔드 DOWN 7일째** |
| 4 | vf2_backend_bin process | 0건 | 🚨 |
| 5 | vite (5174) process | 0건 | 🚨 |
| 6 | PostgreSQL (postgres_hermes) | Up 6 days (Docker restart policy로 복구됨) | ✅ |
| 7 | curl /api/health | exit 7 (Connection refused) | 🚨 |
| 8 | backend.log 마지막 timestamp | **2026-06-19 16:58:37** (10일 침묵, 변동 0) | 🚨 |
| 9 | **디스크 /** | **41%** (06-27 93% → 06-29 41%, **-52%p/2일**) | ✅ 정상 범위 복귀 |
| 10 | DB 테이블 (pg_class fallback) | **28 tables** (06-27 28 → 06-29 28, 변동 0) | ✅ |
| 11 | production_plans 존재 | `to_regclass` 1행 BUT exists=빈문자열 (NULL) | ⚠️ 부재 (계승) |
| 12 | production_logs count | 15,886 (06-27 15,886 → 변동 0) | ✅ |
| 13 | pg_stat_user_tables | 0 rows (stale 통계, §7 #21 fallback pg_class 사용) | ⚠️ stale |

**🚨 시스템 종합**: 백엔드/프론트 7일째 DOWN 미복구 (systemd 등록 미실행 §7 #26 3회째 반복), **디스크 41%로 급락 (의심: 사용자 수동 cleanup)**. 침묵 19일째 (max_date 기준).

## ② 발견된 문제 (06-27 대비 변화 명시)

### 🚨 CRITICAL — 백엔드/프론트 7일째 DOWN

- **증상**: 5176/5174 LISTEN 0건, vf2_backend_bin + vite 프로세스 0건
- **원인**: systemd/s6 미등록, 재부팅 후 수동 복구 안 됨 (06-23 → 06-26 → 06-27 → **06-29 보고서** systemd 등록 미실행, **3회 반복**)
- **06-27 → 06-29 변화**: 변동 0 (계속 DOWN, **2일 추가 경과**)
- **영향**: production-log POST 자체 불가 → 침묵 일수 구조적 보장 (§3.3 침묵 보정)
- **권고**: `systemd 등록 (즉시 실행 의무, §7 #26 3회째 반복 경고)` + `./start.sh` + `npm run dev`

### ✅ **🆕 디스크 41%로 급락 (-52%p/2일)** — 사용자 수동 cleanup 추정

- **증상**: 06-27 93% → 06-29 41% (-52%p/2일, 약 -26%p/1일)
- **원인 추정**: nightly 2일 부재(06-28, 06-29 06:30 이전) 동안 사용자가 수동 cleanup 수행 (backend.log rotate, USB 백업 이동 등). **nightly cron 자체 부재 → disk 변동 미감지**.
- **현재 상태**: 91G used / 233G total / 131G 가용 (41%) → **정상 범위 복귀** (WARNING/CRITICAL 임계치 미만)
- **이전 가속 추세 무효화**: 06-23 75% → 06-27 93% 가속 추세는 cleanup으로 해소됨. carry-forward 정정 (§7 #2) 적용 → "WARNING/CRITICAL 해소" 표현 금지, "**사용자 수동 cleanup 추정**"으로 보고.
- **권고**: cleanup 원인 확인 (어떤 경로/파일을 정리했는지) → 다음 nightly에서 동일 패턴 방지. **disk free 추세는 정상이지만, cleanup 메커니즘 자동화 필요** (예: backend.log rotate + USB 백업 cron).

### 🚨 운영 침묵 19일 (max_date 기준)

- **max_date**: 2026-06-09 (15,886행, dates=375)
- **침묵 계산**:
  - 단순 계산 (마지막 POST 시점 기준): **10일** (06-19 16:58 → 06-29 06:31, backend.log 마지막 GIN 기록)
  - **max_date 기준: 19일** (06-09 → 06-29, 운영상 마지막 등록일, 더 보수적)
- **06-27 → 06-29**: 변동 0 (DB 15,886 변동 0, 백엔드 DOWN으로 변동 불가)
- **원인**: 백엔드 DOWN으로 인위적 침묵 (사용자 의도 침묵과 구분 불가, §3.3)
- **판정**: max_date 기준 ≥3일 임계치 도달 (3.2) — 사용자 확인 요청 (계승)

### 📊 SQL 7종 결과 (06-27 대비)

| SQL | 결과 | 06-27 대비 |
|:---:|------|:---------:|
| (a) pg_stat_user_tables | 0 rows (stale, fallback pg_class 사용) | 변동 0 (계속 stale) |
| (a-fallback) pg_class | **28 tables** (06-27 28 → 06-29 28, 변동 0) | ✅ |
| (b) status | started=10,916 / pending=4,967 / ended=3 | 변동 0 |
| (c) max_date | 2026-06-09 (침묵 19일) | 변동 0 |
| (d) 운영 2026 1:1 위반 | 0건 (mold 중복 없음) | 변동 0 |
| (d-h) historical 1:1 위반 | **15종** (mold 40=6 names, 115/114/34=5, ...) | 변동 0 |
| (e) 6-튜플 운영 중복 | **4행** (mold 111 Butter YELLO-3093 unit=30: 6/8·6/9 각 2건×2일 = 4행) | 변동 0 (06-27 4행과 일치) |
| (f) 빈 필드 합계 | blank_mold=1 / blank_color1=1 / blank_color2=3 | 변동 0 |
| (g) color2 WHITE 180 | WHITE 180=148 + White 180=10 = **158건** (ILIKE 정확) | 변동 0 |
| **(h) inventory_stock 침묵 (§7 #28)** | max_updated=06-10 01:42 UTC, silence=18일 19시간 | ⚠️ 침묵 진행 중 |
| (i) production_logs count | 15,886 (변동 0) | ✅ |

### 🔍 신규 발견 / 정정

1. **🆕 디스크 41% 급락 (carry-forward 정정, §7 #2)**: 06-27 93% → 06-29 41% (-52%p/2일). nightly 2일 부재(06-28, 06-29 06:30 이전) 동안 사용자 수동 cleanup 추정. 06-27 보고서의 "CRITICAL +4%p/1일 가속" 추세는 cleanup으로 무효화됨. **"WARNING/CRITICAL 해소" 표현 금지** 정책 적용 → "사용자 수동 cleanup 추정"으로 표현. §7 #2 carry-forward 금지 + cleanup 메커니즘 자동화 권고.
2. **🆕 inventory_stock 침묵 18일 19시간 (계승 + 측정)**: 06-10 01:42 UTC 마지막 updated_at → 18일 정체. §7 #28 `updated_at` 컬럼 정책 적용, `SELECT MAX(updated_at)` 사용. 침묵 일수와 무관한 별도 동기화 메커니즘으로 보임 (재고 데이터 미갱신).
3. **🆕 inventory_items 0 rows (계승)**: 06-27 신규 발견 테이블, 여전히 데이터 미수신.
4. **6-튜플 중복 변동 0 (06-27 4행 → 06-29 4행)**: 06-26 5건 → 06-27 4행 정정 후 06-29까지 유지. carry-forward 정정 안정화 확인.
5. **backend.log 10일 침묵**: 06-19 16:58:37 마지막 GIN 기록 → 10일 정체 (06-27 8일 → 06-29 10일, +2일). §3.1 `grep -a` 적용, 0 hit.
6. **🆕 보고서 2일 부재 (06-28, 06-29 06:30 이전)**: §7 #23 단기 부재 (8일 미만). 장기 부재 프로토콜은 미발동이지만, 2일 부재 동안 **disk 52%p 변동 + cleanup 미감지** 사례 → **nightly cron 자체 부재가 cleanup 메커니즘을 놓치는 위험** 확인. 별도 watchdog cron 필요 (계승 권고).

## ③ 사용자 확인 요청

### Q1. 백엔드/프론트 복구 + systemd 등록 (즉시, 3회 반복 경고)

**상황**: **7일째 DOWN 미복구**, 06-23 → 06-26 → 06-27 → 06-29 보고서 **3회 systemd 등록 권고 미실행** (§7 #26 3회째 반복, **CRITICAL 위반 누적**).

**가능성 표**:

| # | 가능성 | 확인 방법 | 액션 |
|:-:|--------|----------|------|
| A | 사용자가 수동 기동 대기 | uptime 6일 (재부팅 후 미복구 6일 경과) | 즉시 `./start.sh` + `npm run dev` |
| B | systemd 등록 누락 | `/etc/systemd/system/vf2-backend.service` 부재 확인 | 단위 파일 작성 + `daemon-reload && enable --now` |
| C | 의도된 DOWN (유지보수) | cron 변동 0 + 사용자 응답 부재 | 사용자 확인 필요 |
| D | 사용자 cleanup 작업 중 의도적 DOWN | disk 41% 급락 = cleanup 작업 추정 | cleanup 완료 후 복구 |

**권고**: A+B 동시 실행 (수동 기동 후 systemd 영구 등록). **3회 반복 경고**: §7 #26 "systemd 등록은 권고가 아닌 즉시 실행 의무" 정책에 따라 CRITICAL 강조.

### Q2. 디스크 41% cleanup 원인 확인

**상황**: 06-27 93% → 06-29 41% (-52%p/2일). 사용자 수동 cleanup 추정, nightly 2일 부재로 cleanup 메커니즘 미감지.

**가능성 표**:

| # | 가능성 | 영향 | 액션 |
|:-:|--------|------|------|
| A | backend.log rotate / truncate | 100% 미사용 log | OK (cleanup 정당) |
| B | USB 백업 이동 | 50GB+ 누적 정리 | OK (cleanup 정당) |
| C | production_logs 정리 | 데이터 손실 위험 | ⚠️ 사용자 확인 (DB 15,886 변동 0 = 무손실로 보임) |
| D | PostgreSQL WAL/archive 정리 | archive_command 점검 | OK (cleanup 정당) |
| E | 의도하지 않은 데이터 손실 | nightly 부재로 미감지 | ⚠️ 사용자 인지 확인 |

**권고**: cleanup 경로/파일 사용자가 인지하고 있는지 확인. **cleanup 메커니즘 자동화**: `backend.log` rotate cron + USB 백업 cron + WAL archive cleanup cron. **nightly watchdog cron 별도 권고** (2일 부재 방지를 위해).

### Q3. 침묵 19일 사용자 인지 (계승)

**상황**: max_date 06-09 → 19일 무등록 (백엔드 DOWN으로 인위적 침묵이지만 DB 정합성 확인 필요).

**가능성 표**:

| # | 가능성 | 확인 방법 | 액션 |
|:-:|--------|----------|------|
| A | 사용자 1.xlsx import 후 자연 정체 | pending 4,967건 status | 사용자 결정 대기 |
| B | 백엔드 DOWN으로 인한 인위적 침묵 | DB 직접 SELECT (이미 확인) | 백엔드 복구 후 자동 해소 |
| C | 등록 누락 (의도 침묵) | status 분포 점검 | 사용자 확인 필요 |

## ④ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 백엔드/프론트 7일째 DOWN (systemd 미등록 3회 반복) | 모든 API 정지 | 🚨 사용자 즉시 | 5일째 → 7일째 |
| 2 | **🆕 디스크 41% cleanup 원인 미확인** | cleanup 자동화 부재 | 👀 사용자 확인 | 93% → 41% (cleanup 추정) |
| 3 | 운영 침묵 19일 (max_date 06-09) | 등록 의도 | ⏳ 사용자 | 18일 → 19일 |
| 4 | 운영 6-튜플 중복 mold 111 Butter YELLO-3093 4행 | 운영 정확성 | ⏳ 사용자 | 변동 없음 (4행 안정) |
| 5 | 데크타일(114) color2 빈값 2건 (6/7) | 룰 위반 | ⏳ 사용자 | 변동 없음 |
| 6 | 운영 blank_mold 1건 (5/24 M01) | 노이즈 | ⏳ 사용자 | 변동 없음 |
| 7 | started 10,916건 (옵션 1·2·3) | UI 표시 정책 | ⏳ 사용자 | 변동 없음 |
| 8 | 운영 (mold, product) 1:1 위반 | 룰 위반 | ✅ | 0건 (정상) |
| 9 | color2 WHITE 180 158건 (WHITE=148 + White=10) | 표기 통일 | ⏳ 사용자 | 변동 없음 |
| 10 | production_plans 부재 | 1.xlsx import 누락 단서 | ⏳ 사용자 | 변동 없음 |
| 11 | **🆕 inventory_stock 침묵 18일 19시간** | 재고 동기화 정지 | ⏳ 사용자 | 17일 → 18일 19시간 (진행) |
| 12 | inventory_items 0 rows (빈 테이블) | 신규 테이블 데이터 미수신 | ⏳ 사용자 | 변동 없음 |
| 13 | **🆕 nightly 2일 부재 (06-28, 06-29 06:30 이전)** | cleanup 미감지 사례 | 👀 watchdog cron 권고 | 2일 부재 |

## ⑤ 액션/옵션

### 즉시 (사용자 결정 대기)

1. **백엔드/프론트 복구 + systemd 등록**: §7 #26 3회째 반복 — **CRITICAL 즉시 실행 의무**
   ```bash
   cd /home/comtop/workspace/VF2/backend && ./start.sh
   cd /home/comtop/workspace/VF2/frontend && npm run dev
   sudo tee /etc/systemd/system/vf2-backend.service > /dev/null << 'EOF'
   [Unit]
   Description=VF2 Backend (vf2_backend_bin)
   After=network.target docker.service
   [Service]
   WorkingDirectory=/home/comtop/workspace/VF2/backend
   ExecStart=/home/comtop/workspace/VF2/backend/vf2_backend_bin
   Restart=on-failure
   RestartSec=5
   [Install]
   WantedBy=multi-user.target
   EOF
   sudo systemctl daemon-reload && sudo systemctl enable --now vf2-backend
   ```
2. **디스크 cleanup 원인 확인**: 06-27 93% → 06-29 41% 변동 원인 사용자가 인지하고 있는지 확인
3. **cleanup 메커니즘 자동화**: backend.log rotate cron + USB 백업 cron + WAL archive cleanup cron

### 시스템 (장기)

4. **nightly watchdog cron**: 2일 부재 방지를 위해 별도 watchdog cron (예: 매일 06:00에 VF2-Project-Nightly-YYYYMMDD.md 존재 여부 확인, 부재 시 알림) 권고
5. 침묵 일수 두 가지 기준 보고 정책 (단순 + max_date) 유지
6. carry-forward 정정 강화 — 매 실행 SQL 재측정
7. 시스템 재부팅 시 systemd 자동 시작 보장 (Q1 systemd 등록)

## ⑥ 디스크 추이 (cleanup 추정)

| 일자 | 사용량 | 일일 Δ | 판정 |
|:----:|:------:|:------:|:----:|
| 06-23 | 75% | - | ⚠️ WARNING |
| 06-24 | 79% | +4%p | ⚠️ WARNING |
| 06-26 | 89% | +5%p/2일 | 🚨 CRITICAL 임박 |
| 06-27 | 93% | +4%p/1일 | 🚨 CRITICAL |
| 06-28 | (nightly 부재) | ? | ⚠️ 미측정 |
| 06-29 | **41%** | -52%p/2일 (-26%p/1일) | ✅ 정상 범위 (cleanup 추정) |

**추세 판정**: 06-23~06-27 가속 → **06-29 cleanup 추정으로 정상화**. "WARNING/CRITICAL 해소" 표현 금지 (§7 #2 carry-forward 정책) → "**사용자 수동 cleanup 추정**"으로 보고. cleanup 메커니즘 자동화 권고 (Q2).

## ⑦ 결론

🚨 **CRITICAL**:
- **백엔드/프론트 7일째 DOWN** (systemd 미등록 3회 반복 경고) → 사용자 즉시 액션 (Q1)
- **디스크 41% cleanup 추정** (nightly 2일 부재로 cleanup 미감지) → cleanup 메커니즘 자동화 권고 (Q2)
- **침묵 19일 (max_date 기준)** → 백엔드 복구 후 자동 해소 (Q3)

SQL 7종 정밀 카운트 결과 carry-forward 정정 0건 (06-27 4행과 일치). 신규 발견: 디스크 41% cleanup 추정 + inventory_stock 침묵 18일 19시간 + nightly 2일 부재 (06-28, 06-29 06:30 이전) → cleanup 메커니즘 자동화 + watchdog cron 권고.

## References

- 직전 보고서: `VF2-Project-Nightly-20260627.md` (2일 전 06-27 06:30)
- 직전 동일 prefix: `VF2-Project-Nightly-20260627.md` (06-28 부재, 06-29 06:30 1회차)
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (06-27 28 → 06-29 28, 변동 0)
- 점검 시각: 2026-06-29 06:31:30 KST
- 스킬 부재: `vf2-production-plan-conventions` (loadable skill 부재, skip)
- USER.md / MEMORY.md 부재: skip
- 단기 부재: 06-28, 06-29 06:30 이전 (2일 부재, §7 #23 8일 미만)
- 디스크 41% cleanup 추정: 06-27 93% → 06-29 41% (-52%p/2일), nightly 2일 부재로 cleanup 메커니즘 미감지
- systemd 미등록 3회 반복: 06-23 → 06-26 → 06-27 → 06-29 보고서, §7 #26 즉시 실행 의무 CRITICAL
