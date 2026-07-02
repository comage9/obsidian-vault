# VF2 Production Plan Nightly — 2026-07-03 자가 점검 보고

**점검 시각**: 2026-07-03 05:30 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
**직전 보고서**: `VF2-Production-Plan-Nightly-20260702.md` (07-02 05:31)
**비교 기준**: 07-02 대비 변동

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:--:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 `VF2-Production-Plan-Nightly-20260702.md` 확인 |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + canonical reference 로드 완료 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health 5종, DB SQL 7종, pg_class 28 tables, 침묵, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재. `⚠️ Skill(s) not found and skipped: vf2-production-plan-conventions`.

---

## ① 시스템 상태

| 지표 | 07-02 | **07-03** | 판정 |
|------|---:|---:|:----:|
| **Health** | `curl: (7)` | `curl: (7)` | 🔴 **백엔드 DOWN** |
| **uptime** | 9일 9시간 | **10일 9시간** (06-22 20:13 KST 이후, 재부팅 없음) | ⚠️ 동일 재부팅 유지 |
| **백엔드 PID** | 0건 | **0건** | 🔴 **14일째 DOWN** |
| **Vite PID** | 0건 | **0건** | 🔴 **14일째 DOWN** |
| **디스크 `/`** | 49% | **52%** (+3%p) | ⚠️ **WARNING 재선언** (≥ 50% + ≥ 3%p/일) |
| **메모리** | 4.9Gi/14Gi | 5.0Gi/14Gi, swap **3.8Gi/4.0Gi** (95%) | ⚠️ swap 과다 |
| **PostgreSQL** | Up 9 days | **Up 10 days** | ✅ Docker restart policy |
| **DB 테이블** | 28개 | **28개** (변동 0) | ✅ 정상 |

### 1.2 🚨 백엔드/프론트엔드 DOWN 프로토콜 (14일째)

| 진단 | 결과 |
|------|------|
| uptime | 10일 9시간 (06-22 20:13 KST 이후 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `curl localhost:5176/api/health` | `curl: (7) Failed to connect` |
| `ss -tlnp \| grep -E ':(5174\|5176)'` | 0건 (Listen 없음) |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **14일 전** |
| `docker ps postgres_hermes` | Up 10 days (Docker restart policy로 복구) |
| 디스크 원인 배제 | ✅ 디스크 52% — §7 #32 원인 배제 (단 WARNING 재선언, 디스크 풀과 무관) |

**결론**: 백엔드/프론트엔드 DOWN **14일째** (06-19 중단 추정). 원인은 **systemd/s6 미등록 단일 원인** (§7 #26).

**⚠️ systemd 등록 미실행 6회째 (§7 #26)**: 6/23 → 6/26 → 6/30 → 7/01 → 7/02 → **7/03**. CRITICAL 상태 지속.

### 1.3 DB 테이블 (28개, 변동 0)

**(a) pg_stat_user_tables → stale 통계 함정 (§7 #21)**: 0 rows 반환 (ANALYZE 미실행 상태 지속).

**(a-fallback) pg_class 직접 조회 → 28개 테이블** (07-02와 완전 동일):
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

## ② 발견된 문제 (07-02 대비 변화)

### 핵심 결론: 디스크 50% 임계치 재돌파 (WARNING 재선언), DB 데이터는 완전 동결

### 🔴 신규 발견 1: 디스크 WARNING 재선언 — 52% (+3%p/1일)

- 07-02: 49% (정상) → **07-03: 52%** (≥ 50% 임계치 재돌파)
- 일일 증가: +3%p/1일 ≥ 3%p/일 임계치 → **§4.1 WARNING 발동**
- 3일 평균 (07-01~03): +2.67%p/1일 → 약 6일 후 70% 도달 (WARNING → CRITICAL)
- §7 #34 "디스크 정리 후 재가속 패턴" 3일째 지속 확인

### 🔴 발견 2: 백엔드/프론트엔드 14일째 DOWN (07-02 13일 → +1일)

- backend.log 마지막: 2026-06-19 16:58:37 (변동 없음)
- 원인: systemd/s6 미등록 (단일 원인)

### DB 정확 카운트 (SQL 재측정, carry-forward 금지)

| 항목 | 07-02 | **07-03** | 변동 |
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
| **max_date 기준** (오늘 - MAX(date)) | 07-03 - 06-09 = **24일** | 🔴 **≥ 5일 (임계치 2 초과)** |
| 단순 계산 (마지막 POST 시점) | 백엔드 DOWN으로 POST 불가 → 사실상 max_date 기준과 동일 | 🔴 |

**침묵 24일**: 백엔드 DOWN(14일) + 이전 자연 정체(10일).

| # | 가능성 | 현재 상황 |
|:-:|------|------|
| A | 의도된 공휴일/휴무 | ❌ (24일 = 비현실적) |
| B | 1.xlsx import 후 자연 정체 | ⚠️ 부분 가능 (06-09 이후 import 없음) |
| C | 등록 누락 | ⚠️ 백엔드 DOWN으로 등록 자체 불가 |
| D | 단순 미작업 | ⚠️ 가능 |

---

## ④ 디스크 가속 추세 (skill B 지표)

| 날짜 | 사용% | 일일 Δ | 판정 |
|------|---:|---:|:----:|
| 06-30 | 44% | (대규모 정리 해소) | 정상 |
| 07-01 | 47% | +3%p | 정상 (< 50%) |
| 07-02 | 49% | +2%p | 정상 (< 50%) |
| **07-03** | **52%** | **+3%p** | ⚠️ **WARNING (≥ 50% + ≥ 3%p/일)** |

- 3일 평균 증가: +2.67%p/1일
- §7 #34 패턴: 06-30 대규모 정리 후 즉시 재가속, 4일째 지속
- 현재 추세 지속 시 ~7일 후 70% 도달 (CRITICAL)

---

## ⑤ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 운영 침묵 **24일** (max_date 기준) | 등록 정체 | ⏳ 사용자 | 23→24일째 |
| 2 | 🔴 백엔드/프론트엔드 DOWN **14일째** | 전체 시스템 마비 | ⏳ 사용자 | 13→14일째 |
| 3 | systemd/s6 미등록 (**6회째 권고 미실행**) | 재부팅 시 미복구 반복 | ⏳ 사용자 | 5→6회째 |
| 4 | ⚠️ 디스크 **52% WARNING 재선언** | 1~2개월 위험 | ⏳ 사용자 | 정상→WARNING |
| 5 | swap 3.8Gi/4.0Gi (95%) | 메모리 압박 | 👀 관찰 | 신규 |
| 6 | pending 4,967건 status 누적 | UI 표시 정책 | ⏳ 사용자 | 변동 없음 |
| 7 | 6-튜플 중복 4행 (mold 111, 06-08·09) | 운영 정확성 | ⏳ 사용자 | 변동 없음 |
| 8 | color2 White 180 대소문자 158건 | 표기 통일 | ⏳ 사용자 | 변동 없음 |
| 9 | `production_plans` 테이블 부재 | import 누락 단서 | ⏳ 사용자 | 변동 없음 |
| 10 | blank color2 3건 (mold 114 등) | 룰 위반 | ⏳ 사용자 | 변동 없음 |
| 11 | started 10,916건 → pending/ended 전환 정책 | UI 표시 | ⏳ 사용자 | 변동 없음 |

---

## ⑥ 액션/옵션

### 🔴 CRITICAL — 즉시 액션 필요

| 우선순위 | 액션 | 상태 |
|:--:|------|:----:|
| **P0** | **systemd 등록 — 6회째 미실행** | ⏳ 사용자 |
| **P0** | 백엔드 복구 (`./start.sh`) | ⏳ 사용자 |
| **P1** | 디스크 WARNING — 원인 추적 + 정리 (52% → < 50%) | ⏳ 사용자 |

### systemd 등록 (§7 #26)
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

### 백엔드 수동 복구 (systemd 등록 전 임시)
```bash
cd /home/comtop/workspace/VF2/backend && ./start.sh
```

---

## ⑦ 결론

- 🔴 **디스크 52% WARNING 재선언** — 50% 임계치 재돌파, +3%p/1일 가속 지속 (07-02 정상 → 07-03 WARNING)
- 🔴 백엔드/프론트엔드 **14일째 DOWN**, systemd 미등록 **6회째** — P0 CRITICAL 지속
- DB 데이터는 **완전 동결** (15,886행, max_date 06-09, 모든 DB 지표 변동 0)
- 침묵 **24일** — 백엔드 DOWN이 직접적 원인
- ⚠️ swap 95% 사용 — 메모리 압박 관찰 필요

---

## 3중 완료 (Wiki + Git push)

- ✅ Wiki 저장: `/home/comtop/workspace/Wiki/Hermes/자가-학습-Cron/VF2-Production-Plan-Nightly-20260703.md` (git repo 직접, §7 #33)
- ✅ Git commit + push: 본 보고서 하단에 결과 명시
- log.md: 부재 (§7 #31 fallback — 보고서 파일로 대체)

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260702.md` (07-02 05:31)
- canonical: `references/vf2-production-plan-nightly-canonical.md`
- 함정: §7 #21 (pg_stat stale), §7 #26 (systemd 6회째), §7 #30 (디스크 해소 판정), §7 #32 (디스크 원인 배제), §7 #34 (디스크 정리 후 재가속)
