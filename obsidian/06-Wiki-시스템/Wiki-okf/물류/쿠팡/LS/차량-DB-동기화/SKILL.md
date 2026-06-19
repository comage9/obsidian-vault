---
name: ls-vehicle-sync
description: 'LS 차량 정보를 PostgreSQL ls_vehicle DB에 동기화. 매일 자동 실행, 차량-운전자 매핑 이력 추적, 케이스 1(운전자 변경)/케이스 2(임시 운전자) 자동 분류. 트리거: 차량 DB 동기화, LS DB 저장, 차량 이력.'
---

# LS Vehicle Sync (PostgreSQL)

## 트리거
- "차량 DB 동기화"
- "LS DB 저장"
- "차량 이력"
- "차량 정보 DB"

## DB 정보
- **DB**: ls_vehicle (PostgreSQL 16.14)
- **User**: ls_user
- **Host**: 127.0.0.1:5432
- **비번**: 자동생성 (`/tmp/ls_vehicle_db_pass.txt`)

## 테이블 스키마

### vehicles (차량 마스터)
- `vehicle_id` SERIAL PK
- `truck_num` VARCHAR(20) UNIQUE
- `template_id` VARCHAR(20) — 90626/90628/90269/101740
- `tonnage` VARCHAR(10) — 5T/11T/14T
- `is_active` BOOLEAN
- `created_at`, `updated_at`

### drivers (운전자 마스터)
- `driver_id` SERIAL PK
- `driver_name` VARCHAR(50)
- `driver_phone` VARCHAR(20)
- `is_temporary` BOOLEAN — 임시 운전자 플래그
- UNIQUE(driver_name, driver_phone)

### ls_vehicle_snapshot (LS 일일 스냅샷, 원본)
- `snapshot_id` SERIAL PK
- `order_date` DATE
- `template_id`, `truck_num`, `driver_name`, `driver_phone`
- `order_status` — SUBMITTED/CONFIRMED/CANCELED/BACK
- `request_time` VARCHAR(30)
- `truck_request_id` BIGINT
- `raw_data` JSONB — 전체 API 응답
- UNIQUE(order_date, template_id) — 하루에 템플릿당 1건

### vehicle_driver_assignments (차량-운전자 매핑 이력)
- `assignment_id` SERIAL PK
- `vehicle_id`, `driver_id` FK
- `start_date`, `end_date` (NULL = 현재 운행 중)
- `is_temporary` BOOLEAN — 케이스 2 (임시 운전자)
- `source_snapshot` FK
- `notes` TEXT — 변경 사유

## 케이스 분류 로직

### 케이스 1: 차량번호+전화번호 동일, 이름만 다름
- = 정식 운전자 변경 (교대/대체)
- 기존 assignment 종료 (end_date = 오늘)
- 새 assignment 생성 (is_temporary=FALSE)
- notes: "운전자 변경: {old} → {new}"

### 케이스 2: 차량번호 동일, 이름+전화번호 모두 다름
- = 임시 운전자 (다른 사람이 그 차량으로 운행)
- 기존 정식 assignment 유지
- 새 임시 assignment 추가 (is_temporary=TRUE)
- notes: "임시 운전자 (기존: {old_name}/{old_phone})"

### 케이스 0: 신규 차량/정보
- 새 assignment 생성 (is_temporary=FALSE)
- notes: "신규 등록"

## 실행

```bash
# 1) 가상환경 활성화
source /tmp/po_venv/bin/activate

# 2) 동기화 실행 (날짜 지정 또는 오늘)
python3 ~/.hermes/skills/automation/ls-vehicle-sync/scripts/sync_ls_to_db.py 2026-06-03

# 3) 결과 확인
psql -h 127.0.0.1 -U ls_user -d ls_vehicle -c "
  SELECT v.truck_num, v.tonnage, d.driver_name, d.driver_phone, vda.notes
  FROM vehicles v
  JOIN vehicle_driver_assignments vda ON v.vehicle_id = vda.vehicle_id AND vda.end_date IS NULL
  JOIN drivers d ON vda.driver_id = d.driver_id
  ORDER BY v.vehicle_id
"
```

## Pitfalls

### 1. LS API dateFrom/dateTo 무시
- 서버가 50건 반환 (전체 최신순)
- **`orderDate` 필드로 클라이언트 필터 필수**
- 필터 전 50건 → 필터 후 3건 (6/3의 경우)

### 2. truckInfo 객체 비어있음
- `/order` API 응답에 `truckInfo`가 None 또는 빈 dict
- **차량번호는 `LinehaulSlip-{id}.pdf`에서 추출** (스킬 ls-coupang/references/truck-info-source-comparison.md)
- 현재는 snapshot만 저장, vehicles/drivers는 PDF 가져온 후 갱신

### 3. [DELETED] 플레이스홀더
- CANCELED된 차량에 `driver_name='[DELETED]', driver_phone='[DELETED]'` 표시
- **None으로 정규화** 후 처리
- CANCELED는 vehicles/drivers 갱신 안 함 (스냅샷만)

### 4. pg_hba.conf trust 모드 (해결 완료, 2026-06-03)
- DB 생성 직후 `host 127.0.0.1/32 scram-sha-256`를 `trust`로 변경
- **작업 완료 후 scram-sha-256로 복구 완료** (현재 상태)
- **비번 저장**: `~/.pgpass` (chmod 600, 59 B)
- **Python `DB_DSN`**: 비번 하드코딩 X, `~/.pgpass` 또는 `PGPASSWORD` 환경변수에서 자동 로드 (보안 운영원칙)
  ```bash
  sudo sed -i 's/^host    all             all             127.0.0.1\/32            trust/host    all             all             127.0.0.1\/32            scram-sha-256/' /etc/postgresql/16/main/pg_hba.conf
  sudo systemctl restart postgresql
  ```

### 5. PostgreSQL 비번 인증 단계
- `ls_user` CREATE 시 PASSWORD '...'로 비번 설정됨
- scram-sha-256 인증 시 자동 생성 24자 비번이 매칭 실패할 수 있음
- **임시 우회**: pg_hba.conf `host 127.0.0.1/32`를 `trust`로 (위 4번)
- **영구 해결**: trust 상태에서 postgres로 접속 후 `ALTER USER ls_user WITH PASSWORD '...'` 실행

### 6. psycopg2 JSONB dict 직접 못 넣음
- `cur.execute(... , {'raw_data': order})` → `psycopg2.ProgrammingError: can't adapt type 'dict'`
- **반드시 `Json(order)` 래퍼** 사용:
  ```python
  from psycopg2.extras import Json
  cur.execute("""... raw_data = EXCLUDED.raw_data ... """, {'raw_data': Json(order), ...})
  ```

### 7. PostgreSQL sudo 권한 필요
- `apt install` / `systemctl restart` / `pg_hba.conf` 수정 모두 root 또는 sudo 필요
- **Hermes 시스템이 `sudo -S` (stdin 파이프) 차단** (보안 규칙)
- **해결**: 사용자가 직접 PC 새 터미널에서 sudo 명령 실행
- **자동화 불가**: 사용자 PC 작업 단계는 매뉴얼로 안내

### 8. sudo 비번 차이 (실제 경험 2026-06-03)
- 사용자 진술 "비번 2242" → **틀린 비번** (3회 실패, sudo 잠금)
- 정확한 비번 모르면 다른 우회 필요 (recovery mode, NOPASSWD, 다른 사용자)
- **정직 보고**: 2242는 비번 아님, 다른 비번 필요

## cron 자동화 (예정)

```bash
# 매일 13:30 KST (LS 등록 후 30분)
30 13 * * * /home/comage/.hermes/skills/automation/ls-vehicle-sync/scripts/sync_ls_to_db.py $(date +\%Y-\%m-\%d)
```

## 참고
- LS API: `~/.hermes/skills/automation/ls-coupang/SKILL.md`
- 트럭 정보 소스: `ls-coupang/references/truck-info-source-comparison.md`
- DB 스키마: `ls-vehicle-sync/scripts/schema.sql`
- PostgreSQL 설치/설정 단계: `ls-vehicle-sync/references/postgresql-install-and-setup.md` (sudo 우회, trust/scram, psycopg2 JSONB, 9가지 Pitfalls 표)
## 2026-06-03 업데이트: Tracking API + PDF 다운로드 통합

### fetch_ls_daily.py (신규, 2026-06-03)
- Tracking API + PDF 다운로드 + DB 저장을 한 번에
- 일일 운영 자동화 권장 스크립트
- `python3 ~/.hermes/skills/automation/ls-vehicle-sync/scripts/fetch_ls_daily.py 2026-06-03`

### Tracking API 톤수 필드 (2026-06-03 발견)
- 응답에 `truckType: {name: "5T" | "11T" | "14T"}` 별도 필드 존재
- **이전 메모리의 TEMPLATE_TONNAGE는 fallback** (API 응답 우선)
- 현재 템플릿 매핑 (2026-06-03 사용자 확인):
  - 90626 = 5T (예전 11T에서 변경됨)
  - 90628 = 5T
  - 90269 = 11T
  - 101740 = 5T

### PDF endpoint (2026-06-03 발견)
- `GET /linehaul/slip/generate?truckRequestId={id}&locale=ko_KR`
- Headers: `Accept: application/json,application/pdf` (필수)
- 응답: application/pdf, 1.5MB, 1페이지
- 파싱: `pdftotext -layout` → 운행일자/차량번호/트럭바코드/성함/연락처
- ⚠️ **POST 아님, GET 방식**
- ⚠️ **PDF 파일 저장 불필요, 정보만 추출** (사용자 진술 2026-06-03)
