# 2026-08-20 VF2 Self-Check — 일일 자가 점검 보고서

> 2026-08-20 06:30 KST 실행. SOUL.md 5단계 체크리스트 준수.

---

## 시스템 상태 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| **백엔드 (Go/Gin, 포트 5176)** | ✅ 실행 중 | 인증 토큰 필요 응답 (정상) |
| **프론트엔드 (React/Vite, 포트 5174)** | ✅ 실행 중 | HTML 서빙 확인 |
| **PostgreSQL (vf2_db, Docker)** | ✅ 실행 중 | Up 3 days, 포트 5432 |
| **systemd 서비스 등록** | ❌ 미등록 | **7회째 반복 함정** (06-23~08-20) |
| **디스크 사용률 (/dev/nvme0n1p2)** | 🔴 **96%** | 212G/233G 사용, **CRITICAL** |

---

## 데이터베이스 상태

### production_logs 현황
- started: 10,916 (68.7%) — 70% 경보 임박
- pending: 4,967 (31.3%)
- ended: 3 (0.02%)
- 총계: 15,886

### production_plans 테이블
- **54일째 부재** (to_regclass NULL 지속) — 마이그레이션 미수행

### 마지막 운영 데이터
- max(created_at) = 2026-06-09 08:20:13
- 운영 침묵: **72일째**
- backend.log 운영 호출: 0건

---

## 미해결 데이터 결함 4건 (잔존 일수 갱신)

| # | 결함 | 최초 발견 | 잔존 일수 | 현황 |
|---|------|----------|----------|------|
| 1 | 6-튜플 중복: mold 111 Butter | 06-08/09 | **73일** | 0건 (해소됨?) — 재확인 필요 |
| 2 | 데크타일(114) color2 빈값 | 06-07 | **74일** | 27건 (Black 25, Ivory 1, WHITE2 1) |
| 3 | 빈 moldNumber (M01 등) | 05-24 | **88일** | **14건** (증가: 1→14) |
| 4 | color2 'White 180' 비표준 | 06-08 | **73일** | 10건, 표준은 'WHITE 180' |

---

## 데이터 무결성 검증 (vf2-production-plan-conventions)

| 검사 항목 | 쿼리 | 결과 | 기준 | 상태 |
|-----------|------|------|------|------|
| **SWAP 탐지** | `unit_quantity < quantity` | **8,006건** | 0건 | 🔴 **CRITICAL** |
| **유일 제약** | `uniq_productionlog_full_key` | **부재** | 1개 존재 | 🔴 **CRITICAL** |
| **product_unit_specs** | `COUNT(*)` | **0건** | >0건 | 🔴 **CRITICAL** |
| **master_specs.default_quantity** | `COUNT(*) WHERE >0` | **0건** | >0건 | 🔴 **CRITICAL** |

---

## 인프라/운영 이슈

### systemd 미등록 — 7회째 반복 함정 (CRITICAL)
- 07-04 수동 기동 후 48시간 만 재종료 → 08-16 기동 후 14시간 만 재발 → 08-18 기동 후 1일 경과 → 현재 2일째
- 수동 기동만으로는 재발 방지 불가, systemd 등록이 유일한 영구 해법

### 디스크 사용률 96% — 재가속 가속화 **악화**
- 08-17: 73% (-10%p/1일 정리 후) → 08-19: 87% (+14%p/2일) → **08-20: 96% (+9%p/1일)**
- 현재 **+9%p/일** 가속 (이전 평균 +2.5~3%p/일)
- **수시간 내 100% 도달 위험** — DB 쓰기 실패 임박

---

## Cron Job 건강도

| Cron ID | 이름 | 상태 | 마지막 실행 |
|---------|------|------|-------------|
| 48144ff13cee | VF2 생산계획 자가 학습 | ✅ Active | 2026-08-20 05:35 OK |
| 27c1b2555f38 | VF2 프로젝트 자가 학습 | 🔄 **Running** | 현재 실행 중 (이 리포트) |

### 연관 Cron 이슈
- **429 Token Limit 다수**: auto-daily-summary, auto-weekly-optimization, Wiki Git Auto-Sync, Wiki Daily Cleanup, Wiki Daily Briefing 등 5개 작업 실패
- hermes_backup_* 5개 파일 존재 (3일 보관 정책 위반)

---

## 백업 위생

| 위치 | 파일 수 | 총 용량 | 정책 준수 |
|------|---------|---------|-----------|
| `/home/comtop/workspace/backups/` | 8개 (VF2 4 + ki-ai-trader 4) | ~7GB | ✅ 일일 백업 수행 중 |
| `/home/comtop/hermes_backup_*.tar.gz` | **5개** | ~93GB | ❌ **3일 보관 초과** (최소 2개 삭제 필요) |

---

## Canonical 절차 준수 검증 (SOUL.md 5단계)

| 단계 | 수행 | 비고 |
|------|------|------|
| 1. Wiki 검색 | ✅ | vf2 스킬 + references 로드, 직전 보고서 확인 |
| 2. 스킬 로드 | ✅ | vf2 umbrella skill, vf2-production-plan-conventions |
| 3. 질문/실행 구분 | ✅ | 크론 자동 실행 모드 (27c1b2555f38) |
| 4. 검증 | ✅ | DB 조회, 프로세스 확인, 디스크 체크, Cron 상태 완료 |
| 5. 승인 | ✅ | Read-only 점검, 사용자 결정 대기 항목만 보고 |

**Skip 명시**: USER.md/MEMORY.md/mandatory-verification 스킬 부재, hermes cron list 상 VF2 관련 작업 모두 active 상태 (paused 아님)

---

## 차기 점검 예측 (2026-08-21 06:30)

| 항목 | 예측 | 조건 |
|------|------|------|
| 백엔드/프론트 | **DOWN 임박** | systemd 미등록 + 디스크 100% 시 프로세스 강제 종료 |
| 디스크 | **100%** | +9%p/일 현재 가속도 유지 시 수시간 내 |
| 운영 침묵 | 73일째 | max_date 변동 없음 시 |
| 미해결 결함 | 4건 잔존 (3번 증가) | 사용자 정정 명령 없음 시 |
| started 비율 | ~68.7% | 변동 없음 시 70% 임계치 미도달 |

---

## 권고 사항 (우선순위순) — **즉시 조치 필요**

### 🔴 1순위: 디스크 비상 정리 (수시간 내)
```bash
# hermes 백업 3일 정책 적용 (최신 3개만 유지)
ls -t /home/comtop/hermes_backup_*.tar.gz | tail -n +4 | xargs rm -f

# Docker 볼륨 정리
docker system prune -f --volumes

# 로그 로테이션 설정 추가
```

### 🔴 2순위: systemd 서비스 등록 (영구 해법)
```bash
# 백엔드 서비스
sudo tee /etc/systemd/system/vf2-backend.service <<'EOF'
[Unit]
Description=VF2 Backend
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/home/comtop/workspace/VF2/backend
ExecStart=/home/comtop/workspace/VF2/backend/vf2-backend
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 프론트엔드 서비스
sudo tee /etc/systemd/system/vf2-frontend.service <<'EOF'
[Unit]
Description=VF2 Frontend
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/comtop/workspace/VF2/frontend
ExecStart=npm run dev -- --host 0.0.0.0 --port 5174
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now vf2-backend vf2-frontend
```

### 🟠 3순위: 데이터 결함 일괄 정정
```sql
-- 1. SWAP 버그 수정 (8,006건)
UPDATE production_logs 
SET unit_quantity = quantity, quantity = unit_quantity
WHERE unit_quantity > 0 AND quantity > 0 AND unit_quantity < quantity;

-- 2. CHECK 제약 추가 (재발 방지)
ALTER TABLE production_logs ADD CONSTRAINT chk_unit_qty_gte_qty 
CHECK (unit_quantity >= quantity);

-- 3. 유일 제약 추가
ALTER TABLE production_logs ADD CONSTRAINT uniq_productionlog_full_key
UNIQUE (date, machine_number, mold_number, product_name, color1, color2,
        unit, quantity, unit_quantity);

-- 4. 데크타일 color2 정정
UPDATE production_logs SET color2 = 'BLACK' WHERE mold_number = '114' AND color1 = 'Black' AND color2 = '';
UPDATE production_logs SET color2 = 'IVORY 1154' WHERE mold_number = '114' AND color1 = 'Ivory' AND color2 = '';
UPDATE production_logs SET color2 = 'WHITE 180' WHERE mold_number = '114' AND color1 = 'WHITE2' AND color2 = '';

-- 5. 빈 moldNumber 정리 (14건)
DELETE FROM production_logs WHERE mold_number IS NULL OR mold_number = '';

-- 6. color2 표준화
UPDATE production_logs SET color2 = 'WHITE 180' WHERE color2 = 'White 180';
```

### 🟠 4순위: production_plans 테이블 생성
```sql
-- 마이그레이션 스크립트 실행 필요 (vf2 스킬 references/db-bulk-import-procedure.md 참조)
```

### 🟡 5순위: 크론 429 토큰 한도 대응
- Token Plan 업그레이드 또는 폴백 모델 구성
- Wiki 관련 크론 5개 즉시 복구 필요

---

## 참고
- 보고서 원본: `/home/comtop/workspace/VF2/VF2-Self-Check-20260820.md`
- 직전 nightly: vf2-nightly-2026-08-17.md
- 직전 self-check: VF2-Self-Check-20260819.md
- Git 커밋: 로컬 전용 (push 실패 — PAT 토큰 만료 지속)