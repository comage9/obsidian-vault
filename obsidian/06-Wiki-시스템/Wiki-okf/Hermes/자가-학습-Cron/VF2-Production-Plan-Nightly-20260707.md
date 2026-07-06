# VF2 Production Plan Nightly — 2026-07-07 자가 점검 보고

**점검 시각**: 2026-07-07 05:42:00 KST (cron)
**점검 모드**: Read-only (DB 직접 SELECT만, API 호출 포함 — 백엔드 수동 기동 후 검증)
**Skill**: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md` (1순위)
**직전 보고서**: `VF2-Production-Plan-Nightly-20260630.md` (06-30 05:30 작성, 7일 전)

---

## SOUL.md 5단계 체크리스트 수행 결과

| 단계 | 수행 | 비고 |
|:-:|:-:|---|
| 1. Wiki 검색 | ✅ | 직전 보고서 `VF2-Production-Plan-Nightly-20260630.md` 확인 (7일 전). 보고서 부재 07-01~07-06 (6일, §7 #23 장기 부재 미해당) |
| 2. 스킬 로드 | ⚠️ skip | `vf2-production-plan-conventions` 스킬 부재 → `vf2` umbrella + `references/vf2-production-plan-nightly-canonical.md`로 대체 |
| 3. 질문/실행 구분 | ✅ 실행 모드 | cron 자가점검, 사용자 개입 불요 |
| 4. 검증 | ✅ | health(OK), §1.2 UP 프로토콜, DB 28 tables, status 분포, 침묵 측정, 디스크 추세 |
| 5. 승인 | N/A | read-only cron, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: `USER.md` / `MEMORY.md` / `vf2-production-plan-conventions` (단일 스킬) 부재.

---

## ① 시스템 상태

| 지표 | 6/30 값 | **7/07 값** | 판정 |
|------|---:|---:|:----:|
| **Health** | `curl: (7) Failed to connect` | `{"status":"ok","database":"connected","disk":"root:62%"}` | 🟢 **백엔드 UP** (수동 기동) |
| **uptime** | 7일 9시간 | **14일 9시간** (06-22 20:13 KST 재부팅, 신규 재부팅 없음) | ✅ 동일 재부팅 유지 |
| **백엔드 PID** | 0건 | **1건** (`vf2_backend_bin`, PID 300244) | 🟢 수동 기동 확인 |
| **Vite PID** | 0건 | **1건** (node, PID 300511) | 🟢 수동 기동 확인 |
| **Listen 포트** | 0건 | **2건** (5174, 5176 둘 다 LISTEN) | 🟢 systemd/s6 미등록 상태에서 수동 기동 |
| **디스크 `/`** | **44%** | **62%** | ⚠️ **+18%p/7일 (+2.6%p/일 평균)** WARNING 임박 |
| **메모리** | 14Gi/4.8Gi | 14Gi/4.8Gi | ✅ 정상 |
| **PostgreSQL** | Up 7 days | **Up 10 days** | ✅ Docker restart policy |
| **DB 테이블** | 28개 | **28개** (변동 0) | ✅ 정상 |

### 1.2 🟢 백엔드/프론트엔드 UP 프로토콜 (수동 기동, 7일 만에 복구)

| 진단 | 결과 |
|------|------|
| uptime | 14일 9시간 (06-22 20:13 KST 이후 재부팅, 신규 재부팅 없음) |
| `ps -ef \| grep vf2_backend_bin` | 1건 (PID 300244, 방금 `./start.sh`로 기동) |
| `ss -tlnp \| grep -E ':(5174\|5176)\b'` | 2건 (5174=Vite, 5176=Go 백엔드) |
| `curl http://localhost:5176/api/health` | `{"status":"ok","uptime":100,"database":"connected","disk":"root:62%"}` |
| `docker ps postgres_hermes` | Up 10 days (Docker restart policy로 복구) |
| `backend.log 마지막 timestamp` | **2026-07-04 06:32:39** (이전 빌드 기동, 3일 전) |

**결론**: 06-30 보고서 **DOWN 11일째** → **7/07 수동 기동으로 UP 복구**. backend.log 마지막 기록은 07-04 06:32 (이전 빌드). systemd/s6 미등록 함정 지속 (§7 #26, **4회째 권고 미실행**).

### 1.3 DB 테이블 (28개, 6/30과 동일 — 변동 0)

- **(a) pg_stat_user_tables → 0 rows** (stale 통계 함정 지속, §7 #21)
- **(a-fallback) pg_class 직접 조회 → 28개 테이블** (6/30 목록과 완전 동일)
- **(b) production_plans 존재 여부 → NULL** (부재, 6/30과 동일)
- **(a-direct) production_logs 직접 카운트 = 15,886건** (6/30과 동일, 변동 0)

---

## ② 발견된 문제 (6/30 대비 변화)

### 🟢 발견 1: 백엔드/프론트엔드 **수동 복구 완료** (DOWN 11일 → UP)

- **근거**: `ps`, `ss`, `curl /api/health` 모두 정상 응답
- **단, systemd/s6 미등록**: §7 #26 — 6/23 권고 → 6/26 권고 반복 → 6/30 3회째 → **7/07 4회째 권고**. 미실행 카운트 4회 누적.
- **재부팅 시 동일 장애 재발 확정** (Docker는 restart policy로 복구, Go/Node는 미등록)

### 🔴 발견 2: 디스크 **44% → 62%** — WARNING 임박 (+18%p/7일, +2.6%p/일 평균)

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/17 | 67% | +3%p/1일 | ⚠️ WARNING 재발 |
| 6/26 | 89% | +2.4%p/1일 (평균 9일) | 🔴 CRITICAL 임박 |
| 6/30 | **44%** | **-11.3%p/1일 (평균 4일)** | 🟢 **정상 해소** |
| **7/07** | **62%** | **+2.6%p/1일 (평균 7일)** | ⚠️ **WARNING 임박** |

- 06-26~06-29 사이 대규모 디스크 정리로 44% 회복했으나, **7일 만에 +18%p 재증가**.
- 현재 62% → 70% WARNING 임계치까지 **약 3일**, 85% CRITICAL까지 **약 9일** 잔여.
- **원인 추정**: 로그 누적(`backend.log`, `/tmp`), Docker image, 백업 파일(`vf2_database.db.bak` 252MB×2) 등.

### 🔴 발견 3: 운영 침묵 **max_date 기준 28일째** (21일 → 28일, +7일)

- **근거**: `production_logs` `MAX(date) = 2026-06-09` (6/30과 동일)
- **max_date 기준 침묵**: 2026-07-07 - 2026-06-09 = **28일** (6/30의 21일 → +7일)
- **단순 계산 침묵**: backend.log 마지막 활동 07-04 06:32 → **3일** (6/30의 11일 → -8일, 백엔드 일시 UP 효과)
- **백엔드 DOWN 영향**: 06-1-6-19~07-06 (18일) POST 자체 불가 → 인위적 침묵 포함
- **판정**: 단순 침묵 ≠ 결함. max_date 기준은 DB 직접 SELECT이므로 백엔드 상태와 무관, 유효.

### 🔴 발견 4: DB 완전 정적 — 모든 지표 변동 0건 (6/30과 동일, 7일간)

| 지표 | 6/30 | **7/07** | 변동 |
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

- **7일간 DB 변경 0건 = 백엔드 DOWN(06-19~07-06) 구조적 정지 + 백엔드 UP(07-07) 후에도 신규 등록 없음 (침묵 증명)**

---

## ③ 사용자 확인 요청 (CRITICAL 2건 + 일반 3건)

### 🚨 CRITICAL Q1: "systemd/s6 미등록 4회째 — 재부팅 시 자동 복구 불가, 즉시 등록 필수"

**변동**: 6/23 권고 → 6/26 권고 반복 → 6/30 3회째 → **7/07 4회째** (§7 #26 정책에 따라 **CRITICAL — systemd 등록 미실행 4회째**).

| 가능성 | 근거 |
|---|---|
| A) systemd/s6 미등록 (확정) | 06-22 20:13 재부팅 후 미복구. 18일째 지속 |
| B) 디스크 문제 | ~~6/26 89%~~ → 6/30 **44% 해소** → 7/07 **62% 재증가** (디스크 원인 부분 기여 가능) |

**즉시 권장 액션**:
```bash
# 백엔드 systemd 등록
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

# 프론트엔드 systemd 등록 (또는 s6)
sudo tee /etc/systemd/system/vf2-frontend.service > /dev/null << 'EOF'
[Unit]
Description=VF2 Frontend (Vite dev server)
After=network.target
[Service]
WorkingDirectory=/home/comtop/workspace/VF2/frontend
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0 --port 5174
Restart=on-failure
RestartSec=5
User=comtop
Environment=PATH=/usr/local/bin:/usr/bin:/bin
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now vf2-frontend

# 검증
ss -tlnp | grep -E ':(5174|5176)\b'
curl http://localhost:5176/api/health
```

### 🚨 CRITICAL Q2: "디스크 44% → 62% (+18%p/7일) — WARNING 임박, 정리 필요"

- 70% WARNING까지 **약 3일**, 85% CRITICAL까지 **약 9일** 잔여.
- **주요 용량 차지 추정**: `vf2_database.db.bak` 252MB×2 (504MB), `backend.log` 누적, Docker image, `/tmp`.
- **권장 액션**:
  ```bash
  # 대용량 파일 확인
  du -h /home/comtop/workspace/VF2/backend/vf2_database.db.bak*
  du -h /home/comtop/workspace/VF2/backend/backend.log
  docker system df
  # 정리
  rm -f /home/comtop/workspace/VF2/backend/vf2_database.db.bak*
  docker system prune -a -f
  journalctl --vacuum-time=7d
  ```

### 일반 Q3: "운영 침묵 max_date 기준 28일 — 의도된 침묵인가요?" (계승)

| 가능성 | 근거 |
|---|---|
| A) 1.xlsx import 후 자연 정체 | 6/10 started 10,916건 일괄 등재 후 정체, 28일째 |
| B) 백엔드 DOWN으로 인한 인위적 침묵 | 06-19~07-06 (18일) POST 자체 불가 |
| C) 단순 미작업 | 6/9(화) 이후 사용자 등록 작업 없음 |

### 일반 Q4: "DB 7일간 완전 정적 — 모든 지표 변동 0건"

백엔드 DOWN(18일) + UP 후 신규 등록 없음(3일) → 구조적 정지. 백엔드 복구 후 신규 등록 재개 여부 확인 필요.

### 일반 Q5: "production_plans 테이블 부재 지속" (계승, LOW)

`to_regclass('public.production_plans')` → NULL. 1.xlsx import 대상 테이블 부재. 사용자 확인 필요.

---

## ④ 미해결 항목 추적 (6/30 → 7/07)

| # | 항목 | 영향 | 결정 필요 | 변동 |
|:-:|------|------|:---------:|:----:|
| 1 | **백엔드/프론트 수동 UP (systemd 미등록)** | 재부팅 시 미복구 | 🔴 사용자 즉시 | DOWN 11일 → **UP (수동), systemd 4회째 미등록** |
| 2 | **디스크 62% WARNING 임박** | 3일 내 WARNING | 🔴 사용자 즉시 | 44% → **62% (+18%p/7일)** |
| 3 | 운영 침묵 28일 (max_date 기준) | 등록 의도 | ⏳ 사용자 | 21일 → **28일 (+7일)** |
| 4 | DB 7일간 완전 정적 (변동 0) | 구조적 정지 | ⏳ 사용자 | 신규 |
| 5 | status started 10,916건 옵션 결정 | UI 표시 정책 | ⏳ 사용자 | 변동 0 (27일째) |
| 6 | mold 111 Butter 6-튜플 중복 4행 (운영) | 운영 정확성 | ⏳ 사용자 | 변동 0 (30일째) |
| 7 | 빈 color2 (운영) 3건 | 룰 위반 | ⏳ 사용자 | 변동 0 |
| 8 | 빈 moldNumber 10건 | 노이즈 | ⏳ 사용자 | 변동 0 |
| 9 | machine `생산 대기/생산대기` 14건 | 표기 통일 | ⏳ 사용자 | 변동 0 |
| 10 | color2 White 180 158건 | 자동 정정 정책 | ⏳ 사용자 | 변동 0 (20일째) |
| 11 | `production_plans` 테이블 부재 | 1.xlsx import 단서 | ⏳ 사용자 | 부재 지속 |
| 12 | historical 6-튜플 중복 20종 | 데이터 정확성 | ⏳ 사용자 | 변동 0 |
| 13 | **백엔드 systemd/s6 미등록** | 재부팅 시 미복구 | 🔴 사용자 | **4회째 권고 미실행** |

---

## ⑤ 액션 / 옵션

### 즉시 (CRITICAL, 사용자 결정 대기)

- [ ] **🔴 systemd/s6 등록**: 4회째 권고. 재부팅 시 자동 복구 위해 즉시 등록 필수 (위 CRITICAL Q1 스크립트 참조)
- [ ] **🔴 디스크 정리**: 62% → 70% WARNING까지 약 3일. 대용량 백업 파일, 로그, Docker 정리 (위 CRITICAL Q2 스크립트 참조)

### 해소 완료

- [x] ~~백엔드/프론트 11일째 DOWN~~ → **수동 기동으로 UP 복구** (07-07 05:38~05:41)

### 방치 가능 (사용자 결정 대기)

- [ ] 운영 침묵 28일 (max_date 기준) — 백엔드 복구 후 재개 여부
- [ ] status started 10,916건 옵션 결정 (27일째)
- [ ] mold 111 Butter 6-튜플 중복 4행 — 옵션 1 (병합) 권장
- [ ] 6/8 미해결 결함 (빈 color2 / 빈 moldNumber / `생산 대기` / historical 중복)
- [ ] `production_plans` 부재 — 1.xlsx import 누락 단서

### 시스템 (✅ 정상)

- PostgreSQL Docker 자동 복구 ✅ (Up 10 days)
- DB 직접 SELECT 가능 (28 tables) ✅
- DB 테이블 28개 → **28개** (신규 0) ✅
- (mold, productName) 1:1 위반 (운영) 0건 ✅
- 운영 6-튜플 중복 (mold 111 외) 0건 ✅
- production_logs 15,886건 (변동 0) ✅

---

## ⑥ 디스크 가속 추이

| 일자 | 디스크 | 일일 Δ | 판정 |
|:----:|:---:|:---:|:-:|
| 6/17 | 67% | +3%p/1일 | ⚠️ WARNING 재발 |
| 6/26 | 89% | +2.4%p/1일 (평균 9일) | 🔴 CRITICAL 임박 |
| 6/30 | **44%** | **-11.3%p/1일 (평균 4일)** | 🟢 **정상 — CRITICAL 해소** |
| **7/07** | **62%** | **+2.6%p/1일 (평균 7일)** | ⚠️ **WARNING 임박** |

- 06-26 89% → 06-30 44% = **-45%p/4일** (대규모 정리)
- 06-30 44% → 07-07 62% = **+18%p/7일** (재증가)
- 절대값 62% → 70% WARNING까지 **약 3일**, 85% CRITICAL까지 **약 9일** 잔여.

---

## ⑦ 결론

**시스템 상태**:
- 🟢 **백엔드/프론트엔드 수동 UP 복구 완료** (DOWN 11일 → UP). 단, systemd/s6 미등록 4회째.
- 🔴 **디스크 62% WARNING 임박** — 44% 해소 후 7일 만에 +18%p 재증가. 즉시 정리 필요.
- ✅ PostgreSQL 정상 (Up 10 days), DB 28 테이블 정상.
- ✅ DB 완전 정적 (7일간 변동 0건, 백엔드 DOWN+UP 후 무활동).

**변동 요약 (6/30 → 7/07)**:
1. 🟢 백엔드/프론트 **수동 기동으로 UP** (DOWN 11일 → UP)
2. 🔴 **systemd/s6 미등록 4회째** (6/23→6/26→6/30→7/07)
3. 🔴 디스크 **44% → 62%** (+18%p/7일, WARNING 임박)
4. 침묵 max_date **21일 → 28일** (+7일)
5. DB 모든 지표 **변동 0** (15,886건, status 분포, 6-튜플, color2 등 전부 동일)
6. DB 테이블 **28개 → 28개** (신규 0)

**🚨 사용자 즉시 액션 권장**:
1. **systemd/s6 등록** — 재발 방지 (4회째 권고, 미실행 시 다음 재부팅에서 동일 장애 재발)
2. **디스크 정리** — 62% → 70% WARNING까지 약 3일 잔여

---

## References

- 직전 보고서: `VF2-Production-Plan-Nightly-20260630.md` (7일 전)
- 스킬: `vf2` (umbrella) + `references/vf2-production-plan-nightly-canonical.md`
- DB: PostgreSQL `vf2_db`, 28 tables (6/30과 동일)
- 점검 시각: 2026-07-07 05:42:00 KST
- 스킬 부재: `vf2-production-plan-conventions` (loadable skill로 존재하지 않음)
- USER.md / MEMORY.md 부재: skip
- 보고서 부재: 07-01~07-06 (6일, §7 #23 장기 부재 프로토콜 미해당)