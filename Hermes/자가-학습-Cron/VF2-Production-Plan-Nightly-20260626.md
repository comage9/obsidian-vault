# VF2 Project Nightly — 2026-06-26 자가 점검 보고

**점검 시각**: 2026-06-26 05:30:56 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md` (1순위)
**직전 보고서**: `VF2-Production-Plan-Nightly-20260617.md` (06-18~06-25 8일간 부재 후 9일 만 재개)

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:-:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 `VF2-Production-Plan-Nightly-20260617.md` 확인 (6/17 05:33 작성). **06-18~06-25 8일간 보고서 부재** → 이번이 첫 재개 |
| 2. 스킬 로드 | ⚠️ skip | `vf2-production-plan-conventions` 스킬 부재 → `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md` + `references/gorm-snakecase-columns-20260616.md`로 대체 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health(connect fail/DOWN), §1.2 DOWN 프로토콜 발동, DB 28 tables (pg_stat stale fallback), status 분포, 침묵 측정, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고. **🚨 백엔드/프론트 7일째 DOWN — 사용자 복구 지시 필수** |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재.

---

## ① 시스템 상태

| 지표 | 값 | 판정 |
|------|---:|:----:|
| **Health** | `curl: (7) Failed to connect to localhost port 5176` | 🔴 **백엔드 DOWN** (curl exit 7 = connect fail) |
| **uptime** | **3일 9시간** (06-22 20:13 KST 재부팅 추정) | 🔴 **직전 재부팅 감지** |
| **백엔드 PID** | **0건** (`vf2_backend_bin` 프로세스 부재) | 🔴 **7일째 DOWN** (06-19 16:58 backend.log 마지막 기록) |
| **Vite PID** | **0건** (`vite` 프로세스 부재) | 🔴 **7일째 DOWN** |
| **Listen 포트** | **0건** (5174/5176 둘 다 DOWN) | 🔴 **systemd/s6 미등록 함정 재확인** |
| **디스크 `/`** | **89%** (6/17 67% → 6/26 89%, **+22%p/9일 = +2.4%p/1일**) | 🔴 **CRITICAL 임박** (90% 미만 1%p) |
| **메모리** | 14Gi 사용 4.8Gi (34%), swap 4.0Gi 사용 1.4Gi | ✅ 정상 |
| **PostgreSQL 컨테이너** | `postgres_hermes Up 3 days` | ✅ Docker restart policy로 자동 복구 |
| **DB 직접 조회** | 28개 테이블 응답 (PostgreSQL `vf2_db`) | ✅ (pg_stat stale 0 rows → fallback으로 테이블 28개 확인) |

### 1.2 🚨 백엔드/프론트엔드 DOWN 프로토콜 발동 (6/23 정형화)

| 진단 | 결과 |
|------|------|
| uptime | 3일 9시간 (06-22 20:13 KST 이후 재부팅) |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | 0건 |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **7일 전** |
| `docker ps postgres_hermes` | Up 3 days (Docker restart policy로 복구) |

**결론**: 06-19 16:58경 외부 스캐너(`66.132.195.107` PRI 시도) 활동 시점까지 vf2_backend_bin은 살아있었으나, **06-22 20:13 KST 시스템 재부팅과 함께 vf2_backend_bin + vite 미복구**. PostgreSQL만 Docker 컨테이너로 자동 복구됨. **systemd/s6 미등록 함정 재발 (6/23 사례와 동일 패턴)**.

**🚨 침묵 측정에 미치는 영향**: 백엔드 DOWN 기간 중 production-log POST 자체 불가능. **침묵 일수 = max_date 기준 17일 (DB 직접 SELECT 기준, 유효)**, 단순 POST 시점 침묵은 마지막 200/400 응답 기준 06-14 06:32 → 12일 (단순).

### 1.3 DB 테이블 (28개, 6/17 9개 → 28개로 +19개 신규 발견)

**(a) pg_stat_user_tables → 0 rows** (PostgreSQL 컨테이너 재시작 후 stale 통계 함정, §1.3 fallback 적용)
**(a-fallback) pg_class 직접 조회 → 28개 테이블**:

```
barcode_master, barcode_transfer_records, data_sources,
delivery_daily_records, delivery_special_notes,                ← 🆕
fc_inbound_file_uploads, fc_inbound_records,                   ← 🆕 (6/25 보고서 기재 정정: inbound_records가 아닌 fc_inbound_records가 진짜)
inbound_order_lines, inbound_order_uploads,                    ← 🆕
inbound_policies,                                              ← 🆕
inventory_adjustments, inventory_baseline_items, inventory_baseline_uploads,
inventory_items, inventory_receipt_items, inventory_receipt_uploads,  ← 🆕
inventory_stock, machine_plans, machine_users,                  ← 🆕 (machine_users 등)
master_colors, master_molds, master_specs, master_units,       ← 🆕
outbound_analysis, outbound_records, product_unit_specs,       ← 🆕
production_logs, unit_price_history                            ← 🆕
```

**(a-direct) production_logs 직접 카운트 = 15,886건** (6/17과 동일, 변동 0건)

**🚨 신규 테이블 19개**: `delivery_special_notes`, `fc_inbound_file_uploads`, `fc_inbound_records`, `inbound_order_lines`, `inbound_order_uploads`, `inbound_policies`, `inventory_adjustments`, `inventory_items`, `inventory_receipt_items`, `inventory_receipt_uploads`, `machine_plans`, `machine_users`, `master_colors`, `master_molds`, `master_specs`, `master_units`, `outbound_analysis`, `product_unit_specs`, `unit_price_history`

**판단**: 8일간 보고서 부재 중 **DB 마이그레이션/신규 테이블 대량 추가** 발생 추정. 사용자 확인 필요.

---

## ② 발견된 문제 (6/17 대비 변화)

### 발견 1: 🚨🚨 **백엔드/프론트엔드 7일째 DOWN 미복구** (CRITICAL, 최우선)

- **근거**: `curl localhost:5176/api/health` → exit 7 (connect fail), `ps -ef | grep vf2_backend_bin` → 0건, `ss -tlnp | grep -E ':(5174|5176)\b'` → 0건
- **backend.log 마지막 기록**: 2026-06-19 16:58:37 (외부 스캐너 `66.132.195.107` PRI 시도)
- **systemd/s6 미등록 함정 재발**: 06-22 20:13 KST 시스템 재부팅 후 vf2_backend_bin + vite 자동 시작 안 됨
- **PostgreSQL만 Docker restart policy로 자동 복구** (`postgres_hermes Up 3 days`)
- **6/23 보고서와 동일 패턴**: 6/23은 1일 미복구, 6/26은 **7일째 미복구** (이전 6/23 사례의 7배)
- **사용자 액션 필수**:
  ```bash
  cd /home/comtop/workspace/VF2/backend && ./start.sh
  cd /home/comtop/workspace/VF2/frontend && npm run dev
  ```
- **영향**: production-log POST 등록 불가, 프론트엔드 페이지 로드 불가, 1.xlsx 등 데이터 임포트 시도 시 무반응

### 발견 2: 디스크 **89% CRITICAL 임박** (6/17 67% → 6/26 89%, +22%p/9일)

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/17 | 67% | +3%p/1일 | ⚠️ WARNING 재발 |
| **6/26** | **89%** | **+2.4%p/1일 (평균)** | 🔴 **CRITICAL 임박** (90% 미만 1%p) |

- **+22%p/9일 = +2.4%p/1일**: 임계치(절대≥50% + 일일≥2%p) **WARNING 유지/CRITICAL 진입 임박**
- **추세 분석**:
  - 6/14 64% → 6/16 64% (정체) → 6/17 67% (재가속)
  - **6/17~6/26 9일간 평균 +2.4%p/1일로 가속 지속**
  - 절대값 89%는 1%p 더 상승 시 **CRITICAL (≥90%)** 확정
- **원인 추정**: 8일간 보고서 부재 중 대량 파일/로그 누적 가능성. **DB 테이블 19개 신규 추가** (총 28개)와의 상관관계 추정
- **즉시 액션 권장**:
  - 불필요 로그 백업 후 삭제 (`backend/backend.log` 337KB, 6/19 정지 → 보존 가능)
  - PostgreSQL vacuum full / archive
  - `/tmp`, `/var/log` 점검

### 발견 3: 운영 침묵 **max_date 기준 17일째** (단순 계산 12일)

- **근거**:
  - `production_logs` 전체 `MAX(date) = 2026-06-09` (6/17과 동일)
  - `backend.log` 마지막 production-log POST = **06-14 06:32:28 (400 응답)**, 마지막 200 응답은 06-12 추정
  - **max_date 기준 침묵 = 2026-06-26 - 2026-06-09 = 17일** (가장 보수적, "침묵"의 본질)
  - **단순 계산 침묵 = 2026-06-26 - 2026-06-14 06:32 = 12일** (POST 시점 기준)
- **백엔드 DOWN 영향**: 백엔드 DOWN 기간(06-19~06-26)에는 POST 자체가 불가능 → **침묵이 인위적 침묵**임을 명시
- **6/17 보고서 대비**: 침묵 5일 → **17일** (+12일, 그러나 백엔드 DOWN 7일 포함하면 실질 +5일)
- **판정**: 단순 침묵 ≠ 결함. 1.xlsx import(6/10) 후 자연 정체 + 백엔드 DOWN 7일 = 인위적 침묵. **사용자 확인 요청**.

### 발견 4: status 분포 미변경 (DB 변동 0건, 6/17과 동일)

| status | 6/13 | 6/17 | **6/26** | 추세 |
|---|---:|---:|---:|:-:|
| started | 10,916 | 10,916 | **10,916** | 정체 (1.xlsx 잔재) |
| pending | 4,967 | 4,967 | **4,967** | 정체 |
| ended | 3 | 3 | **3** | 정체 |
| **합계** | **15,886** | **15,886** | **15,886** | **변동 0건** (9일째) |

- started 비율 68.7% (1.xlsx import 패턴 유지)
- 옵션 결정 미체결 16일째 (6/10~)
- **총 변동 0건 = 침묵 증명** (DB 직접 SELECT는 백엔드와 무관, 신규 등록 없음)

### 발견 5: ⚠️ historical 6-튜플 중복 **+5종 신규 발생** (6/25 보고서 15→20종)

- (e-h) historical 6-튜플 중복 **20그룹 × 2행 = 40행**
- 6/25 보고서: "historical 15→16종" → **6/26 20종 (+5종)** → 단 **6/25 보고서가 16종만 보고했을 가능성** (canonical §6.1 carry-forward 금지 정정 필요)
- **신규 5종 (6/25 미보고 가능성)**:
  - `2025-06-17, machine=13, mold=20, color1=Daiso-32, color2=IVORY 1060, unit_quantity=10` (2행)
  - `2025-06-17, machine=13, mold=20, color1=Daiso-33, color2=IVORY 1060, unit_quantity=10` (2행)
  - `2025-06-06, machine=11, mold=114, color1=WHITE2, color2=IVORY 1154, unit_quantity=9` (2행)
  - `2025-05-26, machine=10, mold=114, color1=Ivory, color2=IVORY 1060, unit_quantity=9` (2행)
  - `2024-12-17, machine=9, mold=32, color1=WHITE1, color2=WHITE 180, unit_quantity=180` (2행)
- **운영 2026 6-튜플 중복 = 4행** (mold 111 Butter 2그룹 × 2행, 6/17과 동일)

### 발견 6: ⚠️ **빈 moldNumber 1건 → 10건** (+9건 historical 발견)

- 운영 2026: id=19416 (2026-05-24, machine=M01) **1건** (6/17과 동일)
- **historical 신규 발견 9건** (2024년 분):
  - 21b7084a (2024-01-11, machine=6, color1=Black)
  - 2eec8352 (2024-06-26, machine=13, Butter/YELLO-3093)
  - 52900a61 (2024-06-26, machine=13, Pink(P3)/PINK 6078)
  - 69d9f541 (2024-08-02, machine=11, Gray2/GRAY 11215-1)
  - 7a8d61c6 (2024-05-30, machine=11, Gray2/GRAY 11215-1)
  - 838d9e8f (2024-08-02, machine=11, WHITE1/WHITE 180)
  - a12f6213 (2024-01-11, machine=6, Navy2/BLUE 20311)
  - a33c4b29 (2024-08-01, machine=11, Gray2/GRAY 11215-1)
  - dc6cc1a4 (2024-08-01, machine=11, WHITE1/WHITE 180)
- **6/17 보고서 "빈 moldNumber 1건 (id=19416)" → 6/26 10건 (id=19416 + 9건 historical)**. **carry-forward 정정 필요**.

### 발견 7: ⚠️ **machine `생산 대기/생산대기` 4건 → 14건** (+10건)

- 운영 2026:
  - `생산대기` **10건** (6/17 미보고, **+10건 신규**)
  - `생산 대기` **4건** (6/17과 동일)
  - **합계 14건** (6/17 4건 → 14건, **+10건**)
- 표기 통일 정책 사용자 결정 보류 중

### 발견 8: ⚠️ **빈 color2 운영 2건 → 3건** (+1건)

- (f-detail) 운영 2026 blank_color2:
  - 2026-06-07, machine=10, mold=114, color1=Ivory, color2=빈값 (1건) — **6/7 등록**
  - 2026-06-07, machine=10, mold=114, color1=WHITE2, color2=빈값 (1건) — **6/7 등록**
  - 2026-05-24, machine=M01, mold=빈값, color1=빈값, color2=빈값 (1건) — **6/17 미보고 (M01 mold/color 둘 다 빈값, 발견 1)**
- 6/17 "데크타일(114) WHITE2/Ivory 빈 color2 2건" → **6/26 3건 (M01 전체 빈값 1건 추가)**

### 발견 9: ⚠️ **DB 테이블 19개 신규 추가** (총 9 → 28개)

- 6/17 9개 테이블 → 6/26 28개 테이블 (**+19개**)
- **신규 카테고리**:
  - `master_*` (master_colors, master_molds, master_specs, master_units) — 마스터 데이터 4종
  - `fc_inbound_*` (fc_inbound_file_uploads, fc_inbound_records) — **🏷️ 6/25 보고서가 `inbound_records`라고 기재한 테이블은 실제로 미존재. 정정: `fc_inbound_records`**
  - `inbound_order_*` (inbound_order_lines, inbound_order_uploads) — 발주 관리
  - `inbound_policies` — 입고 정책
  - `inventory_*` (inventory_adjustments, inventory_items, inventory_receipt_items, inventory_receipt_uploads) — 재고 관리 강화
  - `machine_*` (machine_plans, machine_users) — 설비 관리
  - `delivery_special_notes` — 배송 특이사항
  - `outbound_analysis`, `product_unit_specs`, `unit_price_history` — 분석/스펙/이력
- **판단**: 8일간 보고서 부재 중 **DB 마이그레이션 또는 신규 기능 출시** 발생. **사용자 확인 필수**.

### 발견 10: ⚠️ `production_plans` 테이블 **부재** (canonical §1.3 LOW #3)

- `SELECT to_regclass('public.production_plans')` → NULL
- 1.xlsx import 대상 테이블로 부재 시 **1.xlsx import 누락 단서**
- 사용자 확인 필요

### 발견 11: color2 White 180 변동 0건 (6/17과 동일)

- `WHITE 180` (대문자) 148건 + `White 180` (혼합) 10건 = **158건** (6/17과 동일)
- 자동 정정 정책(skill §19(2)) "0건이 아니면 알림"은 유지되나, 신규 발생 0건으로 **변동 없음**

### 기타 6/8 이후 미해결 결함 (계승)

| # | 항목 | 6/17 | **6/26** | 비고 |
|:-:|------|:----:|:----:|------|
| 1 | 데크타일(114) color2 빈값 | 2건 | **3건** | 6/7 등록, 19일째 미해결, M01 1건 추가 발견 |
| 2 | mold 111 Butter 6-튜플 중복 (운영) | 4건 | **4건** | 변동 0 (19일째 정체) |
| 3 | 빈 moldNumber (id=19416) | 1건 | **10건** | 6/8~ 미해결, **historical 9건 추가 발견 (정정)** |
| 4 | machine `생산 대기/생산대기` (운영) | 4건 | **14건** | `생산대기` 10건 + `생산 대기` 4건, **+10건 신규** |
| 5 | `IVORY 1060` + `WHITE1` color2 오매칭 (운영) | 0건 | **0건** | 변동 0 |
| 6 | (mold, productName) 1:1 위반 (운영 2026) | 0건 | **0건** | 변동 0 |
| 7 | 6-튜플 중복 (운영 2026, mold 111 외) | 0건 | **0건** | mold 111 외 중복 없음 |
| 8 | historical 6-튜플 중복 (변경) | (6/25 15→16종) | **20종** | **+5종 신규 발생 (6/25 보고서 16종 보고는 carry-forward 누락 의심)** |
| 9 | status started 10,916건 옵션 결정 | 미결 | **미결** | 16일째 정체 |
| 10 | `production_plans` 테이블 부재 | (확인 안 함) | **부재 확정** | canonical §1.3 LOW #3, 사용자 확인 필요 |
| 11 | 백엔드/프론트 systemd/s6 미등록 | (미발생) | **🔴 7일째 DOWN** | 06-22 20:13 재부팅 후 미복구 (6/23 사례와 동일 패턴) |

---

## ③ 사용자 확인 요청 (CRITICAL 4건 + 일반 3건)

### 🚨 CRITICAL Q1: "백엔드/프론트엔드 7일째 DOWN — 복구 지시 부탁드립니다"

| 가능성 | 근거 |
|---|---|
| A) systemd/s6 미등록 (확정) | 06-22 20:13 재부팅 후 vf2_backend_bin + vite 자동 시작 실패. PostgreSQL은 Docker restart policy로 복구 |
| B) 디스크 풀 (89%) | 디스크 89%로 cron/systemd 기동 실패 가능성 (90% 미만이지만 마진 1%p) |
| C) 8일간 보고서 부재 중 마이그레이션 실패 | DB 테이블 19개 신규 추가와 무관할 수 있으나, 백엔드 빌드 실패 가능성 |

**즉시 권장 액션**:
```bash
cd /home/comtop/workspace/VF2/backend && ./start.sh
cd /home/comtop/workspace/VF2/frontend && npm run dev
ss -tlnp | grep -E ':(5174|5176)\b'
curl http://localhost:5176/api/health
```

**🚨 systemd 등록 권고 (장기)**: 6/23 보고서에서 권고했으나 미실행. 7일째 DOWN 사례가 다시 발생 → **이번에 반드시 등록**:
```bash
# /etc/systemd/system/vf2-backend.service (예시)
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
```

### 🚨 CRITICAL Q2: "디스크 89% CRITICAL 임박 — 가속 원인 + 정리 계획?"

| 가능성 | 근거 |
|---|---|
| A) 8일간 DB 마이그레이션 로그 누적 | 신규 테이블 19개 + 대량 insert/update |
| B) backend.log 337KB 누적 (단순 로그) | 6/19 정지 후 추가 기록 없음 → 보존 가능, 큰 부담 아님 |
| C) PostgreSQL archive/wal 누적 | 자동 vacuum 미실행 가능성 |
| D) `/var/log` 시스템 로그 | 8일간 무점검 |

**즉시 권장 액션**:
```bash
du -sh /home/comtop/workspace/VF2/backend/backend.log /var/log/* 2>/dev/null | sort -h | tail -10
PGPASSWORD=*** psql "$DATABASE_URL" -c "VACUUM FULL;"
# 또는 archive/wal 정리
```

### 🚨 CRITICAL Q3: "DB 테이블 9개 → 28개로 +19개 신규 — 어떤 마이그레이션이었나요?"

| 신규 카테고리 | 추정 용도 |
|---|---|
| `master_*` (4종) | 마스터 데이터 (color/mold/spec/unit) |
| `fc_inbound_*` (2종) | 입고 관리 (보노하우스 FC) |
| `inbound_order_*` (3종) | 발주 관리 |
| `inventory_receipt_*` (2종) | 입고 영수증 |
| `machine_*` (2종) | 설비 계획/사용자 |
| 기타 6종 | 분석/스펙/이력/특이사항 |

**질문**: "사용자 직접 SQL 마이그레이션이었나요, 자동화 스크립트였나요, 아니면 백엔드 ORM 자동 init이었나요?"

### 🚨 CRITICAL Q4: "`fc_inbound_records` vs `inbound_records` — 6/25 보고서 오기재 정정"

6/25 보고서가 `inbound_records`로 기재했으나 실제로는 **`fc_inbound_records`**가 존재. **사용자 인지 차원 확인 + 6/25 보고서 정정 필요**.

### 일반 Q5: "침묵 max_date 기준 17일 — 의도된 침묵인가요?" (계승)

| 가능성 | 근거 |
|---|---|
| A) 의도된 공휴일/주말 침묵 | 06-09(화)~06-26(금), 공휴일 아님, 그러나 백엔드 DOWN 7일 포함 |
| B) 1.xlsx import 후 자연 정체 | 6/10 started 10,916건 일괄 등재 후 등록 정체, 16일째 |
| C) 등록 누락 (워크플로우 결함) | 프론트엔드 또는 API 결함 가능, 사용자 확인 필요 |
| D) 단순 미작업 | 6/9(화) 이후 사용자 작업 없음 |
| E) **백엔드 DOWN으로 인한 인위적 침묵** | 06-19 16:58 이후 vf2_backend_bin DOWN, POST 자체 불가 |

### 일반 Q6: "빈 moldNumber 1건 → 10건 (정정) — historical 9건 처리 정책?"

### 일반 Q7: "historical 6-튜플 중복 15→20종 (정정) — carry-forward 금지 정책 위반 정정?"

---

## ④ 미해결 항목 추적 (6/17 → 6/26)

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **백엔드/프론트 7일째 DOWN** | **서비스 불가** | 🔴 **사용자 즉시** | 0건 → **7일째** |
| 2 | **디스크 89% CRITICAL 임박** | **1~2주 위험** | 🔴 **사용자 즉시** | 67% → **89% (+22%p/9일)** |
| 3 | **DB 테이블 19개 신규 추가** | **마이그레이션 추적** | 🔴 **사용자 즉시** | 9개 → **28개** |
| 4 | **`fc_inbound_records` 테이블 정정** | 6/25 보고서 오기재 | 🔴 **사용자** | 신규 발견 |
| 5 | 운영 침묵 17일 (max_date 기준) | 등록 의도 | ⏳ 사용자 | 5일째 → **17일째** |
| 6 | color2 White 180 158건 | 자동 정정 정책 | ⏳ 사용자 | 변동 0 (9일째) |
| 7 | mold 111 Butter 6-튜플 중복 (운영) | 운영 정확성 | ⏳ 사용자 | 변동 0 (19일째) |
| 8 | 데크타일(114) color2 빈값 | 룰 위반 | ⏳ 사용자 | 2건 → **3건 (+1)** |
| 9 | 빈 moldNumber 10건 (정정) | 노이즈 | ⏳ 사용자 | 1건 → **10건 (+9, historical 발견)** |
| 10 | machine `생산 대기/생산대기` 14건 (정정) | 표기 통일 | ⏳ 사용자 | 4건 → **14건 (+10)** |
| 11 | started 10,916건 옵션 결정 | UI 표시 정책 | ⏳ 사용자 | 변동 0 (16일째) |
| 12 | `production_plans` 테이블 부재 | 1.xlsx import 누락 단서 | ⏳ 사용자 | (확인 안 함) → **부재 확정** |
| 13 | historical 6-튜플 중복 20종 (정정) | 데이터 정확성 | ⏳ 사용자 | 15종(6/25) → **20종 (+5)** |

---

## ⑤ 액션 / 옵션

### 즉시 (CRITICAL, 사용자 결정 대기)

- [ ] **🔴 백엔드/프론트 복구**: `./start.sh` + `npm run dev`
- [ ] **🔴 systemd/s6 등록 (장기 방지)**: 위 예시 unit 파일 참조
- [ ] **🔴 디스크 89% 정리**: backend.log archive, PostgreSQL VACUUM FULL, /var/log 점검
- [ ] **🔴 DB 마이그레이션 확인**: 19개 신규 테이블 백업 + 사용자 인지 차원 확인
- [ ] **🔴 6/25 보고서 정정**: `inbound_records` → `fc_inbound_records`

### 즉시 (방치 가능, 사용자 결정 대기)

- [ ] 운영 침묵 17일 (max_date 기준) — 사용자 확인 (질문 5)
- [ ] 색상/색상2 변동 0건 — 자동 정정 정책 유지
- [ ] mold 111 Butter 6-튜플 중복 4건 — 옵션 1 (병합) 권장
- [ ] 6/8 미해결 결함 4종 (데크타일 / 빈 moldNumber / `생산 대기` / 6-튜플 중복)
- [ ] status started 10,916건 옵션 1·2·3 결정 (16일째)
- [ ] `production_plans` 부재 — 1.xlsx import 누락 단서
- [ ] historical 6-튜플 중복 20종 — 정정 보고

### 시스템 (✅ 정상, 변경 불요)

- PostgreSQL Docker 자동 복구 ✅
- DB 직접 SELECT 가능 (28 tables) ✅
- (mold, productName) 1:1 위반 (운영) 0건 ✅
- 운영 6-튜플 중복 (mold 111 외) 0건 ✅
- production_logs 총 15,886건 (변동 0) ✅

---

## ⑥ 디스크 가속 추이 (skill §0.2 임계치 추적)

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/8 | 33% | - | 기준 |
| 6/10 | 51% | +9%p/2일 | WARNING (1.xlsx import) |
| 6/11 | 54% | +3%p | WARNING |
| 6/14 | 64% | (skip) | WARNING 해소 (정체) |
| 6/16 | 64% | 0%p/2일 | ✅ 안정 |
| 6/17 | 67% | +3%p/1일 | ⚠️ WARNING 재발 |
| (06-18~06-25 부재, 8일간 미측정) | - | - | ⚠️ 미측정 |
| **6/26** | **89%** | **+2.4%p/1일 (평균 9일)** | 🔴 **CRITICAL 임박** |

- 6/17 → 6/26 9일간 미측정 → +22%p 누적 (평균 +2.4%p/1일)
- **임계치 검증**: 절대값 89% (CRITICAL 임박) AND 일일 +2.4%p (WARNING 유지)
- **다음 점검(6/27)**: 90% 도달 시 CRITICAL 확정. **즉시 정리 권장**
- **원인 추정**: 8일간 DB 마이그레이션(테이블 19개 신규) + 사용자 백업 부재 + 로그 누적

---

## ⑦ 결론

**시스템**: 🔴 **백엔드/프론트엔드 7일째 DOWN** (systemd/s6 미등록 함정 재발), 🔴 **디스크 89% CRITICAL 임박**, ✅ PostgreSQL 자동 복구.

**🚨 CRITICAL 발견 4건**:
1. **백엔드/프론트 7일째 DOWN** — 사용자 즉시 복구 지시 + systemd 등록 필수
2. **디스크 89%** — 1%p 추가 상승 시 CRITICAL (≥90%) 확정
3. **DB 테이블 19개 신규 추가** (9→28) — 8일간 마이그레이션 발생
4. **6/25 보고서 테이블명 오기재 정정** (`inbound_records` → `fc_inbound_records`)

**정정/변경 사항 (5건)**:
1. 빈 moldNumber 1건 → **10건** (+9건 historical 발견)
2. machine `생산 대기/생산대기` 4건 → **14건** (+10건)
3. 운영 blank_color2 2건 → **3건** (M01 전체 빈값 1건 추가)
4. historical 6-튜플 중복 15종(6/25) → **20종** (+5종, 6/25 보고서 carry-forward 누락 의심)
5. 침묵 5일 → **17일 (max_date 기준)** (+12일, 백엔드 DOWN 7일 포함)

**시스템 정상 (변동 0)**:
- production_logs 15,886건 (status 분포 정체)
- (mold, productName) 1:1 위반 0건
- 운영 mold 111 외 6-튜플 중복 0건
- color2 White 180 158건 (변동 0)

**🚨 사용자 즉시 액션 권장**:
1. **백엔드/프론트 복구**: `./start.sh` + `npm run dev`
2. **systemd 등록**: 재발 방지
3. **디스크 정리**: 89% → 70% 이하
4. **DB 마이그레이션 인지 확인**: 19개 신규 테이블 의도 확인

---

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260617.md` (06-18~06-25 8일간 부재 후 9일 만)
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (6/17 9 → 6/26 28, +19)
- 점검 시각: 2026-06-26 05:30:56 KST
- 스킬 부재: `vf2-production-plan-conventions` (loadable skill로 존재하지 않음, 6/15~ 정체)
- USER.md / MEMORY.md 부재: skip
- 8일간 보고서 부재 (06-18~06-25): 정기 cron 부재 또는 실행 실패 추정
