# LS 차량 정보 DB 동기화 (PostgreSQL)

**최종 업데이트**: 2026-06-03 (주현 김)
**대상**: 쿠팡 LS (ls.coupang.com) 차량 정보를 PostgreSQL `ls_vehicle` DB에 저장
**목적**: 매일매일 차량 정보 가져와서 중복 제거, 운전자 변경 이력 추적

## 1. DB 설정

| 항목 | 값 |
|---|---|
| PostgreSQL 버전 | 16.14 (Ubuntu) |
| DB 이름 | ls_vehicle |
| User | ls_user |
| Host | 127.0.0.1:5432 |
| 인증 | trust (임시, localhost only) |
| 비번 | `/tmp/ls_vehicle_db_pass.txt` (자동생성 24자) |

## 2. 테이블 4개

### vehicles (차량 마스터)
- `vehicle_id` PK
- `truck_num` UNIQUE
- `template_id` (90626/90628/90269/101740)
- `tonnage` (5T/11T/14T)

### drivers (운전자 마스터)
- `driver_id` PK
- `driver_name`, `driver_phone`
- `is_temporary` (임시 운전자 플래그)
- UNIQUE(name, phone)

### ls_vehicle_snapshot (LS 일일 스냅샷, 원본)
- `snapshot_id` PK
- `order_date`, `template_id`, `truck_num`, `driver_name`, `driver_phone`
- `order_status` (SUBMITTED/CONFIRMED/CANCELED/BACK)
- `raw_data` JSONB
- UNIQUE(order_date, template_id)

### vehicle_driver_assignments (차량-운전자 매핑 이력)
- `assignment_id` PK
- `vehicle_id`, `driver_id` FK
- `start_date`, `end_date` (NULL=현재 운행)
- `is_temporary` (케이스 2)
- `notes` (변경 사유)

## 3. 케이스 자동 분류

### 케이스 1: 차량번호+전화번호 동일, 이름만 다름
- = 정식 운전자 변경 (교대)
- 기존 assignment 종료, 새 assignment 생성
- notes: "운전자 변경: {old} → {new}"

### 케이스 2: 차량번호 동일, 이름+전화 모두 다름
- = 임시 운전자
- 기존 정식 assignment 유지, 임시 assignment 추가
- notes: "임시 운전자 (기존: {old_name}/{old_phone})"

## 4. 실행

```bash
source /tmp/po_venv/bin/activate
python3 ~/.hermes/skills/automation/ls-vehicle-sync/scripts/sync_ls_to_db.py 2026-06-03
```

## 5. Pitfalls (실제 경험 2026-06-03)

1. **LS API dateFrom/dateTo 무시**: 서버는 항상 최신 50건 반환. `orderDate`로 클라이언트 필터 필수
2. **truckInfo 객체 비어있음**: CONFIRMED인데 차량번호/기사 모두 None. PDF로 보충 필요
3. **[DELETED] 플레이스홀더**: CANCELED 차량에 "[DELETED]" 문자열. None 정규화 후 처리
4. **pg_hba.conf trust 임시**: 작업 중에는 trust, 완료 후 scram-sha-256로 복구

## 6. 6/3 동기화 결과 (검증됨)

- 50건 서버 응답 → 3건 필터 (6/3)
- 6/3 활성 3건 모두 snapshot 저장
- vehicles/drivers/assignments = 0건 (차량번호 부재로 매핑 안 됨)
- 다음 단계: `LinehaulSlip-{id}.pdf` 파싱 → 차량번호/기사/연락처 추출 → vehicles/drivers 보강

## 7. 관련

- 스킬: `~/.hermes/skills/automation/ls-vehicle-sync/SKILL.md`
- LS 자동화: `~/.hermes/skills/automation/ls-coupang/SKILL.md`
