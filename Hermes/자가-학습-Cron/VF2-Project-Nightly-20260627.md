# VF2 Project Nightly — 2026-06-27 자가 점검 보고

## 0. SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 동작 | 결과 |
|:-:|------|------|
| 1. Wiki 검색 | 직전 보고서 `VF2-Production-Plan-Nightly-20260626.md` 발견 | ✅ 발견 (어제 06-26 05:30, 1일 후 2회차) |
| 2. 스킬 로드 | `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md` | ✅ 로드 완료 |
| 3. 질문/실행 구분 | cron scheduled → 자동 실행 (read-only) | ✅ 실행 |
| 4. 검증 | §1 health → §2 SQL 7종 → §3 침묵 → §4 디스크 | ✅ 완료 (DB 28 tables, production_logs 15,886 정상) |
| 5. 승인 | 사용자 결정 대기 항목만 보고. DB 직접 수정 금지 | ✅ read-only |

**Skip 명시**: USER.md / MEMORY.md / `vf2-production-plan-conventions` (단일 스킬) 부재 → skip. `mandatory-verification` 부재 → skip.

## ① 시스템 상태

| # | 항목 | 값 | 판정 |
|:-:|------|----|:----:|
| 1 | uptime | 4일 10시간 (마지막 재부팅 ~06-23 20:12) | ⚠️ §1.2 백엔드 DOWN 프로토콜 발동 확인 |
| 2 | 5176 Listen | **NONE (curl exit 7)** | 🚨 **백엔드 DOWN 5일째** (06-23~) |
| 3 | 5174 Listen | **NONE** | 🚨 **프론트엔드 DOWN 5일째** (06-23~) |
| 4 | vf2_backend_bin process | 0건 (ki-ai-trader의 vite:3000만 동작) | 🚨 |
| 5 | vite (5174) process | 0건 | 🚨 |
| 6 | PostgreSQL (postgres_hermes) | Up 4 days (Docker restart policy로 복구됨) | ✅ |
| 7 | curl /api/health | exit 7 (Connection refused) | 🚨 |
| 8 | backend.log 마지막 timestamp | **2026-06-19 16:58:37** (8일 침묵) | 🚨 |
| 9 | **디스크 /** | **93%** (06-26 89% → 06-27 93%, **+4%p/1일**) | 🚨 **CRITICAL** (≥90%) |
| 10 | DB 테이블 (pg_class fallback) | **28 tables** (06-26 28 → 06-27 28, 변동 0) | ✅ |
| 11 | production_plans 존재 | `to_regclass → NULL` (빈행) | ⚠️ 부재 (계승) |
| 12 | production_logs count | 15,886 (06-26 15,886 → 변동 0) | ✅ |
| 13 | pg_stat_user_tables | 0 rows (stale 통계, §7 #21 fallback pg_class 사용) | ⚠️ stale |

**🚨 시스템 종합**: 백엔드/프론트 5일째 DOWN 미복구, 디스크 93% CRITICAL (가속 재개), 침묵 18일째 (max_date 기준). 06-23 보고서에서 systemd 등록 권고했으나 **미실행 → 5일째 반복** (§7 #26 위반).

## ② 발견된 문제 (06-26 대비 변화 명시)

### 🚨 CRITICAL — 백엔드/프론트 5일째 DOWN

- **증상**: 5176/5174 LISTEN 0건, vf2_backend_bin + vite 프로세스 0건
- **원인**: systemd/s6 미등록, 재부팅 후 수동 복구 안 됨 (06-23 보고서 권고 systemd 등록 **미실행**)
- **06-26 → 06-27 변화**: 변동 0 (계속 DOWN)
- **영향**: production-log POST 자체 불가 → 침묵 일수 구조적 보장 (§3.3 침묵 보정)
- **권고**: `systemd 등록 (즉시 실행 의무, §7 #26)` + `./start.sh` + `npm run dev`

### 🚨 CRITICAL — 디스크 93% (+4%p/1일)

- **절대값**: 233G 중 205G 사용, 17G 가용
- **추세**: 06-23 75% → 06-24 79% → 06-26 89% → **06-27 93%** (가속 재개, 06-26 일시 정체 해소 후 폭증)
- **일일 증가**: +4%p/1일 (06-26 89→93)
- **권고**: 1~2개월 위험 → 즉시 정리 (백업/로그 압축/`backend.log` 8일 정체 + production_logs 누적 등)

### 🚨 운영 침묵 18일 (max_date 기준)

- **max_date**: 2026-06-09 (15,886행, dates=375)
- **침묵 계산**:
  - 단순 계산 (마지막 POST 시점 기준): **8일** (06-19 16:58 → 06-27 06:30, backend.log 마지막 GIN 기록)
  - **max_date 기준: 18일** (06-09 → 06-27, 운영상 마지막 등록일, 더 보수적)
- **06-26 → 06-27**: 변동 0 (DB 15,886 변동 0)
- **원인**: 백엔드 DOWN으로 인위적 침묵 (사용자 의도 침묵과 구분 불가, §3.3)
- **판정**: max_date 기준 ≥3일 임계치 도달 (3.2) — 사용자 확인 요청

### 📊 SQL 7종 결과 (06-26 대비)

| SQL | 결과 | 06-26 대비 |
|:---:|------|:---------:|
| (a) pg_stat_user_tables | 0 rows (stale, fallback pg_class 사용) | 변동 0 (계속 stale) |
| (a-fallback) pg_class | **28 tables** (6/26 28 → 6/27 28, 변동 0) | ✅ |
| (b) status | started=10,916 / pending=4,967 / ended=3 | 변동 0 |
| (c) max_date | 2026-06-09 (침묵 18일) | 변동 0 |
| (d) 운영 2026 1:1 위반 | 0건 (mold 중복 없음) | 변동 0 |
| (d-h) historical 1:1 위반 | **15종** (mold 40=6 names, 115/114/34=5, ...) | 변동 0 |
| (e) 6-튜플 운영 중복 | **4행** (mold 111 Butter YELLO-3093 unit=30: 6/8·6/9 각 2건×2일 = 4행) | 06-26 5행 → 06-27 4행 (**-1행 정정**) |
| (f) 빈 필드 합계 | blank_mold=1 / blank_color1=1 / blank_color2=3 | 변동 0 |
| (g) color2 WHITE 180 | WHITE 180=148 + White 180=10 = **158건** (ILIKE 정확) | 변동 0 |

### 🔍 신규 발견 / 정정

1. **6-튜플 중복 carry-forward 정정 (06-26 5건 → 06-27 4행, §7 #2)**: 06-26 보고서가 5건으로 보고했으나 SQL 재측정 결과 4행 (6/8·6/9 각 unit=30 한정 2건씩 × 2일 = 4행). 06-26 보고서가 1행 과대. **§7 #2 carry-forward 금지 정책 적용 — SQL 재측정 결과 우선**.
2. **blank_color2 디테일**: 2026-06-07 mold 114 Ivory(1) + WHITE2(1), 2026-05-24 M01 빈 mold+color1+color2 (1). 운영 color2 빈값 3건 모두 디테일 확인.
3. **inventory_stock max_updated**: 2026-06-10 01:42:34 UTC (DB에 17일 정체). 침묵 일수와 무관 (별도 동기화 메커니즘).
4. **inventory_items 0 rows**: 빈 테이블 (6/26 신규 발견 테이블 중 하나, 데이터 미수신).
5. **backend.log 8일 침묵**: 06-19 16:58:37 마지막 GIN 기록 → 8일 정체. §3.1 `grep -a` 권장 적용.

## ③ 사용자 확인 요청

### Q1. 백엔드/프론트 복구 + systemd 등록 (즉시)

**상황**: 5일째 DOWN 미복구, 06-23 보고서 권고 systemd 등록 미실행 (§7 #26 위반 반복).

**가능성 표**:

| # | 가능성 | 확인 방법 | 액션 |
|:-:|--------|----------|------|
| A | 사용자가 수동 기동 대기 | uptime 4일 (재부팅 후 미복구) | 즉시 `./start.sh` + `npm run dev` |
| B | systemd 등록 누락 | `/etc/systemd/system/vf2-backend.service` 부재 확인 | 단위 파일 작성 + `daemon-reload && enable --now` |
| C | 의도된 DOWN (유지보수) | cron 변동 0 + 사용자 응답 부재 | 사용자 확인 필요 |

**권고**: A+B 동시 실행 (수동 기동 후 systemd 영구 등록)

### Q2. 디스크 93% CRITICAL (즉시)

**상황**: 06-26 89% → 06-27 93% (+4%p/1일), 가속 재개.

**가능성 표**:

| # | 가능성 | 영향 | 액션 |
|:-:|--------|------|------|
| A | backend.log 누적 (8일 정체 + GIN-debug) | 100% 미사용 | truncate 또는 rotate |
| B | production_logs 15,886행 증가분 | 누적 | 백업 후 정리 |
| C | PostgreSQL WAL/archive | 누적 | archive_command 점검 |
| D | workspace 백업본 | 누적 | USB 이동 |

**권고**: A 즉시 (수 MB 절감), D 주말 정리

### Q3. 침묵 18일 사용자 인지

**상황**: max_date 06-09 → 18일 무등록 (백엔드 DOWN으로 인위적 침묵이지만 DB 정합성 확인 필요).

**가능성 표**:

| # | 가능성 | 확인 방법 | 액션 |
|:-:|--------|----------|------|
| A | 사용자 1.xlsx import 후 자연 정체 | pending 4,967건 status | 사용자 결정 대기 |
| B | 백엔드 DOWN으로 인한 인위적 침묵 | DB 직접 SELECT (이미 확인) | 백엔드 복구 후 자동 해소 |
| C | 등록 누락 (의도 침묵) | status 분포 점검 | 사용자 확인 필요 |

## ④ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 백엔드/프론트 5일째 DOWN (systemd 미등록) | 모든 API 정지 | 🚨 사용자 즉시 | 4일째 → 5일째 |
| 2 | 디스크 93% CRITICAL (+4%p/1일 가속) | 1~2개월 위험 | 🚨 사용자 즉시 | 89% → 93% (+4%p) |
| 3 | 운영 침묵 18일 (max_date 06-09) | 등록 의도 | ⏳ 사용자 | 17일 → 18일 |
| 4 | 운영 6-튜플 중복 mold 111 Butter YELLO-3093 4행 | 운영 정확성 | ⏳ 사용자 | 5행 → 4행 (정정) |
| 5 | 데크타일(114) color2 빈값 2건 (6/7) | 룰 위반 | ⏳ 사용자 | 변동 없음 |
| 6 | 운영 blank_mold 1건 (5/24 M01) | 노이즈 | ⏳ 사용자 | 변동 없음 |
| 7 | started 10,916건 (옵션 1·2·3) | UI 표시 정책 | ⏳ 사용자 | 변동 없음 |
| 8 | 운영 (mold, product) 1:1 위반 | 룰 위반 | ✅ | 0건 (정상) |
| 9 | color2 WHITE 180 158건 (WHITE=148 + White=10) | 표기 통일 | ⏳ 사용자 | 변동 없음 |
| 10 | production_plans 부재 | 1.xlsx import 누락 단서 | ⏳ 사용자 | 변동 없음 |
| 11 | inventory_stock max_updated 06-10 (17일 정체) | 재고 동기화 정지 | ⏳ 사용자 | 변동 없음 |
| 12 | inventory_items 0 rows (빈 테이블) | 신규 테이블 데이터 미수신 | ⏳ 사용자 | 변동 없음 |

## ⑤ 액션/옵션

### 즉시 (사용자 결정 대기)

1. **백엔드/프론트 복구 + systemd 등록**: §7 #26 즉시 실행 의무
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
2. **디스크 정리**: backend.log rotate, USB 백업 후 정리

### 시스템 (장기)

3. 침묵 일수 두 가지 기준 보고 정책 (단순 + max_date) 유지
4. carry-forward 정정 강화 — 매 실행 SQL 재측정
5. 시스템 재부팅 시 systemd 자동 시작 보장

## ⑥ 디스크 가속 추이

| 일자 | 사용량 | 일일 Δ | 판정 |
|:----:|:------:|:------:|:----:|
| 06-23 | 75% | - | ⚠️ WARNING |
| 06-24 | 79% | +4%p | ⚠️ WARNING |
| 06-26 | 89% | +5%p/2일 | 🚨 CRITICAL 임박 |
| **06-27** | **93%** | **+4%p/1일** | 🚨 **CRITICAL** |

**추세 판정**: WARNING → CRITICAL 임박 (2일) → CRITICAL (1일). 가속 재개 확인. 1~2개월 내 100% 도달 위험.

## ⑦ 결론

🚨 **CRITICAL**: 백엔드/프론트 5일째 DOWN (systemd 미등록 2회 반복) + 디스크 93% CRITICAL + 침묵 18일. 사용자 즉시 액션 권고 (Q1 백엔드 복구 + Q2 디스크 정리). SQL 7종 정밀 카운트 결과 carry-forward 정정 1건 발견 (6-튜플 5행 → 4행).

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260626.md` (1일 전 06-26 05:30, 1회차)
- 직전 동일 prefix: `VF2-Project-Nightly-20260626.md`
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (06-17 9 → 06-26 28 → 06-27 28)
- 점검 시각: 2026-06-27 06:30:41 KST
- 스킬 부재: `vf2-production-plan-conventions` (loadable skill 부재, skip)
- USER.md / MEMORY.md 부재: skip
- 동일 날짜 2회차: 06-27 VF2-Project-Nightly (06-26 VF2-Production-Plan-Nightly 1회차 후 1일)
