# VF 프로젝트 - 창고 관리 시스템 설계

## 🎯 요구사항

### 1. 창고 구분 시스템
- **생산동**: A, B 구역
- **생산동 창고**: C, D (씨하고 뒤)
- **물류동 창고**: E, F, G, H, I, J

### 2. 재고 자동 계산
- "로코스 8개 화이트 한 팔레트" → DB 확인 → "32박스"
- 제품별 박스/팔레트 변환 규칙
- 자동 정리 시스템

### 3. 실시간 재고 관리
- 매일 출고 수량에 따른 재고 변동
- 창고 위치 추적
- 재고 변동 이력

---

## 🗄️ 데이터베이스 설계

### 1. 창고 테이블 (Warehouse)
```sql
CREATE TABLE warehouse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(2) NOT NULL UNIQUE,  -- A, B, C, D, E, F, G, H, I, J
    name VARCHAR(50) NOT NULL,        -- 창고 이름
    type VARCHAR(20) NOT NULL,        -- '생산동', '생산동창고', '물류동창고'
    location_description TEXT,        -- 위치 설명
    capacity INTEGER,                 -- 최대 수용량 (박스 단위)
    current_usage INTEGER DEFAULT 0,  -- 현재 사용량
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 제품 박스 변환 테이블 (ProductConversion)
```sql
CREATE TABLE product_conversion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(100) NOT NULL,      -- '로코스', '토이', '와이드' 등
    color VARCHAR(50),                       -- '화이트', '블랙' 등
    pieces_per_box INTEGER NOT NULL,         -- 박스당 개수
    boxes_per_pallet INTEGER NOT NULL,       -- 팔레트당 박스 수
    standard_unit VARCHAR(20) DEFAULT 'pcs', -- 기본 단위
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 재고 테이블 (Inventory)
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    warehouse_code VARCHAR(2) NOT NULL,      -- 창고 코드 (A-J)
    quantity INTEGER NOT NULL,               -- 수량 (기본 단위)
    unit VARCHAR(20) DEFAULT 'pcs',          -- 단위: pcs, box, pallet
    calculated_boxes INTEGER,                -- 계산된 박스 수
    calculated_pallets INTEGER,              -- 계산된 팔레트 수
    last_updated DATE NOT NULL,              -- 마지막 업데이트 일자
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_code) REFERENCES warehouse(code)
);
```

### 4. 재고 변동 이력 (InventoryHistory)
```sql
CREATE TABLE inventory_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL,        -- '입고', '출고', '조정'
    previous_quantity INTEGER,
    new_quantity INTEGER,
    change_amount INTEGER,
    change_reason TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id)
);
```

---

## 🔢 제품 변환 규칙

### 기본 변환 규칙
| 제품 | 색상 | 개수/박스 | 박스/팔레트 | 팔레트/개수 |
|------|------|-----------|-------------|-------------|
| 로코스 | 화이트 | 8개 | 32박스 | 256개 |
| 로코스 | 블랙 | 8개 | 32박스 | 256개 |
| 토이 | 화이트 | 10개 | 30박스 | 300개 |
| 와이드 | 화이트 | 6개 | 36박스 | 216개 |
| 모던+ | 화이트 | 8개 | 32박스 | 256개 |

### 계산 공식
```
1. 개수 → 박스: boxes = quantity / pieces_per_box
2. 박스 → 팔레트: pallets = boxes / boxes_per_pallet
3. 팔레트 → 개수: quantity = pallets * boxes_per_pallet * pieces_per_box
```

---

## 🚀 구현 계획

### 1단계: 데이터베이스 마이그레이션
- 새 테이블 생성
- 기존 데이터 마이그레이션
- 기본 데이터 삽입 (창고 정보, 변환 규칙)

### 2단계: API 엔드포인트 개발
```
GET    /api/warehouse/              # 창고 목록
POST   /api/warehouse/              # 창고 추가
GET    /api/inventory/              # 재고 목록
POST   /api/inventory/calculate/    # 재고 계산
PUT    /api/inventory/{id}/         # 재고 수정
GET    /api/inventory/history/      # 변동 이력
```

### 3단계: 자동 계산 엔진
```python
def calculate_inventory(product_name, color, quantity, unit):
    """
    제품 수량을 자동으로 계산
    예: "로코스 8개 화이트 한 팔레트" → 32박스, 256개
    """
    # 1. 변환 규칙 조회
    conversion = get_conversion_rule(product_name, color)
    
    # 2. 단위 변환
    if unit == 'pallet':
        boxes = quantity * conversion['boxes_per_pallet']
        pieces = boxes * conversion['pieces_per_box']
    elif unit == 'box':
        boxes = quantity
        pieces = boxes * conversion['pieces_per_box']
    else:  # pcs
        pieces = quantity
        boxes = pieces / conversion['pieces_per_box']
    
    return {
        'pieces': pieces,
        'boxes': boxes,
        'pallets': boxes / conversion['boxes_per_pallet'],
        'conversion_rule': conversion
    }
```

### 4단계: 웹 인터페이스
- 창고 현황 대시보드
- 재고 조회 및 검색
- 입출고 관리
- 실시간 업데이트

---

## 📊 초기 데이터

### 창고 데이터
```sql
INSERT INTO warehouse (code, name, type) VALUES
('A', '생산동 A구역', '생산동'),
('B', '생산동 B구역', '생산동'),
('C', '생산동 창고 C', '생산동창고'),
('D', '생산동 창고 D', '생산동창고'),
('E', '물류동 창고 E', '물류동창고'),
('F', '물류동 창고 F', '물류동창고'),
('G', '물류동 창고 G', '물류동창고'),
('H', '물류동 창고 H', '물류동창고'),
('I', '물류동 창고 I', '물류동창고'),
('J', '물류동 창고 J', '물류동창고');
```

### 제품 변환 규칙
```sql
INSERT INTO product_conversion (product_name, color, pieces_per_box, boxes_per_pallet) VALUES
('로코스', '화이트', 8, 32),
('로코스', '블랙', 8, 32),
('로코스', '그레이', 8, 32),
('토이', '화이트', 10, 30),
('토이', '블랙', 10, 30),
('와이드', '화이트', 6, 36),
('와이드', '블랙', 6, 36),
('모던+', '화이트', 8, 32),
('모던+', '블랙', 8, 32);
```

---

## 🔧 개발 우선순위

### 높음 (High)
1. 데이터베이스 테이블 생성
2. 기본 API 엔드포인트
3. 자동 계산 로직

### 중간 (Medium)
1. 웹 인터페이스
2. 실시간 업데이트
3. 보고서 생성

### 낮음 (Low)
1. 고급 분석 기능
2. 예측 알고리즘
3. 모바일 앱

---

## 📈 기대 효과

1. **정확한 재고 관리**: 실시간 창고 위치 추적
2. **자동 계산**: 수동 계산 오류 제거
3. **효율성 향상**: 입출고 프로세스 최적화
4. **데이터 기반 의사결정**: 정확한 재고 데이터 제공

---

## ⚠️ 고려사항

1. **기존 시스템 통합**: 현재 VF 프로젝트와의 호환성
2. **데이터 마이그레이션**: 기존 재고 데이터 이전
3. **사용자 교육**: 새 시스템 사용 방법 교육
4. **테스트**: 충분한 테스트 후 배포