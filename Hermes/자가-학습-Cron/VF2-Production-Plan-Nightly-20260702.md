# VF2 Production Plan Nightly — 2026-07-02 자가 점검 보고

**점검 시각**: 2026-07-02 05:31 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
**직전 보고서**: `VF2-Project-Nightly-20260701.md` (07-01 06:30, 어제 2차 cron)
**비교 기준**: 07-01 대비 변동

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:--:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 `VF2-Project-Nightly-20260701.md` 확인 (어제) |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md` 로드 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health 5종, DB SQL 7종, pg_class 28 tables, 침묵, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재. `⚠️ Skill(s) not found and skipped: vf2-production-plan-conventions`.

---

## ① 시스템 상태

| 지표 | 07-01 | **07-02** | 판정 |
|------|---:|---:|:----:|
| **Health** | `curl: (7) Failed to connect` | `curl: (7) Failed to connect` | 🔴 **백엔드 DOWN** |
| **uptime** | 8일 10시간 | **9일 9시간** (06-22 20:13 KST 이후, 신규 재부팅 없음) | ⚠️ 동일 재부팅 유지 |
| **백엔드 PID** | 0건 | **0건** (`vf2_backend_bin` 부재) | 🔴 **13일째 DOWN** |
| **Vite PID** | 0건 | **0건** | 🔴 **13일째 DOWN** |
| **디스크 `/`** | 47% | **49%** (+2%p) | 🟢 **정상** (< 50%) |
| **메모리** | — | 4.9Gi/14Gi 사용, swap 3.4Gi/4.0Gi | ✅ 정상 |
| **PostgreSQL** | Up 8 days | **Up 9 days** | ✅ Docker restart policy |
| **DB 테이블** | 28개 | **28개** (변동 0) | ✅ 정상 |

### 1.2 🚨 백엔드/프론트엔드 DOWN 프로토콜 (13일째)

| 진단 | 결과 |
|------|------|
| uptime | 9일 9시간 (06-22 20:13 KST 이후 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `curl localhost:5176/api/health` | `curl: (7) Failed to connect` |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **13일 전** |
| `docker ps postgres_hermes` | Up 9 days (Docker restart policy로 복구) |
| 디스크 원인 배제 | ✅ 디스크 49% (< 50%) — §7 #32 디스크 원인 확정 배제 |

**결론**: 백엔드/프론트엔드 DOWN **13일째** (06-19 중단 추정). 디스크 정상이므로 원인은 **systemd/s6 미등록 단일 원인** (§7 #26, §7 #32).

**⚠️ systemd 등록 미실행 5회째 (§7 #26)**: 6/23 → 6/26 → 6/30 → 7/01 → **7/02**. CRITICAL 상태 지속.

### 1.3 DB 테이블 (28개, 변동 0)

**(a) pg_stat_user_tables → stale 통계 함정 (§7 #21)**: 0 rows 반환 (컨테이너 재시작 후 통계 미갱신).

**(a-fallback) pg_class 직접 조회 → 28개 테이블** (07-01과 완전 동일):
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

**(b) `production_plans` 존재 여부 → NULL** (부재, 동일)

---

## ② 발견된 문제 (07-01 대비 변화)

### 핵심 결론: 07-01 대비 **디스크 +2%p를 제외하고 모든 지표 변동 0**

### 🔴 발견 1: 백엔드/프론트엔드 **13일째 DOWN** (07-01 12일째 → +1일)

- backend.log 마지막: 2026-06-19 16:58:37 (변동 없음)
- 원인: systemd/s6 미등록 (단일 원인, 디스크 배제 완료)

### 🟢 발견 2: 디스크 49% (+2%p/1일)

- 07-01: 47% → 07-02: **49%**
- 절대값 < 50% → **정상** 유지 (§7 #30)
- 단, +2%p/1일 추세 — 주의 관찰. 지속 시 약 1일 후 50% 도달 → WARNING 재선언

### DB 정확 카운트 (SQL 재측정, carry-forward 금지)

| 항목 | 07-01 | **07-02** | 변동 |
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

---

## ③ 운영 침묵 측정 (skill A 지표)

| 기준 | 일수 | 판정 |
|------|---:|:----:|
| **max_date 기준** (오늘 - MAX(date)) | 07-02 - 06-09 = **23일** | 🔴 **≥ 5일 (임계치 2 초과)** |
| 단순 계산 (마지막 POST 시점) | 백엔드 DOWN으로 POST 불가 → 사실상 max_date 기준과 동일 | 🔴 |

**침묵 23일**: 백엔드 DOWN(13일) + 이전 자연 정체(10일). max_date 기준이 본질적.

**가능성**:
| # | 가능성 | 현재 상황 |
|:-:|------|------|
| A | 의도된 공휴일/휴무 | ❌ (23일 = 비현실적) |
| B | 1.xlsx import 후 자연 정체 | ⚠️ 부분 가능 (06-09 이후 import 없음) |
| C | 등록 누락 | ⚠️ 백엔드 DOWN으로 등록 자체 불가 |
| D | 단순 미작업 | ⚠️ 가능 |

**핵심**: 백엔드 DOWN이 침묵의 직접적 원인. 백엔드 복구 전까지 침묵 지속 불가피.

---

## ④ 디스크 가속 추세 (skill B 지표)

| 날짜 | 사용% | 일일 Δ |
|------|---:|---:|
| 06-30 | 44% | (대규모 정리 해소) |
| 07-01 | 47% | +3%p |
| **07-02** | **49%** | **+2%p** |

- 절대값 < 50% → **정상** (§7 #30)
- 일일 평균 증가: +2.5%p/일 (07-01~02 평균)
- **판정**: 정상 유지, 단 +2%p/1일 추세 지속 시 약 1일 후 50% 도달

---

## ⑤ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 운영 침묵 **23일** (max_date 기준) | 등록 정체 | ⏳ 사용자 | 22→23일째 |
| 2 | 🔴 백엔드/프론트엔드 DOWN **13일째** | 전체 시스템 마비 | ⏳ 사용자 | 12→13일째 |
| 3 | systemd/s6 미등록 (**5회째 권고 미실행**) | 재부팅 시 미복구 반복 | ⏳ 사용자 | 4→5회째 |
| 4 | pending 4,967건 status 누적 | UI 표시 정책 | ⏳ 사용자 | 변동 없음 |
| 5 | 6-튜플 중복 4행 (mold 111, 06-08·09) | 운영 정확성 | ⏳ 사용자 | 변동 없음 |
| 6 | color2 White 180 대소문자 158건 | 표기 통일 | ⏳ 사용자 | 변동 없음 |
| 7 | `production_plans` 테이블 부재 | import 누락 단서 | ⏳ 사용자 | 변동 없음 |
| 8 | blank color2 3건 (mold 114 등) | 룰 위반 | ⏳ 사용자 | 변동 없음 |
| 9 | started 10,916건 → pending/ended 전환 정책 | UI 표시 | ⏳ 사용자 | 변동 없음 |

---

## ⑥ 액션/옵션

### 🔴 CRITICAL — 즉시 액션 필요

| 우선순위 | 액션 | 상태 |
|:--:|------|:----:|
| **P0** | **systemd 등록 — 5회째 미실행** | ⏳ 사용자 |
| **P0** | 백엔드 복구 (`./start.sh`) | ⏳ 사용자 |

### systemed 등록 (§7 #26)
```bash
sudo tee /etc/systemd/system/vf2-backend.service > /dev/null << 'EOF'
[Unit]
Description=VF2 Backend
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

---

## ⑦ 결론

- 백엔드/프론트엔드 **13일째 DOWN**, systemd 미등록 5회째 — **P0 CRITICAL 지속**
- DB 데이터는 **완전 동결** (15,886행, max_date 06-09, 모든 지표 변동 0)
- 디스크 49% (+2%p) — 정상이나 주의 관찰
- 백엔드 복구 없이는 침묵 23일 해소 불가

---

## References

- 직전 보고서: `VF2-Project-Nightly-20260701.md` (07-01 06:30, 2차 cron)
- canonical: `references/vf2-production-plan-nightly-canonical.md`
- 함정: §7 #21 (pg_stat stale), §7 #26 (systemd 5회째), §7 #30 (디스크 해소 판정), §7 #32 (디스크 원인 배제)
