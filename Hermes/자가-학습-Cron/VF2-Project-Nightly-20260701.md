# VF2 Project Nightly — 2026-07-01 자가 점검 보고 (2차 cron)

**점검 시각**: 2026-07-01 06:30:57 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
**직전 보고서**: `VF2-Production-Plan-Nightly-20260701.md` (07-01 05:30, **같은 날 1회차**, §0.1)
**비교 기준**: 1회차(05:30) 대비 변동

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:-:|---|
| 1. Wiki 검색 | ✅ | 1회차 `VF2-Production-Plan-Nightly-20260701.md` 확인 (같은 날, 1시간 전) |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + canonical reference 로드 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health, DB SQL 7종, pg_class 28 tables, status 분포, 침묵 측정, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재.

---

## ① 시스템 상태

| 지표 | 1회차 (05:30) | **2회차 (06:30)** | 판정 |
|------|---:|---:|:----:|
| **Health** | `curl: (7) Failed to connect` | `curl: (7) Failed to connect` | 🔴 **백엔드 DOWN** |
| **uptime** | 8일 9시간 | **8일 10시간** (06-22 20:13 KST 이후, 신규 재부팅 없음) | ⚠️ 동일 재부팅 유지 |
| **백엔드 PID** | 0건 | **0건** (`vf2_backend_bin` 부재) | 🔴 **12일째 DOWN** |
| **Vite PID** | 0건 | **0건** | 🔴 **12일째 DOWN** |
| **Listen 포트** | 0건 | **0건** (5174/5176 둘 다) | 🔴 systemd/s6 미등록 |
| **디스크 `/`** | **47%** | **47%** | 🟢 **정상** (변동 0) |
| **PostgreSQL** | Up 8 days | **Up 8 days** | ✅ Docker restart policy |
| **DB 테이블** | 28개 | **28개** (변동 0) | ✅ 정상 |

### 1.2 🚨 백엔드/프론트엔드 DOWN 프로토콜 (12일째, 1회차와 동일)

| 진단 | 결과 |
|------|------|
| uptime | 8일 10시간 (06-22 20:13 KST 이후 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | 0건 (NO_PORTS_LISTENING) |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **12일 전** |
| `docker ps postgres_hermes` | Up 8 days (Docker restart policy로 복구) |

**결론**: 1회차(05:30)와 **완전 동일**. 백엔드/프론트엔드 DOWN 12일째. backend.log 마지막 기록 동일 (06-19 16:58:37). **systemd/s6 미등록 함정 지속 (§7 #26, 4회째 권고 미실행)**.

### 1.3 DB 테이블 (28개, 1회차와 동일 — 변동 0)

**(a) pg_stat_user_tables → stale 통계 함정 지속 (§7 #21)**
**(a-fallback) pg_class 직접 조회 → 28개 테이블** (1회차 목록과 완전 동일):

```
barcode_master, barcode_transfer_records, data_sources, delivery_daily_records,
delivery_special_notes, fc_inbound_file_uploads, fc_inbound_records,
inbound_order_lines, inbound_order_uploads, inbound_policies,
inventory_adjustments, inventory_baseline_items, inventory_baseline_uploads,
inventory_items, inventory_receipt_items, inventory_receipt_uploads,
inventory_stock, machine_plans, machine_users, master_colors, master_molds,
master_specs, master_units, outbound_analysis, outbound_records,
product_unit_specs, production_logs, unit_price_history
```

**(b) production_plans 존재 여부 → NULL** (부재, 1회차와 동일)

---

## ② 발견된 문제 (1회차 대비 변화)

### ✅ 핵심 결론: 1회차(05:30) 대비 **모든 지표 변동 0**

같은 날 2회 실행(§0.1)으로 1시간 간격 이중 검증 결과, **1회차와 완전 동일**.

### 🔴 발견 1: 백엔드/프론트엔드 **12일째 DOWN** (1회차와 동일)

- **근거**: `ps -ef | grep vf2_backend_bin` → 0건, `ss -tlnp` → 0건
- **backend.log 마지막**: 2026-06-19 16:58:37 (1회차와 동일, 신규 기록 없음)
- **systemd/s6 미등록**: §7 #26 — **4회째 권고 미실행** (6/23 → 6/26 → 6/30 → 7/01)

### 발견 2: 운영 침묵 **max_date 기준 22일째** (1회차와 동일)

- **근거**: `production_logs` `MAX(date) = 2026-06-09` (1회차와 동일)
- **max_date 기준 침묵**: 2026-07-01 - 2026-06-09 = **22일**
- **백엔드 DOWN 영향**: 06-19~07-01 (12일) POST 자체 불가 → 인위적 침묵 포함

### 발견 3: DB 완전 정적 — 모든 지표 변동 0건 (1회차와 동일)

| 지표 | 1회차 (05:30) | **2회차 (06:30)** | 변동 |
|------|---:|---:|:----:|
| production_logs total | 15,886 | **15,886** | 0 |
| status: started | 10,916 | **10,916** | 0 |
| status: pending | 4,967 | **4,967** | 0 |
| status: ended | 3 | **3** | 0 |
| max_date | 2026-06-09 | **2026-06-09** | 0 |
| 6-튜플 중복 (운영) | 4행 | **4행** (mold 111 Butter ×2일 ×2행) | 0 |
| mold 1:1 위반 (운영) | 0건 | **0건** | 0 |
| blank_mold (운영) | 1 | **1** | 0 |
| blank_color1 (운영) | 1 | **1** | 0 |
| blank_color2 (운영) | 3 | **3** | 0 |
| WHITE 180 (대문자) | 148 | **148** | 0 |
| White 180 (혼합) | 10 | **10** | 0 |
| DB 테이블 수 | 28 | **28** | 0 |
| production_plans | 부재 | **부재** (NULL) | 0 |

- **1시간 간격 이중 검증 = 모든 지표 변동 0건** (독립적 확인, §0.1 원칙)

---

## ③ 사용자 확인 요청 (1회차와 동일 — 계승)

### 🚨 CRITICAL Q1: "백엔드/프론트엔드 12일째 DOWN — 복구 지시 + systemd 등록 필수"

**systemd 등록 미실행 카운트**: **4회** (6/23 → 6/26 → 6/30 → 7/01). §7 #26 정책.

**즉시 권장 액션**:
```bash
cd /home/comtop/workspace/VF2/backend && ./start.sh
cd /home/comtop/workspace/VF2/frontend && npm run dev
ss -tlnp | grep -E ':(5174|5176)\b'
curl http://localhost:5176/api/health
```

### 일반 Q2: "운영 침묵 max_date 기준 22일 — 의도된 침묵인가요?" (계승)

### 일반 Q3: "production_plans 테이블 부재 지속" (계승, LOW)

---

## ④ 미해결 항목 추적 (1회차 → 2회차, 변동 0)

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **백엔드/프론트 12일째 DOWN** | 서비스 불가 | 🔴 사용자 즉시 | 변동 0 |
| 2 | 디스크 47% (안정) | 정상 | 👀 관찰 | 변동 0 |
| 3 | 운영 침묵 22일 (max_date 기준) | 등록 의도 | ⏳ 사용자 | 변동 0 |
| 4 | DB 완전 정적 (변동 0) | 구조적 정지 | ⏳ 사용자 | 변동 0 |
| 5 | status started 10,916건 옵션 결정 | UI 표시 정책 | ⏳ 사용자 | 변동 0 |
| 6 | mold 111 Butter 6-튜플 중복 4행 (운영) | 운영 정확성 | ⏳ 사용자 | 변동 0 |
| 7 | 빈 color2 (운영) 3건 | 룰 위반 | ⏳ 사용자 | 변동 0 |
| 8 | color2 White 180 158건 | 자동 정정 정책 | ⏳ 사용자 | 변동 0 |
| 9 | `production_plans` 테이블 부재 | 1.xlsx import 단서 | ⏳ 사용자 | 부재 지속 |
| 10 | 백엔드 systemd/s6 미등록 | 재부팅 시 미복구 | 🔴 사용자 | **4회째 권고 미실행** |

---

## ⑤ 액션 / 옵션

### 즉시 (CRITICAL, 사용자 결정 대기)

- [ ] **🔴 백엔드/프론트 복구**: `./start.sh` + `npm run dev` (12일째)
- [ ] **🔴 systemd/s6 등록**: **4회째 권고**. 재부팅 시 자동 복구 위해 즉시 등록 필수

### 관찰 (✅ 정상)

- [ ] 디스크 47% — 정상 유지 (50% 미만)

### 시스템 (✅ 정상)

- PostgreSQL Docker 자동 복구 ✅ (Up 8 days)
- DB 직접 SELECT 가능 (28 tables) ✅
- 디스크 47% 정상 ✅
- (mold, productName) 1:1 위반 (운영) 0건 ✅
- 운영 6-튜플 중복 (mold 111 외) 0건 ✅
- production_logs 15,886건 (변동 0) ✅

---

## ⑥ 디스크 가속 추이

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/26 | 89% | +2.4%p/1일 | 🔴 CRITICAL 임박 |
| 6/30 | 44% | -11.3%p/1일 | 🟢 정상 — CRITICAL 해소 |
| 7/01 05:30 | 47% | +3%p/1일 | 🟢 정상 유지 |
| **7/01 06:30** | **47%** | **0%p/1h** | 🟢 **정상 유지** (1회차와 동일) |

---

## ⑦ 결론

**2차 cron 이중 검증 결과**: 1회차(05:30) 대비 **모든 지표 변동 0건** 확인.

**시스템 상태**:
- 🟢 **디스크 정상 유지**: 47% (50% 미만)
- 🔴 **백엔드/프론트엔드 12일째 DOWN**: systemd/s6 미등록 (권고 **4회째** 미실행)
- ✅ PostgreSQL 정상 (Up 8 days), DB 28 테이블 정상
- ✅ DB 완전 정적 (1시간 간격 변동 0건)

**변동 요약 (1회차 → 2회차)**:
1. 모든 DB 지표 **변동 0** (15,886건, status 분포, 6-튜플, color2 등 전부 동일)
2. 백엔드 DOWN 12일째 (변동 없음)
3. 디스크 47% (변동 없음)
4. DB 테이블 28개 (변동 없음)

**🚨 사용자 즉시 액션 권장** (1회차와 동일):
1. **백엔드/프론트 복구**: `./start.sh` + `npm run dev`
2. **systemd 등록**: 재발 방지 (**4회째 권고**)

---

## References

- 직전 보고서 (1회차): `VF2-Production-Plan-Nightly-20260701.md` (07-01 05:30, 같은 날)
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (1회차와 동일)
- 점검 시각: 2026-07-01 06:30:57 KST
- 같은 날 2회 실행 패턴: canonical §0.1 적용
- USER.md / MEMORY.md 부재: skip
- Wiki git repo: `/home/comtop/workspace/Wiki/` (master, push 가능)
