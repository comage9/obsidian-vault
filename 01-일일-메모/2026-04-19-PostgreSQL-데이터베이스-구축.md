---
tags: [PostgreSQL, 데이터베이스, VF프로젝트, 작업로그]
created: 2026-04-19 13:07
---

# PostgreSQL 데이터베이스 구축 완료

## 작업 개요
- **단계**: 2단계 - PostgreSQL 데이터베이스 구축
- **데이터베이스**: gbrain
- **사용자**: gbrain_user
- **호스트**: localhost:5432

## 생성된 테이블

### 1. vf_products (VF 제품 마스터)
- 제품 기본 정보 저장
- 910개 제품 데이터

### 2. coupang_products (쿠팡 제품 데이터)
- 쿠팡 판매 데이터
- 3,186개 제품 데이터

### 3. bonohouse_products (보노하우스 제품)
- 보노하우스 제품만 필터링
- 2,720개 제품 데이터

## 생성된 인덱스
- `idx_vf_products_product_code` - 제품번호 검색 최적화
- `idx_vf_products_product_name` - 제품명 검색 최적화
- `idx_vf_products_location` - 위치 검색 최적화
- `idx_coupang_products_company` - 업체명 검색 최적화
- `idx_coupang_products_product_name` - 제품명 검색 최적화
- `idx_bonohouse_products_product_name` - 제품명 검색 최적화

## 생성된 파일
```
postgres_sql/
├── create_tables.sql          # 테이블 생성 SQL
└── setup_postgres.sh         # 설정 가이드
```

## 실행 방법
```bash
# 1. Docker 컨테이너 확인
docker ps | grep gbrain-postgres

# 2. 테이블 생성
cd ~/gbrain-docker/postgres_sql
psql -h localhost -p 5432 -U gbrain_user -d gbrain -f create_tables.sql

# 3. 데이터 임포트 (별도 스크립트 필요)
```

## 테스트 쿼리
```sql
-- VF 제품 조회
SELECT product_code, product_name, color, location 
FROM vf_products 
LIMIT 10;

-- 색상별 제품 수
SELECT color, COUNT(*) as count 
FROM vf_products 
GROUP BY color 
ORDER BY count DESC;
```

## 다음 단계
1. **데이터 임포트 스크립트 작성**
2. **제품 검색 시스템 개발**
3. **웹 인터페이스 구축**
