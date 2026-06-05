-- LS 차량-운전자 매핑 테이블
-- 기준일: 2026-06-03
-- 운영원칙: 매일 LS에서 차량 정보 가져와서 중복 제거 INSERT
-- 케이스 1: 차량번호+전화번호 동일, 이름만 다름 → 운전자 변경
-- 케이스 2: 차량번호 동일, 이름+전화번호 모두 다름 → 임시 운전자 (별도 레코드)

-- 1) 메인 테이블: 차량 마스터
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id      SERIAL PRIMARY KEY,
    truck_num       VARCHAR(20) NOT NULL UNIQUE,  -- 차량번호 (예: 경기89자3822)
    template_id     VARCHAR(20),                  -- LS 템플릿 ID (90626, 90628, 90269, 101740)
    tonnage         VARCHAR(10),                  -- 5T / 11T / 14T
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- 2) 운전자 마스터
CREATE TABLE IF NOT EXISTS drivers (
    driver_id       SERIAL PRIMARY KEY,
    driver_name     VARCHAR(50) NOT NULL,
    driver_phone    VARCHAR(20) NOT NULL,
    is_temporary    BOOLEAN DEFAULT FALSE,  -- 임시 운전자 여부
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(driver_name, driver_phone)
);

-- 3) LS 일일 차량 스냅샷 (원본)
CREATE TABLE IF NOT EXISTS ls_vehicle_snapshot (
    snapshot_id     SERIAL PRIMARY KEY,
    order_date      DATE NOT NULL,           -- 오더 날짜 (예: 2026-06-03)
    template_id     VARCHAR(20),              -- 90626 / 90628 / 90269 / 101740
    truck_num       VARCHAR(20),              -- 차량번호 (없을 수 있음)
    driver_name     VARCHAR(50),              -- 기사명
    driver_phone    VARCHAR(20),              -- 기사 연락처
    order_status    VARCHAR(20),              -- SUBMITTED / CONFIRMED / CANCELED / BACK
    request_time    VARCHAR(30),              -- "20:00:00" 형식
    truck_request_id BIGINT,                  -- LS 오더 ID
    raw_data        JSONB,                    -- 전체 API 응답 (디버깅/감사)
    fetched_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(order_date, template_id)           -- 하루에 템플릿당 1건
);

-- 4) 차량-운전자 매핑 (이력 추적)
-- 케이스 1 (정식 운전자 변경): 같은 vehicle_id에 새 driver_id 연결, old_assignment에 end_date 설정
-- 케이스 2 (임시 운전자): 별도 assignment 레코드 (is_temporary=TRUE)
CREATE TABLE IF NOT EXISTS vehicle_driver_assignments (
    assignment_id   SERIAL PRIMARY KEY,
    vehicle_id      INT NOT NULL REFERENCES vehicles(vehicle_id),
    driver_id       INT NOT NULL REFERENCES drivers(driver_id),
    start_date      DATE NOT NULL,
    end_date        DATE,                     -- NULL = 현재 운행 중
    is_temporary    BOOLEAN DEFAULT FALSE,    -- 케이스 2 (임시 운전자)
    source_snapshot INT REFERENCES ls_vehicle_snapshot(snapshot_id),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_vehicles_truck_num ON vehicles(truck_num);
CREATE INDEX IF NOT EXISTS idx_drivers_phone ON drivers(driver_phone);
CREATE INDEX IF NOT EXISTS idx_drivers_name_phone ON drivers(driver_name, driver_phone);
CREATE INDEX IF NOT EXISTS idx_snapshot_date ON ls_vehicle_snapshot(order_date);
CREATE INDEX IF NOT EXISTS idx_assignments_vehicle ON vehicle_driver_assignments(vehicle_id, end_date);

-- 확인
SELECT 'tables created' AS status;
