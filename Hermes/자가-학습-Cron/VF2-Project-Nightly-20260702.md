# VF2 Project Nightly — 2026-07-02 자가 점검 보고 (2차 cron)

**점검 시각**: 2026-07-02 06:31 KST (cron 2회차)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
**직전 보고서**: `VF2-Production-Plan-Nightly-20260702.md` (07-02 05:31, 1회차 cron)
**비교 기준**: 오늘 1회차 (05:31) 대비 변동 — §0.1 같은 날 2회 실행 패턴

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:--:|---|
| 1. Wiki 검색 | ✅ | 1회차 `VF2-Production-Plan-Nightly-20260702.md` 확인 |
| 2. 스킬 로드 | ✅ | `vf2` umbrella + canonical reference 로드 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health 5종 + SQL 7종 + pg_class 28 tables + 침묵 + 디스크 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬 부재, umbrella `vf2` reference로 우회).

---

## ① 시스템 상태 (1회차 대비 변동)

| 지표 | 1회차 (05:31) | **2회차 (06:31)** | 변동 |
|------|:---:|:---:|:----:|
| **Health** | `curl: (7) Failed to connect` | `curl: (7) Failed to connect` | 동일 |
| **uptime** | 9일 9시간 | **9일 10시간** (+1h 자연 경과) | — |
| **백엔드 PID** | 0건 | **0건** | 동일 |
| **Vite PID** | 0건 | **0건** | 동일 |
| **디스크 `/`** | 49% | **49%** | 0%p ✅ |
| **PostgreSQL** | Up 9 days | **Up 9 days** | 동일 |
| **DB 테이블** | 28개 | **28개** | 변동 0 |

### 1.2 🔴 백엔드/프론트엔드 DOWN 프로토콜 (13일째)

| 진단 | 결과 |
|------|------|
| uptime | 9일 10시간 (06-22 20:13 KST 이후 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | **0건** |
| `curl localhost:5176/api/health` | `curl: (7) Failed to connect` |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **13일 전** |
| `docker ps postgres_hermes` | Up 9 days |
| 디스크 원인 배제 | ✅ 49% (< 50%) — §7 #32 디스크 원인 확정 배제 |

**결론**: 백엔드/프론트엔드 DOWN **13일째** (06-19 중단). 단일 원인: **systemd/s6 미등록** (§7 #26).

**⚠️ systemd 등록 미실행 5회째**: 6/23 → 6/26 → 6/30 → 7/01 → **7/02**. CRITICAL 상태 지속.

### 1.3 DB 테이블 (28개, 변동 0)

**(a) pg_stat_user_tables → stale (§7 #21)**: 컨테이너 Up 9 days 상태에서도 stale 지속.
**(a-fallback) pg_class 직접 조회 → 28개 테이블** (1회차와 완전 동일):

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

**(b) `production_plans` → NULL** (부재, 동일)

---

## ② 발견된 문제 (1회차 대비 변화)

### 핵심 결론: 1회차 대비 **모든 지표 변동 0** — 데이터 완전 동결

### DB 정확 카운트 (SQL 재측정, carry-forward 금지)

| 항목 | 1회차 (05:31) | **2회차 (06:31)** | 변동 |
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

## ③ 운영 침묵 측정

| 기준 | 일수 | 판정 |
|------|---:|:----:|
| **max_date 기준** (오늘 - MAX(date)) | 07-02 - 06-09 = **23일** | 🔴 **≥ 5일 (임계치 2 초과)** |

백엔드 DOWN(13일)이 침묵의 직접적 원인. 복구 전까지 침묵 지속 불가피.

---

## ④ 디스크 추세

| 날짜 | 사용% | 일일 Δ |
|------|---:|---:|
| 06-30 | 44% | (대규모 정리 해소) |
| 07-01 | 47% | +3%p |
| 07-02 (1회차) | 49% | +2%p |
| **07-02 (2회차)** | **49%** | **0%p** |

- 절대값 < 50% → **정상** (§7 #30)
- 1회차→2회차: **0%p 정체** — 디스크 증가 일시 정지 (양호)
- 2일 평균: +2.5%p/일

---

## ⑤ 미해결 항목 추적

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | 운영 침묵 **23일** (max_date 기준) | 등록 정체 | ⏳ 사용자 | 동일 |
| 2 | 🔴 백엔드/프론트엔드 DOWN **13일째** | 전체 시스템 마비 | ⏳ 사용자 | 동일 |
| 3 | systemd/s6 미등록 (**5회째 권고 미실행**) | 재부팅 시 미복구 반복 | ⏳ 사용자 | 동일 |
| 4 | pending 4,967건 status 누적 | UI 표시 정책 | ⏳ 사용자 | 동일 |
| 5 | 6-튜플 중복 4행 (mold 111, 06-08·09) | 운영 정확성 | ⏳ 사용자 | 동일 |
| 6 | color2 White 180 대소문자 158건 | 표기 통일 | ⏳ 사용자 | 동일 |
| 7 | `production_plans` 테이블 부재 | import 누락 단서 | ⏳ 사용자 | 동일 |
| 8 | blank color2 3건 (mold 114 등) | 료 위반 | ⏳ 사용자 | 동일 |
| 9 | started 10,916건 → pending/ended 전환 정책 | UI 표시 | ⏳ 사용자 | 동일 |

---

## ⑥ 액션/옵션

### 🔴 CRITICAL — 즉시 액션 필요

| 우선순위 | 액션 | 상태 |
|:--:|------|:----:|
| **P0** | **systemd 등록 — 5회째 미실행** | ⏳ 사용자 |
| **P0** | 백엔드 복구 (`./start.sh`) | ⏳ 사용자 |

```bash
# systemd 등록 (§7 #26)
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

- **1회차(05:31) 대비 모든 지표 변동 0** — 데이터 완전 동결 상태 이중 확인 완료
- 백엔드/프론트엔드 **13일째 DOWN**, systemd 미등록 **5회째** — **P0 CRITICAL 지속**
- 디스크 49% (1회차→2회차 0%p 정체) — 정상 유지
- 백엔드 복구 없이는 침묵 23일 해소 불가

---

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260702.md` (07-02 05:31, 1회차 cron)
- canonical: `references/vf2-production-plan-nightly-canonical.md`
- 함정: §7 #21 (pg_stat stale), §7 #26 (systemd 5회째), §7 #30 (디스크 해소 판정), §7 #32 (디스크 원인 배제)
