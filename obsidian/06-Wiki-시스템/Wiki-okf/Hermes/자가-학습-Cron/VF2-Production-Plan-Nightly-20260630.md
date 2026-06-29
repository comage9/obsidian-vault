# VF2 Production Plan Nightly — 2026-06-30 자가 점검 보고

**점검 시각**: 2026-06-30 05:30:52 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 없음)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md` (1순위)
**직전 보고서**: `VF2-Production-Plan-Nightly-20260626.md` (06-26 05:30 작성, 4일 전)

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:-:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 `VF2-Production-Plan-Nightly-20260626.md` 확인 (4일 전). 보고서 부재 06-27~06-29 (3일, §7 #23 장기 부재 미해당) |
| 2. 스킬 로드 | ⚠️ skip | `vf2-production-plan-conventions` 스킬 부재 → `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md`로 대체 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health(connect fail/DOWN), §1.2 DOWN 프로토콜, DB 28 tables, status 분포, 침묵 측정, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재.

---

## ① 시스템 상태

| 지표 | 6/26 값 | **6/30 값** | 판정 |
|------|---:|---:|:----:|
| **Health** | connect fail | `curl: (7) Failed to connect` | 🔴 **백엔드 DOWN** |
| **uptime** | 3일 9시간 | **7일 9시간** (06-22 20:13 KST 재부팅, 신규 재부팅 없음) | ⚠️ 동일 재부팅 유지 |
| **백엔드 PID** | 0건 | **0건** (`vf2_backend_bin` 부재) | 🔴 **11일째 DOWN** |
| **Vite PID** | 0건 | **0건** | 🔴 **11일째 DOWN** |
| **Listen 포트** | 0건 | **0건** (5174/5176 둘 다) | 🔴 systemd/s6 미등록 |
| **디스크 `/`** | **89%** | **44%** | 🟢 **정상** (-45%p/4일, **CRITICAL 해소**) |
| **메모리** | 14Gi/4.8Gi | 14Gi/4.8Gi | ✅ 정상 |
| **PostgreSQL** | Up 3 days | **Up 7 days** | ✅ Docker restart policy |
| **DB 테이블** | 28개 | **28개** (변동 0) | ✅ 정상 |

### 1.2 🚨 백엔드/프론트엔드 DOWN 프로토콜 (11일째)

| 진단 | 결과 |
|------|------|
| uptime | 7일 9시간 (06-22 20:13 KST 이후 재부팅, 신규 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | 0건 |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | 0건 (NO_PORTS_LISTENING) |
| `tail -5 backend.log` 마지막 timestamp | **2026-06-19 16:58:37** (`/login` 401) — **11일 전** |
| `docker ps postgres_hermes` | Up 7 days (Docker restart policy로 복구) |

**결론**: 06-26 보고서와 동일 상태 유지. 백엔드/프론트엔드 **DOWN 7일 → 11일** (+4일). backend.log 마지막 기록 동일 (06-19 16:58:37). **systemd/s6 미등록 함정 지속 (§7 #26, 3회째 권고 미실행)**.

### 1.3 DB 테이블 (28개, 6/26과 동일 — 변동 0)

**(a) pg_stat_user_tables → 0 rows** (stale 통계 함정 지속, §7 #21)
**(a-fallback) pg_class 직접 조회 → 28개 테이블** (6/26 목록과 완전 동일)
**(b) production_plans 존재 여부 → NULL** (부재, 6/26과 동일)
**(a-direct) production_logs 직접 카운트 = 15,886건** (6/26과 동일, 변동 0)

---

## ② 발견된 문제 (6/26 대비 변화)

### 🟢 발견 1: 디스크 89% → **44%** — CRITICAL 해소 (-45%p/4일)

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/26 | 89% | +2.4%p/1일 (평균) | 🔴 CRITICAL 임박 |
| (6/27~6/29 미측정) | - | - | - |
| **6/30** | **44%** | **-45%p/4일 (-11.3%p/1일 평균)** | 🟢 **정상 해소** |

- **6/26 89% → 6/30 44%**: 절대값 50% 미만 회복. CRITICAL 및 WARNING 모두 해소.
- **원인 추정**: 06-26~06-29 사이 대규모 디스크 정리 발생 (사용자 또는 자동화). `/tmp`, 로그, Docker image, 백업 파일 등 정리 추정.
- **canonical §4.2 주의**: "WARNING 해소" 표현은 7일 이상 정체 후 확정이 원칙이나, **절대값 44% (< 50%)는 임계치 자체 미해당** → 명확한 해소 선언 가능.

### 🔴 발견 2: 백엔드/프론트엔드 **11일째 DOWN** (7일 → 11일, +4일)

- **근거**: `ps -ef | grep vf2_backend_bin` → 0건, `ss -tlnp` → 0건
- **backend.log 마지막**: 2026-06-19 16:58:37 (6/26과 동일, 신규 기록 없음)
- **systemd/s6 미등록**: §7 #26 — 6/23 권고 → 6/26 권고 반복 → **6/30 3회째 권고**. 미실행 카운트 3회 누적.
- **사용자 액션 필수** (변동 없음, 6/26 권고 계승):
  ```bash
  cd /home/comtop/workspace/VF2/backend && ./start.sh
  cd /home/comtop/workspace/VF2/frontend && npm run dev
  ```

### 발견 3: 운영 침묵 **max_date 기준 21일째** (17일 → 21일, +4일)

- **근거**: `production_logs` `MAX(date) = 2026-06-09` (6/26과 동일)
- **max_date 기준 침묵**: 2026-06-30 - 2026-06-09 = **21일** (6/26의 17일 → +4일)
- **단순 계산 침묵**: backend.log 마지막 활동 06-19 16:58 → **11일** (6/26의 7일 → +4일)
- **백엔드 DOWN 영향**: 06-19~06-30 (11일) POST 자체 불가 → 인위적 침묵 포함
- **판정**: 단순 침묵 ≠ 결함. max_date 기준은 DB 직접 SELECT이므로 백엔드 상태와 무관, 유효.

### 발견 4: DB 완전 정적 — 모든 지표 변동 0건 (6/26과 동일)

| 지표 | 6/26 | **6/30** | 변동 |
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

- **4일간 DB 변경 0건 = 백엔드 DOWN으로 인한 구조적 정지 (침묵 증명)**

---

## ③ 사용자 확인 요청 (CRITICAL 1건 + 일반 3건)

### 🚨 CRITICAL Q1: "백엔드/프론트엔드 11일째 DOWN — 복구 지시 + systemd 등록 필수"

**변동**: 6/26 7일째 → **6/30 11일째** (+4일)

**systemd 등록 미실행 카운트**: 3회 (6/23 → 6/26 → 6/30). §7 #26 정책에 따라 **CRITICAL — systemd 등록 미실행 3회째**.

| 가능성 | 근거 |
|---|---|
| A) systemd/s6 미등록 (확정) | 06-22 20:13 재부팅 후 미복구. 11일째 지속 |
| B) 디스크 문제 | ~~6/26 89%~~ → 6/30 **44% 해소** (디스크 원인 배제) |

**즉시 권장 액션**:
```bash
cd /home/comtop/workspace/VF2/backend && ./start.sh
cd /home/comtop/workspace/VF2/frontend && npm run dev
ss -tlnp | grep -E ':(5174|5176)\b'
curl http://localhost:5176/api/health
```

### 🟢 해소 보고: 디스크 CRITICAL 해소 (89% → 44%)

06-26 CRITICAL Q2로 보고했던 디스크 89%가 **44%로 회복**. 원인 추정: 대규모 디스크 정리. 본 보고서에서는 해소 사실만 기록, 정리 내용 확인 불필요.

### 일반 Q2: "운영 침묵 max_date 기준 21일 — 의도된 침묵인가요?" (계승)

| 가능성 | 근거 |
|---|---|
| A) 1.xlsx import 후 자연 정체 | 6/10 started 10,916건 일괄 등재 후 정체, 20일째 |
| B) 백엔드 DOWN으로 인한 인위적 침묵 | 06-19~06-30 (11일) POST 자체 불가 |
| C) 단순 미작업 | 6/9(화) 이후 사용자 등록 작업 없음 |

### 일반 Q3: "DB 4일간 완전 정적 — 모든 지표 변동 0건"

백엔드 DOWN으로 인한 구조적 정지. 백엔드 복구 후 신규 등록 재개 여부 확인 필요.

### 일반 Q4: "production_plans 테이블 부재 지속" (계승, LOW)

`to_regclass('public.production_plans')` → NULL. 1.xlsx import 대상 테이블 부재. 사용자 확인 필요.

---

## ④ 미해결 항목 추적 (6/26 → 6/30)

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **백엔드/프론트 11일째 DOWN** | 서비스 불가 | 🔴 사용자 즉시 | 7일 → **11일 (+4일)** |
| 2 | ~~디스크 89% CRITICAL~~ | ~~1~2주 위험~~ | ✅ **해소** | 89% → **44% (-45%p)** |
| 3 | 운영 침묵 21일 (max_date 기준) | 등록 의도 | ⏳ 사용자 | 17일 → **21일 (+4일)** |
| 4 | DB 4일간 완전 정적 (변동 0) | 구조적 정지 | ⏳ 사용자 | 신규 |
| 5 | status started 10,916건 옵션 결정 | UI 표시 정책 | ⏳ 사용자 | 변동 0 (20일째) |
| 6 | mold 111 Butter 6-튜플 중복 4행 (운영) | 운영 정확성 | ⏳ 사용자 | 변동 0 (23일째) |
| 7 | 빈 color2 (운영) 3건 | 룰 위반 | ⏳ 사용자 | 변동 0 |
| 8 | 빈 moldNumber 10건 | 노이즈 | ⏳ 사용자 | 변동 0 |
| 9 | machine `생산 대기/생산대기` 14건 | 표기 통일 | ⏳ 사용자 | 변동 0 |
| 10 | color2 White 180 158건 | 자동 정정 정책 | ⏳ 사용자 | 변동 0 (13일째) |
| 11 | `production_plans` 테이블 부재 | 1.xlsx import 단서 | ⏳ 사용자 | 부재 지속 |
| 12 | historical 6-튜플 중복 20종 | 데이터 정확성 | ⏳ 사용자 | 변동 0 |
| 13 | 백엔드 systemd/s6 미등록 | 재부팅 시 미복구 | 🔴 사용자 | **3회째 권고 미실행** |

---

## ⑤ 액션 / 옵션

### 즉시 (CRITICAL, 사용자 결정 대기)

- [ ] **🔴 백엔드/프론트 복구**: `./start.sh` + `npm run dev` (11일째)
- [ ] **🔴 systemd/s6 등록**: 3회째 권고. 재부팅 시 자동 복구 위해 즉시 등록 필수
  ```bash
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

### 해소 완료

- [x] ~~디스크 89% 정리~~ → **44% 회복** (06-26~06-29 사이 정리 완료)

### 방치 가능 (사용자 결정 대기)

- [ ] 운영 침묵 21일 (max_date 기준) — 백엔드 복구 후 재개 여부
- [ ] status started 10,916건 옵션 결정 (20일째)
- [ ] mold 111 Butter 6-튜플 중복 4행 — 옵션 1 (병합) 권장
- [ ] 6/8 미해결 결함 (빈 color2 / 빈 moldNumber / `생산 대기` / historical 중복)
- [ ] `production_plans` 부재 — 1.xlsx import 누락 단서

### 시스템 (✅ 정상)

- PostgreSQL Docker 자동 복구 ✅ (Up 7 days)
- DB 직접 SELECT 가능 (28 tables) ✅
- 디스크 44% 정상 ✅
- (mold, productName) 1:1 위반 (운영) 0건 ✅
- 운영 6-튜플 중복 (mold 111 외) 0건 ✅
- production_logs 15,886건 (변동 0) ✅

---

## ⑥ 디스크 가속 추이

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/17 | 67% | +3%p/1일 | ⚠️ WARNING 재발 |
| 6/26 | 89% | +2.4%p/1일 (평균 9일) | 🔴 CRITICAL 임박 |
| (6/27~6/29 미측정) | - | - | - |
| **6/30** | **44%** | **-11.3%p/1일 (평균 4일)** | 🟢 **정상 — CRITICAL 해소** |

- 06-26 89% → 06-30 44% = **-45%p/4일**
- 절대값 44% (< 50%) → 임계치 미해당. WARNING 및 CRITICAL 모두 해소.
- **원인 추정**: 사용자 또는 자동화 스크립트에 의한 대규모 디스크 정리.

---

## ⑦ 결론

**시스템 상태**:
- 🟢 **디스크 CRITICAL 해소**: 89% → 44% (-45%p/4일). 본 점검의 가장 긍정적 변화.
- 🔴 **백엔드/프론트엔드 11일째 DOWN**: systemd/s6 미등록 (권고 3회째 미실행). 사용자 즉시 복구 + systemd 등록 필수.
- ✅ PostgreSQL 정상 (Up 7 days), DB 28 테이블 정상.
- ✅ DB 완전 정적 (4일간 변동 0건, 백엔드 DOWN으로 인한 구조적 정지).

**변동 요약 (6/26 → 6/30)**:
1. 🟢 디스크 89% → **44%** (CRITICAL 해소)
2. 🔴 백엔드 DOWN 7일 → **11일** (+4일)
3. 침묵 max_date 17일 → **21일** (+4일)
4. DB 모든 지표 **변동 0** (15,886건, status 분포, 6-튜플, color2 등 전부 동일)
5. DB 테이블 28개 → **28개** (신규 0)

**🚨 사용자 즉시 액션 권장**:
1. **백엔드/프론트 복구**: `./start.sh` + `npm run dev`
2. **systemd 등록**: 재발 방지 (3회째 권고, 미실행 시 다음 재부팅에서 동일 장애 재발)

---

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260626.md` (4일 전)
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (6/26과 동일)
- 점검 시각: 2026-06-30 05:30:52 KST
- 스킬 부재: `vf2-production-plan-conventions` (loadable skill로 존재하지 않음)
- USER.md / MEMORY.md 부재: skip
- 보고서 부재: 06-27~06-29 (3일, §7 #23 장기 부재 프로토콜 미해당)
